import json

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView

from apps.core.forms import DeviceForm
from apps.core.models import Device
from apps.core.serializers import DeviceSerializer


class DeviceList(PermissionRequiredMixin, ListView):
    model = Device
    template_name = 'core/device_list.html'
    permission_required = 'core.view_patient'

    def get_queryset(self):
        return Device.objects.filter(compte=self.request.user.profil.compte)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        devices_json = DeviceSerializer(self.get_queryset(), many=True)
        context['devices_json'] = json.dumps(devices_json.data)
        return context


class DeviceCreate(PermissionRequiredMixin, CreateView):
    model = Device
    form_class = DeviceForm
    template_name = 'core/device_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('devices_list')


class DeviceUpdate(PermissionRequiredMixin, UpdateView):
    model = Device
    form_class = DeviceForm
    template_name = 'core/device_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('devices_list')


@login_required
@permission_required('core.change_patient', raise_exception=True)
def supprimer_device(request, pk):
    query = get_object_or_404(Device, pk=pk)
    query.delete()
    return redirect(reverse("devices_list"))
