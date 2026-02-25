import json
import os
import pdb
import random
from datetime import datetime
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Union, cast
from logging import getLogger, basicConfig, DEBUG

import requests
from pydicom.datadict import dictionary_VM, dictionary_VR
from pydicom.dataset import FileDataset, Dataset
from pydicom.filewriter import write_file_meta_info
from pydicom.multival import MultiValue
from pydicom.sequence import Sequence
from pydicom.sr.codedict import codes
from pydicom.uid import generate_uid
from pydicom import sr
from pynetdicom import events, AE, DEFAULT_TRANSFER_SYNTAXES, ALL_TRANSFER_SYNTAXES, debug_logger, \
    AllStoragePresentationContexts
from pynetdicom.events import Event
from pynetdicom import sop_class

from apps.core.services.sr_parser import parse_ds
from apps.core.services.utils import *

basicConfig(filename='./logs/storage_scp.log', level=DEBUG)
logger = getLogger()
logger.setLevel("DEBUG")
debug_logger()
logger.info("-----------------------------------------------------------------------------------")

archive_dicom_files = True

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
        print('AE', event.assoc.requestor.ae_title.strip().decode('UTF-8'))
        return 0x0000

    def handle_c_store(self, event: Event) -> int:
        ds = event.dataset
        ds.file_meta = event.file_meta

        metadata: Dict[str, Optional[ParsedElementValue]] = {
            "CallingAET": cast(str, event.assoc.requestor.ae_title.strip()),
            "SopInstanceUID": safe_get(ds, 0x00080018),
            "StudyInstanceUID": safe_get(ds, 0x0020000D),
            "Modality": safe_get(ds, 0x00080060),
        }
        log_message_meta = " - ".join([f"{k}={v}" for k, v in metadata.items() if v])
        logger.info(f"Processed C-STORE {log_message_meta}")

        print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        studyId = ds.StudyInstanceUID
        print('Study Instance UID', studyId)

        if ds.Modality == 'SR':
            print('Structured report received')
            # print(ds)
            concept_name_code_sequence = safe_get(ds, 0x0040A043)
            #print('Concept Name Code Sequence Attribute', concept_name_code_sequence)
            content_template_sequence = safe_get(ds, 0x0040A504)
            #print('Content Template Sequence', content_template_sequence)
            content_sequence = safe_get(ds, 0x0040A730)
            #print('Content Sequence', content_sequence)

            code_value = concept_name_code_sequence[0].CodeValue
            #print(code_value)

            if code_value == '125000':
                # OB-GYN Ultrasound Procedure Report
                print('OB-GYN Ultrasound Procedure Report')
                result = parse_ds(ds)
                print(result)
                post_data = {'study_uid': studyId, 'data': json.dumps(result)}
                response = requests.post(f'{web_url}:{web_port}/worklists/sr/', data=post_data)
            if code_value == '125100':
                # Vascular Ultrasound Procedure Report
                print('Vascular Ultrasound Procedure Report')
            if code_value == '125200':
                # Adult Echocardiography Procedure Report
                print('Adult Echocardiography Procedure Report')
            for item in content_sequence:
                pass
                #print(item)
            # pdb.set_trace()

        else:
            print('Image received')

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
                post_data = {'study_uid': studyId, 'path': os.path.abspath(out_img_file)}
                response = requests.post(f'{web_url}:{web_port}/worklists/image/', data=post_data)
                # res = response.json()
            except:
                logger.info(f"Received an animated image sequence")

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
        ]
        self.ae.start_server(self.address, block=True, evt_handlers=self.handlers)


def main() -> None:
    run_server()


def run_server():
    print('Running Storage server')
    config = ServiceClassProviderConfig(implementation_class_uid=generate_uid(),
                                        port=os.environ.get('EE_STORE_SCP_PORT', 11113))
    server = ServiceClassProvider("EXPERTECHO", config)
    server.start()


if __name__ == "__main__":
    main()
