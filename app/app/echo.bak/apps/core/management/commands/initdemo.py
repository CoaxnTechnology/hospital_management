from django.contrib.auth.models import User, Group
from django.core.management import BaseCommand

from apps.core.models import Compte, Profil, Adresse, CategorieConsultation


class Command(BaseCommand):
    help = 'Créer un nouveau compte client'

    def handle(self, *args, **options):
        nom_compte = "Cabinet X"
        c = Compte.objects.filter(raison_sociale=nom_compte)
        if c:
            c[0].categories_consultations.set(CategorieConsultation.objects.all())
            c[0].save()
            return
        compte = Compte(raison_sociale=nom_compte)
        compte.save()

        nom = "JALLOUL"
        prenom = "Taieb"
        username = 'dr'
        password = 'dr1234'
        email = 'dr@example.com'
        tel = '71986754'
        user = User.objects.create_user(
            first_name=prenom, last_name=nom,
            username=username, email=email, password=password)
        user.groups.clear()
        user.groups.add(Group.objects.get(name='Médecin'))

        profil = Profil(compte=compte, user=user, titre='dr')
        profil.save()
        compte.categories_consultations.set(CategorieConsultation.objects.all())
        compte.responsable = user
        compte.adresse = Adresse.objects.create(ville="Tunis")
        compte.telephone = tel
        compte.parametrescompte.praticien_defaut = profil
        compte.parametrescompte.save()
        compte.save()
