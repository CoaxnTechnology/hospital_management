from django.core.management import BaseCommand

from apps.core.models import Compte, TypeOrdonnance, Patient


class Command(BaseCommand):

    def handle(self, *args, **options):
        comptes = Compte.objects.all()
        for c in comptes:
            praticien = c.parametrescompte.praticien_defaut
            if praticien:
                Patient.objects.update(praticien_principal=praticien)
