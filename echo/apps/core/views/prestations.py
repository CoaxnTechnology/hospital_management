import json
from datetime import date

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView
from apps.core.forms import PrestationForm
from apps.core.models import Prestation, Patient
from apps.core.serializers import PrestationSerializer


class PrestationList(PermissionRequiredMixin, ListView):
    model = Prestation
    template_name = 'core/prestation_list.html'
    permission_required = 'core.view_prestation'

    def get_queryset(self):
        return Prestation.objects.filter(compte=self.request.user.profil.compte)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prestations_json = PrestationSerializer(self.get_queryset(), many=True)
        context['prestations_json'] = json.dumps(prestations_json.data)
        return context


class PrestationCreate(PermissionRequiredMixin, CreateView):
    model = Prestation
    form_class = PrestationForm
    template_name = 'core/prestation_form.html'
    permission_required = 'core.add_prestation'
    success_url = reverse_lazy('prestations_list')

    def form_valid(self, form):
        if form.is_valid():
            if form.cleaned_data['par_defaut'] == True:
                self.request.user.profil.compte.prestation_set.update(par_defaut=False)
        return super().form_valid(form)


class PrestationUpdate(PermissionRequiredMixin, UpdateView):
    model = Prestation
    form_class = PrestationForm
    template_name = 'core/prestation_form.html'
    permission_required = 'core.change_prestation'
    success_url = reverse_lazy('prestations_list')

    def form_valid(self, form):
        if form.is_valid():
            if form.cleaned_data['par_defaut'] == True:
                self.request.user.profil.compte.prestation_set.update(par_defaut=False)
        return super().form_valid(form)


@login_required
@permission_required('core.delete_prestation', raise_exception=True)
def supprimer_prestation(request, pk):
    query = get_object_or_404(Prestation, pk=pk)
    query.delete()
    return redirect(reverse("prestations_list"))
