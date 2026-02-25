import math
import os
import datetime
import random
import time
import uuid

import django.utils.timezone
from django.contrib.auth.models import User
from django.contrib.postgres.forms import SimpleArrayField
from django.db import models
from collections import defaultdict
from apps.core.middleware.request_provider.middleware import get_request
from apps.core.storage import OverwriteStorage
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.postgres.fields import ArrayField
import sys
from tinymce.models import HTMLField

from apps.core.utils import pretty_duration


class BaseModelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True, default=None)
    objects = BaseModelManager()
    objects_with_deleted = models.Manager()

    class Meta:
        abstract = True

    def delete(self, hard=False, **kwargs):
        if hard:
            super().delete()
        else:
            self.deleted_at = datetime.datetime.now()
            self.save()

    def restore(self):
        self.deleted_at = None
        self.save()


class DefaultSelectOrPrefetchManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self._select_related = kwargs.pop('select_related', None)
        self._prefetch_related = kwargs.pop('prefetch_related', None)

        super(DefaultSelectOrPrefetchManager, self).__init__(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        qs = super(DefaultSelectOrPrefetchManager, self).get_queryset(*args, **kwargs)

        if self._select_related:
            qs = qs.select_related(*self._select_related)
        if self._prefetch_related:
            qs = qs.prefetch_related(*self._prefetch_related)

        return qs


class CategorieConsultation(models.Model):
    libelle = models.CharField(max_length=128)

    def __str__(self):
        return self.libelle


class CompteModelBase(BaseModel):
    def save(self, *args, **kwargs):
        try:
            if hasattr(get_request().user, 'profil'):
                self.compte = get_request().user.profil.compte
        except:
            pass
        print('Saving', self.__str__())
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Adresse(models.Model):
    numero = models.PositiveSmallIntegerField(blank=True, null=True)
    rue = models.CharField(max_length=128, blank=True, null=True)
    cite = models.CharField(max_length=128, blank=True, null=True)
    ville = models.CharField(max_length=128, blank=True, null=True)
    cp = models.PositiveSmallIntegerField(blank=True, null=True)
    gouvernorat = models.CharField(max_length=128, blank=True, null=True)
    pays = models.CharField(max_length=128)

    def __str__(self):
        result = ""
        if self.numero:
            result = result + str(self.numero) + " "
        if self.rue:
            result = result + "rue " + self.rue + ", "
        if self.ville:
            result = result + self.ville
        if self.gouvernorat:
            result = result + ", " + self.gouvernorat
        return result

    def natural_key(self):
        return self.ville


GYNECOLOGIE = 'gyneco'
CARDIOLOGIE = 'cardio'
GENERALISTE = 'general'
DISTRIBUTIONS = [(GYNECOLOGIE, 'Gynecologie'), (CARDIOLOGIE, 'Cardiologie'), (GENERALISTE, 'Generaliste')]


class Compte(models.Model):
    raison_sociale = models.CharField(max_length=128)
    adresse = models.ForeignKey(Adresse, on_delete=models.SET_NULL, blank=True, null=True)
    telephone = models.CharField(max_length=20)
    fax = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    langue = models.CharField(max_length=8, default="fr")
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    categories_consultations = models.ManyToManyField(CategorieConsultation, blank=True)

    distribution = models.CharField(max_length=128, choices=DISTRIBUTIONS, default=GYNECOLOGIE)

    objects = DefaultSelectOrPrefetchManager(select_related=('parametrescompte',))

    def __str__(self):
        return self.raison_sociale

    @staticmethod
    def storage_path(instance, filename):
        print('Storage path', 'comptes/compte_{0}/{1}'.format(instance.compte.pk, filename))
        return 'comptes/compte_{0}/{1}'.format(instance.compte.pk, filename)

    def categories(self):
        return [cat.pk for cat in self.categories_consultations.all()]

    def is_gyneco(self):
        return self.distribution == GYNECOLOGIE

    def is_general(self):
        return self.distribution == GENERALISTE

    def is_cardio(self):
        return self.distribution == CARDIOLOGIE

    def product_brand(self):
        if self.distribution == GYNECOLOGIE:
            return 'Expert Echo'
        if self.distribution == CARDIOLOGIE:
            return 'Expert Echo'
        if self.distribution == GENERALISTE:
            return 'Expert Médical'

def repertoire_utilisateur(instance, filename):
    path = 'comptes/compte_{0}/utilisateurs/{1}/{2}'.format(instance.compte.pk, instance.user.pk, filename)
    print('Enregistrement dans ', path)
    return path


class Profil(CompteModelBase):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    titre = models.CharField(max_length=8, choices=[('dr', 'Docteur'), ('pr', 'Professeur'), ('mme', 'Madame'),
                                                    ('mlle', 'Mademoiselle'),
                                                    ('mr', 'Monsieur')])
    code_conventionnel=models.CharField(max_length=128, blank=True, null=True)
    date_naissance = models.DateField(blank=True, null=True)
    telephone_principal = models.CharField(max_length=20, blank=True, null=True)
    telephone_secondaire = models.CharField(max_length=20, blank=True, null=True)
    signature = models.ImageField(upload_to=repertoire_utilisateur, storage=OverwriteStorage(), blank=True, null=True)
    ajouter_signature_edition = models.BooleanField(default=True)
    code_securite_sociale = models.CharField(max_length=128, blank=True, null=True)
    enligne = models.SmallIntegerField(default=0)
    default_device = models.ForeignKey('Device', on_delete=models.SET_NULL, blank=True, null=True)
    objects = DefaultSelectOrPrefetchManager(select_related=('user', 'compte',))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.signature:
            return
        fichier_temp = self.signature.path
        im = Image.open(self.signature)
        format = im.format
        mime = Image.MIME[format]
        f, extension = os.path.splitext(self.signature.name)
        output = BytesIO()
        max_height = 100
        ratio = im.width / im.height
        if im.height > max_height:
            # Resize/modify the image
            im = im.resize((int(max_height * ratio), max_height))
        # after modifications, save it to the output
        im.save(output, format=format, quality=100)
        output.seek(0)
        # change the imagefield value to be the newley modifed image value
        filename = "signature{}".format(extension)
        self.signature = InMemoryUploadedFile(output, 'ImageField', filename, mime, sys.getsizeof(output), None)
        #super().save(*args, **kwargs)
        # Supprimer le fichier temporaire
        #if os.path.isfile(fichier_temp):
        #    os.remove(fichier_temp)

    def __str__(self):
        return self.user.get_full_name()

    @property
    def nom(self):
        return self.user.get_full_name()

    @property
    def titre_nom(self):
        return u'{}. {}'.format(self.titre.capitalize(), self.user.get_full_name())

    @property
    def initiales(self):
        return self.user.first_name[0] + self.user.last_name[0]

    @property
    def groupe(self):
        res = []
        for g in self.user.groups.all():
            res.append(g.name)
        return " ".join(res)

    @property
    def responsable(self):
        return self.compte.responsable == self.user

    def is_medecin(self):
        return 'Médecin' in self.user.profil.groupe

    def ville(self):
        return self.compte.adresse.ville


class MedecinManager(DefaultSelectOrPrefetchManager):

    def get_queryset(self, *args, **kwargs):
        qs = super(DefaultSelectOrPrefetchManager, self).get_queryset(*args, **kwargs)
        return qs.filter(user__groups__name='Médecin')


class Medecin(Profil):
    objects = MedecinManager(prefetch_related=('user',))

    class Meta:
        proxy = True

    def __str__(self):
        return u'{}. {}'.format(self.titre.capitalize(), self.user.get_full_name())

    def natural_key(self):
        return '{}. {}'.format(self.titre.capitalize(), self.user.get_full_name())

    @property
    def nom(self):
        return u'{}. {}'.format(self.titre.capitalize(), self.user.get_full_name())


def logo_storage_path(instance, filename):
    name, ext = os.path.splitext(filename)
    return 'comptes/compte_{0}/{1}'.format(instance.compte.pk, 'logo' + ext)


def logo_storage_path_a4(instance, filename):
    name, ext = os.path.splitext(filename)
    return 'comptes/compte_{0}/{1}'.format(instance.compte.pk, 'logo_a4' + ext)


def footer_storage_path(instance, filename):
    name, ext = os.path.splitext(filename)
    return 'comptes/compte_{0}/{1}'.format(instance.compte.pk, 'footer' + ext)


def footer_storage_path_a4(instance, filename):
    name, ext = os.path.splitext(filename)
    return 'comptes/compte_{0}/{1}'.format(instance.compte.pk, 'footer_a4' + ext)


class ParametresCompte(models.Model):
    compte = models.OneToOneField(Compte, on_delete=models.CASCADE)
    timezone = models.CharField(max_length=128, blank=True, null=True)
    duree_rdv_defaut = models.PositiveSmallIntegerField(blank=True, null=True)
    praticien_defaut = models.ForeignKey(Medecin, on_delete=models.SET_NULL, blank=True, null=True)
    antecedents_familiaux_defaut = models.TextField(blank=True, null=True)
    antecedents_medico_chirurgicaux_defaut = models.TextField(blank=True, null=True)
    antecedents_gynecologiques_defaut = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to=logo_storage_path, max_length=128, blank=True, null=True)
    logo_a4 = models.ImageField(upload_to=logo_storage_path_a4, max_length=128, blank=True, null=True)
    footer = models.ImageField(upload_to=footer_storage_path, max_length=128, blank=True, null=True)
    footer_a4 = models.ImageField(upload_to=footer_storage_path_a4, max_length=128, blank=True, null=True)
    nom_entete = models.TextField(blank=True, null=True)
    marge_entete = models.SmallIntegerField(default=100)
    marge_footer = models.SmallIntegerField(default=80)
    marge_gauche = models.SmallIntegerField(default=20)
    marge_droite = models.SmallIntegerField(default=20)

    # Parametres impression
    ajouter_antecedents_edition = models.BooleanField(default=False)
    ajouter_entetes_edition = models.BooleanField(default=True)
    ajouter_entete_ord = models.BooleanField(default=True)
    ajouter_entete_cert_med = models.BooleanField(default=True)
    ajouter_entete_cert_pres = models.BooleanField(default=True)
    ajouter_entete_lettre_acc = models.BooleanField(default=True)
    ajouter_entete_prescr_bio = models.BooleanField(default=True)
    ajouter_entete_lettre_confidentielle = models.BooleanField(default=True)
    ajouter_entete_attestation_grossesse = models.BooleanField(default=True)
    ajouter_entete_lettre_fittofly = models.BooleanField(default=True)
    ajouter_date_courriers = models.BooleanField(default=True)
    ajouter_date_cro = models.BooleanField(default=True)

    # Grossesse
    duree_gross_sa = models.PositiveSmallIntegerField(default=40)
    duree_gross_j = models.PositiveSmallIntegerField(default=3)

    gross_echo_datation_sa_1 = models.PositiveSmallIntegerField(default=7)
    gross_echo_datation_j_1 = models.PositiveSmallIntegerField(default=0)
    gross_echo_datation_sa_2 = models.PositiveSmallIntegerField(default=9)
    gross_echo_datation_j_2 = models.PositiveSmallIntegerField(default=0)

    gross_echo_t1_sa_1 = models.PositiveSmallIntegerField(default=11)
    gross_echo_t1_j_1 = models.PositiveSmallIntegerField(default=0)
    gross_echo_t1_sa_2 = models.PositiveSmallIntegerField(default=14)
    gross_echo_t1_j_2 = models.PositiveSmallIntegerField(default=0)

    gross_echo_t2_sa_1 = models.PositiveSmallIntegerField(default=20)
    gross_echo_t2_j_1 = models.PositiveSmallIntegerField(default=0)
    gross_echo_t2_sa_2 = models.PositiveSmallIntegerField(default=25)
    gross_echo_t2_j_2 = models.PositiveSmallIntegerField(default=0)

    gross_echo_t3_sa_1 = models.PositiveSmallIntegerField(default=30)
    gross_echo_t3_j_1 = models.PositiveSmallIntegerField(default=0)
    gross_echo_t3_sa_2 = models.PositiveSmallIntegerField(default=35)
    gross_echo_t3_j_2 = models.PositiveSmallIntegerField(default=0)

    gross_12_sa = models.PositiveSmallIntegerField(default=12)
    gross_12_j = models.PositiveSmallIntegerField(default=0)
    gross_22_sa = models.PositiveSmallIntegerField(default=22)
    gross_22_j = models.PositiveSmallIntegerField(default=0)
    gross_32_sa = models.PositiveSmallIntegerField(default=32)
    gross_32_j = models.PositiveSmallIntegerField(default=0)

    gross_triso_1_sa_1 = models.PositiveSmallIntegerField(default=11)
    gross_triso_1_j_1 = models.PositiveSmallIntegerField(default=0)
    gross_triso_1_sa_2 = models.PositiveSmallIntegerField(default=13)
    gross_triso_1_j_2 = models.PositiveSmallIntegerField(default=0)

    gross_triso_2_sa_1 = models.PositiveSmallIntegerField(default=14)
    gross_triso_2_j_1 = models.PositiveSmallIntegerField(default=0)
    gross_triso_2_sa_2 = models.PositiveSmallIntegerField(default=18)
    gross_triso_2_j_2 = models.PositiveSmallIntegerField(default=0)

    gross_gly_sa_1 = models.PositiveSmallIntegerField(default=24)
    gross_gly_j_1 = models.PositiveSmallIntegerField(default=0)
    gross_gly_sa_2 = models.PositiveSmallIntegerField(default=28)
    gross_gly_j_2 = models.PositiveSmallIntegerField(default=0)


    # Modèles courriers
    modele_certificat_medical = HTMLField(blank=True, null=True)
    modele_certificat_presence = HTMLField(blank=True, null=True)
    modele_lettre_accouchement = HTMLField(blank=True, null=True)
    modele_presc_analyse_bio = HTMLField(blank=True, null=True)
    modele_lettre_confidentielle = HTMLField(blank=True, null=True)
    modele_attestation_grossesse = HTMLField(blank=True, null=True)
    modele_lettre_fittofly = HTMLField(blank=True, null=True)

    # Horarires d'ouverture
    h_deb_mat_lundi = models.TimeField(default=datetime.time(8, 0, 0))
    h_fin_mat_lundi = models.TimeField(default=datetime.time(13, 0, 0))
    h_deb_mat_mardi = models.TimeField(default=datetime.time(8, 0, 0))
    h_fin_mat_mardi = models.TimeField(default=datetime.time(13, 0, 0))
    h_deb_mat_mercredi = models.TimeField(default=datetime.time(8, 0, 0))
    h_fin_mat_mercredi = models.TimeField(default=datetime.time(13, 0, 0))
    h_deb_mat_jeudi = models.TimeField(default=datetime.time(8, 0, 0))
    h_fin_mat_jeudi = models.TimeField(default=datetime.time(13, 0, 0))
    h_deb_mat_vendredi = models.TimeField(default=datetime.time(8, 0, 0))
    h_fin_mat_vendredi = models.TimeField(default=datetime.time(13, 0, 0))
    h_deb_mat_samedi = models.TimeField(default=datetime.time(8, 0, 0))
    h_fin_mat_samedi = models.TimeField(default=datetime.time(13, 0, 0))
    h_deb_am_lundi = models.TimeField(default=datetime.time(14, 0, 0))
    h_fin_am_lundi = models.TimeField(default=datetime.time(18, 0, 0))
    h_deb_am_mardi = models.TimeField(default=datetime.time(14, 0, 0))
    h_fin_am_mardi = models.TimeField(default=datetime.time(18, 0, 0))
    h_deb_am_mercredi = models.TimeField(default=datetime.time(14, 0, 0))
    h_fin_am_mercredi = models.TimeField(default=datetime.time(18, 0, 0))
    h_deb_am_jeudi = models.TimeField(default=datetime.time(14, 0, 0))
    h_fin_am_jeudi = models.TimeField(default=datetime.time(18, 0, 0))
    h_deb_am_vendredi = models.TimeField(default=datetime.time(14, 0, 0))
    h_fin_am_vendredi = models.TimeField(default=datetime.time(18, 0, 0))
    h_deb_am_samedi = models.TimeField(default=datetime.time(14, 0, 0))
    h_fin_am_samedi = models.TimeField(default=datetime.time(18, 0, 0))

    def __str__(self):
        return self.compte.raison_sociale

    def save(self, *args, **kwargs):
        # Opening the uploaded image
        super().save(*args, **kwargs)
        if not self.logo:
            return
        return
        print('Resizing logo')
        im = Image.open(self.logo)
        output = BytesIO()
        max_height = 100
        ratio = im.width / im.height
        if im.height > max_height:
            # Resize/modify the image
            im = im.resize((int(max_height * ratio), max_height), Image.LANCZOS)
        # after modifications, save it to the output
        im.save(output, format='PNG', quality=100)
        output.seek(0)
        # change the imagefield value to be the newley modifed image value
        self.logo = InMemoryUploadedFile(output, 'ImageField', "logo.png", 'image/png', sys.getsizeof(output), None)
        super().save(*args, **kwargs)

    @property
    def duree_grossesse(self):
        return self.duree_gross_sa * 7 + self.duree_gross_j


class Etablissement(CompteModelBase):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, null=True)
    nom = models.CharField(max_length=128)
    telephone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nom

    def natural_key(self):
        return self.nom


class Praticien(CompteModelBase):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    titre = models.CharField(max_length=8, default='Dr',
                             choices=[('Dr', 'Dr'), ('Pr', 'Pr'),
                                      ('Mme', 'Mme'),
                                      ('Mlle', 'Mlle'),
                                      ('Mr', 'Mr')])
    prenom = models.CharField(max_length=128)
    nom = models.CharField(max_length=128)
    specialite = models.CharField(max_length=128)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return '{}. {} {}'.format(self.titre, self.nom, self.prenom)

    @property
    def nom_complet(self):
        return 'Dr. {} {}'.format(self.nom, self.prenom)


class InformationsConjoint(models.Model):
    nom_conjoint = models.CharField(max_length=256, blank=True, null=True)
    prenom_conjoint = models.CharField(max_length=256, blank=True, null=True)
    date_naissance_conjoint = models.DateField(blank=True, null=True)
    telephone_conjoint = models.CharField(max_length=20, blank=True, null=True)
    groupe_sanguin_conjoint = models.CharField(
        choices=[('A-', 'A négatif'), ('A+', 'A positif'),
                 ('B-', 'B négatif'), ('B+', 'B positif'),
                 ('AB-', 'AB négatif'), ('AB+', 'AB positif'),
                 ('O-', 'O négatif'), ('O+', 'O positif')],
        max_length=3, blank=True, null=True
    )
    consanguinite_conjoint = models.CharField(max_length=256, default='', blank=True, null=True, choices=[('', ''), ('oui', 'Oui'), ('non', 'Non')])
    etat_sante_conjoint = models.TextField(blank=True, null=True)
    profession_conjoint = models.CharField(max_length=512, blank=True, null=True)
    date_mariage = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True

    @property
    def anciennete_mariage(self):
        if self.date_mariage:
            return pretty_duration((datetime.date.today() - self.date_mariage).days)
        else:
            return ""


class InformationsMutuelle(models.Model):
    mutuelle = models.BooleanField(default=False)
    designation = models.CharField(max_length=128, default='CNAM')
    caisse_affectation = models.CharField(max_length=128, blank=True, null=True, default='1',
                                          choices=[('1', 'CNRPS'), ('2', 'CNSS')])
    regime = models.CharField(max_length=128, blank=True, null=True, default='1',
                              choices=[('1', 'Tiers payant'), ('2', 'Remboursement'),
                                       ('3', 'Publique')])
    lien_parente = models.CharField(max_length=128, blank=True, null=True, default='1',
                                    choices=[('1', 'Assuré'), ('2', 'Conjoint'),
                                             ('3', 'Enfant'), ('4', 'Pere'), ('5', 'Mere')])
    num_carnet_soin = models.CharField(max_length=10, blank=True, null=True)
    code_medecin_famille = models.CharField(max_length=128, blank=True, null=True)
    date_validite_mutuelle = models.DateField(blank=True, null=True)
    code_apci = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        abstract = True


class Patient(CompteModelBase, InformationsConjoint, InformationsMutuelle):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    civilite = models.CharField(max_length=8, default='mme',
                                choices=[('mme', 'Madame'), ('mlle', 'Mademoiselle'), ('mr', 'Monsieur')])
    prenom = models.CharField(max_length=128)
    nom = models.CharField(max_length=128, blank=True, null=True)
    nom_naissance = models.CharField(max_length=128, blank=True, null=True)
    sexe = models.CharField(max_length=1, default='F', choices=[('F', 'Femme'), ('H', 'Homme')])
    date_naissance = models.DateField()
    numero_identite = models.CharField(max_length=128, blank=True, null=True)
    code_securite_sociale = models.CharField(max_length=128, blank=True, null=True)
    adresse = models.ForeignKey(Adresse, on_delete=models.SET_NULL, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    telephone_secondaire = models.CharField(max_length=20, blank=True, null=True)
    telephone_autre = models.CharField(max_length=20, blank=True, null=True)
    profession = models.CharField(max_length=128, blank=True, null=True)
    observation = models.TextField(blank=True, null=True)
    taille = models.FloatField(blank=True, null=True)  # Taille en cm
    poids = models.FloatField(blank=True, null=True)  # Poids en kg
    groupe_sanguin = models.CharField(
        choices=[('A-', 'A négatif'), ('A+', 'A positif'),
                 ('B-', 'B négatif'), ('B+', 'B positif'),
                 ('AB-', 'AB négatif'), ('AB+', 'AB positif'),
                 ('O-', 'O négatif'), ('O+', 'O positif')],
        max_length=3, blank=True, null=True
    )
    fumeur = models.BooleanField(default=False)
    nombre_cigarettes = models.PositiveSmallIntegerField(blank=True, null=True)
    origine = models.CharField(max_length=128, blank=True, null=True,
                               choices=[('1', 'Europe/Afrique du nord'), ('2', 'Afrique sud-saharienne'),
                                        ('3', 'Amérique latine'), ('4', 'Asie'), ('10', 'Autre')])
    antecedents_familiaux = models.TextField(blank=True, null=True)
    antecedents_medico_chirurgicaux = models.TextField(blank=True, null=True)
    antecedents_gynecologiques = models.TextField(blank=True, null=True)
    antecedents_cardio = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    praticien_principal = models.ForeignKey(Medecin, on_delete=models.SET_NULL, blank=True, null=True)
    praticiens_correspondants = models.ManyToManyField(Praticien, blank=True)
    lieu_accouchement = models.ForeignKey(Etablissement, on_delete=models.SET_NULL, blank=True, null=True)
    mot_cle = models.CharField(max_length=256, blank=True, null=True)
    notes = models.TextField(blank=True, default='')
    nouveau = models.BooleanField(default=True)  # nouveau patient = 1ère consultation
    # Numéro dans l'ancien systeme du client
    ancien_numero = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return "{} {}".format(self.prenom, self.nom)

    @property
    def identifiant_unique(self):
        return 'IPP' + str(self.pk).zfill(5)

    @property
    def ville(self):
        if self.adresse:
            return self.adresse.ville
        else:
            return ''

    @property
    def age(self):
        if self.date_naissance is None:
            return '-'
        today = datetime.date.today()
        return today.year - self.date_naissance.year - (
                (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day))

    @property
    def titre(self):
        feminin = 'e' if self.sexe == 'F' else ''
        return "Patient{} {} - {} ans".format(feminin, self.nom_complet, self.age)

    @property
    def nom_complet(self):
        if self.nom_naissance is None:
            self.nom_naissance = self.nom
        if self.nom is None:
            self.nom = self.nom_naissance
        if self.nom != self.nom_naissance:
            return f"{self.prenom} {self.nom_naissance} ep {self.nom}"
        else:
            return f"{self.prenom} {self.nom_naissance}"

    @property
    def nom_famille(self):
        if self.nom_naissance is None:
            self.nom_naissance = self.nom
        if self.nom is None:
            self.nom = self.nom_naissance
        if self.nom != self.nom_naissance:
            return f"{self.nom_naissance} ep {self.nom}"
        else:
            return f"{self.nom_naissance}"

    @property
    def conjoint(self):
        ret = ""
        if self.prenom_conjoint:
            ret = ret + self.prenom_conjoint
        if self.nom_conjoint:
            ret = ret + " " + self.nom_conjoint
        return ret

    @property
    def grossesse_encours(self):
        grossesse = self.grossesse_set.filter(encours=True)
        if len(grossesse):
            return grossesse[0]
        else:
            return None

    @property
    def interrogatoire_pma(self):
        interrogatoirepma = None
        if self.interrogatoirepma_set.all().count() > 0:
            print("Count", self.interrogatoirepma_set.all().count())
            interrogatoirepma = self.interrogatoirepma_set.first()
        return interrogatoirepma

    @property
    def pma_encours(self):
        pma = self.tentativepma_set.filter(encours=True)
        if len(pma):
            return pma[0]
        else:
            return None

    @property
    def antecedents_obstetriques(self):
        return AntecedentObstetrique.objects\
            .filter(patient=self, sous_categorie__categorie=4)\
            .order_by('-date_accouchement')

    @property
    def imc(self):
        if self.taille and self.poids:
            taille = self.taille * 0.01
            IMC = self.poids / (taille * taille)
            return round(IMC, 1)
        return ''

    def fichiers(self):
        fichiers = defaultdict(list)
        for result in self.fichierpatient_set.values('dossier__nom', 'nom', 'fichier', 'pk', 'date').order_by(
                'dossier__nom', 'nom'):
            fichiers[result['dossier__nom']].append(
                {'pk': result['pk'], 'nom': result['nom'], 'chemin': result['fichier'], 'date': result['date']})
        return dict(fichiers)

    def check_doublon_consultation(self, motif, date):
        print('check_doublon_consultation', motif, date)
        return self.consultation_set.filter(motif=motif,
                                            date__day=date.day,
                                            date__month=date.month,
                                            date__year=date.year).first()

    def antecedents_medico_chirurgicaux_compresse(self):
        if not self.antecedents_medico_chirurgicaux:
            return ''
        res = self.antecedents_medico_chirurgicaux\
            .replace('<p>', '').replace('</p>', ', ').replace('<br />', ', ')
        if len(res) > 2 and res[-2] == ',':
            res = res[:len(res)-2]
        if res[0] == ',':
            res = res[1:]
        return res

    def antecedents_gynecologiques_compresse(self):
        if not self.antecedents_gynecologiques:
            return ''
        res = self.antecedents_gynecologiques\
            .replace('<p>', '').replace('</p>', ', ').replace('<br />', ', ')
        if len(res) > 2 and res[-2] == ',':
            res = res[:len(res)-2]
        if res[0] == ',':
            res = res[1:]
        return res

    @property
    def mesures_jour(self):
        t = datetime.date.today()
        mesures = self.mesurespatient_set.filter(date__day=t.day, date__month=t.month, date__year=t.year).first()
        #print('Mesures du jour', mesures)
        return mesures

    def ta(self):
        g = self.grossesse_encours
        if g:
            exams = g.consultationobstetrique_set.all().order_by('-id')
            if len(exams) > 0:
                dernier_exam = exams[0]
                return dernier_exam.ta if dernier_exam.ta else ""


class Bordereau(models.Model):
    bordereau_id = models.IntegerField()
    nom_medecin = models.CharField(max_length=128, blank=True, null=True)
    code_conventionnel = models.CharField(max_length=128, blank=True, null=True)
    date_bordereau = models.DateTimeField(default=django.utils.timezone.now)

    @property
    def periode(self):
        r = self.reglement_set.order_by('date_creation')
        if len(r) > 0:
            return f"{r.first().date_creation.strftime('%d/%m/%y')} - {r.last().date_creation.strftime('%d/%m/%y')}"
        return ""

    @property
    def periode_format(self):
        r = self.reglement_set.order_by('date_creation')
        if len(r) > 0:
            return f"du {r.first().date_creation.strftime('%d/%m/%y')} au {r.last().date_creation.strftime('%d/%m/%y')}"
        return ""

    def periode_debut(self):
        r = self.reglement_set.order_by('date_creation')
        if len(r) > 0:
            return r.first().date_creation
        return None

    def periode_fin(self):
        r = self.reglement_set.order_by('date_creation')
        if len(r) > 0:
            return r.last().date_creation
        return None

    @property
    def nombre_reglements(self):
        return self.reglement_set.count()

    @property
    def num_bordereau(self):
       return f"{self.bordereau_id} / {self.date_bordereau.strftime('%Y')}"

    @property
    def total(self):
        t = 0
        for r in self.reglement_set.all():
            t += r.total
        return t

    @property
    def ticket_moderateur(self):
        t = 0
        for r in self.reglement_set.all():
            t += r.ticket_moderateur
        return t

    @property
    def prise_en_charge(self):
        return self.total - self.ticket_moderateur


class DossierFichiersPatient(models.Model):
    nom = models.CharField(max_length=128)

    def __str__(self):
        return self.nom


def repertoire_patient(instance, filename):
    return 'comptes/compte_{0}/patients/{1}/{2}'.format(instance.patient.compte.pk, instance.patient.pk, filename)


class FichierPatient(models.Model):
    nom = models.CharField(max_length=128)
    dossier = models.ForeignKey(DossierFichiersPatient, on_delete=models.CASCADE)
    fichier = models.FileField(upload_to=repertoire_patient)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateTimeField()

    def __str__(self):
        return "{}/{}".format(self.dossier, self.nom)


class CatgeorieAntecedent(models.Model):
    libelle = models.CharField(max_length=128)

    def __str__(self):
        return self.libelle

    def natural_key(self):
        return self.libelle


class SousCatgeorieAntecedent(models.Model):
    libelle = models.CharField(max_length=128)
    categorie = models.ForeignKey(CatgeorieAntecedent, on_delete=models.CASCADE)

    def __str__(self):
        return self.libelle

    def natural_key(self):
        return self.libelle


class Antecedent(CompteModelBase):
    sous_categorie = models.ForeignKey(SousCatgeorieAntecedent, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.text

    def natural_key(self):
        return self.text


class MotifRdv(models.Model):
    libelle = models.CharField(max_length=128)

    def __str__(self):
        return self.libelle

    def natural_key(self):
        return self.libelle


class Rdv(CompteModelBase):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    debut = models.DateTimeField()
    fin = models.DateTimeField()
    ancien_debut = models.DateTimeField(blank=True, null=True)  # Pour retrouver les rdv modifiés
    prenom = models.CharField(max_length=128)
    nom = models.CharField(max_length=128, blank=True, null=True)
    nom_naissance = models.CharField(max_length=128, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    cp = models.PositiveSmallIntegerField(blank=True, null=True)
    ville = models.CharField(max_length=128, blank=True, null=True)
    gouvernorat = models.CharField(max_length=128, blank=True, null=True)
    motif = models.ForeignKey(MotifRdv, on_delete=models.CASCADE)
    nouveau = models.BooleanField(default=True)
    observation = models.CharField(max_length=256, blank=True, null=True)
    praticien = models.ForeignKey(Medecin, on_delete=models.SET_NULL, blank=True, null=True)
    statut = models.CharField(max_length=2, default=1,
                              choices=[(1, 'Confirmé'), (2, 'En salle'), (3, 'Consultation terminée'), (10, 'Annulé')])
    motif_modification = models.CharField(max_length=128, blank=True, null=True)  # Motif de modification/annulation
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, blank=True, null=True)
    patient_rappele = models.BooleanField(default=False)

    class Meta:
        ordering = ['-debut']

    def __str__(self):
        return "{}-{} - {}".format(self.debut, self.fin, self.motif)

    @property
    def nom_famille(self):
        if self.nom_naissance is None:
            self.nom_naissance = self.nom
        if self.nom is None:
            self.nom = self.nom_naissance
        if self.nom != self.nom_naissance:
            return f"{self.nom_naissance} ep {self.nom}"
        else:
            return f"{self.prenom} {self.nom_naissance}"

    @property
    def is_missed(self):
        p = self.patient
        today = datetime.date.today()
        if self.debut.date() >= today:
            return False
        if p:
            return p.consultation_set.filter(date__day=self.debut.day,
                                             date__month=self.debut.month,
                                             date__year=self.debut.year).count() == 0
        return False


class MesuresPatient(BaseModel):
    date = models.DateTimeField(default=django.utils.timezone.now)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    ta = models.CharField(max_length=256, blank=True, null=True)
    temperature = models.FloatField(blank=True, null=True)
    poids = models.FloatField(blank=True, null=True)
    gly = models.CharField(max_length=256, blank=True, null=True)


class MotifConsultation(models.Model):
    libelle = models.CharField(max_length=128)
    code = models.CharField(max_length=128)
    categorie = models.ForeignKey(CategorieConsultation, on_delete=models.CASCADE)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.libelle

    def natural_key(self):
        return self.code


class Consultation(CompteModelBase):
    motif = models.ForeignKey(MotifConsultation, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.date.today)
    praticien = models.ForeignKey(Medecin, on_delete=models.SET_NULL, blank=True, null=True)
    conclusion = models.TextField(blank=True, null=True)
    conduite = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.motif.libelle} - {self.patient.nom_complet} - {self.date}"

    def modif_url(self):
        if self.motif.code == 'gynecologique-defaut':
            return f"/consultation_gynecologique/{self.id}/modifier/"
        if self.motif.code == 'colposcopie':
            return f"/consultation_colposcopie/{self.id}/modifier/"
        if self.motif.code == 'echo-pelvienne':
            return f"/consultation_echo_pelvienne/{self.id}/modifier/"
        if self.motif.code == 'obs_echo_11SA':
            return f"/consultation_obs_echo_11SA/{self.id}/modifier/"
        if self.motif.code == 'obs_echo_trimestre_1':
            return f"/consultation_obs_echo_premier_trimestre/{self.id}/modifier/"
        if self.motif.code == 'obs_echo_trimestre_2':
            return f"/consultation_obs_echo_deuxieme_trimestre/{self.id}/modifier/"
        if self.motif.code == 'obs_echo_trimestre_3':
            return f"/consultation_obs_echo_troisieme_trimestre/{self.id}/modifier/"
        if self.motif.code == 'obs_echo_croissance':
            return f"/consultation_obs_echo_croissance/{self.id}/modifier/"
        return f"/patients/{self.patient.id}/consultation/{self.id}/modifier/"


#class ConsultationRapport(CompteModelBase):
#    categorie = models.

class FormulaireConsultation(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    edition = models.TextField()


class Admission(models.Model):
    numero = models.PositiveIntegerField()
    date = models.DateTimeField()
    debut_consultation = models.DateTimeField(blank=True, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    praticien = models.ForeignKey(Medecin, on_delete=models.SET_NULL, blank=True, null=True)
    motif = models.ForeignKey(MotifRdv, default=1, on_delete=models.CASCADE)
    ordre = models.PositiveSmallIntegerField()
    statut = models.CharField(max_length=2, default=1,
                              choices=[(1, 'En attente'), (2, 'En consultation'), (3, 'Consultation terminée'),
                                       (10, 'Annulé')])

    def numero_admission(self):
        return "{}/{}".format(str(self.numero).zfill(5), self.date.year)

    @property
    def nb_reglements(self):
        return self.reglements.count()


class PhrasierAntecedent(models.Model):
    libelle = models.CharField(max_length=256)
    text = models.TextField()
    categorie = models.ForeignKey(CatgeorieAntecedent, on_delete=models.CASCADE)

    def __str__(self):
        return self.libelle


class TypeOrdonnance(CompteModelBase):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    libelle = models.CharField(max_length=256)
    modele = HTMLField(blank=True)

    def __str__(self):
        return f"{self.libelle}"

    def natural_key(self):
        return self.__str__()


class Ordonnance(models.Model):
    date = models.DateField()
    type = models.ForeignKey(TypeOrdonnance, on_delete=models.SET_NULL, blank=True, null=True)
    text = models.TextField()
    praticien = models.ForeignKey(Medecin, on_delete=models.SET_NULL, blank=True, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-date']


class Prescription(CompteModelBase):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    libelle = models.CharField(max_length=256)
    categorie = models.CharField(max_length=256, default='',
                                 choices=[('examen_complementaire', 'Examen complémentaire')])
    text = models.TextField()

    def __str__(self):
        return self.libelle


class Traitement(CompteModelBase):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    libelle = models.CharField(max_length=256)
    forme = models.CharField(max_length=256, default='comprime',
                             choices=[('comprime', 'Comprimé'), ('gelule', 'Gélule'), ('gel', 'Gel'), ('gouttes', 'Gouttes'), ('injection', 'Injection'),
                                      ('pommade', 'Pommade'), ('poudre', 'Poudre'), ('sirop', 'Sirop'), ('suppositoire', 'Suppositoire'), ('autre', 'Autre')])
    text = models.TextField()  # Posologie

    def __str__(self):
        return self.libelle


CERTIFICAT_MEDICAL = 'certificat_medical'
CERTIFICAT_PRESENCE = 'certificat_presence'
LETTRE_ACCOUCHEMENT = 'lettre_accouchement'
LETTRE_CONFIDENTIELLE = 'lettre_confidentielle'
ATTESTATION_GROSSESSE = 'attestation_grossesse'
LETTRE_FITTOFLY = 'lettre_fittofly'
TYPES_CERTIFICATS = [(CERTIFICAT_MEDICAL, 'CERTIFICAT MEDICAL'),
                     (CERTIFICAT_PRESENCE, 'CERTIFICAT MEDICAL DE PRESENCE'),
                     (LETTRE_ACCOUCHEMENT, "LETTRE D'ACCOUCHEMENT"),
                     (LETTRE_CONFIDENTIELLE, "LETTRE CONFIDENTIELLE"),
                     (ATTESTATION_GROSSESSE, "ATTESTATION DE GROSSESSE"),
                     (LETTRE_FITTOFLY, "CERTIFICAT MEDICAL FIT TO FLY")]


class Certificat(models.Model):
    date = models.DateField()
    duree = models.IntegerField(default=1)
    type = models.CharField(max_length=128, default=CERTIFICAT_MEDICAL, choices=TYPES_CERTIFICATS)
    text = models.TextField()
    praticien = models.ForeignKey(Medecin, on_delete=models.SET_NULL, blank=True, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)


class Prestation(CompteModelBase):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    prestation = models.CharField(max_length=128)
    code = models.CharField(max_length=128)
    prix_ttc = models.FloatField(blank=True, null=True)
    prix_pec= models.FloatField(blank=True, null=True)
    date_creation = models.DateTimeField(default=django.utils.timezone.now)
    par_defaut = models.BooleanField(default=False)

    def __str__(self):
        return self.code


class MotifAbsence(CompteModelBase):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    motif = models.CharField(max_length=128)

    def __str__(self):
        return self.motif

    def natural_key(self):
        return self.motif


class AbsenceMedecin(CompteModelBase):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, blank=True, null=True)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    motif = models.ForeignKey(MotifAbsence, on_delete=models.SET_NULL, blank=True, null=True)
    praticien = models.ForeignKey(Medecin, on_delete=models.SET_NULL, blank=True, null=True,
                                  related_name='medecin_principale')
    praticien_remplacant = models.ForeignKey(Medecin, on_delete=models.SET_NULL, blank=True, null=True,
                                             related_name='medecin_remplacant')


class ProgrammeOperatoire(CompteModelBase):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    debut = models.DateTimeField()
    fin = models.DateTimeField()
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, blank=True, null=True)
    type_acte = models.CharField(max_length=256, blank=True, null=True)
    lieu_accouchement = models.ForeignKey(Etablissement, blank=True, null=True, on_delete=models.SET_NULL)
    observation = models.CharField(max_length=256, blank=True, null=True)
    praticien = models.ForeignKey(Medecin, on_delete=models.SET_NULL, blank=True, null=True)


# Liste choix pour les formulaires
class ListeChoix(models.Model):
    formulaire = models.CharField(max_length=256)
    champ = models.CharField(max_length=256)
    libelle = models.CharField(max_length=256)
    valeur = models.TextField(blank=True)
    actif = models.BooleanField(default=True)
    normale = models.BooleanField(default=False) # Utilisé avec la fonction "Tout normal" des formulaires

    def __str__(self):
        return "{}".format(self.libelle)


class ListeChoixActifManager(DefaultSelectOrPrefetchManager):

    def get_queryset(self, *args, **kwargs):
        qs = super(DefaultSelectOrPrefetchManager, self).get_queryset(*args, **kwargs)
        return qs.filter(actif=True)


class ListeChoixActif(ListeChoix):
    objects = ListeChoixActifManager()

    class Meta:
        proxy = True


class Grossesse(BaseModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    encours = models.BooleanField(default=True)
    # Conjoint
    nom_conjoint = models.CharField(max_length=256, blank=True, null=True)
    prenom_conjoint = models.CharField(max_length=256, blank=True, null=True)
    date_naissance_conjoint = models.DateField(blank=True, null=True)
    telephone_conjoint = models.CharField(max_length=20, blank=True, null=True)
    groupe_sanguin_conjoint = models.CharField(
        choices=[('A-', 'A négatif'), ('A+', 'A positif'),
                 ('B-', 'B négatif'), ('B+', 'B positif'),
                 ('AB-', 'AB négatif'), ('AB+', 'AB positif'),
                 ('O-', 'O négatif'), ('O+', 'O positif')],
        max_length=3, blank=True, null=True
    )
    consanguinite_conjoint = models.CharField(max_length=256, default='', blank=True, null=True, choices=[('', ''), ('oui', 'Oui'), ('non', 'Non')])
    etat_sante_conjoint = models.TextField(blank=True, null=True)
    # Mere
    poids_avant_grossesse = models.FloatField(blank=True, null=True)
    taille = models.FloatField(blank=True, null=True)
    ddr = models.DateField(blank=True, null=True)
    ddr_corrige = models.DateField(blank=True, null=True)
    ddg_corrige = models.DateField(blank=True, null=True)
    cycle = models.IntegerField(default=28)
    nb_foetus = models.CharField(max_length=256, default='unique', blank=True, null=True, choices=[('', ''), ('unique', 'Unique'), ('gemellaire', 'Gémellaire'), ('triple', 'Triple')])
    type_grossesse = models.CharField(max_length=256, default='', blank=True, null=True, choices=[('', ''), ('bichoriale_biamniotique', 'bichoriale biamniotique'), ('monochoriale_biamniotique', 'monochoriale biamniotique'), ('monochoriale_monoamniotique', 'monochoriale monoamniotique')])
    type_grossesse_v2 = models.ForeignKey(ListeChoix, related_name='type_grossesse', blank=True, null=True, on_delete=models.SET_NULL)
    conception = models.CharField(max_length=256, default='', blank=True, null=True, choices=[('', ''), ('spontannee', 'Spontannée'), ('iac', 'IAC'), ('fiv', 'FIV')])
    conception_v2 = models.ForeignKey(ListeChoix, related_name='conception', blank=True, null=True, on_delete=models.SET_NULL)

    # Echo 1er Trimestre
    date_echo = models.DateField(blank=True, null=True)
    lcc_1 = models.FloatField(blank=True, null=True)
    lcc_2 = models.FloatField(blank=True, null=True)
    lcc_3 = models.FloatField(blank=True, null=True)
    cn_1 = models.FloatField(blank=True, null=True)
    cn_2 = models.FloatField(blank=True, null=True)
    cn_3 = models.FloatField(blank=True, null=True)
    score_herman_1 = models.CharField(max_length=256, default='', null=True, blank=True,
                                      choices=[('', ''), ('cn_non_connue', 'CN non connue'),
                                               ('cn_non_mesuree', 'CN non mesurée'),
                                               ('cn_non_significative', 'CN non significative pour cette LCC'),
                                               ('score_9', 'Score de Herman 9'), ('score_4', 'Score de Herman < 4')])
    score_herman_1_v2 = models.ForeignKey(ListeChoix, related_name='score_herman_1', blank=True, null=True, on_delete=models.SET_NULL)
    score_herman_2 = models.CharField(max_length=256, default='', null=True, blank=True,
                                      choices=[('', ''), ('cn_non_connue', 'CN non connue'),
                                               ('cn_non_mesuree', 'CN non mesurée'),
                                               ('cn_non_significative', 'CN non significative pour cette LCC'),
                                               ('score_9', 'Score de Herman 9'), ('score_4', 'Score de Herman < 4')])
    score_herman_2_v2 = models.ForeignKey(ListeChoix, related_name='score_herman_2', blank=True, null=True, on_delete=models.SET_NULL)
    score_herman_3 = models.CharField(max_length=256, default='', null=True, blank=True,
                                      choices=[('', ''), ('cn_non_connue', 'CN non connue'),
                                               ('cn_non_mesuree', 'CN non mesurée'),
                                               ('cn_non_significative', 'CN non significative pour cette LCC'),
                                               ('score_9', 'Score de Herman 9'), ('score_4', 'Score de Herman < 4')])
    score_herman_3_v2 = models.ForeignKey(ListeChoix, related_name='score_herman_3', blank=True, null=True, on_delete=models.SET_NULL)
    #msmoyen = models.ForeignKey(ListeChoix, related_name='msmoyen', blank=True, null=True, on_delete=models.SET_NULL)
    test_t21_fait = models.BooleanField(default=False)
    risque = models.FloatField(blank=True, null=True)
    risque_t21_age = models.FloatField(blank=True, null=True)
    risque_t21_bio = models.FloatField(blank=True, null=True)
    risque_t18_13 = models.FloatField(blank=True, null=True)
    msres_1_type = models.CharField(max_length=256, default='', blank=True, null=True)
    msres_1_type_v2 = models.ForeignKey(ListeChoix, related_name='msres_1_type', blank=True, null=True, on_delete=models.SET_NULL)
    msres_1_val = models.FloatField(blank=True, null=True)
    msres_1_mom = models.FloatField(blank=True, null=True)
    msres_2_type = models.CharField(max_length=256, default='', blank=True, null=True)
    msres_2_type_v2 = models.ForeignKey(ListeChoix, related_name='msres_2_type', blank=True, null=True, on_delete=models.SET_NULL)
    msres_2_val = models.FloatField(blank=True, null=True)
    msres_2_mom = models.FloatField(blank=True, null=True)

    screening_premier_trimestre = models.CharField(max_length=128, blank=True, null=True)
    screening_deuxieme_trimestre = models.CharField(max_length=128, blank=True, null=True)
    caryotype_type = models.ForeignKey(ListeChoix, related_name='caryotype', blank=True, null=True, on_delete=models.SET_NULL)
    caryotype_val = models.CharField(max_length=128, blank=True, null=True)
    dpni = models.FloatField(blank=True, null=True)
    dpni_comment = models.CharField(max_length=256, blank=True, null=True)
    diabete = models.CharField(max_length=256, default='',
                               blank=True, null=True, choices=[
                                        ('', ''),
                                        ('diabete_gest_regime', 'Diabète gestationnel sous régime seul'),
                                        ('diabete_gest_insul', 'Diabète gestationnel sous insuline'),
                                        ('hgpo', 'HGPO Normale'),
                                        ('diabete_1', 'Diabète type 1'),
                                        ('diabete_2', 'Diabète type 2'),
                                        ])
    diabete_v2 = models.ForeignKey(ListeChoix, related_name='diabete', blank=True, null=True, on_delete=models.SET_NULL)
    # Recommendations
    tabac = models.BooleanField(blank=True, null=True)
    listeria = models.BooleanField(blank=True, null=True)
    toxoplasmose = models.BooleanField(blank=True, null=True)
    toxoplasmose_v2 = models.CharField(max_length=256, default='', blank=True, null=True, choices=[('', 'Non défini'), ('0', 'Non immunisée'), ('1', 'Immunisée')])
    cmv = models.BooleanField(blank=True, null=True)
    alcool = models.BooleanField(blank=True, null=True)
    # Projet d'accouchement
    epp = models.BooleanField(blank=True, null=True)
    ppo = models.BooleanField(blank=True, null=True)
    adp = models.BooleanField(blank=True, null=True)
    allaitement_maternel = models.BooleanField(blank=True, null=True)
    allaitement_artificiel = models.BooleanField(blank=True, null=True)
    aspegic = models.BooleanField(blank=True, null=True)
    # Infos
    infos_complemenatires = models.TextField(blank=True, null=True)
    lieu_accouchement_principal = models.CharField(max_length=1, blank=True,
                                                   choices=[('H', 'Hôpital'),('C', 'Clinique'), ('A', 'Autre')])
    lieu_accouchement = models.ForeignKey(Etablissement, blank=True, null=True, on_delete=models.SET_NULL)
    lieu_accouchement_libre = models.CharField(max_length=512, blank=True, null=True)

    notes = models.TextField(blank=True, null=True)

    def get_ddr(self):
        if self.ddr_corrige:
            return self.ddr_corrige
        else:
            return self.ddr

    def get_ddg(self):
        if self.ddg_corrige:
            return self.ddg_corrige
        else:
            if self.ddr:
                return self.ddr + datetime.timedelta(self.cycle - 14)
            else:
                return ""

    @property
    def terme_disp(self):
        ddr = self.get_ddr()
        if ddr is not None:
            t = datetime.date.today() - ddr # pour ajouter + datetime.timedelta(duree_gros)
            res = "{} SA".format(math.floor(t.days / 7))
            d = t.days % 7
            if d > 0:
                res = res + f" {d} J"
            return res
        return 0

    def date_echo_morpho(self):
        ddr = self.get_ddr()
        if ddr is not None:
            t1 = ddr + datetime.timedelta(weeks=22)
            t2 = ddr + datetime.timedelta(weeks=24)
            return f'{t1.strftime("%d/%m/%Y")} et {t2.strftime("%d/%m/%Y")}'
        return ""

    @property
    def date_accouch_disp(self):
        duree_gros = self.patient.compte.parametrescompte.duree_grossesse
        ddr = self.get_ddr()
        if ddr is not None:
            accouch = ddr + datetime.timedelta(duree_gros)
            return accouch.strftime("%d/%m/%Y")
        return ""


class AntecedentObstetrique(Antecedent):
    grossesse_patient = models.ForeignKey(Grossesse, on_delete=models.CASCADE, blank=True, null=True)
    grossesse = models.ManyToManyField(ListeChoix, related_name='grossesse', blank=True)
    issue_grossesse = models.ForeignKey(ListeChoix, related_name='issue_grossesse', blank=True, null=True, on_delete=models.SET_NULL)
    mise_en_travail = models.ForeignKey(ListeChoix, related_name='mise_en_travail', blank=True, null=True, on_delete=models.SET_NULL)
    analgesie = models.ForeignKey(ListeChoix, related_name='analgesie', blank=True, null=True, on_delete=models.SET_NULL)
    indications = models.ForeignKey(ListeChoix, related_name='indications', blank=True, null=True, on_delete=models.SET_NULL)
    nb_foetus = models.IntegerField(default=1, blank=True, choices=[(1, 1), (2, 2), (3, 3)])
    date_accouchement = models.DateField(blank=True, null=True)

    # Foetus 1
    terme_1 = models.CharField(max_length=256, blank=True, null=True)
    sexe_1 = models.CharField(max_length=1, blank=True, choices=[('F', 'Féminin'), ('M', 'Masculin'), ('I', 'Inconnu')])
    prenom_1 = models.CharField(max_length=256, blank=True, null=True)
    poids_naissance_1 = models.FloatField(blank=True, null=True)
    etat_sante_1 = models.ForeignKey(ListeChoix, related_name='etat_sante_1', blank=True, null=True, on_delete=models.SET_NULL)
    allaitement_1 = models.BooleanField(blank=True, null=True)
    t21_1 = models.CharField(max_length=256, blank=True, null=True)

    # Foetus 2
    terme_2 = models.CharField(max_length=256, blank=True, null=True)
    sexe_2 = models.CharField(max_length=1, blank=True, choices=[('F', 'Féminin'), ('M', 'Masculin'), ('I', 'Inconnu')])
    prenom_2 = models.CharField(max_length=256, blank=True, null=True)
    poids_naissance_2 = models.FloatField(blank=True, null=True)
    etat_sante_2 = models.ForeignKey(ListeChoix, related_name='etat_sante_2', blank=True, null=True, on_delete=models.SET_NULL)
    allaitement_2 = models.BooleanField(blank=True, null=True)
    t21_2 = models.CharField(max_length=256, blank=True, null=True)

    # Foetus 3
    terme_3 = models.CharField(max_length=256, blank=True, null=True)
    sexe_3 = models.CharField(max_length=1, blank=True, choices=[('F', 'Féminin'), ('M', 'Masculin'), ('I', 'Inconnu')])
    prenom_3 = models.CharField(max_length=256, blank=True, null=True)
    poids_naissance_3 = models.FloatField(blank=True, null=True)
    etat_sante_3 = models.ForeignKey(ListeChoix, related_name='etat_sante_3', blank=True, null=True, on_delete=models.SET_NULL)
    allaitement_3 = models.BooleanField(blank=True, null=True)
    t21_3 = models.CharField(max_length=256, blank=True, null=True)

    perinee = models.ForeignKey(ListeChoix, related_name='perinee', blank=True, null=True, on_delete=models.SET_NULL)
    suite_couche_type = models.ForeignKey(ListeChoix, related_name='suite_couche_type', blank=True, null=True, on_delete=models.SET_NULL)
    suite_couche_detail = models.ForeignKey(ListeChoix, related_name='suite_couche_detail', blank=True, null=True, on_delete=models.SET_NULL)
    atcd_surligner = models.TextField(blank=True, null=True)
    evacuation_grossesse = models.ForeignKey(ListeChoix, related_name='evacuation_grossesse', blank=True, null=True, on_delete=models.SET_NULL)
    lieu_accouchement_principal = models.CharField(max_length=1, blank=True, choices=[('H', 'Hôpital'),('C', 'Clinique'), ('A', 'Autre')])
    lieu_accouchement = models.ForeignKey(Etablissement, blank=True, null=True, on_delete=models.SET_NULL)
    lieu_accouchement_libre = models.CharField(max_length=512, blank=True, null=True)

    honoraires = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        return 'Antécédent {}'.format(self.pk)

    @property
    def grossesse_disp(self):
        return ", ".join(g.valeur for g in self.grossesse.all())

    @property
    def lieu_accouchement_disp(self):
        if self.lieu_accouchement_principal in ['H', 'C']:
            if self.lieu_accouchement:
                return self.lieu_accouchement.nom
        else:
            if self.lieu_accouchement_libre:
                return self.lieu_accouchement_libre
        return ''

    @property
    def resume_foetus(self):
        out = ""
        if self.prenom_1:
            out += self.prenom_1
        if self.sexe_1:
            out += f"({self.sexe_1})"
        if self.poids_naissance_1:
            out += f" - {self.poids_naissance_1} g"

        out += "<br>"
        if self.prenom_2:
            out += self.prenom_2
        if self.sexe_2:
            out += f" ({self.sexe_2})"
        if self.poids_naissance_2:
            out += f" - {self.poids_naissance_2} g"

        out += "<br>"
        if self.prenom_3:
            out += self.prenom_3
        if self.sexe_3:
            out += f" ({self.sexe_3})"
        if self.poids_naissance_3:
            out += f" - {self.poids_naissance_3} g"

        return out


class ConsultationEchoPelvienneBase(models.Model):
    titre_echo_pelvienne = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_titre_echo_pelvienne', blank=True, null=True, on_delete=models.SET_NULL)
    # Uterus
    position_uterus = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_position_uterus', blank=True, null=True, on_delete=models.SET_NULL)
    lateralisation = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_lateralisation', blank=True, null=True, on_delete=models.SET_NULL)
    longueur = models.FloatField(blank=True, null=True)
    largeur = models.FloatField(blank=True, null=True)
    hauteur = models.FloatField(blank=True, null=True)
    longueur_totale = models.FloatField(blank=True, null=True)
    volume_uterin = models.FloatField(blank=True, null=True)
    volume_uterin_commentaire = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_volume_uterin_commentaire', blank=True, null=True, on_delete=models.SET_NULL)
    asymetrie = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_asymetrie', blank=True, null=True, on_delete=models.SET_NULL)
    paroi_anterieure = models.FloatField(blank=True, null=True)
    paroi_posterieure = models.FloatField(blank=True, null=True)
    mobilite = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_mobilite', blank=True, null=True, on_delete=models.SET_NULL)
    structures = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_structures', blank=True, null=True, on_delete=models.SET_NULL)
    commentaires_myometre = models.TextField(blank=True, null=True)
    cavite = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_cavite', blank=True, null=True, on_delete=models.SET_NULL)
    malformation = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_malformation', blank=True, null=True, on_delete=models.SET_NULL)
    largeur_interostiale = models.FloatField(blank=True, null=True)
    ligne_cavitaire = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_ligne_cavitaire', blank=True, null=True, on_delete=models.SET_NULL)
    hysterometrie = models.FloatField(blank=True, null=True)
    adenomyose = models.ManyToManyField(ListeChoix, related_name='%(app_label)s_%(class)s_adenomyose', blank=True)
    adenomyose_conclusion = models.ManyToManyField(ListeChoix, related_name='%(app_label)s_%(class)s_adenomyose_conclusion', blank=True)
    #######
    type_dispositif_intra_uterin = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_type_dispositif_intra_uterin', blank=True, null=True, on_delete=models.SET_NULL)
    localisation_dispositif_intra_uterin = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_localisation_dispositif_intra_uterin', blank=True, null=True, on_delete=models.SET_NULL)
    anomalies_dispositif_intra_uterin = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_anomalies_dispositif_intra_uterin', blank=True, null=True, on_delete=models.SET_NULL)
    dispositif_intra_tubaire = models.BooleanField(blank=True, null=True)
    endometre_visualisation = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_endometre_visualisation', blank=True, null=True, on_delete=models.SET_NULL)
    endometre_echogenicite = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_endometre_echogenicite', blank=True, null=True, on_delete=models.SET_NULL)
    endometre_epaisseur = models.FloatField(blank=True, null=True)
    col_longueur = models.FloatField(blank=True, null=True)
    col_aspect = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_col_aspect', blank=True, null=True, on_delete=models.SET_NULL)
    col_vascularisation = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_col_vascularisation', blank=True, null=True, on_delete=models.SET_NULL)
    commentaire_col_endometre = models.TextField(blank=True, null=True)
    # Ovaire gauche
    ovaire_gauche_visibilite = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_ovaire_gauche_visibilite', blank=True, null=True, on_delete=models.SET_NULL)
    ovaire_gauche_aspect = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_ovaire_gauche_aspect', blank=True, null=True, on_delete=models.SET_NULL)
    ovaire_gauche_longueur = models.FloatField(blank=True, null=True)
    ovaire_gauche_largeur = models.FloatField(blank=True, null=True)
    ovaire_gauche_hauteur = models.FloatField(blank=True, null=True)
    ovaire_gauche_volume = models.FloatField(blank=True, null=True)
    ovaire_gauche_mobilite = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_ovaire_gauche_mobilite', blank=True, null=True, on_delete=models.SET_NULL)
    ovaire_gauche_accessibilite = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_ovaire_gauche_accessibilite', blank=True, null=True, on_delete=models.SET_NULL)
    ovaire_gauche_follicules = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_ovaire_gauche_follicules', blank=True, null=True, on_delete=models.SET_NULL)
    ovaire_gauche_follicules_list = models.TextField(blank=True, null=True)
    ovaire_gauche_commentaire = models.TextField(blank=True, null=True)
    # Ovaire gauche
    ovaire_droit_visibilite = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_ovaire_droit_visibilite', blank=True, null=True, on_delete=models.SET_NULL)
    ovaire_droit_aspect = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_ovaire_droit_aspect', blank=True, null=True, on_delete=models.SET_NULL)
    ovaire_droit_longueur = models.FloatField(blank=True, null=True)
    ovaire_droit_largeur = models.FloatField(blank=True, null=True)
    ovaire_droit_hauteur = models.FloatField(blank=True, null=True)
    ovaire_droit_volume = models.FloatField(blank=True, null=True)
    ovaire_droit_mobilite = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_ovaire_droit_mobilite', blank=True, null=True, on_delete=models.SET_NULL)
    ovaire_droit_accessibilite = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_ovaire_droit_accessibilite', blank=True, null=True, on_delete=models.SET_NULL)
    ovaire_droit_follicules = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_ovaire_droit_follicules', blank=True, null=True, on_delete=models.SET_NULL)
    ovaire_droit_follicules_list = models.TextField(blank=True, null=True)
    ovaire_droit_commentaire = models.TextField(blank=True, null=True)

    cul_de_sac_latero = models.ForeignKey(ListeChoix, related_name='%(app_label)s_%(class)s_cul_de_sac_latero', blank=True, null=True, on_delete=models.SET_NULL)

    conclusion_echo = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True


class ConsultationGynecologique(Consultation, InformationsConjoint, ConsultationEchoPelvienneBase):
    motif_consultation = models.ForeignKey(ListeChoix, related_name='motif_consultation', blank=True, null=True,
                                           on_delete=models.SET_NULL)
    motif_autre = models.CharField(max_length=512, blank=True, null=True)

    # Interrogatoire
    age_menarche = models.IntegerField(blank=True, null=True)
    cycles = models.ForeignKey(ListeChoix, related_name='cycles', blank=True, null=True, on_delete=models.SET_NULL)

    # Menstruation
    duree = models.IntegerField(blank=True, null=True)
    abondance = models.ForeignKey(ListeChoix, related_name='abondance', blank=True, null=True,
                                  on_delete=models.SET_NULL)
    douleur = models.ForeignKey(ListeChoix, related_name='douleur', blank=True, null=True, on_delete=models.SET_NULL)
    syndrome_premenstruel = models.ForeignKey(ListeChoix, related_name='syndrome_premenstruel', blank=True, null=True,
                                              on_delete=models.SET_NULL)
    ddr = models.DateField(blank=True, null=True)

    # Rapports sexuels
    presence_rapports_sexuels = models.ForeignKey(ListeChoix, related_name='presence_rapports_sexuels', blank=True, null=True,
                                   on_delete=models.SET_NULL)
    partenaire = models.ForeignKey(ListeChoix, related_name='partenaire', blank=True, null=True,
                                   on_delete=models.SET_NULL)
    age_premier_rapport = models.IntegerField(blank=True, null=True)

    # Contraception
    mode_contraception = models.ForeignKey(ListeChoix, related_name='mode_contraception', blank=True, null=True,
                                           on_delete=models.SET_NULL)
    commentaire_contraception = models.CharField(max_length=512, blank=True, null=True)
    observance = models.ForeignKey(ListeChoix, related_name='observance', blank=True, null=True,
                                   on_delete=models.SET_NULL)
    satisfaction = models.ForeignKey(ListeChoix, related_name='satisfaction', blank=True, null=True,
                                     on_delete=models.SET_NULL)

    # Ménopause
    ths = models.BooleanField(blank=True, null=True)
    bouffees_chaleur = models.BooleanField(blank=True, null=True)
    incontinence = models.BooleanField(blank=True, null=True)
    sensation_pesanteur = models.BooleanField(blank=True, null=True)
    dyspareunies = models.BooleanField(blank=True, null=True)
    commentaire = models.TextField(blank=True, null=True)

    # Endométriose
    endometriose = models.BooleanField(blank=True, null=True)

    # Examen clinique
    seins = models.ForeignKey(ListeChoix, related_name='seins', blank=True, null=True, on_delete=models.SET_NULL)
    examen_sous_speculum = models.ForeignKey(ListeChoix, related_name='examen_sous_speculum', blank=True, null=True,
                                             on_delete=models.SET_NULL)
    leuco = models.ManyToManyField(ListeChoix, related_name='leuco', blank=True)
    tv = models.CharField(max_length=512, blank=True, null=True)
    poids = models.FloatField(blank=True, null=True)
    ta = models.CharField(max_length=256, blank=True, null=True)
    temperature = models.FloatField(blank=True, null=True)
    alb = models.CharField(max_length=256, blank=True, null=True)
    gly = models.CharField(max_length=256, blank=True, null=True)
    commentaires_cliniques = models.TextField(blank=True, null=True)

    # Examen traitements
    examens = models.TextField(blank=True, null=True)
    traitements = models.TextField(blank=True, null=True)

    # Observations
    observations = models.TextField(blank=True, null=True)

    # Autres
    effets_indesirables = models.ForeignKey(ListeChoix, related_name='effets_indesirables', blank=True, null=True,
                                            on_delete=models.SET_NULL)
    # Supprimé
    signe_clinique = models.BooleanField(blank=True, null=True)
    prochaine_consultation_date = models.DateField(blank=True, null=True)
    prochaine_consultation_approx = models.CharField(max_length=128, blank=True, null=True)


class ConsultationColposcopie(Consultation):
    indications = models.ForeignKey(ListeChoix, related_name='indications_colposcopie', blank=True, null=True,
                                    on_delete=models.SET_NULL)
    test_hpv = models.ForeignKey(ListeChoix, related_name='test_hpv', blank=True, null=True, on_delete=models.SET_NULL)
    typage = models.CharField(max_length=512, blank=True, null=True)
    commentaires_1 = models.TextField(blank=True, null=True)
    examen_sans_preparation = models.ForeignKey(ListeChoix, related_name='examen_sans_preparation', blank=True,
                                                null=True, on_delete=models.SET_NULL)
    commentaires_2 = models.TextField(blank=True, null=True)
    acide_acetique = models.ForeignKey(ListeChoix, related_name='acide_acetique', blank=True, null=True,
                                       on_delete=models.SET_NULL)
    tag = models.ForeignKey(ListeChoix, related_name='tag', blank=True, null=True, on_delete=models.SET_NULL)
    localisation = models.ForeignKey(ListeChoix, related_name='localisation', blank=True, null=True,
                                     on_delete=models.SET_NULL)
    lugol = models.ForeignKey(ListeChoix, related_name='lugol', blank=True, null=True, on_delete=models.SET_NULL)
    commentaires_3 = models.TextField(blank=True, null=True)
    biopsie = models.BooleanField(blank=True, null=True)
    commentaires_4 = models.TextField(blank=True, null=True)


class ConsultationEchoPelvienne(Consultation, ConsultationEchoPelvienneBase):
    pass


class Myome(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    situation = models.ForeignKey(ListeChoix, related_name='situation', blank=True, null=True, on_delete=models.SET_NULL)
    type_figo = models.ForeignKey(ListeChoix, related_name='type_figo', blank=True, null=True, on_delete=models.SET_NULL)
    situation_coupe_longitudinale = models.ForeignKey(ListeChoix, related_name='situation_coupe_longitudinale', blank=True, null=True, on_delete=models.SET_NULL)
    situation_coupe_transversale = models.ForeignKey(ListeChoix, related_name='situation_coupe_transversale', blank=True, null=True, on_delete=models.SET_NULL)
    contours = models.ForeignKey(ListeChoix, related_name='countours', blank=True, null=True, on_delete=models.SET_NULL)
    structure = models.ForeignKey(ListeChoix, related_name='structure', blank=True, null=True, on_delete=models.SET_NULL)
    calcifications = models.ForeignKey(ListeChoix, related_name='calcifications', blank=True, null=True, on_delete=models.SET_NULL)
    vascularisation = models.ForeignKey(ListeChoix, related_name='vascularisation', blank=True, null=True, on_delete=models.SET_NULL)
    longueur = models.FloatField(blank=True, null=True)
    largeur = models.FloatField(blank=True, null=True)
    hauteur = models.FloatField(blank=True, null=True)
    diametre_moyen = models.FloatField(blank=True, null=True)
    volume = models.FloatField(blank=True, null=True)
    mure_posterieur = models.FloatField(blank=True, null=True)


class ConsultationObstetrique(Consultation):
    grossesse = models.ForeignKey(Grossesse, on_delete=models.CASCADE)
    rdv_suivant_apres = models.DateField(blank=True, null=True)
    rdv_suivant_avant = models.DateField(blank=True, null=True)
    ip_droit = models.FloatField(blank=True, null=True)
    ir_droit = models.FloatField(blank=True, null=True)
    ip_gauche = models.FloatField(blank=True, null=True)
    ir_gauche = models.FloatField(blank=True, null=True)
    notch_droit = models.ForeignKey(ListeChoix, related_name='notch_droit', blank=True, null=True, on_delete=models.SET_NULL)
    notch_gauche = models.ForeignKey(ListeChoix, related_name='notch_gauche', blank=True, null=True, on_delete=models.SET_NULL)
    col_long = models.FloatField(blank=True, null=True)
    col_entonnoir = models.ForeignKey(ListeChoix, related_name='col_entonnoir', blank=True, null=True, on_delete=models.SET_NULL)
    col_orifice_interne = models.FloatField(blank=True, null=True)

    echo_morpho = models.TextField(blank=True, null=True)
    echo_t3 = models.TextField(blank=True, null=True)

    # Examen clinique
    seins = models.ForeignKey(ListeChoix, related_name='obs_seins', blank=True, null=True, on_delete=models.SET_NULL)
    examen_sous_speculum = models.ForeignKey(ListeChoix, related_name='obs_examen_sous_speculum', blank=True, null=True,
                                             on_delete=models.SET_NULL)
    leuco = models.ManyToManyField(ListeChoix, related_name='obs_leuco', blank=True)
    tv = models.CharField(max_length=512, blank=True, null=True)
    poids = models.FloatField(blank=True, null=True)
    ta = models.CharField(max_length=256, blank=True, null=True)
    temperature = models.FloatField(blank=True, null=True)
    alb = models.CharField(max_length=256, blank=True, null=True)
    gly = models.CharField(max_length=256, blank=True, null=True)
    commentaires_cliniques = models.TextField(blank=True, null=True)

    pelvis_maternel = models.ForeignKey(ListeChoix, related_name='pelvis_maternel', blank=True, null=True, on_delete=models.SET_NULL)
    lmc = models.ForeignKey(ListeChoix, related_name='lmc', blank=True, null=True, on_delete=models.SET_NULL)

    @property
    def terme(self):
        if self.grossesse:
            ddr = self.grossesse.get_ddr()
            if ddr:
                t = self.date.date() - ddr
                res = "{} SA".format(math.floor(t.days / 7))
                d = t.days % 7
                if d > 0:
                    res = res + f" {d} J"
                return res
        return ""

    def terme_sa(self):
        if self.grossesse:
            ddr = self.grossesse.get_ddr()
            if ddr:
                t = self.date.date() - ddr
                res = math.floor(t.days / 7)
                return res
        return ""


class DonneesFoetus(models.Model):
    consultation = models.ForeignKey(ConsultationObstetrique, on_delete=models.CASCADE)
    presentation = models.ForeignKey(ListeChoix, related_name='presentation', blank=True, null=True, on_delete=models.SET_NULL)
    activite_cardiaque = models.ForeignKey(ListeChoix, related_name='activite_cardiaque_foetus', blank=True, null=True, on_delete=models.SET_NULL)
    mobilite = models.ForeignKey(ListeChoix, related_name='f_mobilite', blank=True, null=True, on_delete=models.SET_NULL)
    poids = models.FloatField(blank=True, null=True)
    lcc = models.FloatField(blank=True, null=True)
    dat = models.FloatField(blank=True, null=True)
    cn = models.FloatField(blank=True, null=True)
    fc = models.FloatField(blank=True, null=True)
    bip = models.FloatField(blank=True, null=True)
    pc = models.FloatField(blank=True, null=True)
    pa = models.FloatField(blank=True, null=True)
    femur = models.FloatField(blank=True, null=True)
    bassinet_droit = models.FloatField(blank=True, null=True)
    bassinet_gauche = models.FloatField(blank=True, null=True)
    cc = models.FloatField(blank=True, null=True)
    cervelet = models.FloatField(blank=True, null=True)
    cubitus = models.FloatField(blank=True, null=True)
    dio = models.FloatField(blank=True, null=True)
    epn = models.FloatField(blank=True, null=True)
    humerus = models.FloatField(blank=True, null=True)
    opn = models.FloatField(blank=True, null=True)
    opn_presence = models.CharField(max_length=1, blank=True, null=True, choices=[('0', 'Absent'), ('1', 'Présent')])
    oreille = models.FloatField(blank=True, null=True)
    perone = models.FloatField(blank=True, null=True)
    pied = models.FloatField(blank=True, null=True)
    placenta = models.FloatField(blank=True, null=True)
    radius = models.FloatField(blank=True, null=True)
    rein_droite = models.FloatField(blank=True, null=True)
    rein_gauche = models.FloatField(blank=True, null=True)
    thyroide = models.FloatField(blank=True, null=True)
    tibia = models.FloatField(blank=True, null=True)
    vl = models.FloatField(blank=True, null=True)
    poids_estime = models.FloatField(blank=True, null=True)
    doppler_cordon_ip = models.FloatField(blank=True, null=True)
    doppler_cordon_ir = models.FloatField(blank=True, null=True)
    doppler_cordon_diastole = models.ForeignKey(ListeChoix, related_name='doppler_cordon_diastole', blank=True, null=True, on_delete=models.SET_NULL)
    doppler_acm_ip = models.FloatField(blank=True, null=True)
    doppler_acm_ir = models.FloatField(blank=True, null=True)
    doppler_acm_vitesse = models.FloatField(blank=True, null=True)
    doppler_acm_mom = models.FloatField(blank=True, null=True)
    doppler_dv_ip = models.FloatField(blank=True, null=True)
    doppler_dv_ir = models.FloatField(blank=True, null=True)
    doppler_dv_onde = models.ForeignKey(ListeChoix, related_name='doppler_dv_onde', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_crane = models.ForeignKey(ListeChoix, related_name='morpho_crane', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_struct = models.ForeignKey(ListeChoix, related_name='morpho_struct', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_face = models.ForeignKey(ListeChoix, related_name='morpho_face', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_thorax = models.ForeignKey(ListeChoix, related_name='morpho_thorax', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_coeur = models.ForeignKey(ListeChoix, related_name='morpho_coeur', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_pole_cepha = models.ForeignKey(ListeChoix, related_name='morpho_pole_cepha', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_abdo = models.ForeignKey(ListeChoix, related_name='morpho_abdo', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_digest = models.ForeignKey(ListeChoix, related_name='morpho_digest', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_urine = models.ForeignKey(ListeChoix, related_name='morpho_urine', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_rachis = models.ForeignKey(ListeChoix, related_name='morpho_rachis', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_membres = models.ForeignKey(ListeChoix, related_name='morpho_membre', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_oge = models.ForeignKey(ListeChoix, related_name='morpho_oge', blank=True, null=True, on_delete=models.SET_NULL)
    annexe_liquide_amnio = models.ForeignKey(ListeChoix, related_name='annexe_liquide_amnio', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_liquide_amnio = models.ForeignKey(ListeChoix, related_name='morpho_liquide_amnio', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_trophoblaste_localisation = models.ForeignKey(ListeChoix, related_name='morpho_trophoblaste_localisation', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_trophoblaste_aspect = models.ForeignKey(ListeChoix, related_name='morpho_trophoblaste_aspect', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_decol = models.ForeignKey(ListeChoix, related_name='morpho_decol', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_placenta = models.ForeignKey(ListeChoix, related_name='morpho_placenta', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_cordon = models.ForeignKey(ListeChoix, related_name='morpho_cordon', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_cou = models.ForeignKey(ListeChoix, related_name='morpho_cou', blank=True, null=True, on_delete=models.SET_NULL)
    commentaires = models.TextField(blank=True, null=True)


class ConsultationEcho11SA(ConsultationObstetrique):
    sac_gestationnel_localisation = models.ForeignKey(ListeChoix, related_name='sac_gestationnel_localisation', blank=True, null=True, on_delete=models.SET_NULL)
    sac_gestationnel_tonicite = models.ForeignKey(ListeChoix, related_name='sac_gestationnel_tonicite', blank=True, null=True, on_delete=models.SET_NULL)
    sac_gestationnel_trophoblaste = models.ForeignKey(ListeChoix, related_name='sac_gestationnel_trophoblaste', blank=True, null=True, on_delete=models.SET_NULL)
    sac_gestationnel_longueur = models.FloatField(blank=True, null=True)
    sac_gestationnel_largeur = models.FloatField(blank=True, null=True)
    sac_gestationnel_hauteur = models.FloatField(blank=True, null=True)
    sac_gestationnel_diametre = models.FloatField(blank=True, null=True)
    sac_gestationnel_decollement = models.ForeignKey(ListeChoix, related_name='sac_gestationnel_decollement', blank=True, null=True, on_delete=models.SET_NULL)
    embryon_visible = models.BooleanField(default=True)
    morpho_extremite_cephalique = models.ForeignKey(ListeChoix, related_name='morpho_extremite_cephalique', blank=True, null=True, on_delete=models.SET_NULL)
    morpho_membres = models.ForeignKey(ListeChoix, related_name='morpho_membres', blank=True, null=True, on_delete=models.SET_NULL)
    lcc = models.FloatField(blank=True, null=True)
    bip = models.FloatField(blank=True, null=True)
    activite_cardiaque = models.ForeignKey(ListeChoix, related_name='activite_cardiaque', blank=True, null=True, on_delete=models.SET_NULL)
    commentaires = models.TextField(blank=True, null=True)


class ConsultationEchoPremierTrimestre(ConsultationObstetrique):
    pass


class ConsultationEchoDeuxiemeTrimestre(ConsultationObstetrique):
    pass


class ConsultationEchoTroisiemeTrimestre(ConsultationObstetrique):
    pass


class ConsultationEchoCroissance(ConsultationObstetrique):
    pass


class ConsultationEchoCol(ConsultationObstetrique):
    pass


class ConsultationEchoCardiofoetale(ConsultationObstetrique):
    pass


class ConsultationGrossesse(ConsultationObstetrique):
    pass


#################################################################################################

class TentativesHistoriquesPMA(BaseModel):
    TYPE_ACTE = [('IAC', 'IAC'), ('FIV', 'FIV'), ('DPI', 'DPI')]
    RESULT_ACTE = [('Succès', 'Succès'), ('Echec', 'Echec')]
    interrogatoire = models.ForeignKey('InterrogatoirePMA', related_name='tentatives', on_delete=models.CASCADE)
    date = models.DateField(blank=True, null=True)
    acte = models.CharField(max_length=32, blank=True, null=True, choices=TYPE_ACTE)
    resultat = models.CharField(max_length=32, blank=True, null=True, choices=RESULT_ACTE)
    remarques = models.CharField(max_length=512, blank=True, null=True)


#class ExamenComplementairePMA:
#    nom = models.CharField(max_length=128, blank=True, null=True)
#    valeur = models.CharField(max_length=512, blank=True, null=True)
#    interrogatoire = models.ForeignKey('InterrogatoirePMA', related_name='examens_complentaires', on_delete=models.CASCADE)


class BilanEndocrinienPMA(BaseModel):
    date = models.DateField(blank=True, null=True)
    fsh = models.CharField(max_length=512, blank=True, null=True)
    lh = models.CharField(max_length=512, blank=True, null=True)
    prolactine = models.CharField(max_length=512, blank=True, null=True)
    e2 = models.CharField(max_length=512, blank=True, null=True)
    inhibine = models.CharField(max_length=512, blank=True, null=True)
    amh = models.CharField(max_length=512, blank=True, null=True)
    testosterone = models.CharField(max_length=512, blank=True, null=True)
    spermoculture = models.CharField(max_length=512, blank=True, null=True)
    biochoimie = models.CharField(max_length=512, blank=True, null=True)
    cytogen = models.CharField(max_length=512, blank=True, null=True)
    autres = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        abstract = True


class BilanEndocrinienPMAFeminin(BilanEndocrinienPMA):
    interrogatoire = models.ForeignKey('InterrogatoirePMA', related_name='bilans_endocriniens_feminin', on_delete=models.CASCADE)


class BilanEndocrinienPMAMasculin(BilanEndocrinienPMA):
    interrogatoire = models.ForeignKey('InterrogatoirePMA', related_name='bilans_endocriniens_masculin', on_delete=models.CASCADE)


class SpermogrammePMA(BaseModel):
    interrogatoire = models.ForeignKey('InterrogatoirePMA', related_name='spermogrammes', on_delete=models.CASCADE)
    date = models.DateField(blank=True, null=True)
    vol = models.CharField(max_length=512, blank=True, null=True)
    num = models.CharField(max_length=512, blank=True, null=True)
    mob = models.CharField(max_length=512, blank=True, null=True)
    vit = models.CharField(max_length=512, blank=True, null=True)
    ft = models.CharField(max_length=512, blank=True, null=True)
    leuco = models.CharField(max_length=512, blank=True, null=True)
    agg = models.CharField(max_length=512, blank=True, null=True)
    tms = models.CharField(max_length=512, blank=True, null=True)


class InterrogatoirePMA(InformationsConjoint):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    praticien = models.ForeignKey(Medecin, on_delete=models.SET_NULL, blank=True, null=True)
    text = models.TextField(blank=True)
    date = models.DateTimeField(default=datetime.date.today)
    TYPE_INFERTILITE = [('Primaire', 'Primaire'), ('Secondaire', 'Secondaire')]
    type_infertilite = models.CharField(max_length=32, default='Primaire', choices=TYPE_INFERTILITE)
    duree_infertilite = models.SmallIntegerField(blank=True, null=True)
    duree_infertilite_mois = models.SmallIntegerField(blank=True, null=True)
    duree_desir_gross = models.SmallIntegerField(blank=True, null=True)
    # Conceptions naturelles
    gross_nb = models.SmallIntegerField(blank=True, null=True)
    gross_dt = models.CharField(max_length=128, blank=True, null=True)
    enfants_nb = models.SmallIntegerField(blank=True, null=True)
    enfants_dt = models.CharField(max_length=128, blank=True, null=True)
    geu_nb = models.SmallIntegerField(blank=True, null=True)
    geu_dt = models.CharField(max_length=128, blank=True, null=True)
    avort_nb = models.SmallIntegerField(blank=True, null=True)
    avort_dt = models.CharField(max_length=128, blank=True, null=True)
    # Technique souhaitée
    TECH_AMP = [('IAC', 'IAC'), ('FIV', 'FIV'), ('DPI', 'DPI'), ('ICSI', 'ICSI'), ('Freeze all', 'Freeze all'),
                ('Préservation de la fertilité', 'Préservation de la fertilité')]
    technique = models.CharField(max_length=32, blank=True, null=True, choices=TECH_AMP)
    # Bilan féminin
    exam_echo = models.TextField(blank=True, null=True)
    exam_hsg = models.TextField(blank=True, null=True)
    exam_hsc = models.TextField(blank=True, null=True)
    exam_coelioscopie = models.TextField(blank=True, null=True)
    exam_tpc = models.TextField(blank=True, null=True)
    # Bilan masculin
    antec_medicaux = models.TextField(blank=True, null=True)
    antec_chirugicaux = models.TextField(blank=True, null=True)
    antec_familiaux = models.TextField(blank=True, null=True)
    antec_tabac = models.TextField(blank=True, null=True)
    antec_alcool = models.TextField(blank=True, null=True)
    sperme_normal = models.BooleanField(default=False)
    # oligo-asthéno-tératospermie
    sperme_oats_o = models.BooleanField(default=False)
    sperme_oats_a = models.BooleanField(default=False)
    sperme_oats_t = models.BooleanField(default=False)
    SPERME_OAT_GRAVITE = [('Modérée', 'Modérée'), ('Sévère', 'Sévère')]
    sperme_oat_gravite = models.CharField(max_length=32, blank=True, null=True, choices=SPERME_OAT_GRAVITE)
    sperme_azoospermie = models.BooleanField(default=False)
    SPERME_AZOO_GRAVITE = [('Obstructive', 'Obstructive'), ('Non obstructive', 'Non obstructive')]
    sperme_azoo_gravite = models.CharField(max_length=32, blank=True, null=True, choices=SPERME_AZOO_GRAVITE)
    sperme_congenalation = models.BooleanField(default=False)
    sperme_congenalation_clinique = models.ForeignKey(Etablissement, on_delete=models.SET_NULL, blank=True, null=True)
    nb_paillettes = models.SmallIntegerField(blank=True, null=True)
    RENDEMENT = [('bon', 'Bon'), ('mauvais', 'Mauvais')]
    rendement = models.CharField(max_length=32, blank=True, null=True, choices=RENDEMENT)
    echo_testiculaire = models.BooleanField(default=False)
    echo_testiculaire_comment = models.TextField(blank=True, null=True)
    bilan_infect = models.BooleanField(default=False)
    bilan_infect_comment = models.TextField(blank=True, null=True)
    conduite = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.patient.nom_complet


class TraitementPMA(CompteModelBase):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    libelle = models.CharField(max_length=512, blank=True, null=True)


class TentativePMA(BaseModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    praticien = models.ForeignKey(Medecin, on_delete=models.SET_NULL, blank=True, null=True)
    text = models.TextField(blank=True)
    rang = models.PositiveSmallIntegerField(blank=True, null=True)
    encours = models.BooleanField(default=True)
    diagnostic = models.CharField(max_length=512, blank=True, null=True)
    REMARQUE_TENTATIVE = [('Echec', 'Echec'), ('Succès', 'Succès')]
    remarques_tentatives = models.CharField(max_length=512, blank=True, null=True)
    pretraitement = models.CharField(max_length=512, blank=True, null=True)
    protocole = models.CharField(max_length=512, blank=True, null=True)
    # Résultat tentative
    reussie = models.BooleanField(default=False)
    commentaires = models.TextField(blank=True, null=True)


class SuiviTraitementPMA(BaseModel):
    tentative = models.ForeignKey(TentativePMA, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    traitments_valeurs = models.ManyToManyField(TraitementPMA, through='TraitementValeurPMA', blank=True)
    oestradiol = models.CharField(max_length=512, blank=True, null=True)
    lh = models.CharField(max_length=512, blank=True, null=True)
    progesterone = models.CharField(max_length=512, blank=True, null=True)
    ovaire_droit = models.CharField(max_length=512, blank=True, null=True)
    ovaire_gauche = models.CharField(max_length=512, blank=True, null=True)
    endometre = models.CharField(max_length=512, blank=True, null=True)


class TraitementValeurPMA(BaseModel):
    valeur = models.CharField(max_length=512, blank=True, null=True)
    traitement = models.ForeignKey(TraitementPMA, on_delete=models.SET_NULL, blank=True, null=True)
    suivi = models.ForeignKey(SuiviTraitementPMA, on_delete=models.CASCADE)
    rang = models.PositiveSmallIntegerField(blank=True, null=True)

    class Meta:
        ordering = ['rang']


##################################################################################################

class Cloture(CompteModelBase):
    date_cloture = models.DateTimeField(default=django.utils.timezone.now)

    @property
    def total(self):
        total = 0
        for r in self.reglement_set.all():
            total += r.somme_payee
        return total

    @property
    def periode(self):
        r = self.reglement_set.order_by('date_creation')
        if len(r) > 0:
            return f"{r.first().date_creation.strftime('%d/%m/%y')} - {r.last().date_creation.strftime('%d/%m/%y')}"


class Reglement(models.Model):
    admission = models.ForeignKey(Admission, related_name='reglements', on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    praticien = models.ForeignKey(Medecin, on_delete=models.SET_NULL, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    mutuelle = models.BooleanField(default=False)
    nom_mutuelle = models.CharField(max_length=128, blank=True, null=True)
    espece_payment = models.FloatField(blank=True, null=True)
    cheque_payment = models.FloatField(blank=True, null=True)
    cb_payment = models.FloatField(blank=True, null=True)
    cheque_number = models.PositiveSmallIntegerField(blank=True, null=True)
    titulaire = models.CharField(max_length=128, blank=True, null=True)
    date_cheque = models.DateField(blank=True, null=True)
    cloture = models.ForeignKey(Cloture, on_delete=models.SET_NULL, blank=True, null=True)
    bordereau = models.ForeignKey(Bordereau, on_delete=models.SET_NULL, blank=True, null=True)
    date_creation = models.DateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return f"{self.date_creation} - {self.patient.nom_complet} - Total {self.total} - Ticket {self.ticket_moderateur} - PEC {self.prise_en_charge}"

    @property
    def somme_payee(self):
        res = 0
        if self.espece_payment:
            res = res + self.espece_payment
        if self.cheque_payment:
            res = res + self.cheque_payment
        if self.cb_payment:
            res = res + self.cb_payment
        return res

    @property
    def total(self):
        t = 0
        for r in self.lignes_reglement.all():
            if r.prix_initial:
                t += r.prix_initial
        return t

    @property
    def ticket_moderateur(self):
        t = 0
        for r in self.lignes_reglement.all():
            t += r.prix_ttc
        return t

    @property
    def prise_en_charge(self):
        return self.total - self.ticket_moderateur

    class Meta:
        ordering = ['-date_creation']


class LigneReglement(models.Model):
    prestation = models.CharField(max_length=128, blank=True, null=True)
    code = models.CharField(max_length=128, blank=True, null=True)
    prix_ttc = models.FloatField(blank=True, null=True)  # Montant ticket modérateur
    prix_initial = models.FloatField(blank=True, null=True)  # Montant total = montant prise en charge + ticket modérateur
    reglement = models.ForeignKey(Reglement, related_name='lignes_reglement', on_delete=models.CASCADE, blank=True,
                                  null=True)

    def __str__(self):
        return self.code


class Facture(models.Model):
    reglement = models.ForeignKey(Reglement, related_name='factures', on_delete=models.CASCADE)

    def __str__(self):
        return "{}, {}".format(self.reglement.patient.prenom, self.reglement.patient.nom)


def repertoire_images_utilisateur(compte_pk, patient_pk, nom_fichier):
    return 'comptes/compte_{0}/patients/{1}/images/{2}'.format(compte_pk, patient_pk, nom_fichier)


def upload_repertoire_images_utilisateur(instance, filename):
    ext = filename.split('.')[-1]
    new_name = f"{random.randint(10000000, 99999999)}.{ext}"
    path = repertoire_images_utilisateur(instance.consultation.patient.compte.pk,
                                         instance.consultation.patient.pk,
                                         new_name)
    print(f'Enregistrement de image dans {path}')
    return path


class ImageConsultation(models.Model):
    IMG_GRAPH = 'G'
    IMG_ECHO = 'E'
    MPPS_STATUS_INPROGRESS = 'IN PROGRESS'
    image = models.ImageField(upload_to=upload_repertoire_images_utilisateur, blank=True, null=True)
    type = models.CharField(max_length=1, choices=[(IMG_GRAPH, 'Graphique'), (IMG_ECHO, 'Echographie')])
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    date = models.DateTimeField()
    impression = models.BooleanField(default=False)


class SRConsultation(BaseModel):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    date = models.DateTimeField()
    data = models.TextField(null=True, blank=True)


##################################################################################################

class AnalyseBiologique(CompteModelBase):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    libelle = models.CharField(max_length=128)
    code = models.CharField(max_length=32)
    type = models.CharField(max_length=32, choices=[('text', 'Texte'), ('number', 'Numérique')])
    unite = models.CharField(max_length=32, default="", null=True, blank=True)
    modele_resultat = models.TextField(default="", null=True, blank=True)
    ordre = models.SmallIntegerField(default=1000)

    class Meta:
        ordering = ['ordre', 'libelle']

    def __str__(self):
        return self.code + ' - ' + self.libelle


class AnalyseOrderedManyToManyField(models.ManyToManyField):
    """This fetches from the join table, then fetches the Analyses in the fixed id order."""
    def value_from_object(self, object):
        print('value_from_object')
        rel = getattr(object, self.attname)
        qry = {'collectionanalysebiologique': object}
        qs = rel.through.objects.filter(**qry).order_by('id')
        aids = qs.values_list('analysebiologique_id', flat=True)
        print('IDS', aids)
        analyses = dict((a.pk, a) for a in AnalyseBiologique.objects.filter(pk__in=aids))
        ret = [analyses[aid] for aid in aids if aid in analyses]
        print(ret)
        return ret


class CollectionAnalyseBiologique(CompteModelBase):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    nom = models.CharField(max_length=128)
    analyses = AnalyseOrderedManyToManyField(AnalyseBiologique)

    class Meta:
        ordering = ['nom']

    def __str__(self):
        return self.nom

    @property
    def analyses_list(self):
        analyses = [a.analysebiologique for a in
                    self.analyses.through.objects.filter(collectionanalysebiologique_id=self.id)
                        .select_related('analysebiologique')
                        .order_by('id')]
        return analyses
        #return self.analyses.order_by('CollectionAnalyseBiologique_analyses__id')


class PrescriptionAnalyseBiologique(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    analyses = models.ManyToManyField(AnalyseBiologique, through='ResultatAnalyseBiologique')
    date_prescription = models.DateTimeField()
    date_resultat = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_prescription', '-id']

    @property
    def resultats_display(self):
        resultats = self.resultatanalysebiologique_set.all()
        if len(resultats) == 0:
            return 'Pas de résultats saisis'
        str = ''
        for res in resultats:
            str = str + f"<strong>{res.analyse.libelle}</strong>:"
            if res.valeur is not None and res.valeur != '':
                if '\n' in res.valeur:
                    val = res.valeur.replace('\n', '<br>')
                    str = str + f"<br>{val}<br><br>"
                else:
                    val = res.valeur
                    str = str + f" {val}<br><br>"
            else:
                str = str + f" - <br><br>"
        return str

    @property
    def date(self):
        if self.date_resultat is not None:
            return self.date_resultat
        else:
            return self.date_prescription

    @property
    def titre(self):
        if self.date_resultat is not None:
            return "Résultat"
        else:
            return "Prescription"


class ResultatAnalyseBiologique(models.Model):
    analyse = models.ForeignKey(AnalyseBiologique, on_delete=models.CASCADE)
    prescription = models.ForeignKey(PrescriptionAnalyseBiologique, on_delete=models.CASCADE)
    date = models.DateTimeField(null=True, blank=True)
    valeur = models.TextField(null=True, blank=True)
    observation = models.TextField(null=True, blank=True)
    valeur_anormale = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']

    @property
    def resultat_display(self):
        str = ''
        if self.valeur is not None and self.valeur != '':
            if '\n' in self.valeur:
                val = self.valeur.replace('\n', '<br>')
                str = str + f"<br>{val}<br><br>"
            else:
                val = self.valeur
                str = str + f" {val}<br><br>"
        return str


##################################################################################################

class Device(CompteModelBase):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    marque = models.CharField(max_length=256)
    modele = models.CharField(max_length=256)
    mise_circulation = models.DateField(null=True, blank=True)
    informations = models.CharField(max_length=512, null=True, blank=True)
    reference = models.CharField(max_length=256, null=True, blank=True)
    ae_title = models.CharField(max_length=256)
    ip = models.CharField(max_length=14)
    port = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.marque} - {self.modele}"


class WorklistItem(models.Model):
    MPPS_STATUS_PENDING = 'PENDING'
    MPPS_STATUS_INPROGRESS = 'IN PROGRESS'
    MPPS_STATUS_COMPLETED = 'COMPLETED'
    MPPS_STATUS_DISCONTINUED = 'DISCONTINUED'
    MPPS_STATUSES = [(MPPS_STATUS_PENDING, 'pending'), (MPPS_STATUS_INPROGRESS, 'inprogress'),
                     (MPPS_STATUS_COMPLETED, 'completed'), (MPPS_STATUS_DISCONTINUED, 'discontinued')]
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, blank=True, null=True)
    study_instance_uid = models.CharField(max_length=256)
    requested_procedure_description = models.CharField(max_length=256, null=True, blank=True)
    requested_procedure_id = models.CharField(max_length=256, null=True, blank=True)
    mpps_status = models.CharField(max_length=128, default=MPPS_STATUS_PENDING, choices=MPPS_STATUSES)

    @property
    def patient_name(self):
        return f'{self.consultation.patient.prenom}^{self.consultation.patient.nom}'

    def __str__(self):
        return f"{self.consultation.date} - {self.study_instance_uid}"


##################################################################################################

class TemplateEdition(CompteModelBase):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    categorie_consultation = models.ForeignKey(CategorieConsultation, related_name='categorie_consultation', on_delete=models.CASCADE)
    motif_consultation = models.ForeignKey(MotifConsultation, related_name='motif_consultation', on_delete=models.SET_NULL,
                                           blank=True, null=True)
    libelle = models.CharField(max_length=256)
    contenu = models.TextField(blank=True)

    def __str__(self):
        return f"{self.libelle} - {self.categorie_consultation.libelle}"

class AlertePatient(BaseModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    text = models.CharField(max_length=512)
    lien = models.CharField(max_length=512)
