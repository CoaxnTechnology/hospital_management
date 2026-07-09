import json
from datetime import date, datetime, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.cache import cache
from django.db.models import Q, F
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, View
from django.core import serializers

from apps.core.models import Rdv, Patient, Consultation, MotifConsultation, Admission, Medecin, Device
from apps.core.serializers import AdmissionSerializer, ConsultationSerializer, RdvSerializer, MedecinSerializer, \
    MotifRdv, MotifRdvSerializer, DeviceSerializer


# Reinitialise l'ordre de passage des patients de la journée
# Todo transférer comme signal ou dans le module patients
def reinitialiser_ordre_passage(request):
    today = date.today()
    try:
        compte = request.user.profil.compte
    except:
        return
    admissions = Admission.objects.filter(date__day=today.day, date__month=today.month, date__year=today.year,
                                          statut='1',
                                          patient__compte=compte).order_by('ordre')
    count = 1
    for adm in admissions:
        # print('Admission {} ordre {}'.format(adm.patient, adm.ordre))
        adm.ordre = count
        adm.save()
        count = count + 1


class Accueil(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'core/accueil_v2.html'
    permission_required = 'core.view_rdv'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        reinitialiser_ordre_passage(self.request)

        try:
            compte = self.request.user.profil.compte
        except:
            context['rdvs_json'] = '[]'
            context['rdvs_jour_today'] = '[]'
            context['admissions_json'] = '[]'
            context['en_exam_count'] = 0
            context['terminated_admissions_json'] = '[]'
            context['consultations_json'] = '[]'
            context['motifs_consultation_json'] = '[]'
            context['praticiens'] = []
            context['praticiens_json'] = '[]'
            context['motifs_rdv'] = []
            context['motifs_rdv_json'] = '[]'
            context['devices_json'] = '[]'
            context['date'] = date.today()
            return context

        if 'msg' in self.request.GET:
            if self.request.GET['msg'] == 'admission_succes':
                context['msg'] = _('Patient admis avec succès')
            if self.request.GET['msg'] == 'consultation_terminee_succes':
                context['msg'] = _('Consultation terminée avec succès')
            if self.request.GET['msg'] == 'consultation_demarree_succes':
                context['msg'] = _('Consultation démarrée avec succès')

        if self.request.GET.get('error') == 'exam_en_cours':
            nom = self.request.GET.get('nom', '')
            context['error_msg'] = (
                f"Un examen est déjà en cours pour {nom}. "
                f"Terminez-le depuis l'onglet « En examen » avant d'en démarrer un autre."
            )

        today = date.today()

        if 'date' in self.request.GET:
            today = self.request.GET['date']

        context['date'] = today

        now = datetime.now()
        periode_debut = now - timedelta(days=10)
        periode_debut = periode_debut.replace(hour=0, minute=0)
        periode_fin = now + timedelta(days=60)
        periode_fin = periode_fin.replace(hour=23, minute=59)
        jour_min = now.replace(hour=0, minute=0)
        jour_max = now.replace(hour=23, minute=59)

        rdvs = Rdv.objects.filter(Q(compte=compte) &
                                  (Q(debut__gte=periode_debut) & Q(debut__lte=periode_fin)
                                   | (Q(ancien_debut__gte=periode_debut) & Q(
                                               ancien_debut__lte=periode_fin))))\
                                    .select_related('patient').select_related('praticien')
        rdvs_json = RdvSerializer(rdvs, many=True)
        context['rdvs_json'] = json.dumps(rdvs_json.data)

        rdvs_today = [r for r in rdvs if r.debut.date() == today and r.statut != '10']
        context['rdvs_jour_today'] = json.dumps(RdvSerializer(rdvs_today, many=True).data)

        admissions = Admission.objects.filter(date__gte=jour_min,
                                              date__lte=jour_max,
                                              patient__compte=compte) \
                                        .order_by('ordre') \
                                        .select_related('patient').select_related('patient__adresse')
        admissions_json = AdmissionSerializer(admissions, many=True)
        context['admissions_json'] = json.dumps(admissions_json.data)

        en_exam_count = Admission.objects.filter(
            date__gte=jour_min, date__lte=jour_max,
            patient__compte=compte,
            statut='2',
        ).count()
        context['en_exam_count'] = en_exam_count

        terminated_admissions = Admission.objects.filter(date__gte=jour_min,
                                                         date__lte=jour_max,
                                                         patient__compte=compte,
                                                         statut='4') \
                                                   .order_by('ordre') \
                                                   .select_related('patient').select_related('patient__adresse')
        context['terminated_admissions_json'] = json.dumps(AdmissionSerializer(terminated_admissions, many=True).data)

        consultations = Consultation.objects.filter(patient__compte=compte,
                                                    date__gte=periode_debut, date__lte=periode_fin) \
                                            .exclude(patient__admission__statut__in=['2', '4'],
                                                     patient__admission__date__gte=jour_min,
                                                     patient__admission__date__lte=jour_max)
        consultations_json = ConsultationSerializer(consultations, many=True)
        context['consultations_json'] = json.dumps(consultations_json.data)

        motifs_consultation = MotifConsultation.objects.all()
        motifs_consultation_json = serializers.serialize('json', list(motifs_consultation),
                                                         use_natural_foreign_keys=True)
        context['motifs_consultation_json'] = motifs_consultation_json

        praticiens = Medecin.objects.filter(compte=compte)
        seen = set()
        unique_praticiens = []
        for p in praticiens:
            key = p.nom
            if key not in seen:
                seen.add(key)
                unique_praticiens.append(p)
        context['praticiens'] = unique_praticiens
        context['praticiens_json'] = json.dumps(MedecinSerializer(unique_praticiens, many=True).data)

        motifs_rdvs = MotifRdv.objects.all()
        context['motifs_rdv'] = motifs_rdvs
        context['motifs_rdv_json'] = json.dumps(MotifRdvSerializer(motifs_rdvs, many=True).data)

        devices = Device.objects.filter(compte=compte)
        context['devices_json'] = json.dumps(DeviceSerializer(devices, many=True).data)

        return context


class AdmissionsAujourdhuiJson(LoginRequiredMixin, View):
    def get(self, request):
        try:
            compte = request.user.profil.compte
        except:
            return JsonResponse({'admissions': []})
        today = date.today()
        jour_min = datetime.now().replace(hour=0, minute=0)
        jour_max = datetime.now().replace(hour=23, minute=59)
        admissions = Admission.objects.filter(date__gte=jour_min, date__lte=jour_max,
                                              patient__compte=compte) \
                                      .order_by('ordre') \
                                      .select_related('patient__adresse')
        data = AdmissionSerializer(admissions, many=True).data
        return JsonResponse({'admissions': data})
