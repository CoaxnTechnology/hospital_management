import os

from pydicom import dcmread
from pydicom.dataset import Dataset

from pynetdicom import AE, evt
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind, VerificationSOPClass


# Implement a handler for evt.EVT_C_ECHO
def handle_echo(event):
    """Handle a C-ECHO request event."""
    return 0x0000


# Implement the handler for evt.EVT_C_FIND
def handle_find(event):
    """Handle a C-FIND request event."""
    ds = event.identifier

    # Import stored SOP Instances
    instances = []
    fdir = '/path/to/directory'
    for fpath in os.listdir(fdir):
        instances.append(dcmread(os.path.join(fdir, fpath)))

    if 'QueryRetrieveLevel' not in ds:
        # Failure
        yield 0xC000, None
        return

    if ds.QueryRetrieveLevel == 'PATIENT':
        if 'PatientName' in ds:
            if ds.PatientName not in ['*', '', '?']:
                matching = [
                    inst for inst in instances if inst.PatientName == ds.PatientName
                ]

            # Skip the other possibile values...

        # Skip the other possible attributes...

    # Skip the other QR levels...

    for instance in matching:
        # Check if C-CANCEL has been received
        if event.is_cancelled:
            yield (0xFE00, None)
            return

        identifier = Dataset()
        identifier.PatientName = instance.PatientName
        identifier.QueryRetrieveLevel = ds.QueryRetrieveLevel

        # Pending
        yield (0xFF00, identifier)


handlers = [
    (evt.EVT_C_FIND, handle_find),
    (evt.EVT_C_ECHO, handle_echo)
]

addr = '127.0.0.1'
port = 4242
title = b'EXPERTECHO'

# Initialise the Application Entity and specify the listen port
ae = AE(ae_title=title)

# Add the supported presentation context
ae.add_supported_context(VerificationSOPClass)

# Add the supported presentation context
ae.add_supported_context(PatientRootQueryRetrieveInformationModelFind)

# Start listening for incoming association requests
ae.start_server(('', 11112), evt_handlers=handlers)
