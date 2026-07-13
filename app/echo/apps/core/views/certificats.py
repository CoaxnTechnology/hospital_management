import json

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, ListView, DetailView

from apps.core.forms import CertificatForm
from apps.core.models import Certificat, Patient, Traitement, Medecin, TYPES_CERTIFICATS
from apps.core.serializers import CertificatSerializer, TraitementSerializer, PatientSerializer, MedecinSerializer
from apps.core.services.patients import *

class CertificatList(PermissionRequiredMixin, ListView):
    model = Certificat
    template_name = 'core/certificat_list.html'
    permission_required = 'core.view_patient'

    def get_queryset(self):
        patient = get_object_or_404(Patient, pk=self.kwargs['patient_pk'])
        return Certificat.objects.filter(patient=patient)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        certificats_json = CertificatSerializer(self.get_queryset(), many=True)
        context['certificats_json'] = json.dumps(certificats_json.data)
        patient = get_object_or_404(Patient, pk=self.kwargs['patient_pk'])
        context['patient'] = patient
        return context


class CertificatCreate(PermissionRequiredMixin, CreateView):
    model = Certificat
    form_class = CertificatForm
    template_name = 'core/certificat_form.html'
    permission_required = 'core.change_patient'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = get_object_or_404(Patient, pk=self.kwargs['patient_pk'])
        context['patient'] = patient
        context['patient_json'] = json.dumps(PatientSerializer(patient).data)
        praticiens = Medecin.objects.filter(compte=self.request.user.profil.compte)
        praticiens_json = MedecinSerializer(praticiens, many=True)
        context['praticiens_json'] = json.dumps(praticiens_json.data)
        context['types_certificats'] = TYPES_CERTIFICATS
        context['grossesse_data'] = json.dumps(get_grossesse_data(patient))
        return context

    def get_initial(self):
        initial_base = super().get_initial()
        initial_base['praticien'] = self.request.user.profil
        initial_base['patient'] = self.kwargs['patient_pk']
        return initial_base

    def form_valid(self, form):
        if form.is_valid():
            print('Form valid')
            certificat = form.save()
            print('Certificat', certificat)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("certificat_modifier", kwargs={'pk': self.object.pk})


class CertificatView(PermissionRequiredMixin, DetailView):
    model = Certificat
    template_name = 'core/certificat_detail.html'
    permission_required = 'core.view_patient'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        traitements = Traitement.objects.filter(compte=self.request.user.profil.compte)
        traitements_json = TraitementSerializer(traitements, many=True)
        context['traitements_json'] = json.dumps(traitements_json.data)
        praticiens = Medecin.objects.filter(compte=self.request.user.profil.compte)
        praticiens_json = MedecinSerializer(praticiens, many=True)
        context['praticiens_json'] = json.dumps(praticiens_json.data)
        return context


class CertificatUpdate(PermissionRequiredMixin, UpdateView):
    model = Certificat
    form_class = CertificatForm
    template_name = 'core/certificat_form.html'
    permission_required = 'core.change_patient'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        certificat = self.object
        context['patient'] = certificat.patient
        context['patient_json'] = json.dumps(PatientSerializer(certificat.patient).data)
        praticiens = Medecin.objects.filter(compte=self.request.user.profil.compte)
        praticiens_json = MedecinSerializer(praticiens, many=True)
        context['praticiens_json'] = json.dumps(praticiens_json.data)
        context['types_certificats'] = TYPES_CERTIFICATS
        context['grossesse_data'] = json.dumps(get_grossesse_data(certificat.patient))
        return context

    def get_success_url(self):
        return reverse("certificat_modifier", kwargs={'pk': self.object.pk})


@login_required
@permission_required('core.change_patient', raise_exception=True)
def supprimer_certificat(request, pk):
    query = get_object_or_404(Certificat, pk=pk)
    patient_pk = query.patient.pk
    query.delete()
    return redirect(reverse("certificats_list", kwargs={'patient_pk': patient_pk}))
