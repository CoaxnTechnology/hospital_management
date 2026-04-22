from pydicom.dataset import Dataset

from pynetdicom import AE, evt
from pynetdicom.sop_class import ModalityPerformedProcedureStepSOPClass

managed_instances = {}

# Implement the evt.EVT_N_CREATE handler
def handle_create(event):
    # MPPS' N-CREATE request must have an *Affected SOP Instance UID*
    req = event.request
    if req.AffectedSOPInstanceUID is None:
        # Failed - invalid attribute value
        return 0x0106, None

    # Can't create a duplicate SOP Instance
    if req.AffectedSOPInstanceUID in managed_instances:
        # Failed - duplicate SOP Instance
        return 0x0111, None

    # The N-CREATE request's *Attribute List* dataset
    attr_list = event.attribute_list

    # Performed Procedure Step Status must be 'IN PROGRESS'
    if "PerformedProcedureStepStatus" not in attr_list:
        # Failed - missing attribute
        return 0x0120, None
    if attr_list.PerformedProcedureStepStatus.upper() != 'IN PROGRESS':
        return 0x0106, None

    # Skip other tests...

    # Create a Modality Performed Procedure Step SOP Class Instance
    #   DICOM Standard, Part 3, Annex B.17
    ds = Dataset()

    # Add the SOP Common module elements (Annex C.12.1)
    ds.SOPClassUID = ModalityPerformedProcedureStepSOPClass
    ds.SOPInstanceUID = req.AffectedSOPInstanceUID

    # Update with the requested attributes
    ds.update(attr_list)

    # Add the dataset to the managed SOP Instances
    managed_instances[ds.SOPInstanceUID] = ds

    # Return status, dataset
    return 0x0000, ds

# Implement the evt.EVT_N_SET handler
def handle_set(event):
    req = event.request
    if req.RequestedSOPInstanceUID not in managed_instances:
        # Failure - SOP Instance not recognised
        return 0x0112, None

    ds = managed_instances[req.RequestedSOPInstanceUID]

    # The N-SET request's *Modification List* dataset
    mod_list = event.attribute_list

    # Skip other tests...

    ds.update(mod_list)

    # Return status, dataset
    return 0x0000, ds

handlers = [(evt.EVT_N_CREATE, handle_create), (evt.EVT_N_SET, handle_set)]

# Initialise the Application Entity and specify the listen port
ae = AE()

# Add the supported presentation context
ae.add_supported_context(ModalityPerformedProcedureStepSOPClass)

# Start listening for incoming association requests
ae.start_server(('', 11112), evt_handlers=handlers)