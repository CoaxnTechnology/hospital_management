import csv
from io import TextIOWrapper

from django.contrib.auth.models import User, Group
from django.core.management import BaseCommand

from apps.core.models import Compte, Profil, Traitement


def _input(question, min_length=1, default=''):
    while True:
        i = input(question)
        if len(i) == 0 and default != '':
            return default
        if len(i) > min_length:
            break
    return i


class Command(BaseCommand):
    help = 'Créer un nouveau compte client'

    def handle(self, *args, **options):
        nom_compte = _input('Nom du compte: ', min_length=2)

        compte = Compte(raison_sociale=nom_compte)
        compte.save()

        self.stdout.write(self.style.WARNING('Utilisateur principal'))
        nom = _input('Nom: ', min_length=2)
        prenom = _input('Prénom: ', min_length=2)
        def_username = prenom[:1].lower() + '_'.join(nom.split(' ')).lower()
        username = _input('Identifiant ({}): '.format(def_username), min_length=2, default=def_username)
        password = _input('Mot de passe: ', min_length=6)
        email = _input('Email: ', min_length=2)
        user = User.objects.create_user(
            first_name=prenom, last_name=nom,
            username=username, email=email, password=password)
        user.groups.clear()
        user.groups.add(Group.objects.get(name='Médecin'))

        profil = Profil(compte=compte, user=user, titre='dr')
        profil.save()
        compte.responsable = user
        compte.parametrescompte.praticien_defaut = profil
        compte.parametrescompte.save()
        compte.save()
        return

        if _input('Charger les médicaments ? y/n') == 'y':
            # charger les médicaments
            csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='cp1252', errors='replace')
            reader = csv.DictReader(csv_file, delimiter=';')
            entries = []
            compte_pk = -1
            compte = None
            for row in reader:
                libelle = row['libelle']
                text = row['text']
                forme = row['forme']
                entries.append(Traitement(compte=compte, libelle=libelle, text=text, forme=forme))

            Traitement.objects.bulk_create(entries)
            print("Fichier csv importé avec succès")

        if _input('Charger les prescriptions ? y/n') == 'y':
            # charger les prescriptions
            pass


