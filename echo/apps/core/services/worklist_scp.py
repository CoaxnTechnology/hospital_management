import json
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Union, cast
from logging import getLogger, basicConfig, DEBUG

import requests
from pydicom.datadict import dictionary_VM, dictionary_VR
from pydicom.dataset import FileDataset, Dataset
from pydicom.multival import MultiValue
from pydicom.sequence import Sequence
from pydicom.uid import generate_uid
from pynetdicom import events, AE, DEFAULT_TRANSFER_SYNTAXES, ALL_TRANSFER_SYNTAXES, debug_logger
from pynetdicom.events import Event
from pynetdicom import sop_class

basicConfig(filename='./logs/worklist_scp.log', level=DEBUG)
logger = getLogger()
logger.setLevel("DEBUG")
debug_logger()
logger.info("-----------------------------------------------------------------------------------")

m1 = Dataset()
m1.PatientID = '11788759296811'
m1.PatientName = 'Donia^Aloui'
m1.AccessionNumber = '122299'
m1.StudyInstanceUID = '1.2.826.0.1.3680043.8.498.27672981623877115699485941743652586519'
m1.RequestedProcedureDescription = 'lorem'
m1.RequestedProcedureID = '9000'

m2 = Dataset()
m2.PatientID = '11788759296822'
m2.PatientName = 'Ines^Karaoui'
m2.AccessionNumber = '133399'
m2.StudyInstanceUID = '1.2.826.0.1.3680043.8.498.88590328415665439113874179505096257448'
m2.RequestedProcedureDescription = 'lorem'
m2.RequestedProcedureID = '9000'


web_url = os.environ.get('EE_URL', 'http://localhost')
web_port = os.environ.get('EE_HTTP_PORT', '8000')

@dataclass
class ServiceClassProviderConfig:
    implementation_class_uid: str
    port: int


def to_dicom_tag(tag: int, padding: int = 10) -> str:
    return f"{tag:#0{padding}x}"


def parse_da_vr(value: str) -> Optional[datetime]:
    for format in ("%Y%m%d", "%Y-%m-%d", "%Y:%m:%d"):
        try:
            return datetime.strptime(value, format)
        except ValueError:
            pass
    return None


ParsedElementValue_ = Union[str, float, int, datetime]
ParsedElementValue = Union[List[ParsedElementValue_], ParsedElementValue_]

DicomVRParseDictionary: Dict[str, Callable[[str], Optional[ParsedElementValue_]]] = {
    "DA": parse_da_vr,
    "DS": lambda value: float(value),
    "TM": lambda value: float(value),
    "US": lambda value: int(value),
    "IS": lambda value: int(value),
    "PN": lambda value: value.encode("utf-8").decode("utf-8"),
}


def safe_get_(dcm: FileDataset, tag: int) -> Optional[ParsedElementValue]:
    try:
        element = dcm[tag]
        VR, element_value = dictionary_VR(tag), element.value

        if element_value == "" or element_value is None:
            return None

        vr_parser = DicomVRParseDictionary.get(VR, lambda value: value)
        if isinstance(element_value, MultiValue) is not isinstance(element_value, Sequence):
            return cast(ParsedElementValue, [vr_parser(item) for item in element_value])

        return vr_parser(element_value)
    except KeyError:
        logger.debug(f"Cannot find element using for tag={to_dicom_tag(tag)}")
        return None
    except ValueError as error:
        logger.warning(f"Encountered ValueError extracting element for tag={to_dicom_tag(tag)} - err={error}")
        return None


def safe_get(dcm: FileDataset, tag: int) -> Optional[ParsedElementValue]:
    element = safe_get_(dcm, tag)
    VM: str = dictionary_VM(tag)
    return [] if element is None and VM != "1" else element


class ServiceClassProvider:
    def __init__(self, aet: str, config: ServiceClassProviderConfig) -> None:
        self.config = config
        self.address = ("0.0.0.0", config.port)

        self.ae = AE(ae_title=aet)
        self.ae.implementation_class_uid = config.implementation_class_uid
        self.ae.implementation_version_name = f'{aet}_{config.implementation_class_uid.split(".")[-1]}'[:16]

        self.SUPPORTED_ABSTRACT_SYNTAXES: List[str] = [
            sop_class.DigitalXRayImagePresentationStorage,
            sop_class.DigitalXRayImageProcessingStorage,
            sop_class.CTImageStorage
        ]
        for abstract_syntax in self.SUPPORTED_ABSTRACT_SYNTAXES:
            self.ae.add_supported_context(abstract_syntax, ALL_TRANSFER_SYNTAXES)
        self.ae.add_supported_context(sop_class.VerificationSOPClass, ALL_TRANSFER_SYNTAXES)
        self.ae.add_supported_context(sop_class.PatientRootQueryRetrieveInformationModelFind)
        self.ae.add_supported_context(sop_class.ModalityWorklistInformationFind)
        self.ae.add_supported_context(sop_class.ModalityPerformedProcedureStepSOPClass)

        # self.ae.require_calling_aet = ["MODALITY"]
        self.ae.require_calling_aet = []  # Leave blank to accept all caller AEs

        self.managed_instances = {}

    # Implement a handler for evt.EVT_C_ECHO
    def handle_echo(self, event: Event) -> int:
        """Handle a C-ECHO request event."""
        return 0x0000

    def handle_c_find(self, event: Event) -> int:
        """Handle a C-FIND request event."""
        print('Handle C Find')
        ds = event.identifier
        post_data = {}

        post_data['device'] = event.assoc.requestor.ae_title.strip().decode('UTF-8')

        if 'PatientName' in ds:
            print('Patient Name', str(ds.PatientName))
            post_data['patient_name'] = str(ds.PatientName)
        if 'StudyDate' in ds:
            print('Study Date', str(ds.StudyDate))
            #post_data['date'] = str(ds.StudyDate)

        if 'ScheduledProcedureStepStartDate' in ds:
            post_data['date'] = str(ds.ScheduledProcedureStepStartDate)
        else:
            post_data['date'] = datetime.today().strftime('%Y%m%d')

        response = requests.post(f'{web_url}:{web_port}/worklists/', data=post_data)
        res = response.json()
        #matching = [m1, m2]

        items = json.loads(res['items'])
        print('items', items)

        for instance in items:
            # Check if C-CANCEL has been received
            if event.is_cancelled:
                yield (0xFE00, None)
                return

            # Patient tags https://dicom.nema.org/dicom/2013/output/chtml/part06/chapter_6.html
            consultation = instance['consultation']
            patient = instance['consultation']['patient']
            identifier = Dataset()
            identifier.PatientID = str(patient['id'])
            pname = f"{patient['nom_naissance']}^{patient['prenom']}"
            if patient['ancien_numero']:
                pname = pname + f"^{patient['ancien_numero']}"
            identifier.PatientName = pname
            identifier.PatientBirthDate = patient['date_naissance'].replace('-', '')
            identifier.PatientSex = 'F' if patient['sexe'] == 'F' else 'M'

            if patient['grossesse_encours']:
                g = patient['grossesse_encours']
                if 'ddr' in g:
                    print('=================================================')
                    print('DDR ', g['ddr'])
                    identifier.LastMenstrualDate = g['ddr'].replace('-', '')
            if patient['poids']:
                identifier.PatientWeight = patient['poids']
            identifier.AccessionNumber = str(consultation['id'])
            identifier.StudyInstanceUID = instance['study_instance_uid']
            identifier.StudyDate = consultation['date'].replace('-', '')
            identifier.RequestedProcedureDescription = instance['requested_procedure_description']
            identifier.RequestedProcedureID = instance['requested_procedure_id']

            if 'ScheduledStationAETitle' in ds:
                identifier.ScheduledStationAETitle = ds.ScheduledStationAETitle
            if 'ScheduledProcedureStepStartDate' in ds:
                identifier.ScheduledProcedureStepStartDate = ds.ScheduledProcedureStepStartDate
            else:
                identifier.ScheduledProcedureStepStartDate = datetime.today().strftime('%Y%m%d')
            if 'ScheduledProcedureStepSequence' in ds:
                identifier.ScheduledProcedureStepSequence = ds.ScheduledProcedureStepSequence
            if 'Modality' in ds:
                identifier.Modality = ds.Modality

            if 'QueryRetrieveLevel' in ds:
                identifier.QueryRetrieveLevel = ds.QueryRetrieveLevel

            # Pending
            yield (0xFF00, identifier)

        return 0x0000

    def handle_n_create(self, event: Event):
        # MPPS' N-CREATE request must have an *Affected SOP Instance UID*
        logger.info(f"handle_n_create called")
        req = event.request

        if req.AffectedSOPInstanceUID is None:
            # Failed - invalid attribute value
            logger.error(f"handle_n_create - Didn't receive a AffectedSOPInstanceUID")
            return 0x0106, None

        # Can't create a duplicate SOP Instance
        if req.AffectedSOPInstanceUID in self.managed_instances:
            # Failed - duplicate SOP Instance
            logger.error(f"handle_n_create - AffectedSOPInstanceUID not registered {req.AffectedSOPInstanceUID}")
            return 0x0111, None

        # The N-CREATE request's *Attribute List* dataset
        attr_list = event.attribute_list
        print('############## ', attr_list)

        # Performed Procedure Step Status must be 'IN PROGRESS'
        if "PerformedProcedureStepStatus" not in attr_list:
            # Failed - missing attribute
            logger.error(f"handle_n_create - PerformedProcedureStepStatus not in attribute list")
            return 0x0120, None
        if attr_list.PerformedProcedureStepStatus.upper() != 'IN PROGRESS':
            logger.error(f"handle_n_create - PerformedProcedureStepStatus is not IN PROGRESS {attr_list.PerformedProcedureStepStatus.upper()}")
            return 0x0106, None


        print('#############################################')
        if "ScheduledStepAttributesSequence" not in attr_list:
            # Failed - missing attribute
            logger.error(f"handle_n_create - ScheduledStepAttributesSequence not in attribute list")
            return 0x0120, None

        for seq_item in attr_list.ScheduledStepAttributesSequence:
            if "StudyInstanceUID" not in seq_item:
                # Failed - missing attribute
                logger.error(f"handle_n_create - StudyInstanceUID not in sequence ")
                return 0x0120, None
            studyId = seq_item.StudyInstanceUID
            post_data = {}
            post_data['status'] = attr_list.PerformedProcedureStepStatus.upper()
            post_data['study_uid'] = studyId
            response = requests.post(f'{web_url}:{web_port}/worklists/statut/', data=post_data)
            res = response.json()
            status = res['status']
            print('Worklist API update status', status)
            print('Study instance UID', studyId)

        # Skip other tests...

        # Create a Modality Performed Procedure Step SOP Class Instance
        # DICOM Standard, Part 3, Annex B.17
        ds = Dataset()

        # Add the SOP Common module elements (Annex C.12.1)
        ds.SOPClassUID = sop_class.ModalityPerformedProcedureStepSOPClass
        ds.SOPInstanceUID = req.AffectedSOPInstanceUID

        # Update with the requested attributes
        ds.update(attr_list)

        # Add the dataset to the managed SOP Instances
        self.managed_instances[ds.SOPInstanceUID] = ds
        logger.info(f"handle_n_create - Added ${ds.SOPInstanceUID} to registered instances")

        # Return status, dataset
        return 0x0000, ds

    # Implement the evt.EVT_N_SET handler
    def handle_n_set(self, event):
        logger.info(f"handle_n_set called")
        req = event.request
        if req.RequestedSOPInstanceUID not in self.managed_instances:
            # Failure - SOP Instance not recognised
            logger.error(f"handle_n_set - RequestedSOPInstanceUID not registered {req.RequestedSOPInstanceUID}")
            return 0x0112, None

        ds = self.managed_instances[req.RequestedSOPInstanceUID]

        print('############################################################')
        print(ds.ScheduledStepAttributesSequence)

        # The N-SET request's *Modification List* dataset
        mod_list = event.attribute_list

        status = mod_list.PerformedProcedureStepStatus.upper()
        logger.info(f"handle_n_set - received status {status}")

        for seq_item in ds.ScheduledStepAttributesSequence:
            post_data = {}
            print('Sequence item', seq_item)
            post_data['status'] = status
            post_data['study_uid'] = seq_item.StudyInstanceUID
            response = requests.post(f'{web_url}:{web_port}/worklists/statut/', data=post_data)
            res = response.json()
            status = res['status']
            print('Worklist API update status', status)

        # Skip other tests...
        ds.update(mod_list)

        # Return status, dataset
        return 0x0000, ds

    def start(self) -> None:
        logger.info(f"Starting DIMSE C-STORE AE on address={self.address} aet={self.ae.ae_title}")
        self.handlers = [
            (events.EVT_C_ECHO, self.handle_echo),
            (events.EVT_C_FIND, self.handle_c_find),
            (events.EVT_N_CREATE, self.handle_n_create),
            (events.EVT_N_SET, self.handle_n_set),
        ]
        self.ae.start_server(self.address, block=True, evt_handlers=self.handlers)


def main() -> None:
    run_server()


def run_server():
    print('Running Worklist and MPPS server')
    config = ServiceClassProviderConfig(implementation_class_uid=generate_uid(), port=os.environ.get('EE_WL_MPPS_SCP_PORT', 11112))
    server = ServiceClassProvider("EXPERTECHO", config)
    server.start()


if __name__ == "__main__":
    main()
