import json

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView

from apps.core.forms import GrossesseForm
from apps.core.models import Patient, Grossesse
from apps.core.serializers import GrossesseSerializer
from apps.core.services import patients


class GrossesseCreate(PermissionRequiredMixin, CreateView):
    model = Grossesse
    form_class = GrossesseForm
    template_name = 'core/grossesse_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('fermer_fenetre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = get_object_or_404(Patient, pk=self.kwargs['pk'])
        context['patient'] = patient
        return context

    def get_initial(self):
        init = super().get_initial()
        init['patient'] = self.kwargs['pk']
        init['encours'] = True
        patient = get_object_or_404(Patient, pk=self.kwargs['pk'])
        init['poids_avant_grossesse'] = patient.poids
        init['taille'] = patient.taille
        return init


class GrossesseUpdate(PermissionRequiredMixin, UpdateView):
    model = Grossesse
    form_class = GrossesseForm
    template_name = 'core/grossesse_form.html'
    permission_required = 'core.change_patient'
    success_url = '/utils/fermer_noreload/?event=grossesse:updated'

    def form_valid(self, form):
        if form.is_valid():
            obj = form.save(commit=False)
            if obj.nb_foetus == 'unique':
                obj.type_grossesse = None
            obj.save()
        return super().form_valid(form)


class CalendrierGrossesseDetail(PermissionRequiredMixin, DetailView):
    model = Grossesse
    template_name = 'core/grossesse_calendrier_detail.html'
    permission_required = 'core.change_patient'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grossesse_json'] = json.dumps(GrossesseSerializer(self.object).data)
        return context


@permission_required('core.view_patient', raise_exception=True)
def mesures(request, pk):
    grossesse = get_object_or_404(Grossesse, pk=pk)
    data = patients.get_all_obs_measure_history(grossesse)
    return JsonResponse(data, safe=False)