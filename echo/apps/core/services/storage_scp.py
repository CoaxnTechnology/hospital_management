import json
import logging as _logging
import os
import pdb
import random
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
            # print(abstract_syntax.abstract_syntax)

        # self.ae.require_calling_aet = ["MODALITY"]
        self.ae.require_calling_aet = []  # Leave blank to accept all caller AEs

    # Implement a handler for evt.EVT_C_ECHO
    def handle_echo(self, event: Event) -> int:
        """Handle a C-ECHO request event."""
        calling = event.assoc.requestor.ae_title.strip().decode('UTF-8')
        logger.info(f"C-ECHO received from {calling}")
        return 0x0000

    def handle_c_store(self, event: Event) -> int:
        try:
            ds = event.dataset
            ds.file_meta = event.file_meta

            called_aet = cast(str, event.assoc.acceptor.ae_title.strip()) if hasattr(event.assoc, 'acceptor') else ''
            metadata: Dict[str, Optional[ParsedElementValue]] = {
                "CallingAET": cast(str, event.assoc.requestor.ae_title.strip()),
                "CalledAET": called_aet,
                "SopInstanceUID": safe_get(ds, 0x00080018),
                "StudyInstanceUID": safe_get(ds, 0x0020000D),
                "Modality": safe_get(ds, 0x00080060),
            }
            log_message_meta = " - ".join([f"{k}={v}" for k, v in metadata.items() if v])
            logger.info(f"Processed C-STORE {log_message_meta}")

            print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            studyId = ds.StudyInstanceUID
            print('Study Instance UID', studyId)

            sop_class_uid = str(event.file_meta.MediaStorageSOPClassUID) if event.file_meta else ''
            is_sr = ds.Modality == 'SR' or 'sr' in sop_class_uid.lower() or 'structuredreport' in sop_class_uid.lower()

            if is_sr:
                logger.info(f"SR received: StudyInstanceUID={studyId}, PatientName={str(ds.get('PatientName', ''))}, SOPClassUID={sop_class_uid}")
                try:
                    result = parse_ds(ds)
                    logger.info(f"Parsed SR data: {result}")
                    if result:
                        post_data = {'study_uid': studyId, 'data': json.dumps(result), 'called_aet': called_aet}
                        response = requests.post(f'{web_url}:{web_port}/worklists/sr/', data=post_data)
                        logger.info(f"SR POST to /worklists/sr/ status={response.status_code}")
                except Exception as e:
                    logger.error(f"Failed to process SR: {e}", exc_info=True)

            elif ds.Modality in ['WF', 'OT'] or hasattr(ds, 'WaveformSequence'):
                print(f'Waveform received: {ds.Modality}')
                try:
                    waveform_data = save_waveform(ds, studyId, called_aet)
                    if waveform_data:
                        print(f'Waveform saved: {waveform_data}')
                except Exception as e:
                    logger.error(f'Failed to save waveform: {e}')

            else:
                print('Image received')

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
                out_img_file = outfile + '.jpg'
                try:
                    ds_to_jpeg(ds, out_img_file)
                    patient_name = str(ds.get('PatientName', ''))
                    post_data = {
                        'study_uid': studyId,
                        'path': os.path.abspath(out_img_file),
                        'called_aet': called_aet,
                        'patient_name': patient_name,
                    }
                    response = requests.post(f'{web_url}:{web_port}/worklists/image/', data=post_data)
                except Exception as e:
                    logger.error(f"Failed to save image for study {studyId}: {e}")

            if archive_dicom_files:
                with open(outfile + '.dcm', 'wb') as f:
                    f.write(b'\x00' * 128)
                    f.write(b'DICM')
                    write_file_meta_info(f, event.file_meta)
                    f.write(event.request.DataSet.getvalue())

            return 0x0000

        except Exception as e:
            logger.error(f"Unhandled error in C-STORE handler: {e}", exc_info=True)
            return 0xC000

    def start(self) -> None:
        logger.info(f"Starting DIMSE C-STORE AE on address={self.address} aet={self.ae.ae_title}")
        self.handlers = [
            (events.EVT_C_STORE, self.handle_c_store),
            (events.EVT_C_ECHO, self.handle_echo),
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
    server.start()


if __name__ == "__main__":
    main()
