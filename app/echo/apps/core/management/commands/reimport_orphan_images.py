import os
from datetime import datetime

import pydicom
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.core.models import ImageConsultation, repertoire_images_utilisateur


class Command(BaseCommand):
    help = "Re-import orphaned JPEG images by matching DICOM metadata to consultations"

    def handle(self, *args, **options):
        studies_dir = './data/studies/'
        if not os.path.exists(studies_dir):
            self.stderr.write(f"Studies directory not found: {studies_dir}")
            return

        imported = 0
        skipped_no_consult = 0
        skipped_already = 0
        errors = 0

        for study_uid in sorted(os.listdir(studies_dir)):
            study_path = os.path.join(studies_dir, study_uid)
            if not os.path.isdir(study_path):
                continue

            jpegs = sorted(f for f in os.listdir(study_path) if f.startswith('img_') and f.endswith('.jpg'))
            if not jpegs:
                continue

            dcm_files = sorted(f for f in os.listdir(study_path) if f.startswith('img_') and f.endswith('.dcm'))
            if not dcm_files:
                self.stdout.write(f"  Skipping study {study_uid}: no archived DICOM file")
                skipped_no_consult += len(jpegs)
                continue

            ds = pydicom.dcmread(os.path.join(study_path, dcm_files[0]), stop_before_pixels=True)
            patient_name = str(ds.get('PatientName', ''))
            study_date = str(ds.get('StudyDate', ''))

            self.stdout.write(f"  Study {study_uid}: patient='{patient_name}' date={study_date} ({len(jpegs)} images)")

            if not patient_name:
                self.stdout.write(f"    No patient name in DICOM, skipping")
                skipped_no_consult += len(jpegs)
                continue

            parts = patient_name.split('^')
            last_name = parts[0] if len(parts) >= 1 else ''
            first_name = parts[1] if len(parts) >= 2 else ''

            if not last_name:
                skipped_no_consult += len(jpegs)
                continue

            from apps.core.models import Consultation
            q = Q(patient__nom__iexact=last_name)
            if first_name:
                q &= Q(patient__prenom__iexact=first_name)
            if study_date and len(study_date) == 8:
                try:
                    d = datetime.strptime(study_date, '%Y%m%d').date()
                    q &= Q(date__date=d)
                except ValueError:
                    pass

            consultations = Consultation.objects.filter(q).order_by('-date')

            if not consultations.exists():
                self.stdout.write(f"    No matching consultation found for {last_name} {first_name}")
                skipped_no_consult += len(jpegs)
                continue

            consultation = consultations.first()
            self.stdout.write(f"    Matched consultation pk={consultation.pk} date={consultation.date}")

            existing = set(
                ImageConsultation.objects.filter(consultation=consultation)
                .values_list('image', flat=True)
            )

            for jpg in jpegs:
                jpg_path = os.path.join(study_path, jpg)
                if not os.path.exists(jpg_path):
                    continue

                rel_path = f"comptes/compte_{consultation.patient.compte.pk}/patients/{consultation.patient.pk}/images/{jpg}"
                if rel_path in existing:
                    skipped_already += 1
                    continue

                try:
                    ic = ImageConsultation(
                        type=ImageConsultation.IMG_ECHO,
                        consultation=consultation,
                        date=datetime.now(),
                        impression=False,
                    )
                    ic.save()
                    out_path = repertoire_images_utilisateur(
                        consultation.patient.compte.pk,
                        consultation.patient.pk,
                        jpg,
                    )
                    with open(jpg_path, 'rb') as f:
                        ic.image.save(out_path, File(f))
                    self.stdout.write(f"    Imported {jpg} -> consultation {consultation.pk}")
                    imported += 1
                except Exception as e:
                    self.stderr.write(f"    Error importing {jpg}: {e}")
                    errors += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done: {imported} imported, {skipped_no_consult} skipped (no match), "
            f"{skipped_already} skipped (already exists), {errors} errors"
        ))
