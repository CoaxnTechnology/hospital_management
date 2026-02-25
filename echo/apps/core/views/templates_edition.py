import json

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView

from apps.core.forms import TemplateEditionForm
from apps.core.models import TemplateEdition
from apps.core.serializers import TemplateEditionSerializer


class TemplateEditionList(PermissionRequiredMixin, ListView):
    model = TemplateEdition
    template_name = 'core/template_edition_list.html'
    permission_required = 'core.view_patient'

    def get_queryset(self):
        return TemplateEdition.objects.filter(compte=self.request.user.profil.compte)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        templates_edition_json = TemplateEditionSerializer(self.get_queryset(), many=True)
        context['templates_edition_json'] = json.dumps(templates_edition_json.data)
        return context


class TemplateEditionCreate(PermissionRequiredMixin, CreateView):
    model = TemplateEdition
    form_class = TemplateEditionForm
    template_name = 'core/template_edition_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('templates_edition_list')


class TemplateEditionUpdate(PermissionRequiredMixin, UpdateView):
    model = TemplateEdition
    form_class = TemplateEditionForm
    template_name = 'core/template_edition_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('templates_edition_list')


@login_required
@permission_required('core.change_patient', raise_exception=True)
def supprimer_template_edition(request, pk):
    query = get_object_or_404(TemplateEdition, pk=pk)
    query.delete()
    return redirect(reverse("templates_edition_list"))

