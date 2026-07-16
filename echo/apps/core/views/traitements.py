import json
from datetime import date

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView

from apps.core.forms import TraitementForm
from apps.core.models import Traitement, Patient
from apps.core.serializers import TraitementSerializer


class TraitementList(PermissionRequiredMixin, ListView):
    model = Traitement
    template_name = 'core/traitement_list.html'
    permission_required = 'core.view_patient'

    def get_queryset(self):
        return Traitement.objects.filter(compte=self.request.user.profil.compte)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # traitements_json = TraitementSerializer(self.get_queryset(), many=True)
        # context['traitements_json'] = json.dumps(traitements_json.data)
        return context


class TraitementCreate(PermissionRequiredMixin, CreateView):
    model = Traitement
    form_class = TraitementForm
    template_name = 'core/traitement_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('traitements_list')


class TraitementUpdate(PermissionRequiredMixin, UpdateView):
    model = Traitement
    form_class = TraitementForm
    template_name = 'core/traitement_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('traitements_list')


@login_required
@permission_required('core.change_patient', raise_exception=True)
def supprimer_traitement(request, pk):
    query = get_object_or_404(Traitement, pk=pk)
    query.delete()
    return redirect(reverse("traitements_list"))


@login_required
@permission_required('core.view_patient', raise_exception=True)
def rechercher_traitement(request):
    objects = Traitement.objects.filter(compte=request.user.profil.compte)
    if request.body is not None:
        try:
            body = json.loads(request.body)
            query = body['libelle']
            # Typeahead autocomplete request
            if query is not None:
                filtered = objects.filter(libelle__icontains=query).order_by('libelle')[:20]
                resp = TraitementSerializer(filtered, many=True)
                return JsonResponse(json.dumps(resp.data), safe=False)
        except:
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

    filtered = objects.filter(libelle__icontains=libelle).order_by(dir + order_col_name)
    total = objects.count()
    filtered_count = filtered.count()
    objs = filtered[start:start + length - 1]
    objs_json = TraitementSerializer(objs, many=True)
    resp = {
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': filtered_count,
        'data': objs_json.data
    }
    return JsonResponse(resp)
