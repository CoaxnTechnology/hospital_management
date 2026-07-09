import datetime
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from pydicom.uid import generate_uid
from apps.core.models import *
from echo.settings import common


@receiver(post_save, sender=Compte)
def creer_parametres_compte(sender, instance, **kwargs):
    """
    Fonction qui crée automatiquement les parametres d'un compte dés que celui est créé ou mis à jour.

    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    if not hasattr(instance, 'parametrescompte'):
        params = ParametresCompte(timezone=common.TIME_ZONE, duree_rdv_defaut=10)
        params.compte = instance
        print(instance.parametrescompte)
        params.save()


@receiver(post_save, sender=Consultation)
@receiver(post_save, sender=ConsultationObstetrique)
@receiver(post_save, sender=ConsultationEcho11SA)
@receiver(post_save, sender=ConsultationEchoPremierTrimestre)
@receiver(post_save, sender=ConsultationEchoDeuxiemeTrimestre)
@receiver(post_save, sender=ConsultationEchoTroisiemeTrimestre)
@receiver(post_save, sender=ConsultationEchoPelvienne)
@receiver(post_save, sender=ConsultationGynecologique)
@receiver(post_save, sender=ConsultationEchoCroissance)
def creer_worklist_item(sender, instance, **kwargs):
    """
    Fonction qui crée automatiquement un worklist item pour chaque consultation
    """
    print('creer_worklist_item')
    _, created = WorklistItem.objects.get_or_create(
        consultation=instance,
        defaults={
            'study_instance_uid': generate_uid(),
            'requested_procedure_description': 'US',
            'requested_procedure_id': 'US',
            'mpps_status': WorklistItem.MPPS_STATUS_PENDING,
            'device': instance.praticien.default_device if instance.praticien and instance.praticien.default_device else None,
        }
    )
    if created:
        print(f'WorklistItem créé pour la consultation {instance.id}')
    else:
        print(f'WorklistItem existe déjà pour la consultation {instance.id}')


@receiver(post_save, sender=TentativePMA)
def creer_consultation_pma(sender, instance, **kwargs):
    """
    Fonction qui crée automatiquement une consultation suite à la création/modification d'une tentative PMA
    """
    print('creer_consultation_pma')
    patient = instance.patient
    today = datetime.date.today()
    consultations = patient.consultation_set.filter(
        motif__code="pma",
        date__day=today.day,
        date__month=today.month,
        date__year=today.year)
    if consultations.count() == 0:
        print(f'Création de consultation pour la TentativePMA {instance.id}')
        motif = MotifConsultation.objects.get(code="pma")
        item = Consultation(patient=patient, praticien=instance.praticien, motif=motif)
        item.save()
        # Mettre à jour l'admission
        today = datetime.date.today()
        patient.admission_set.filter(date__day=today.day, date__month=today.month, date__year=today.year).update(statut='3')
        patient.rdv_set.filter(debut__day=today.day, debut__month=today.month, debut__year=today.year).update(statut=3)


@receiver(post_save, sender=Grossesse)
def sauvegarder_lieu_accouchement(sender, instance, **kwargs):
    """
    Fonction qui sauvegarde le lieu d'accouchement au niveau du patient
    """
    print('sauvegarder_lieu_accouchement')
    patient = instance.patient
    if instance.lieu_accouchement_principal == 'A' or instance.lieu_accouchement_principal == '' or instance.lieu_accouchement_principal == None:
        patient.lieu_accouchement = None
    elif instance.lieu_accouchement:
        patient.lieu_accouchement = instance.lieu_accouchement
    patient.save()


@receiver(post_save, sender=ResultatAnalyseBiologique)
def sauvegarder_resultat_grossesse(sender, instance, **kwargs):
    c = instance.analyse.code
    g = instance.prescription.patient.grossesse_encours
    if g:
        if c == 'DPNI':
            g.dpni = instance.valeur
        g.save()
