from django.core.management import BaseCommand

from apps.core.models import *

patients_data = [
    {
        'nom': 'Kelley',
        'nom_naissance': 'Mnajja',
        'prenom': 'Ines',
        'date_naissance': '2000-02-10',
        'telephone': 22019202
    },
    {
        'nom': 'Mcmillan',
        'nom_naissance': 'Kelley',
        'prenom': 'Malachy',
        'date_naissance': '2000-02-10',
        'telephone': 22019202
    },
    {
        'nom': 'Harris',
        'nom_naissance': 'Mcmillan',
        'prenom': 'Phoenix',
        'date_naissance': '2000-02-10',
        'telephone': 22019202
    },
    {
        'nom': 'Mcpherson',
        'nom_naissance': 'Harris',
        'prenom': 'Elisa',
        'date_naissance': '2000-02-10',
        'telephone': 22019202
    },
    {
        'nom': 'Mccullough',
        'nom_naissance': 'Mcpherson',
        'prenom': 'Layla',
        'date_naissance': '2000-02-10',
        'telephone': 22019202
    },
    {
        'nom': 'Nielsen',
        'nom_naissance': 'Mccullough',
        'prenom': 'Jaydon',
        'date_naissance': '2000-02-10',
        'telephone': 22019202
    }
]


class Command(BaseCommand):
    help = "Créer des patients exemple"

    def handle(self, *args, **options):

        c = Compte.objects.first()
        if c:
            for i in range(0, len(patients_data)):
                p = Patient(**patients_data[i], compte=c)
                p.save()

        print('Opération terminée')
