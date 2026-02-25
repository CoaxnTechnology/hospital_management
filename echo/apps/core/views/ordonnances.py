import json
from datetime import date, datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, ListView, DetailView

from apps.core.forms import OrdonnanceForm
from apps.core.models import Ordonnance, Patient, Traitement, Prescription, Medecin, TypeOrdonnance
from apps.core.serializers import OrdonnanceSerializer, TraitementSerializer, PatientSerializer, PrescriptionSerializer, \
    MedecinSerializer
from apps.core.services.patients import get_grossesse_data


class OrdonnanceList(PermissionRequiredMixin, ListView):
    model = Ordonnance
    template_name = 'core/ordonnance_list.html'
    permission_required = 'core.view_patient'

    def get_queryset(self):
        patient = get_object_or_404(Patient, pk=self.kwargs['patient_pk'])
        return Ordonnance.objects.filter(patient=patient)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ordonnances_json = OrdonnanceSerializer(self.get_queryset(), many=True)
        context['ordonnances_json'] = json.dumps(ordonnances_json.data)
        patient = get_object_or_404(Patient, pk=self.kwargs['patient_pk'])
        context['patient'] = patient
        return context


class OrdonnanceCreate(PermissionRequiredMixin, CreateView):
    model = Ordonnance
    form_class = OrdonnanceForm
    template_name = 'core/ordonnance_form.html'
    permission_required = 'core.change_patient'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = get_object_or_404(Patient.objects.select_related('adresse'), pk=self.kwargs['patient_pk'])
        context['patient'] = patient
        context['patient_json'] = json.dumps(PatientSerializer(patient).data)
        praticiens = Medecin.objects.filter(compte=self.request.user.profil.compte).select_related('user')
        praticiens_json = MedecinSerializer(praticiens, many=True)
        context['praticiens_json'] = json.dumps(praticiens_json.data)
        context['grossesse_data'] = json.dumps(get_grossesse_data(patient))
        return context

    def get_initial(self):
        initial_base = super().get_initial()
        initial_base['praticien'] = self.request.user.profil
        initial_base['patient'] = self.kwargs['patient_pk']
        initial_base['date'] = datetime.today()
        type = TypeOrdonnance.objects.filter(compte=self.request.user.profil.compte).first()
        if type:
            initial_base['type'] = type.id
        return initial_base

    def get_success_url(self):
        return reverse("ordonnance_modifier", kwargs={'pk': self.object.pk})


class OrdonnanceView(PermissionRequiredMixin, DetailView):
    model = Ordonnance
    template_name = 'core/ordonnance_detail.html'
    permission_required = 'core.view_patient'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class OrdonnanceUpdate(PermissionRequiredMixin, UpdateView):
    model = Ordonnance
    form_class = OrdonnanceForm
    template_name = 'core/ordonnance_form.html'
    permission_required = 'core.change_patient'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ordonnance = self.object
        context['patient'] = ordonnance.patient
        context['patient_json'] = json.dumps(PatientSerializer(ordonnance.patient).data)
        praticiens = Medecin.objects.filter(compte=self.request.user.profil.compte).select_related('user')
        praticiens_json = MedecinSerializer(praticiens, many=True)
        context['praticiens_json'] = json.dumps(praticiens_json.data)
        context['grossesse_data'] = json.dumps(get_grossesse_data(ordonnance.patient))
        return context

    def get_success_url(self):
        return reverse("ordonnance_modifier", kwargs={'pk': self.object.pk})


@login_required
@permission_required('core.change_patient', raise_exception=True)
def supprimer_ordonnance(request, pk):
    query = get_object_or_404(Ordonnance, pk=pk)
    patient_pk = query.patient.pk
    query.delete()
    return redirect(reverse("ordonnances_list", kwargs={'patient_pk': patient_pk}))
