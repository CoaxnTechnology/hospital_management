"""
Full DICOM test flow without a real machine.

Prerequisites:
  - Django server running:   python manage.py runserver
  - Worklist server running: python worklist.py
  - Storage server running:  python store.py
  - A patient with a consultation + device selected in the UI

Usage:
  python test_full_flow.py
"""
import os
import glob

from pydicom import dcmread
from pydicom.dataset import Dataset
from pydicom.sequence import Sequence
from pydicom.uid import ExplicitVRLittleEndian, ImplicitVRLittleEndian, generate_uid
from pynetdicom import AE

# SOP Class UIDs
VERIFICATION = "1.2.840.10008.1.1"
MODALITY_WORKLIST_FIND = "1.2.840.10008.5.1.4.31"
MPPS = "1.2.840.10008.3.1.2.3.3"

AET = b"TEST_SCU"
WORKLIST_HOST = "127.0.0.1"
WORKLIST_PORT = 11112
STORAGE_HOST = "127.0.0.1"
STORAGE_PORT = 11113
CALLED_AET = b"EXPERTECHO"


def step1_echo():
    """Test connectivity to both servers."""
    print("=" * 60)
    print("STEP 1: Testing connectivity (C-ECHO)")
    print("=" * 60)

    ae = AE(ae_title=AET)
    ae.add_requested_context(VERIFICATION)

    # Test worklist server
    assoc = ae.associate(WORKLIST_HOST, WORKLIST_PORT, ae_title=CALLED_AET)
    if assoc.is_established:
        status = assoc.send_c_echo()
        print(f"  Worklist server (:{WORKLIST_PORT}): OK (0x{status.Status:04X})")
        assoc.release()
    else:
        print(f"  Worklist server (:{WORKLIST_PORT}): FAILED - not running?")
        return False

    # Test storage server
    assoc = ae.associate(STORAGE_HOST, STORAGE_PORT, ae_title=CALLED_AET)
    if assoc.is_established:
        status = assoc.send_c_echo()
        print(f"  Storage server  (:{STORAGE_PORT}): OK (0x{status.Status:04X})")
        assoc.release()
    else:
        print(f"  Storage server  (:{STORAGE_PORT}): FAILED - not running?")
        return False

    return True


def step2_query_worklist():
    """Query worklist (C-FIND) - simulates machine fetching patient list."""
    print()
    print("=" * 60)
    print("STEP 2: Querying worklist (C-FIND)")
    print("=" * 60)

    ae = AE(ae_title=AET)
    ae.add_requested_context(MODALITY_WORKLIST_FIND, ImplicitVRLittleEndian)

    assoc = ae.associate(WORKLIST_HOST, WORKLIST_PORT, ae_title=CALLED_AET)
    if not assoc.is_established:
        print("  FAILED: Could not connect to worklist server")
        return []

    # Query for all patients
    ds = Dataset()
    ds.PatientName = ""
    ds.PatientID = ""
    ds.StudyDate = ""
    ds.StudyInstanceUID = ""
    ds.AccessionNumber = ""
    ds.RequestedProcedureDescription = ""
    ds.RequestedProcedureID = ""
    ds.PatientBirthDate = ""
    ds.PatientSex = ""

    worklist_items = []
    responses = assoc.send_c_find(ds, MODALITY_WORKLIST_FIND)

    for status, identifier in responses:
        if status and status.Status in (0xFF00, 0xFF01) and identifier:
            name = str(getattr(identifier, "PatientName", "?"))
            pid = str(getattr(identifier, "PatientID", "?"))
            study_uid = str(getattr(identifier, "StudyInstanceUID", "?"))
            desc = str(getattr(identifier, "RequestedProcedureDescription", "?"))

            print(f"\n  Found patient:")
            print(f"    Patient Name : {name}")
            print(f"    Patient ID   : {pid}")
            print(f"    Study UID    : {study_uid}")
            print(f"    Procedure    : {desc}")

            worklist_items.append(identifier)

    assoc.release()

    if not worklist_items:
        print("  No worklist items found.")
        print("  --> Make sure you created a consultation with a device selected in the UI!")
    else:
        print(f"\n  Total: {len(worklist_items)} worklist item(s) found")

    return worklist_items


def step3_send_mpps_in_progress(study_uid):
    """Send MPPS N-CREATE (IN PROGRESS) - simulates machine starting exam."""
    print()
    print("=" * 60)
    print("STEP 3: Sending MPPS IN PROGRESS (N-CREATE)")
    print("=" * 60)

    ae = AE(ae_title=AET)
    ae.add_requested_context(MPPS, ImplicitVRLittleEndian)

    assoc = ae.associate(WORKLIST_HOST, WORKLIST_PORT, ae_title=CALLED_AET)
    if not assoc.is_established:
        print("  FAILED: Could not connect")
        return None

    mpps_uid = generate_uid()

    ds = Dataset()
    ds.PerformedProcedureStepStatus = "IN PROGRESS"
    ds.PerformedProcedureStepStartDate = ""
    ds.PerformedProcedureStepStartTime = ""
    ds.PerformedProcedureStepID = "1"
    ds.PerformedProcedureStepDescription = "Test procedure"

    scheduled_step = Dataset()
    scheduled_step.StudyInstanceUID = study_uid
    ds.ScheduledStepAttributesSequence = Sequence([scheduled_step])

    status, attr_list = assoc.send_n_create(ds, MPPS, mpps_uid)

    if status and status.Status == 0x0000:
        print(f"  MPPS IN PROGRESS sent successfully")
        print(f"  MPPS Instance UID: {mpps_uid}")
    else:
        s = f"0x{status.Status:04X}" if status else "None"
        print(f"  MPPS IN PROGRESS failed: {s}")

    assoc.release()
    return mpps_uid


def step4_send_images(study_uid):
    """Send DICOM images (C-STORE) - simulates machine sending captured images."""
    print()
    print("=" * 60)
    print("STEP 4: Sending images (C-STORE)")
    print("=" * 60)

    # Find sample DCM files
    dcm_files = glob.glob("data/studies/*/img_*.dcm")
    if not dcm_files:
        print("  No sample .dcm files found in data/studies/")
        return

    # Send up to 3 images
    files_to_send = dcm_files[:3]
    print(f"  Sending {len(files_to_send)} image(s)...")

    for dcm_path in files_to_send:
        ds = dcmread(dcm_path)

        # Override StudyInstanceUID to match our worklist item
        ds.StudyInstanceUID = study_uid

        # Decompress properly (pylibjpeg handles JPEG pixel data correctly)
        ds.decompress()

        ae_send = AE(ae_title=AET)
        ae_send.add_requested_context(ds.SOPClassUID, [ExplicitVRLittleEndian, ImplicitVRLittleEndian])

        assoc = ae_send.associate(STORAGE_HOST, STORAGE_PORT, ae_title=CALLED_AET)
        if assoc.is_established:
            status = assoc.send_c_store(ds)
            if status and status.Status == 0x0000:
                print(f"  Sent: {os.path.basename(dcm_path)} --> OK")
            else:
                s = f"0x{status.Status:04X}" if status else "None"
                print(f"  Sent: {os.path.basename(dcm_path)} --> FAILED ({s})")
            assoc.release()
        else:
            print(f"  Failed to connect for {os.path.basename(dcm_path)}")


def step5_send_mpps_completed(mpps_uid):
    """Send MPPS N-SET (COMPLETED) - simulates machine finishing exam."""
    print()
    print("=" * 60)
    print("STEP 5: Sending MPPS COMPLETED (N-SET)")
    print("=" * 60)

    ae = AE(ae_title=AET)
    ae.add_requested_context(MPPS, ImplicitVRLittleEndian)

    assoc = ae.associate(WORKLIST_HOST, WORKLIST_PORT, ae_title=CALLED_AET)
    if not assoc.is_established:
        print("  FAILED: Could not connect")
        return

    ds = Dataset()
    ds.PerformedProcedureStepStatus = "COMPLETED"
    ds.PerformedProcedureStepEndDate = ""
    ds.PerformedProcedureStepEndTime = ""

    status, attr_list = assoc.send_n_set(ds, MPPS, mpps_uid)

    if status and status.Status == 0x0000:
        print(f"  MPPS COMPLETED sent successfully")
    else:
        s = f"0x{status.Status:04X}" if status else "None"
        print(f"  MPPS COMPLETED failed: {s}")

    assoc.release()


def main():
    print()
    print("###############################################")
    print("#   DICOM Full Flow Test (No Machine)         #")
    print("###############################################")
    print()

    # Step 1: Test connectivity
    if not step1_echo():
        print("\nServers not running. Start them first:")
        print("  Terminal 1: python worklist.py")
        print("  Terminal 2: python store.py")
        return

    # Step 2: Query worklist
    worklist_items = step2_query_worklist()

    if not worklist_items:
        print()
        print("No worklist items found. To create one:")
        print("  1. Login at http://127.0.0.1:8000/accounts/login")
        print("  2. Create a patient")
        print("  3. Create a consultation and SELECT A DEVICE")
        print("  4. Run this script again")
        return

    # Use the first worklist item
    item = worklist_items[0]
    study_uid = str(item.StudyInstanceUID)
    print(f"\n  Using Study UID: {study_uid}")

    # Step 3: MPPS IN PROGRESS
    mpps_uid = step3_send_mpps_in_progress(study_uid)

    # Step 4: Send images
    step4_send_images(study_uid)

    # Step 5: MPPS COMPLETED
    if mpps_uid:
        step5_send_mpps_completed(mpps_uid)

    print()
    print("=" * 60)
    print("DONE! Check the consultation in the browser.")
    print("Images should appear in the consultation page.")
    print("=" * 60)


if __name__ == "__main__":
    main()
