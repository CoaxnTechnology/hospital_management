from django.contrib.auth.models import User, Group
from django.core.management import BaseCommand

from apps.core.models import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        c = Compte.objects.all()
        if not c:
            return

        bordereaux = Bordereau.objects.all()
        for b in bordereaux:
            #b.code_conventionnel = "01/00028755/43"
            b.save()
            reglements = b.reglement_set.all()
            for r in reglements:
                lignes = r.lignes_reglement.all()
                for l in lignes:
                    l.prix_ttc = 13.5
                    l.prix_initial = 45
                    l.save()
            print(reglements)

