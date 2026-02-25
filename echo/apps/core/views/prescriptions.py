import json

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView

from apps.core.forms import PrescriptionForm
from apps.core.models import Prescription
from apps.core.serializers import PrescriptionSerializer


class PrescriptionList(PermissionRequiredMixin, ListView):
    model = Prescription
    template_name = 'core/prescription_list.html'
    permission_required = 'core.view_patient'

    def get_queryset(self):
        return Prescription.objects.filter(compte=self.request.user.profil.compte)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prescriptions_json = PrescriptionSerializer(self.get_queryset(), many=True)
        context['prescriptions_json'] = json.dumps(prescriptions_json.data)
        return context


class PrescriptionCreate(PermissionRequiredMixin, CreateView):
    model = Prescription
    form_class = PrescriptionForm
    template_name = 'core/prescription_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('prescriptions_list')


class PrescriptionUpdate(PermissionRequiredMixin, UpdateView):
    model = Prescription
    form_class = PrescriptionForm
    template_name = 'core/prescription_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('prescriptions_list')


@login_required
@permission_required('core.change_patient', raise_exception=True)
def supprimer_prescription(request, pk):
    query = get_object_or_404(Prescription, pk=pk)
    query.delete()
    return redirect(reverse("prescriptions_list"))


@login_required
@permission_required('core.view_patient', raise_exception=True)
def rechercher_prescription(request):
    all = Prescription.objects.filter(compte=request.user.profil.compte)

    if request.body is not None:
        try:
            body = json.loads(request.body)
            query = body['libelle']
            print('Query', query)
            # Typeahead autocomplete request
            if query is not None:
                if 'categorie' in body:
                    categorie = body['categorie']
                    filtered = all.filter(libelle__icontains=query, categorie=categorie).order_by('libelle')[:20]
                else:
                    filtered = all.filter(libelle__icontains=query).order_by('libelle')[:20]
                resp = PrescriptionSerializer(filtered, many=True)
                return JsonResponse(json.dumps(resp.data), safe=False)
        except Exception as x:
            print(x)
            pass

    # Data table request
    draw = request.POST.get('draw', None)
    start = int(request.POST.get('start', None))
    length = int(request.POST.get('length', None))
    order_col = int(request.POST.get('order[0][column]', None))
    order_col_name = request.POST.get('columns[{}][data]'.format(order_col))
    order_dir = request.POST.get('order[0][dir]', None)
    dir = ''
    if order_dir == 'desc':
        dir = '-'
    libelle = request.POST.get('columns[0][search][value]')

    filtered = all.filter(libelle__icontains=libelle).order_by(dir + order_col_name)
    total = all.count()
    filtered_count = filtered.count()
    objs = filtered[start:start + length - 1]
    objs_json = PrescriptionSerializer(objs, many=True)
    resp = {
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': filtered_count,
        'data': objs_json.data
    }
    return JsonResponse(resp)
