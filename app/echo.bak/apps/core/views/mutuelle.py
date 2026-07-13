import json
from datetime import date
from typing import Dict, Any

from django.views import View
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.core import serializers
from django.http import HttpResponseNotFound, HttpResponseBadRequest, JsonResponse, HttpResponse
from django.views.generic import CreateView, UpdateView, ListView, TemplateView
from apps.core.models import Admission, Prestation
from django.db.models import Q
from apps.core.models import Reglement, Patient, Praticien, LigneReglement, Bordereau, Profil
from apps.core.forms import ReglementForm, PatientForm, PraticienForm, LigneReglementForm
from apps.core.serializers import PrestationSerializer, AdmissionSerializer, ReglementSerializer, MedecinSerializer, \
    BordereauSerializer
from django import forms

from apps.core.services.mutuelle import generate_report, MissingDataException


class List(LoginRequiredMixin, TemplateView):
    template_name = 'core/mutuelle_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        mutuelles = Reglement.objects \
            .filter(mutuelle=True, nom_mutuelle='CNAM', bordereau__isnull=True) \
            .order_by('date_creation') \
            .select_related('patient')
        mutuelles_json = ReglementSerializer(mutuelles, many=True)
        context['object_list'] = json.dumps(mutuelles_json.data)
        bordereaux = Bordereau.objects.all()
        bordereau_json = BordereauSerializer(bordereaux, many=True)
        context['bordereaux'] = json.dumps(bordereau_json.data)

        return context


@permission_required('core.add_cloture', raise_exception=True)
def bordereau_creation(request):
    current_year = date.today().year
    last_id = Bordereau.objects.filter(Q(date_bordereau__year=current_year)).last()
    if last_id is not None:
        last_bordereau = last_id.bordereau_id + 1
    else:
        last_bordereau = 1
    bordereau = Bordereau()
    bordereau.bordereau_id = last_bordereau
    bordereau.nom_medecin = request.user.profil.nom
    bordereau.code_conventionnel = request.user.profil.code_conventionnel
    bordereau.save()
    reglement_array = request.POST.getlist('reglements_ids[]', None)
    for reglement in reglement_array:
        object = get_object_or_404(Reglement, pk=reglement)
        object.bordereau = bordereau
        object.save()
    return redirect(reverse("bordereau_detail", kwargs={'pk': bordereau.pk}))


class BordereauDetail(LoginRequiredMixin, TemplateView):
    template_name = 'core/bordereau_detail.html'
    permission_required = 'core.view_cloture'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        mutuelles = Reglement.objects.filter(bordereau=self.kwargs['pk']) \
            .select_related('patient')
        profil = Profil.objects.filter(compte=self.request.user.profil.compte) \
            .select_related('user')
        context['profil'] = profil
        mutuelles_json = ReglementSerializer(mutuelles, many=True)
        context['object_list'] = json.dumps(mutuelles_json.data)
        bordereau = Bordereau.objects.filter(pk=self.kwargs['pk'])
        context['bordereau'] = json.dumps(BordereauSerializer(bordereau, many=True).data)
        context['bordereau_object'] = get_object_or_404(Bordereau, pk=self.kwargs['pk'])
        return context


@permission_required('core.view_cloture', raise_exception=True)
def telecharger_rapport(request, pk):
    if pk:
        bordereau = get_object_or_404(Bordereau, pk=pk)
        filename = f"Declaration CNAM - {bordereau.periode_format}.txt"
        try:
            content = generate_report(pk)
        except MissingDataException as x:
            return HttpResponseBadRequest(x)
        print('Content', content)
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(content)
        return response
    else:
        return HttpResponseBadRequest()


@login_required
def supprimer_bordereau(request, pk):
    query = get_object_or_404(Bordereau, pk=pk)
    query.delete()
    return redirect(reverse("mutuelle_list"))
