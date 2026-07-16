import json
from datetime import date

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import UpdateView, CreateView, ListView

from apps.core import models
from apps.core.forms import ConsultationForm
from apps.core.models import Patient, Consultation, MotifConsultation, Medecin, TemplateEdition, \
    ConsultationObstetrique, Device, WorklistItem
from apps.core.serializers import PatientSerializer, MedecinSerializer, ImageConsultationSerializer, \
    TemplateEditionSerializer, ImageConsultationSerializerLight, SRConsultationSerializer, DeviceSerializer
from apps.core.views import patients
from apps.core import utils


class AjaxableResponseMixin(PermissionRequiredMixin):
    permission_required = 'core.change_patient'
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if utils.is_ajax(self.request):
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super().form_valid(form)
        if utils.is_ajax(self.request):
            data = {
                'consultation_pk': self.object.pk,
                'status': 'ok'
            }
            if hasattr(self.object, 'date'):
                data['date'] = self.object.date
            return JsonResponse(data)
        else:
            return response


class ConsultationList(PermissionRequiredMixin, ListView):
    model = Consultation
    template_name = 'core/consultation_list.html'
    permission_required = 'core.view_patient'

    def get_queryset(self):
        patient = get_object_or_404(Patient, pk=self.kwargs['patient_pk'])
        q = Consultation.objects.filter(patient=patient) \
            .select_related('patient') \
            .select_related('praticien') \
            .select_related('praticien__user') \
            .select_related('motif') \
            .order_by('-date')
        return q


class ConsultationCreateBase(CreateView):
    titre = 'Consultation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editor_only'] = True
        context['titre'] = self.titre
        patient = get_object_or_404(Patient, pk=self.kwargs['pk'])
        context['patient'] = patient
        fichiers = patient.fichierpatient_set.order_by('-date')
        context['fichiers'] = fichiers
        context['patient_json'] = json.dumps(PatientSerializer(patient).data)
        medecins = Medecin.objects.filter(compte=self.request.user.profil.compte)
        medecins_json = MedecinSerializer(medecins, many=True)
        context['medecins_json'] = json.dumps(medecins_json.data)
        devices = Device.objects.filter(compte=self.request.user.profil.compte)
        context['devices'] = devices
        context['devices_json'] = json.dumps(DeviceSerializer(devices, many=True).data)
        patients.charger_info_panel_context(self.request, context, patient)
        if patient.mesures_jour:
            if patient.mesures_jour.ta:
                context['ta'] = patient.mesures_jour.ta
            if patient.mesures_jour.poids:
                context['poids'] = patient.mesures_jour.poids
            else:
                context['poids'] = patient.poids
        return context


class ConsultationUpdateBase(UpdateView):
    titre = 'Consultation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editor_only'] = True
        context['titre'] = self.titre
        patient = self.object.patient
        context['patient'] = patient
        fichiers = patient.fichierpatient_set.order_by('-date')
        context['fichiers'] = fichiers
        context['patient_json'] = json.dumps(PatientSerializer(patient).data)
        medecins = Medecin.objects.filter(compte=self.request.user.profil.compte)
        medecins_json = MedecinSerializer(medecins, many=True)
        context['medecins_json'] = json.dumps(medecins_json.data)
        devices = Device.objects.filter(compte=self.request.user.profil.compte)
        context['devices'] = devices
        context['devices_json'] = json.dumps(DeviceSerializer(devices, many=True).data)
        patients.charger_info_panel_context(self.request, context, patient)
        if hasattr(self.object, 'imageconsultation_set'):
            context['images_json'] = json.dumps(ImageConsultationSerializerLight(
                self.object.imageconsultation_set.all(), many=True).data)
        if hasattr(self.object, 'srconsultation_set'):
            context['sr_json'] = json.dumps(SRConsultationSerializer(self.object.srconsultation_set.last()).data)
        if 'edition' in self.request.GET:
            context['mode_edition'] = True
        return context


class ConsultationCreate(PermissionRequiredMixin, ConsultationCreateBase):
    template_name = 'core/consultation_form.html'
    permission_required = 'core.change_patient'
    model = Consultation
    form_class = ConsultationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        motif = MotifConsultation.objects.filter(code=self.request.GET.get('motif'))
        context['motif'] = motif[0]
        templates = TemplateEdition.objects.filter(compte=self.request.user.profil.compte,
                                                   categorie_consultation=motif[0].categorie)
        context['templates'] = templates
        templates_json = TemplateEditionSerializer(templates, many=True)
        context['templates_json'] = json.dumps(templates_json.data)
        context['doublon_consultation'] = context['patient'].check_doublon_consultation(motif=context['motif'],
                                                                                        date=date.today())
        return context

    def get_initial(self):
        initial_base = super().get_initial()
        initial_base['praticien'] = self.request.user.profil
        return initial_base


@login_required
@permission_required('core.change_patient', raise_exception=True)
def enregistrer_consultation(request, pk):
    consultation_pk = int(request.POST.get('consultation_pk', None))
    motif_pk = request.POST.get('motif', None)
    text = request.POST.get('text', None)
    praticien_pk = request.POST.get('praticien', None)
    patient = get_object_or_404(Patient, pk=pk)
    praticien = get_object_or_404(Medecin, pk=praticien_pk)
    if consultation_pk == -1:
        # Créer la consultation et renvoyer le pk au client
        motif = get_object_or_404(MotifConsultation, pk=motif_pk)
        print('Motif', motif)
        if motif.categorie_id == 1:
            # Consultation obstetrique
            consultation = ConsultationObstetrique(motif=motif, grossesse=patient.grossesse_encours)
        else:
            consultation = Consultation(motif=motif)
        consultation.patient = patient
        consultation.date = date.today()
    else:
        if motif_pk is not None:
            motif = get_object_or_404(MotifConsultation, pk=motif_pk)
            if motif.categorie_id == 1:
                # Consultation obstetrique
                consultation = get_object_or_404(ConsultationObstetrique, pk=consultation_pk)
            else:
                consultation = get_object_or_404(Consultation, pk=consultation_pk)
        else:
            consultation = get_object_or_404(Consultation, pk=consultation_pk)

    consultation.text = text
    consultation.praticien = praticien
    consultation.save()

    data = {
        'consultation_pk': consultation.pk,
        'date': consultation.date,
        'message': "Consultation enregistrée avec succès"}
    return JsonResponse(data)


def get_tab_by_motif_categorie(categorie):
    if categorie == 1:
        tab = "tab-obstetrique"
    if categorie == 2:
        tab = "tab-gynecologique"
    if categorie == 3:
        tab = "tab-pma"
    if categorie == 4:
        tab = "tab-examen-libre"
    if categorie == 7:
        tab = "tab-cro"
    return tab


@login_required
@permission_required('core.change_patient', raise_exception=True)
def supprimer_consultation(request, pk):
    consultation = get_object_or_404(Consultation, pk=pk)
    patient_pk = consultation.patient.pk
    #print('Consultation cat', consultation.motif.categorie.pk)
    tab = get_tab_by_motif_categorie(consultation.motif.categorie.pk)
    consultation.delete()
    return redirect(reverse("patient_afficher", kwargs={'pk': patient_pk}) + f"#{tab}")


class ConsultationUpdate(PermissionRequiredMixin, ConsultationUpdateBase):
    template_name = 'core/consultation_form.html'
    permission_required = 'core.change_patient'
    model = Consultation
    form_class = ConsultationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['motif'] = self.object.motif
        templates = TemplateEdition.objects.filter(compte=self.request.user.profil.compte,
                                                   categorie_consultation=self.object.motif.categorie)
        context['templates'] = templates
        templates_json = TemplateEditionSerializer(templates, many=True)
        context['templates_json'] = json.dumps(templates_json.data)
        return context


@login_required
@permission_required('core.change_patient', raise_exception=True)
def terminer_consultation(request, pk):
    consultation = get_object_or_404(Consultation, pk=pk)
    consultation.worklistitem_set.all().update(mpps_status=WorklistItem.MPPS_STATUS_COMPLETED)
    patient = consultation.patient
    today = date.today()
    patient.admission_set.filter(Q(date__day=today.day)
                                 & Q(date__month=today.month)
                                 & Q(date__year=today.year)).update(statut='3')
    d = date.today()
    patient.rdv_set.filter(debut__day=d.day, debut__month=d.month, debut__year=d.year).update(statut=3)
    # return redirect("/accueil?msg=consultation_terminee_succes")
    return redirect(reverse("patient_afficher", kwargs={'pk': patient.pk}))