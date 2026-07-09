import json
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
_handler = __import__('logging').FileHandler('./logs/storage_scp.log')
logger.addHandler(_handler)
logger.info("-----------------------------------------------------------------------------------")

archive_dicom_files = True

_study_images = {}

web_url = os.environ.get('EE_URL', 'http://localhost')
web_port = os.environ.get('EE_HTTP_PORT', '8000')


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
        logger.info(f"C-ECHO from {event.assoc.requestor.ae_title.strip().decode('UTF-8')}")
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

    def handle_c_store(self, event: Event) -> int:
        ds = event.dataset
        ds.file_meta = event.file_meta

        called_aet = event.assoc.acceptor.ae_title.strip().decode('UTF-8') if hasattr(event.assoc, 'acceptor') else ''
        calling_aet = event.assoc.requestor.ae_title.strip().decode('UTF-8')
        metadata: Dict[str, Optional[ParsedElementValue]] = {
            "CallingAET": calling_aet,
            "CalledAET": called_aet,
            "SopInstanceUID": safe_get(ds, 0x00080018),
            "StudyInstanceUID": safe_get(ds, 0x0020000D),
            "Modality": safe_get(ds, 0x00080060),
        }
        log_message_meta = " - ".join([f"{k}={v}" for k, v in metadata.items() if v])
        logger.info(f"Processed C-STORE {log_message_meta}")

        studyId = ds.StudyInstanceUID
        logger.info(f"Study Instance UID: {studyId}")

        patient_name = str(ds.get('PatientName', ''))

        if ds.Modality == 'SR':
            if studyId in _study_images:
                _study_images[studyId]['sr_received'] = True
                logger.info(f"SR received for study {studyId} (patient={patient_name}) after {len(_study_images[studyId]['images'])} prior images")
            logger.info(f"=== SR INVESTIGATION === sop_class={safe_get(ds, 0x00080016)} calling_aet={calling_aet} patient={patient_name} study={studyId}")
            logger.info('Structured report received')
            concept_name_code_sequence = safe_get(ds, 0x0040A043)
            content_template_sequence = safe_get(ds, 0x0040A504)
            content_sequence = safe_get(ds, 0x0040A730)

            code_value = concept_name_code_sequence[0].CodeValue
            logger.info(f"SR concept code value: {code_value}")

            if code_value == '125000':
                logger.info('SR type: OB-GYN Ultrasound Procedure Report')
                result = parse_ds(ds)
                logger.info(f"SR parsed result: {result}")
                post_data = {'study_uid': studyId, 'data': json.dumps(result), 'called_aet': called_aet}
                response = requests.post(f'{web_url}:{web_port}/worklists/sr/', data=post_data)
            elif code_value == '125100':
                logger.info('SR type: Vascular Ultrasound Procedure Report')
            elif code_value == '125200':
                logger.info('SR type: Adult Echocardiography Procedure Report')
            for item in content_sequence:
                pass
                #print(item)
            # pdb.set_trace()

        else:
            logger.info(f"Image received patient='{patient_name}' study={studyId} calling_aet={calling_aet}")
            if studyId not in _study_images:
                _study_images[studyId] = {'images': [], 'sr_received': False, 'patient_name': patient_name, 'calling_aet': calling_aet}
            _study_images[studyId]['images'].append({'time': datetime.now().isoformat()})
            logger.info('Image received')

        outfile = f'./data/studies/{studyId}/'
        if not os.path.exists(outfile):
            os.makedirs(outfile)

        # filename = event.request.AffectedSOPInstanceUID
        filename = f"{random.randint(10000000, 99999999)}"
        if ds.Modality == 'SR':
            outfile += 'sr_'
            outfile += filename
        else:
            outfile += 'img_'
            outfile += filename
            # Enregistrer l'image
            out_img_file = outfile + '.jpg'
            try:
                ds_to_jpeg(ds, out_img_file)
                post_data = {'study_uid': studyId, 'path': os.path.abspath(out_img_file), 'called_aet': called_aet}
                response = requests.post(f'{web_url}:{web_port}/worklists/image/', data=post_data)
                # res = response.json()
            except Exception as e:
                logger.error(f"Failed to save image for study {studyId}: {e}")

        if archive_dicom_files:
            with open(outfile + '.dcm', 'wb') as f:
                # Write the preamble and prefix
                f.write(b'\x00' * 128)
                f.write(b'DICM')
                # Encode and write the File Meta Information
                write_file_meta_info(f, event.file_meta)
                # Write the encoded dataset
                f.write(event.request.DataSet.getvalue())

        return 0x0000

    def start(self) -> None:
        logger.info(f"Starting DIMSE C-STORE AE on address={self.address} aet={self.ae.ae_title}")
        self.handlers = [
            (events.EVT_C_STORE, self.handle_c_store),
            (events.EVT_C_ECHO, self.handle_echo),
            (events.EVT_ESTABLISHED, self.handle_established),
        ]
        self.ae.start_server(self.address, block=True, evt_handlers=self.handlers)


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
