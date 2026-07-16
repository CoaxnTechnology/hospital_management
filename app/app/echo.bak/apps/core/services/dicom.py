from pydicom import Dataset
from pynetdicom import AE
from pynetdicom.sop_class import (
    VerificationSOPClass,
    GeneralRelevantPatientInformationQuery,
    PatientRootQueryRetrieveInformationModelMove,
    PatientRootQueryRetrieveInformationModelFind,
    CTImageStorage,
    MRImageStorage
)
import logging

addr = '127.0.0.1'
port = 4242
title = b'EXPERTECHO'

LOGGER = logging.getLogger('pynetdicom')
LOGGER.setLevel(logging.DEBUG)


def worklist():
    ae = AE(ae_title=title)


def ping():
    ae = AE(ae_title=title)
    ae.add_requested_context(VerificationSOPClass)
    assoc = ae.associate(addr, 11112, ae_title=b'MODALITY')

    if assoc.is_established:
        # Send a DIMSE C-ECHO request to the peer
        status = assoc.send_c_echo()

        # Print the response from the peer
        if status:
            print('C-ECHO Response: 0x{0:04x}'.format(status.Status))

        # Release the association
        assoc.release()
    else:
        print('Connection not established')


def create_patient():
    # Initialise the Application Entity
    ae = AE(ae_title=title)
    # Add a requested presentation context
    ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)
    # ae.requested_contexts = StoragePresentationRequests
    # # Create our Identifier (query) dataset
    ds = Dataset()
    ds.PatientID = "11788759296811"
    ds.QueryRetrieveLevel = 'PATIENT'
    # ds.PatientName = '*'
    # ds.Modality = '*'
    # ds.StudyInstanceUID = '*'
    # ds.SeriesInstanceUID = '*'

    assoc = ae.associate(addr, port, ae_title=b'MODALITY')

    if assoc.is_established:
        print('Association Established')
        responses = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)

        print("============Response done===============")
        print(responses)
        for (status, identifier) in responses:
            if status:
                print('C-FIND query status: 0x{0:04X}'.format(status.Status))
            else:
                print('Connection timed out, was aborted or received invalid response')

        # Release the association
        assoc.release()
        print('Association Released')
    else:
        print('Association rejected or aborted')


ping()
# create_patient()
