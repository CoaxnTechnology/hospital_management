from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views import View
from apps.core.forms import PraticienForm
from apps.core.models import Patient
from apps.core.models import Praticien
from django.http import JsonResponse
from apps.core import utils


class PraticienCreate(BSModalCreateView):
    template_name = 'core/praticien_form.html'
    form_class = PraticienForm
    success_message = 'Praticien créé avec succès.'
    success_url = reverse_lazy('accueil')

    def form_valid(self, form):
        if form.is_valid():
            if not utils.is_ajax(self.request):
                praticien = form.save()
                patient_pk = self.request.GET['patient']
                patient = get_object_or_404(Patient, pk=patient_pk)
                patient.praticiens_correspondants.add(praticien)

        return super().form_valid(form)

    def get_success_url(self):
        return self.request.GET['next']


class PraticienUpdate(BSModalUpdateView):
    template_name = 'core/praticien_form.html'
    permission_required = 'core.change_patient'
    form_class = PraticienForm
    success_message = 'Praticien Modifié avec succès.'
    success_url = reverse_lazy('accueil')
    model = Praticien

    def get_success_url(self):
        return self.request.GET['next']


def supprimer_praticien(request, pk):
    query = get_object_or_404(Praticien, pk=pk)
    query.delete()
    data = {'message': "Praticien supprimé avec succès"}
    return JsonResponse(data)
