import json

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from apps.core.data import adresses
from apps.core.forms import EtablissementForm
from apps.core.models import Patient, Etablissement, Grossesse
from apps.core.serializers import EtablissementSerializer
from apps.core import utils


class EtablissementList(PermissionRequiredMixin, ListView):
    model = Etablissement
    template_name = 'core/etablissement_list.html'
    permission_required = 'core.view_patient'

    def get_queryset(self):
        return Etablissement.objects.filter(compte=self.request.user.profil.compte)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        etablissements_json = EtablissementSerializer(self.get_queryset(), many=True)
        context['etablissements_json'] = json.dumps(etablissements_json.data)
        return context


class EtablissementCreate(PermissionRequiredMixin, CreateView):
    model = Etablissement
    form_class = EtablissementForm
    template_name = 'core/etablissement_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('etablissements_liste')


class EtablissementUpdate(PermissionRequiredMixin, UpdateView):
    model = Etablissement
    form_class = EtablissementForm
    template_name = 'core/etablissement_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('etablissements_liste')


@login_required
@permission_required('core.change_patient', raise_exception=True)
def associer_etablissement(request, pk):
    etablissement_pk = request.POST.get('etablissement', None)
    patient = get_object_or_404(Patient, pk=pk)
    etablissement = get_object_or_404(Etablissement, pk=etablissement_pk)
    patient.lieu_accouchement = etablissement
    patient.save()
    if patient.grossesse_encours:
        g = patient.grossesse_encours
        g.lieu_accouchement = etablissement
        g.lieu_accouchement_principal = 'H'
        g.save()
        print("Sauvegarde du lieu d'accouchement", g.lieu_accouchement_principal)
    data = {'message': "Etablissement associé avec succès"}
    return JsonResponse(data)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def dissocier_etablissement(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    patient.lieu_accouchement = None
    patient.save()
    if patient.grossesse_encours:
        g = patient.grossesse_encours
        g.lieu_accouchement = None
        g.lieu_accouchement_principal = ''
        g.save()
    data = {'message': "Etablissement dissocié avec succès"}
    return JsonResponse(data)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def supprimer_etablissement(request, pk):
    query = get_object_or_404(Etablissement, pk=pk)
    query.delete()
    if utils.is_ajax(request):
        data = {'message': "Etablissement supprimé avec succès"}
        return JsonResponse(data)
    else:
        return redirect(reverse_lazy('etablissements_liste'))
