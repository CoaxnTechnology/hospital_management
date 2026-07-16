"""
Load default templates for ALL existing Comptes that don't have them yet.

Run once after deployment to populate existing doctor accounts:
    python manage.py load_all_templates

Use --force to reload even accounts that already have templates.
"""
from django.core.management.base import BaseCommand

from apps.core.models import Compte, Traitement
from apps.core.services.doctor_setup import load_default_templates


class Command(BaseCommand):
    help = 'Load default templates for all existing Comptes (skips duplicates by default)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help='Load even for comptes that already have templates',
        )

    def handle(self, *args, **options):
        comptes = Compte.objects.all().order_by('pk')
        total = comptes.count()
        self.stdout.write(f'Found {total} compte(s).')

        skipped = 0
        loaded = 0

        for compte in comptes:
            if not options['force']:
                already_has = Traitement.objects.filter(compte=compte).exists()
                if already_has:
                    self.stdout.write(f'  Skipping {compte.raison_sociale} (pk={compte.pk}) — already has templates.')
                    skipped += 1
                    continue

            self.stdout.write(f'  Loading templates for {compte.raison_sociale} (pk={compte.pk})…')
            try:
                summary = load_default_templates(compte)
                self.stdout.write(self.style.SUCCESS(
                    f'    Done — medications:{summary["traitements"]} labs:{summary["analyses"]} '
                    f'prescriptions:{summary["prescriptions"]} reports:{summary["report_templates"]}'
                ))
                loaded += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'    FAILED: {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'\nFinished. Loaded: {loaded}  Skipped (already had templates): {skipped}'
        ))
