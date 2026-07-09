import json
import logging as _logging
import os
import pdb
import random
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Union, cast
from logging import getLogger, DEBUG

import requests
from pydicom.datadict import dictionary_VM, dictionary_VR
from pydicom.dataset import FileDataset, Dataset
from pydicom.filewriter import write_file_meta_info
from pydicom.multival import MultiValue
from pydicom.sequence import Sequence
from pydicom.sr.codedict import codes
from pydicom.uid import generate_uid
from pydicom import sr
from pynetdicom import events, AE, DEFAULT_TRANSFER_SYNTAXES, ALL_TRANSFER_SYNTAXES, \
    AllStoragePresentationContexts
from pynetdicom.events import Event
from pynetdicom import sop_class

from apps.core.services.sr_parser import parse_ds
from apps.core.services.utils import *

from pydicom.dataset import Dataset as _Dataset
from pydicom.sequence import Sequence as _Sequence
from pydicom.multival import MultiValue as _MultiValue


def _sanitize(obj):
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    elif isinstance(obj, _Dataset):
        return _sanitize(dict(obj))
    elif hasattr(obj, 'value'):
        return _sanitize(obj.value)
    elif isinstance(obj, _MultiValue):
        return list(obj)
    return obj

logger = getLogger('dicom.storage')
logger.setLevel(DEBUG)
_handler = _logging.FileHandler('./logs/storage_scp.log')
logger.addHandler(_handler)

pynetdicom_logger = _logging.getLogger('pynetdicom')
pynetdicom_logger.setLevel(DEBUG)
_pynetdicom_handler = _logging.FileHandler('./logs/pynetdicom.log')
pynetdicom_logger.addHandler(_pynetdicom_handler)

logger.info("-----------------------------------------------------------------------------------")

archive_dicom_files = True

_study_images = {}

web_url = os.environ.get('EE_URL', 'http://localhost')
web_port = os.environ.get('EE_HTTP_PORT', '8001')


class ServiceClassProvider:
    def __init__(self, aet: str, config: ServiceClassProviderConfig) -> None:
        self.config = config
        self.address = ("0.0.0.0", config.port)

        self.ae = AE(ae_title=aet)
        self.ae.implementation_class_uid = config.implementation_class_uid
        self.ae.implementation_version_name = f'{aet}_{config.implementation_class_uid.split(".")[-1]}'[:16]
        # Unlimited PDU size
        self.ae.maximum_pdu_size = 0

        self.ae.supported_contexts = AllStoragePresentationContexts
        # Add JPEG and other transfer syntaxes to every supported context
        for cx in self.ae.supported_contexts:
            cx.transfer_syntax = ALL_TRANSFER_SYNTAXES

        self.ae.add_supported_context(sop_class.VerificationSOPClass, ALL_TRANSFER_SYNTAXES)

        # self.ae.require_calling_aet = ["MODALITY"]
        self.ae.require_calling_aet = []  # Leave blank to accept all caller AEs

        self.executor = ThreadPoolExecutor(max_workers=2)

    # Implement a handler for evt.EVT_C_ECHO
    def handle_echo(self, event: Event) -> int:
        """Handle a C-ECHO request event."""
        calling = event.assoc.requestor.ae_title.strip().decode('UTF-8')
        logger.info(f"C-ECHO received from {calling}")
        return 0x0000

    def handle_established(self, event: Event) -> int:
        """Log all negotiated presentation contexts on association."""
        try:
            assoc = event.assoc
            calling = assoc.requestor.ae_title.strip().decode('UTF-8')
            called = assoc.acceptor.ae_title.strip().decode('UTF-8') if hasattr(assoc, 'acceptor') else ''
            contexts = []
            for cx in assoc.negotiated:
                sop = cx.abstract_syntax
                ts = cx.transfer_syntax
                contexts.append(f"cx_id={cx.context_id} sop={sop} ts={ts}")
            logger.info(f"=== ASSOCIATION ESTABLISHED === calling={calling} called={called}")
            for c in contexts:
                logger.info(f"  Accepted context: {c}")
            has_sr = any('1.2.840.10008.5.1.4.1.1.88' in cx.abstract_syntax for cx in assoc.negotiated)
            if has_sr:
                logger.info(f"*** DEVICE {calling} NEGOTIATED SR CONTEXT ***")
        except Exception as e:
            logger.warning(f"Failed to log association details: {e}")
        return 0x0000

    def _process_sr(self, ds, studyId, called_aet, calling_aet):
        try:
            patient_name = str(ds.get('PatientName', ''))
            sop_class_uid = str(ds.get('SOPClassUID', ''))
            concept_name = ''
            code_value = ''
            try:
                cncs = ds.ConceptNameCodeSequence
                if cncs:
                    concept_name = str(cncs[0].CodeMeaning)
                    code_value = str(cncs[0].CodeValue)
            except Exception:
                pass
            logger.info(f"=== SR RECEIVED === patient='{patient_name}' study={studyId} calling_aet={calling_aet} sop_class={sop_class_uid} concept='{concept_name}' code={code_value}")
            if studyId in _study_images:
                _study_images[studyId]['sr_received'] = True
                logger.info(f"SR received for study {studyId} (patient={patient_name}) after {len(_study_images[studyId]['images'])} prior images")
            result = parse_ds(ds)
            logger.info(f"Parsed SR data for {patient_name}: {result}")
            if result:
                patient_name = str(ds.get('PatientName', ''))
                post_data = {
                    'study_uid': studyId,
                    'data': json.dumps(_sanitize(result)),
                    'called_aet': called_aet,
                    'calling_aet': calling_aet,
                    'patient_name': patient_name,
                }
                for attempt in range(3):
                    try:
                        response = requests.post(f'{web_url}:{web_port}/worklists/sr/', data=post_data, timeout=10)
                        logger.info(f"SR POST to /worklists/sr/ status={response.status_code}")
                        if response.status_code == 200:
                            break
                    except requests.RequestException as e:
                        logger.warning(f"SR POST attempt {attempt + 1} failed: {e}")
                        if attempt < 2:
                            __import__('time').sleep(1)
                    else:
                        if attempt < 2:
                            logger.warning(f"SR POST attempt {attempt + 1} returned {response.status_code}, retrying...")
                            __import__('time').sleep(1)
        except Exception as e:
            logger.error(f"Failed to process SR: {e}", exc_info=True)

    def _process_image(self, ds, studyId, outfile, filename, called_aet, calling_aet):
        out_img_file = outfile + '.jpg'
        try:
            patient_name = str(ds.get('PatientName', ''))
            logger.info(f"Image saved patient='{patient_name}' study={studyId} calling_aet={calling_aet}")
            if studyId not in _study_images:
                _study_images[studyId] = {'images': [], 'sr_received': False, 'patient_name': patient_name, 'calling_aet': calling_aet}
            _study_images[studyId]['images'].append({'file': filename, 'time': datetime.now().isoformat()})
            ds_to_jpeg(ds, out_img_file)
            post_data = {
                'study_uid': studyId,
                'path': os.path.abspath(out_img_file),
                'called_aet': called_aet,
                'calling_aet': calling_aet,
                'patient_name': patient_name,
            }
            requests.post(f'{web_url}:{web_port}/worklists/image/', data=post_data, timeout=30)
        except Exception as e:
            logger.error(f"Failed to save image for study {studyId}: {e}")
            try:
                if os.path.exists(out_img_file):
                    os.remove(out_img_file)
            except OSError:
                pass

    def _process_waveform(self, ds, studyId, called_aet):
        try:
            waveform_data = save_waveform(ds, studyId, called_aet)
            if waveform_data:
                logger.info(f'Waveform saved: {waveform_data}')
        except Exception as e:
            logger.error(f'Failed to save waveform: {e}')

    def handle_c_store(self, event: Event) -> int:
        try:
            ds = event.dataset
            ds.file_meta = event.file_meta

            called_aet = event.assoc.acceptor.ae_title.strip().decode('UTF-8') if hasattr(event.assoc, 'acceptor') else ''
            calling_aet = event.assoc.requestor.ae_title.strip().decode('UTF-8')

            # Reject images from unregistered devices
            try:
                from apps.core.models import Device
                if not Device.objects.filter(ae_title=calling_aet).exists():
                    logger.warning(f"Rejected C-STORE from unregistered device AE={calling_aet}")
                    return 0xC000
            except Exception as e:
                logger.error(f"Device lookup failed for AE={calling_aet}: {e}")
            metadata: Dict[str, Optional[ParsedElementValue]] = {
                "CallingAET": calling_aet,
                "CalledAET": called_aet,
                "SopInstanceUID": safe_get(ds, 0x00080018),
                "StudyInstanceUID": safe_get(ds, 0x0020000D),
                "Modality": safe_get(ds, 0x00080060),
            }
            sop_class_uid = str(event.file_meta.MediaStorageSOPClassUID) if event.file_meta else 'UNKNOWN'
            metadata["SOPClassUID"] = sop_class_uid
            log_message_meta = " - ".join([f"{k}={v}" for k, v in metadata.items() if v])
            logger.info(f"Processed C-STORE {log_message_meta}")

            studyId = ds.StudyInstanceUID
            logger.info(f'Study Instance UID: {studyId}')

            is_sr = ds.Modality == 'SR' or sop_class_uid.startswith('1.2.840.10008.5.1.4.1.1.88')
            logger.info(f"SR detection: sop_class_uid={sop_class_uid} modality={ds.get('Modality','')} is_sr={is_sr}")
            if is_sr:
                try:
                    cncs = ds.ConceptNameCodeSequence
                    concept = str(cncs[0].CodeMeaning) if cncs else 'N/A'
                    code_val = str(cncs[0].CodeValue) if cncs else 'N/A'
                except Exception:
                    concept = 'N/A'
                    code_val = 'N/A'
                logger.info(f"=== SR INVESTIGATION === sop_class={sop_class_uid} concept='{concept}' code={code_val} calling_aet={calling_aet} patient={safe_get(ds, 0x00100010)} study={studyId}")

            outfile = f'./data/studies/{studyId}/'
            if not os.path.exists(outfile):
                os.makedirs(outfile)

            filename = f"{random.randint(10000000, 99999999)}"
            if is_sr:
                outfile += 'sr_'
                outfile += filename
            else:
                outfile += 'img_'
                outfile += filename

            # Write raw DICOM file synchronously (fast I/O)
            dcm_path = outfile + '.dcm'
            if archive_dicom_files:
                with open(dcm_path, 'wb') as f:
                    f.write(b'\x00' * 128)
                    f.write(b'DICM')
                    write_file_meta_info(f, event.file_meta)
                    f.write(event.request.DataSet.getvalue())

            # Offload CPU-intensive processing to thread pool
            if is_sr:
                self.executor.submit(self._process_sr, ds, studyId, called_aet, calling_aet)
            elif ds.Modality in ['WF', 'OT'] or hasattr(ds, 'WaveformSequence'):
                self.executor.submit(self._process_waveform, ds, studyId, called_aet)
            else:
                self.executor.submit(self._process_image, ds, studyId, outfile, filename, called_aet, calling_aet)

            return 0x0000

        except Exception as e:
            logger.error(f"Unhandled error in C-STORE handler: {e}", exc_info=True)
            return 0xC000

    def start(self) -> None:
        logger.info(f"Starting DIMSE C-STORE AE on address={self.address} aet={self.ae.ae_title}")
        self.handlers = [
            (events.EVT_C_STORE, self.handle_c_store),
            (events.EVT_C_ECHO, self.handle_echo),
            (events.EVT_ESTABLISHED, self.handle_established),
        ]
        self.ae.start_server(self.address, block=True, evt_handlers=self.handlers)


def save_waveform(ds, study_uid, called_aet):
    """Save DICOM Waveform data and create preview image."""
    import io
    from PIL import Image, ImageDraw, ImageFont
    
    # Create waveform directory
    waveform_dir = f'./data/studies/{study_uid}/waveforms/'
    if not os.path.exists(waveform_dir):
        os.makedirs(waveform_dir)
    
    # Get SOP Instance UID
    sop_uid = safe_get(ds, 0x00080018) or f"wf_{random.randint(10000000, 99999999)}"
    
    # Try to extract waveform data and create a preview
    preview_path = None
    
    try:
        # Try to get waveform sequence data
        waveform_seq = safe_get(ds, 0x54001010)  # WaveformSequence
        
        if waveform_seq:
            # Create a simple visual representation of the waveform
            img = Image.new('RGB', (800, 200), color='white')
            draw = ImageDraw.Draw(img)
            
            # Draw some placeholder waveform visualization
            # In real implementation, this would decode actual waveform data
            draw.line([(50, 100), (750, 100)], fill='black', width=2)
            
            # Add text
            try:
                draw.text((50, 50), f"Waveform - {ds.Modality}", fill='black')
                draw.text((50, 150), f"SOP: {sop_uid}", fill='gray')
            except:
                pass
            
            # Save preview
            preview_filename = f"wf_{sop_uid[:8]}.jpg"
            preview_path = os.path.join(waveform_dir, preview_filename)
            img.save(preview_path, 'JPEG')
            
            # Save raw waveform data if needed
            data_file = os.path.join(waveform_dir, f"wf_{sop_uid[:8]}.bin")
            # Note: Actual waveform binary data would need proper extraction
            
            # Post to server
            patient_name = str(ds.get('PatientName', ''))
            post_data = {
                'study_uid': study_uid,
                'path': preview_path,
                'sop_uid': sop_uid,
                'called_aet': called_aet,
                'patient_name': patient_name,
            }
            response = requests.post(f'{web_url}:{web_port}/worklists/waveform/', data=post_data)
            
            return preview_path
    except Exception as e:
        logger.error(f"Error processing waveform: {e}")
    
    return None


def main() -> None:
    run_server()


def run_server():
    print('Running Storage server')
    config = ServiceClassProviderConfig(implementation_class_uid=generate_uid(),
                                        port=os.environ.get('EE_STORE_SCP_PORT', 11113))
    server = ServiceClassProvider("CABINETPRO", config)
    try:
        server.start()
    except OSError as e:
        logger.error(f"Storage server failed to start on port {config.port}: {e}")


if __name__ == "__main__":
    main()
