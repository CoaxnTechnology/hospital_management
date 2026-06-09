import json

from bootstrap_modal_forms.generic import BSModalUpdateView
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView

from apps.core.forms import InterrogatoirePMAForm, \
    TentativesHistoriquesPMAForm, BilanEndocrinienPMAFemininForm, BilanEndocrinienPMAMasculinForm, SpermogrammePMAForm, \
    TentativePMAForm, TraitementPMAForm, SuiviTraitementPMAForm, TraitementValeurPMAForm, \
    BaseSuiviTraitementCreateFormSet, BaseSuiviTraitementUpdateFormSet, TentativePMAClotureForm
from apps.core.models import ListeChoix, InterrogatoirePMA, TentativesHistoriquesPMA, BilanEndocrinienPMAFeminin, \
    BilanEndocrinienPMAMasculin, SpermogrammePMA, TentativePMA, TraitementPMA, SuiviTraitementPMA, TraitementValeurPMA, \
    Patient, Consultation
from apps.core.serializers import ListeChoixSerializer, TraitementPMASerializer
from apps.core.views.consultations.base import AjaxableResponseMixin, ConsultationCreateBase, ConsultationUpdateBase
from apps.core import utils


class InterrogatoirePMACreate(AjaxableResponseMixin, ConsultationCreateBase):
    permission_required = 'core.change_patient'
    template_name = 'core/interrogatoire_pma_form.html'
    model = InterrogatoirePMA
    form_class = InterrogatoirePMAForm
    success_url = reverse_lazy('accueil')
    titre = 'Interrogatoire PMA'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = self.titre
        listes = ListeChoix.objects.filter(formulaire='interrogatoire_pma')
        context['listes_choix_json'] = json.dumps(ListeChoixSerializer(listes, many=True).data)
        TentativesFormset = inlineformset_factory(InterrogatoirePMA, TentativesHistoriquesPMA,
                                                  form=TentativesHistoriquesPMAForm,
                                                  fields='__all__', extra=1, can_delete=True)
        if self.request.POST:
            context["tentatives_formset"] = TentativesFormset(self.request.POST)
        else:
            context["tentatives_formset"] = TentativesFormset()

        BilanEndocrinienFemininFormset = inlineformset_factory(InterrogatoirePMA, BilanEndocrinienPMAFeminin,
                                                  form=BilanEndocrinienPMAFemininForm,
                                                  fields='__all__', extra=1, can_delete=True)
        if self.request.POST:
            context["bilans_endocriniens_feminin_formset"] = BilanEndocrinienFemininFormset(self.request.POST)
        else:
            context["bilans_endocriniens_feminin_formset"] = BilanEndocrinienFemininFormset()

        BilanEndocrinienMasculinFormset = inlineformset_factory(InterrogatoirePMA, BilanEndocrinienPMAMasculin,
                                                  form=BilanEndocrinienPMAMasculinForm,
                                                  fields='__all__', extra=1, can_delete=True)
        if self.request.POST:
            context["bilans_endocriniens_masculin_formset"] = BilanEndocrinienMasculinFormset(self.request.POST)
        else:
            context["bilans_endocriniens_masculin_formset"] = BilanEndocrinienMasculinFormset()

        SpermogrammePMAFormset = inlineformset_factory(InterrogatoirePMA, SpermogrammePMA,
                                                  form=SpermogrammePMAForm,
                                                  fields='__all__', extra=1, can_delete=True)
        if self.request.POST:
            context["spermogramme_formset"] = SpermogrammePMAFormset(self.request.POST)
        else:
            context["spermogramme_formset"] = SpermogrammePMAFormset()

        return context

    def get_initial(self):
        init = super().get_initial()
        init['patient'] = self.kwargs['pk']
        init['praticien'] = self.request.user.profil
        patient = get_object_or_404(Patient, pk=self.kwargs['pk'])
        init['nom_conjoint'] = patient.nom_conjoint
        init['prenom_conjoint'] = patient.prenom_conjoint
        init['date_naissance_conjoint'] = patient.date_naissance_conjoint
        init['telephone_conjoint'] = patient.telephone_conjoint
        init['groupe_sanguin_conjoint'] = patient.groupe_sanguin_conjoint
        init['consanguinite_conjoint'] = patient.consanguinite_conjoint
        init['etat_sante_conjoint'] = patient.etat_sante_conjoint
        return init

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if utils.is_ajax(self.request):
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        context = self.get_context_data()
        data = {}
        tentatives_formset = context["tentatives_formset"]
        bilans_endocriniens_feminin_formset = context["bilans_endocriniens_feminin_formset"]
        bilans_endocriniens_masculin_formset = context["bilans_endocriniens_masculin_formset"]
        spermogramme_formset = context["spermogramme_formset"]
        if form.is_valid():
            with transaction.atomic():
                self.object = form.save()
                print('form valid')
                if tentatives_formset.is_valid():
                    print('tentatives_formset valid')
                    tentatives_formset.instance = self.object
                    tentatives_formset.save()
                if bilans_endocriniens_feminin_formset.is_valid():
                    print('bilans_endocriniens_feminin_formset valid')
                    bilans_endocriniens_feminin_formset.instance = self.object
                    bilans_endocriniens_feminin_formset.save()
                if bilans_endocriniens_masculin_formset.is_valid():
                    print('bilans_endocriniens_masculin_formset valid')
                    bilans_endocriniens_masculin_formset.instance = self.object
                    bilans_endocriniens_masculin_formset.save()
                if spermogramme_formset.is_valid():
                    print('spermogramme_formset valid')
                    spermogramme_formset.instance = self.object
                    spermogramme_formset.save()

            if utils.is_ajax(self.request):
                data = {
                    'id': self.object.pk,
                    'status': 'ok',
                    'date': self.object.date
                }
        else:
            data = {
                'errors': form.errors,
                'id': -1,
                'status': 'error'
            }

        response = super().form_valid(form)

        if utils.is_ajax(self.request):
            return JsonResponse(data)
        else:
            return response


class InterrogatoirePMAUpdate(AjaxableResponseMixin, ConsultationUpdateBase):
    permission_required = 'core.change_patient'
    template_name = 'core/interrogatoire_pma_form.html'
    model = InterrogatoirePMA
    form_class = InterrogatoirePMAForm
    success_url = reverse_lazy('accueil')
    titre = 'Interrogatoire PMA'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = self.titre
        listes = ListeChoix.objects.filter(formulaire='interrogatoire_pma')
        context['listes_choix_json'] = json.dumps(ListeChoixSerializer(listes, many=True).data)
        TentativesFormset = inlineformset_factory(InterrogatoirePMA, TentativesHistoriquesPMA,
                                                  form=TentativesHistoriquesPMAForm,
                                                  fields='__all__', extra=1, can_delete=True)
        if self.request.POST:
            context["tentatives_formset"] = TentativesFormset(self.request.POST, instance=self.object)
        else:
            context["tentatives_formset"] = TentativesFormset(instance=self.object)

        BilanEndocrinienFemininFormset = inlineformset_factory(InterrogatoirePMA, BilanEndocrinienPMAFeminin,
                                                  form=BilanEndocrinienPMAFemininForm,
                                                  fields='__all__', extra=1, can_delete=True)
        if self.request.POST:
            context["bilans_endocriniens_feminin_formset"] = BilanEndocrinienFemininFormset(self.request.POST, instance=self.object)
        else:
            context["bilans_endocriniens_feminin_formset"] = BilanEndocrinienFemininFormset(instance=self.object)

        BilanEndocrinienMasculinFormset = inlineformset_factory(InterrogatoirePMA, BilanEndocrinienPMAMasculin,
                                                  form=BilanEndocrinienPMAMasculinForm,
                                                  fields='__all__', extra=1, can_delete=True)
        if self.request.POST:
            context["bilans_endocriniens_masculin_formset"] = BilanEndocrinienMasculinFormset(self.request.POST, instance=self.object)
        else:
            context["bilans_endocriniens_masculin_formset"] = BilanEndocrinienMasculinFormset(instance=self.object)

        SpermogrammePMAFormset = inlineformset_factory(InterrogatoirePMA, SpermogrammePMA,
                                                  form=SpermogrammePMAForm,
                                                  fields='__all__', extra=1, can_delete=True)
        if self.request.POST:
            context["spermogramme_formset"] = SpermogrammePMAFormset(self.request.POST, instance=self.object)
        else:
            context["spermogramme_formset"] = SpermogrammePMAFormset(instance=self.object)

        return context

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if utils.is_ajax(self.request):
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        context = self.get_context_data()
        data = {}
        tentatives_formset = context["tentatives_formset"]
        bilans_endocriniens_feminin_formset = context["bilans_endocriniens_feminin_formset"]
        bilans_endocriniens_masculin_formset = context["bilans_endocriniens_masculin_formset"]
        spermogramme_formset = context["spermogramme_formset"]
        if form.is_valid():
            with transaction.atomic():
                self.object = form.save()
                print('form valid')
                if tentatives_formset.is_valid():
                    print('tentatives_formset valid')
                    tentatives_formset.instance = self.object
                    tentatives_formset.save()
                if bilans_endocriniens_feminin_formset.is_valid():
                    print('bilans_endocriniens_feminin_formset valid')
                    bilans_endocriniens_feminin_formset.instance = self.object
                    bilans_endocriniens_feminin_formset.save()
                if bilans_endocriniens_masculin_formset.is_valid():
                    print('bilans_endocriniens_masculin_formset valid')
                    bilans_endocriniens_masculin_formset.instance = self.object
                    bilans_endocriniens_masculin_formset.save()
                if spermogramme_formset.is_valid():
                    print('spermogramme_formset valid')
                    spermogramme_formset.instance = self.object
                    spermogramme_formset.save()

            if utils.is_ajax(self.request):
                data = {
                    'id': self.object.pk,
                    'status': 'ok',
                    'date': self.object.date
                }
        else:
            data = {
                'errors': form.errors,
                'id': self.object.pk,
                'status': 'error'
            }

        response = super().form_valid(form)

        if utils.is_ajax(self.request):
            return JsonResponse(data)
        else:
            return response

######################################################################################################

class TentativePMACreate(AjaxableResponseMixin, ConsultationCreateBase):
    permission_required = 'core.change_patient'
    template_name = 'core/tentative_pma_form.html'
    model = TentativePMA
    form_class = TentativePMAForm
    success_url = reverse_lazy('accueil')
    titre = 'Tentative PMA'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = self.titre
        listes = ListeChoix.objects.filter(formulaire='tentative_pma')
        context['listes_choix_json'] = json.dumps(ListeChoixSerializer(listes, many=True).data)

        traitements = TraitementPMA.objects.filter(compte=self.request.user.profil.compte)
        context['traitements'] = traitements
        #context['traitements_json'] = json.dumps(TraitementPMASerializer(traitements, many=True).data)

        SuiviTraitementFormset = inlineformset_factory(TentativePMA, SuiviTraitementPMA,
                                               formset=BaseSuiviTraitementCreateFormSet,
                                               fields='__all__', extra=21, can_delete=False)

        if self.request.POST:
            context["suivi_traitement_formset"] = SuiviTraitementFormset(self.request.POST)
        else:
            context["suivi_traitement_formset"] = SuiviTraitementFormset()

        return context

    def get_initial(self):
        init = super().get_initial()
        init['patient'] = self.kwargs['pk']
        init['praticien'] = self.request.user.profil
        return init

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if utils.is_ajax(self.request):
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        context = self.get_context_data()
        data = {}
        suivi_traitement_formset = context["suivi_traitement_formset"]
        if form.is_valid():
            with transaction.atomic():
                self.object = form.save()
                print('form valid')
                if suivi_traitement_formset.is_valid():
                    print('suivi_traitement_formset valid')
                    suivi_traitement_formset.instance = self.object
                    suivi_traitement_formset.save()

            if utils.is_ajax(self.request):
                data = {
                    'id': self.object.pk,
                    'status': 'ok',
                    'date': self.object.created_at
                }
        else:
            data = {
                'errors': form.errors,
                'id': -1,
                'status': 'error'
            }

        response = super().form_valid(form)

        if utils.is_ajax(self.request):
            return JsonResponse(data)
        else:
            return response


class TentativePMAUpdate(AjaxableResponseMixin, ConsultationUpdateBase):
    permission_required = 'core.change_patient'
    template_name = 'core/tentative_pma_form.html'
    model = TentativePMA
    form_class = TentativePMAForm
    success_url = reverse_lazy('accueil')
    titre = 'Tentative PMA'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = self.titre
        listes = ListeChoix.objects.filter(formulaire='tentative_pma')
        context['listes_choix_json'] = json.dumps(ListeChoixSerializer(listes, many=True).data)
        traitements = TraitementPMA.objects.filter(compte=self.request.user.profil.compte)
        context['traitements'] = traitements

        SuiviTraitementFormset = inlineformset_factory(TentativePMA, SuiviTraitementPMA,
                                               formset=BaseSuiviTraitementUpdateFormSet,
                                               fields='__all__', extra=0, can_delete=False)

        if self.request.POST:
            context["suivi_traitement_formset"] = SuiviTraitementFormset(self.request.POST, instance=self.object)
        else:
            context["suivi_traitement_formset"] = SuiviTraitementFormset(instance=self.object)

        return context

    def get_initial(self):
        init = super().get_initial()
        init['patient'] = self.kwargs['pk']
        init['praticien'] = self.request.user.profil
        return init

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if utils.is_ajax(self.request):
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        print('*****************************')
        print(self.request.method)
        context = self.get_context_data()
        data = {}
        suivi_traitement_formset = context["suivi_traitement_formset"]
        if form.is_valid():
            with transaction.atomic():
                self.object = form.save()
                print('form valid')
                if suivi_traitement_formset.is_valid():
                    print('suivi_traitement_formset valid')
                    suivi_traitement_formset.instance = self.object
                    suivi_traitement_formset.save()
                else:
                    print('suivi_traitement_formset not valid')
                    print(suivi_traitement_formset.errors)

            if utils.is_ajax(self.request):
                data = {
                    'id': self.object.pk,
                    'status': 'ok',
                    'date': self.object.updated_at
                }
        else:
            data = {
                'errors': form.errors,
                'id': self.object.pk,
                'status': 'error'
            }

        response = super().form_valid(form)

        if utils.is_ajax(self.request):
            return JsonResponse(data)
        else:
            return response


class TraitementPMAList(PermissionRequiredMixin, ListView):
    model = TraitementPMA
    template_name = 'core/traitement_pma_list.html'
    permission_required = 'core.view_patient'

    def get_queryset(self):
        return TraitementPMA.objects.filter(compte=self.request.user.profil.compte)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        traitements_json = TraitementPMASerializer(self.get_queryset(), many=True)
        context['traitements_json'] = json.dumps(traitements_json.data)
        return context


class TraitementPMACreate(PermissionRequiredMixin, CreateView):
    model = TraitementPMA
    form_class = TraitementPMAForm
    template_name = 'core/traitement_pma_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('traitements_pma_list')


class TraitementPMAUpdate(PermissionRequiredMixin, UpdateView):
    model = TraitementPMA
    form_class = TraitementPMAForm
    template_name = 'core/traitement_pma_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('traitements_pma_list')


@login_required
@permission_required('core.change_patient', raise_exception=True)
def supprimer_traitement(request, pk):
    query = get_object_or_404(TraitementPMA, pk=pk)
    query.delete()
    return redirect(reverse("traitements_pma_list"))


@login_required
@permission_required('core.view_patient', raise_exception=True)
def rechercher_traitement(request):
    objects = TraitementPMA.objects.filter(compte=request.user.profil.compte)
    if request.body is not None:
        try:
            body = json.loads(request.body)
            query = body['libelle']
            # Typeahead autocomplete request
            if query is not None:
                filtered = objects.filter(libelle__icontains=query).order_by('libelle')[:20]
                resp = TraitementPMASerializer(filtered, many=True)
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
    objs_json = TraitementPMASerializer(objs, many=True)
    resp = {
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': filtered_count,
        'data': objs_json.data
    }
    return JsonResponse(resp)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def creer_tentative(request, pk):
    nb_traitements = 7
    nb_jours = 21
    patient = get_object_or_404(Patient, id=pk)
    tentative = TentativePMA(patient=patient, praticien=request.user.profil)
    tentative.save()
    for s in range(0, nb_jours+1):
        suivi = SuiviTraitementPMA(tentative=tentative)
        suivi.save()
        for rang in range(1, nb_traitements+1):
            tv = TraitementValeurPMA(suivi=suivi, rang=rang)
            tv.save()
    return redirect(reverse("tentative_pma_modifier", kwargs={'pk': tentative.pk}))


class TentativePMACloture(BSModalUpdateView):
    template_name = 'core/tentative_pma_cloture_form.html'
    permission_required = 'core.change_patient'
    form_class = TentativePMAClotureForm
    success_message = 'Tentative PMA cloturée avec succès.'
    success_url = reverse_lazy('accueil')
    model = TentativePMA

    def get_initial(self):
        init = super().get_initial()
        init['encours'] = False
        return init

    def get_success_url(self):
        return self.request.GET['next']


@login_required
@permission_required('core.change_patient', raise_exception=True)
def supprimer_tentative(request, pk):
    tentative = get_object_or_404(TentativePMA, pk=pk)
    patient_pk = tentative.patient.pk
    tentative.delete()
    return redirect(reverse("patient_afficher", kwargs={'pk': patient_pk}) + '#tab-pma')


@login_required
@permission_required('core.view_patient', raise_exception=True)
def rechercher_tentative(request, consultation_pk):
    # Chercher la tentative PMA correspondant à la consultation
    print("Recherche consultation", consultation_pk)
    consult = get_object_or_404(Consultation, pk=consultation_pk)
    print("Consultation", consult)
    tentatives = TentativePMA.objects.filter(created_at__lte=consult.created_at, updated_at__gte=consult.created_at)
    if len(tentatives) != 0:
        data = {'tentative': tentatives[0].id}
    else:
        data = {'tentative': -1}

    return JsonResponse(data)
