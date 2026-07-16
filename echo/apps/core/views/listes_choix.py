import json

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView

from apps.core.forms import ListeChoixForm
from apps.core.models import ListeChoix
from apps.core.serializers import ListeChoixSerializer


class ListeChoixList(PermissionRequiredMixin, ListView):
    model = ListeChoix
    template_name = 'core/liste_choix_list.html'
    permission_required = 'core.view_patient'

    def get_queryset(self):
        liste = ListeChoix.objects.all()
        if 'formulaire' in self.request.GET:
            liste = liste.filter(formulaire=self.request.GET['formulaire'])
        if 'champ' in self.request.GET:
            liste = liste.filter(champ=self.request.GET['champ'])
        return liste

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        listes_json = ListeChoixSerializer(self.get_queryset(), many=True)
        context['listes_json'] = json.dumps(listes_json.data)
        context['formulaire'] = self.request.GET['formulaire']
        context['champ'] = self.request.GET['champ']
        if 'event' in self.request.GET:
            context['event'] = 'liste:' + self.request.GET['event']
            context['id'] = self.request.GET['id']
        return context


class ListeChoixCreate(PermissionRequiredMixin, CreateView):
    model = ListeChoix
    form_class = ListeChoixForm
    template_name = 'core/liste_choix_form.html'
    permission_required = 'core.change_patient'

    def get_initial(self):
        init = super().get_initial()
        init['formulaire'] = self.request.GET['formulaire']
        init['champ'] = self.request.GET['champ']
        return init

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formulaire'] = self.request.GET['formulaire']
        context['champ'] = self.request.GET['champ']
        return context

    def form_valid(self, form):
        if form.is_valid():
            el = form.save(commit=False)
            ListeChoix.objects.filter(formulaire=el.formulaire, champ=el.champ).update(normale=False)
            el.save()
        return super().form_valid(form)

    def get_success_url(self):
        return f"{reverse('liste_choix_liste')}" \
               f"?formulaire={self.request.GET['formulaire']}" \
               f"&champ={self.request.GET['champ']}" \
               f"&event=created" \
               f"&id={self.object.pk}"


class ListeChoixUpdate(PermissionRequiredMixin, UpdateView):
    model = ListeChoix
    form_class = ListeChoixForm
    template_name = 'core/liste_choix_form.html'
    permission_required = 'core.change_patient'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formulaire'] = self.object.formulaire
        context['champ'] = self.object.champ
        return context

    def form_valid(self, form):
        if form.is_valid():
            el = form.save(commit=False)
            ListeChoix.objects.filter(formulaire=el.formulaire, champ=el.champ).update(normale=False)
            el.save()
        return super().form_valid(form)

    def get_success_url(self):
        return f"{reverse_lazy('liste_choix_liste')}" \
               f"?formulaire={self.object.formulaire}" \
               f"&champ={self.object.champ}" \
               f"&event=updated" \
               f"&id={self.object.pk}"


@login_required
@permission_required('core.change_patient', raise_exception=True)
def supprimer_liste_choix(request, pk):
    item = get_object_or_404(ListeChoix, pk=pk)
    item.delete()
    data = {'message': "ListeChoix supprimé avec succès"}
    return JsonResponse(data)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def desactiver_liste_choix(request, pk):
    item = get_object_or_404(ListeChoix, pk=pk)
    body = json.loads(request.body)
    if 'actif' not in body:
        return JsonResponse({'message': "Aucun statut (actif) fourni"}, status=400)
    if body['actif']:
        item.actif =  True
    else :
        item.actif = False
    item.save()
    data = {'message': "ListeChoix désactivé avec succès"}
    return JsonResponse(data)
