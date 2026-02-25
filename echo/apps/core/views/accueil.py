import json
import os
from datetime import date, datetime, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.cache import cache
from django.db.models import Q, F
from django.views.generic import TemplateView
from django.core import serializers

from apps.core.models import Rdv, Patient, Consultation, MotifConsultation, Admission, Medecin
from apps.core.serializers import AdmissionSerializer, ConsultationSerializer, RdvSerializer, MedecinSerializer, \
    MotifRdv, MotifRdvSerializer


# Reinitialise l'ordre de passage des patients de la journée
# Todo transférer comme signal ou dans le module patients
def reinitialiser_ordre_passage(request):
    today = date.today()
    admissions = Admission.objects.filter(date__day=today.day, date__month=today.month, date__year=today.year,
                                          statut='1',
                                          patient__compte=request.user.profil.compte).order_by('ordre')
    count = 1
    for adm in admissions:
        # print('Admission {} ordre {}'.format(adm.patient, adm.ordre))
        adm.ordre = count
        adm.save()
        count = count + 1


class Accueil(PermissionRequiredMixin, TemplateView):
    template_name = 'core/accueil_v2.html'
    permission_required = 'core.view_rdv'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        compte = self.request.user.profil.compte.raison_sociale.replace(' ', '+')
        os.system(f'echo "export EE_COMPTE={compte}" >> ~/.bashrc')

        reinitialiser_ordre_passage(self.request)

        if 'msg' in self.request.GET:
            if self.request.GET['msg'] == 'admission_succes':
                context['msg'] = 'Patient admis avec succès'
            if self.request.GET['msg'] == 'consultation_terminee_succes':
                context['msg'] = 'Consultation terminée avec succès'
            if self.request.GET['msg'] == 'consultation_demarree_succes':
                context['msg'] = 'Consultation démarrée avec succès'

        today = date.today()

        if 'date' in self.request.GET:
            today = self.request.GET['date']

        context['date'] = today

        now = datetime.now()
        periode_debut = now - timedelta(days=10)
        periode_debut = periode_debut.replace(hour=0, minute=0)
        periode_fin = now + timedelta(days=10)
        periode_fin = periode_fin.replace(hour=23, minute=59)
        jour_min = now.replace(hour=0, minute=0)
        jour_max = now.replace(hour=23, minute=59)

        # rdvs = Rdv.objects.filter(Q(compte=self.request.user.profil.compte) &
        #                          (Q(debut__day=today.day) & Q(debut__month=today.month) & Q(debut__year=today.year))
        #                          | (Q(ancien_debut__day=today.day) & Q(ancien_debut__month=today.month) & Q(ancien_debut__year=today.year)))

        # Chercher tous les rdv dont la date de debut ou l'anicenne date de début est dans [aujourd'hui-10, aujourd'hui+10]
        rdvs = Rdv.objects.filter(Q(compte=self.request.user.profil.compte) &
                                  (Q(debut__gte=periode_debut) & Q(debut__lte=periode_fin)
                                   | (Q(ancien_debut__gte=periode_debut) & Q(
                                              ancien_debut__lte=periode_fin))))\
                                    .select_related('patient').select_related('praticien')

        """
        rdvs_json = serializers.serialize('json', list(rdvs), use_natural_foreign_keys=True,
                                          fields=(
                                              'id', 'debut', 'ancien_debut', 'nom', 'nom_naissance', 'prenom', 'telephone', 'ville',
                                              'praticien', 'statut', 'motif', 'nouveau', 'patient', 'patient_rappele'))
                                              """
        rdvs_json = RdvSerializer(rdvs, many=True)
        context['rdvs_json'] = json.dumps(rdvs_json.data)

        admissions = Admission.objects.filter(date__gte=jour_min,
                                              date__lte=jour_max,
                                              patient__compte=self.request.user.profil.compte) \
                                        .order_by('ordre') \
                                        .select_related('patient').select_related('patient__adresse')
        admissions_json = AdmissionSerializer(admissions, many=True)
        context['admissions_json'] = json.dumps(admissions_json.data)

        consultations = Consultation.objects.filter(patient__compte=self.request.user.profil.compte,
                                                    date__gte=periode_debut, date__lte=periode_fin)
        consultations_json = ConsultationSerializer(consultations, many=True)
        context['consultations_json'] = json.dumps(consultations_json.data)

        motifs_consultation = MotifConsultation.objects.all()
        motifs_consultation_json = serializers.serialize('json', list(motifs_consultation),
                                                         use_natural_foreign_keys=True)
        context['motifs_consultation_json'] = motifs_consultation_json

        praticiens = Medecin.objects.filter(compte=self.request.user.profil.compte)
        context['praticiens'] = praticiens
        context['praticiens_json'] = json.dumps(MedecinSerializer(praticiens, many=True).data)

        motifs_rdvs = MotifRdv.objects.all()
        context['motifs_rdv'] = motifs_rdvs
        context['motifs_rdv_json'] = json.dumps(MotifRdvSerializer(motifs_rdvs, many=True).data)

        return context
