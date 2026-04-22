"""Send a DICOM file to the storage server for testing."""
import sys
from pydicom import dcmread
from pydicom.uid import ExplicitVRLittleEndian, ImplicitVRLittleEndian
from pynetdicom import AE

dcm_path = sys.argv[1] if len(sys.argv) > 1 else "data/studies/1.2.410.200001.101.11.401.1123096237.1.20230501115351672/img_95814292.dcm"

ds = dcmread(dcm_path)

# Decompress if needed so we can send with standard transfer syntax
ds.decompress()

ae = AE(ae_title=b"TEST_SCU")
ae.add_requested_context(ds.SOPClassUID, [ExplicitVRLittleEndian, ImplicitVRLittleEndian])

assoc = ae.associate("127.0.0.1", 11113, ae_title=b"EXPERTECHO")
if assoc.is_established:
    status = assoc.send_c_store(ds)
    if status:
        print(f"C-STORE status: 0x{status.Status:04X}")
    else:
        print("Connection timed out or no response")
    assoc.release()
else:
    print("Association rejected or failed")
