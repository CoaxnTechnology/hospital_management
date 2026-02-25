import json
from datetime import date

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView
from apps.core.forms import MotifAbsenceForm
from apps.core.models import Prestation, Patient,MotifAbsence
from apps.core.serializers import MotifAbsenceSerializer


class MotifList(PermissionRequiredMixin, ListView):
    model = MotifAbsence
    template_name = 'core/motif_list.html'
    permission_required = 'core.view_prestation'

    def get_queryset(self):
        return MotifAbsence.objects.filter(compte=self.request.user.profil.compte)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        motifs_json = MotifAbsenceSerializer(self.get_queryset(), many=True)
        context['motifs_json'] = json.dumps(motifs_json.data)
        return context


class MotifCreate(PermissionRequiredMixin, CreateView):
    model = MotifAbsence
    form_class = MotifAbsenceForm
    template_name = 'core/motif_form.html'
    permission_required = 'core.add_prestation'
    success_url = reverse_lazy('motifs_list')



class MotifUpdate(PermissionRequiredMixin, UpdateView):
    model = MotifAbsence
    form_class = MotifAbsenceForm
    template_name = 'core/motif_form.html'
    permission_required = 'core.change_prestation'
    success_url = reverse_lazy('motifs_list')

@login_required
@permission_required('core.delete_prestation', raise_exception=True)
def supprimer_motif(request, pk):
    query = get_object_or_404(MotifAbsence, pk=pk)
    query.delete()
    return redirect(reverse("motifs_list"))
