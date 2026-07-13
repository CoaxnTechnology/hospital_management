"""
Load medications, lab tests, exam templates and report templates
from CSV files + exported JSON fixture into the database for a given compte.

Usage:
    python manage.py load_templates --compte 1
    python manage.py load_templates --compte 1 --clear   # wipe existing first
"""
import csv
import json
import os

from django.core.management.base import BaseCommand, CommandError

from apps.core.models import (
    AnalyseBiologique,
    CategorieConsultation,
    Compte,
    MotifConsultation,
    Prescription,
    TemplateEdition,
    Traitement,
)

DATA_DIR     = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'fixtures')

TRAITEMENTS_CSV   = os.path.join(DATA_DIR, 'traitements.csv')
ANALYSES_CSV      = os.path.join(DATA_DIR, 'analyses.csv')
PRESCRIPTIONS_CSV = os.path.join(DATA_DIR, 'prescriptions.csv')
TEMPLATES_JSON    = os.path.join(FIXTURES_DIR, 'templates_data.json')


class Command(BaseCommand):
    help = 'Load all template data (medications, labs, exams, report templates) for a compte'

    def add_arguments(self, parser):
        parser.add_argument('--compte', type=int, required=True,
                            help='PK of the Compte to assign data to')
        parser.add_argument('--clear', action='store_true', default=False,
                            help='Delete existing entries for this compte before importing')
        parser.add_argument('--skip-traitements',    action='store_true', default=False)
        parser.add_argument('--skip-analyses',       action='store_true', default=False)
        parser.add_argument('--skip-prescriptions',  action='store_true', default=False)
        parser.add_argument('--skip-report-templates', action='store_true', default=False)

    def handle(self, *args, **options):
        compte_pk = options['compte']
        try:
            compte = Compte.objects.get(pk=compte_pk)
        except Compte.DoesNotExist:
            raise CommandError(f'Compte with pk={compte_pk} does not exist.')

        self.stdout.write(f'Target compte: {compte.raison_sociale} (pk={compte.pk})')

        if options['clear']:
            self.stdout.write(self.style.WARNING('  Clearing existing data...'))
            Traitement.objects.filter(compte=compte).delete()
            AnalyseBiologique.objects.filter(compte=compte).delete()
            Prescription.objects.filter(compte=compte).delete()
            TemplateEdition.objects.filter(compte=compte).delete()

        if not options['skip_traitements']:
            self._load_traitements(compte)

        if not options['skip_analyses']:
            self._load_analyses(compte)

        if not options['skip_prescriptions']:
            self._load_prescriptions(compte)

        if not options['skip_report_templates']:
            self._load_report_templates(compte)

        self.stdout.write(self.style.SUCCESS('Done.'))

    # ------------------------------------------------------------------
    def _load_traitements(self, compte):
        self.stdout.write('  Loading medications (traitements.csv)...')
        existing = set(
            Traitement.objects.filter(compte=compte).values_list('libelle', flat=True)
        )
        entries = []
        skipped = 0
        with open(TRAITEMENTS_CSV, encoding='cp1252', errors='replace') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                libelle = row['libelle'].strip()
                if not libelle or libelle in existing:
                    skipped += 1
                    continue
                entries.append(Traitement(
                    compte=compte,
                    libelle=libelle,
                    text=row.get('text', '').strip(),
                    forme=row.get('forme', 'comprime').strip().lower() or 'comprime',
                ))
        Traitement.objects.bulk_create(entries, ignore_conflicts=True)
        self.stdout.write(f'    Created: {len(entries)}  Skipped: {skipped}')

    # ------------------------------------------------------------------
    def _load_analyses(self, compte):
        self.stdout.write('  Loading lab tests (analyses.csv)...')
        existing = set(
            AnalyseBiologique.objects.filter(compte=compte).values_list('code', flat=True)
        )
        entries = []
        skipped = 0
        with open(ANALYSES_CSV, encoding='cp1252', errors='replace') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                code = row.get('code', '').strip()
                libelle = row.get('libelle', '').strip()
                if not code or code in existing:
                    skipped += 1
                    continue
                entries.append(AnalyseBiologique(
                    compte=compte,
                    code=code,
                    libelle=libelle or code,
                    type=row.get('type', 'text').strip() or 'text',
                    unite=row.get('unite', '').strip(),
                ))
        AnalyseBiologique.objects.bulk_create(entries, ignore_conflicts=True)
        self.stdout.write(f'    Created: {len(entries)}  Skipped: {skipped}')

    # ------------------------------------------------------------------
    def _load_prescriptions(self, compte):
        self.stdout.write('  Loading exam templates (prescriptions.csv)...')
        existing = set(
            Prescription.objects.filter(compte=compte).values_list('libelle', flat=True)
        )
        entries = []
        skipped = 0
        with open(PRESCRIPTIONS_CSV, encoding='cp1252', errors='replace') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                libelle = row.get('libelle', '').strip()
                if not libelle or libelle in existing:
                    skipped += 1
                    continue
                categorie = row.get('categorie', '').strip()
                if categorie not in ('examen_complementaire',):
                    categorie = 'examen_complementaire'
                entries.append(Prescription(
                    compte=compte,
                    libelle=libelle,
                    categorie=categorie,
                    text=row.get('text', libelle).strip(),
                ))
        Prescription.objects.bulk_create(entries, ignore_conflicts=True)
        self.stdout.write(f'    Created: {len(entries)}  Skipped: {skipped}')

    # ------------------------------------------------------------------
    def _load_report_templates(self, compte):
        self.stdout.write('  Loading report templates (templates_data.json)...')
        if not os.path.exists(TEMPLATES_JSON):
            self.stdout.write(self.style.WARNING(
                '    templates_data.json not found — skipping report templates.\n'
                '    Run export_templates on local first, then commit the file.'
            ))
            return

        with open(TEMPLATES_JSON, encoding='utf-8') as f:
            data = json.load(f)

        templates = data.get('template_editions', [])
        existing = set(
            TemplateEdition.objects.filter(compte=compte).values_list('libelle', flat=True)
        )
        created = skipped = errors = 0
        for t in templates:
            libelle = t.get('libelle', '').strip()
            if not libelle or libelle in existing:
                skipped += 1
                continue
            cat_libelle = t.get('categorie_consultation__libelle')
            motif_code = t.get('motif_consultation__code')
            try:
                categorie = CategorieConsultation.objects.get(libelle=cat_libelle)
            except CategorieConsultation.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'    Skipping "{libelle}": categorie "{cat_libelle}" not found'
                ))
                errors += 1
                continue
            motif = None
            if motif_code:
                try:
                    motif = MotifConsultation.objects.get(code=motif_code)
                except MotifConsultation.DoesNotExist:
                    pass
            TemplateEdition.objects.create(
                compte=compte,
                libelle=libelle,
                contenu=t.get('contenu', ''),
                categorie_consultation=categorie,
                motif_consultation=motif,
            )
            created += 1

        self.stdout.write(f'    Created: {created}  Skipped: {skipped}  Errors: {errors}')
