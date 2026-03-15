"""
Export all template data (medications, lab tests, exams, report templates)
from local DB to a portable JSON file — without compte dependency.

Usage:
    python manage.py export_templates --compte 7
    python manage.py export_templates --compte 7 --output apps/core/fixtures/templates_data.json
"""
import json
import os

from django.core.management.base import BaseCommand, CommandError

from apps.core.models import (
    AnalyseBiologique,
    Compte,
    Prescription,
    Traitement,
    TemplateEdition,
)

DEFAULT_OUTPUT = os.path.join(
    os.path.dirname(__file__), '..', '..', 'fixtures', 'templates_data.json'
)


class Command(BaseCommand):
    help = 'Export template data from local DB to a portable JSON fixture'

    def add_arguments(self, parser):
        parser.add_argument('--compte', type=int, required=True,
                            help='PK of the local Compte to export from')
        parser.add_argument('--output', default=DEFAULT_OUTPUT,
                            help='Output JSON file path')

    def handle(self, *args, **options):
        compte_pk = options['compte']
        try:
            compte = Compte.objects.get(pk=compte_pk)
        except Compte.DoesNotExist:
            raise CommandError(f'Compte with pk={compte_pk} does not exist.')

        self.stdout.write(f'Exporting from: {compte.raison_sociale} (pk={compte.pk})')

        data = {
            'traitements': list(
                Traitement.objects.filter(compte=compte)
                .values('libelle', 'text', 'forme')
            ),
            'analyses': list(
                AnalyseBiologique.objects.filter(compte=compte)
                .values('code', 'libelle', 'type', 'unite', 'modele_resultat', 'ordre')
            ),
            'prescriptions': list(
                Prescription.objects.filter(compte=compte)
                .values('libelle', 'categorie', 'text')
            ),
            'template_editions': list(
                TemplateEdition.objects.filter(compte=compte)
                .values(
                    'libelle', 'contenu',
                    'categorie_consultation__libelle',
                    'motif_consultation__code',
                )
            ),
        }

        output_path = os.path.abspath(options['output'])
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(
            f"\nExported to: {output_path}\n"
            f"  Medications      : {len(data['traitements'])}\n"
            f"  Lab tests        : {len(data['analyses'])}\n"
            f"  Exam templates   : {len(data['prescriptions'])}\n"
            f"  Report templates : {len(data['template_editions'])}\n"
        ))
