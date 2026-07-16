import json

from datetime import date

from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from apps.core.forms import *
from apps.core.models import *
from apps.core.serializers import GrossesseSerializer, ListeChoixSerializer, TemplateEditionSerializer
from apps.core.services.patients import get_obs_measure_history, get_all_obs_measure_history
from apps.core.views import patients
from apps.core.views.consultations.base import AjaxableResponseMixin, ConsultationUpdateBase, ConsultationCreateBase
from apps.core import utils


class ConsultationObstetriqueCreateBase(ConsultationCreateBase):
    success_url = reverse_lazy('accueil')
    titre = 'Consultation obstétrique'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editor_only'] = False
        patient = context['patient']
        grossesse = patient.grossesse_set.filter(encours=True)
        if len(grossesse):
            context['grossesse_encours_json'] = json.dumps(GrossesseSerializer(grossesse[0]).data)
            context['grossesse_encours'] = grossesse[0]

        if self.request.POST:
            context["foetus"] = DonneesFoetusFormset(self.request.POST)
        else:
            context["foetus"] = DonneesFoetusFormset()

        listes = ListeChoix.objects.filter(Q(formulaire='consultation_obs_foetus') | Q(formulaire='consultation_obs'))
        context['listes_choix_json'] = json.dumps(ListeChoixSerializer(listes, many=True).data)

        return context

    def get_initial(self):
        init = super().get_initial()
        init['patient'] = self.kwargs['pk']
        init['praticien'] = self.request.user.profil
        patient = get_object_or_404(Patient, pk=self.kwargs['pk'])
        grossesse = patient.grossesse_set.filter(encours=True)
        if len(grossesse):
            init['grossesse'] = grossesse[0].pk

        if patient.mesures_jour:
            init['poids'] = patient.mesures_jour.poids
            init['ta'] = patient.mesures_jour.ta
            init['temperature'] = patient.mesures_jour.temperature
            init['gly'] = patient.mesures_jour.gly
        return init

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if utils.is_ajax(self.request):
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        context = self.get_context_data()
        foetus_formset = context['foetus']
        data = {}
        if form.is_valid():
            with transaction.atomic():
                self.object = form.save()
                patient = self.object.patient
                if self.object.poids:
                    patient.poids = self.object.poids # mise à jour du poids
                    patient.save()
                try:
                    if foetus_formset.is_valid():
                        foetus_formset.instance = self.object
                        foetus_formset.save()
                except ValidationError:
                    print('Foetus data Formset Validation error')

                if utils.is_ajax(self.request):
                    data = {
                        'consultation_pk': self.object.pk,
                        'date': self.object.date,
                        'status': 'ok'
                    }
        else:
            data = {
                'errors': form.errors,
                'consultation_pk': -1,
                'status': 'error'
            }

        response = super().form_valid(form)
        if utils.is_ajax(self.request):
            return JsonResponse(data)
        else:
            return response


class ConsultationObstetriqueUpdateBase(ConsultationUpdateBase):
    success_url = reverse_lazy('accueil')
    titre = 'Consultation obstétrique'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editor_only'] = False
        context['motif'] = self.object.motif
        if self.request.POST:
            context["foetus"] = DonneesFoetusFormset(self.request.POST, instance=self.object)
        else:
            context["foetus"] = DonneesFoetusFormset(instance=self.object)

        listes = ListeChoix.objects.filter(Q(formulaire='consultation_obs_foetus') | Q(formulaire='consultation_obs'))
        context['listes_choix_json'] = json.dumps(ListeChoixSerializer(listes, many=True).data)

        return context

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if utils.is_ajax(self.request):
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        context = self.get_context_data()
        foetus_formset = context['foetus']
        data = {}
        if form.is_valid():
            with transaction.atomic():
                self.object = form.save()
                patient = self.object.patient
                if self.object.poids:
                    patient.poids = self.object.poids # mise à jour du poids
                    patient.save()
                try:
                    if foetus_formset.is_valid():
                        foetus_formset.instance = self.object
                        lst = foetus_formset.save(commit=True)
                        for o in lst:
                            print('Foetus ', o.id)
                except ValidationError:
                    print('Foetus data Formset Validation error')

                foetus_ids = []
                for f in self.object.donneesfoetus_set.all():
                    foetus_ids.append(str(f.id))

                if utils.is_ajax(self.request):
                    data = {
                        'consultation_pk': self.object.pk,
                        'foetus_pk': ",".join(foetus_ids),
                        'date': self.object.date,
                        'status': 'ok'
                    }
        else:
            data = {
                'errors': form.errors,
                'consultation_pk': -1,
                'status': 'error'
            }

        response = super().form_valid(form)
        if utils.is_ajax(self.request):
            return JsonResponse(data)
        else:
            return response


# -----------------------------------------------------------------------------------------------------
class ConsultationEcho11SACreate(ConsultationObstetriqueCreateBase):
    template_name = 'core/consultation_obs_echo_11SA_form.html'
    model = ConsultationEcho11SA
    form_class = ConsultationEcho11SAForm
    titre = 'Examen du 1er trimestre (< 11 SA)'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        motif = MotifConsultation.objects.filter(code='obs_echo_11SA')
        context['motif'] = motif[0]
        context['doublon_consultation'] = context['patient'].check_doublon_consultation(motif=context['motif'],
                                                                                        date=date.today())
        return context


class ConsultationEcho11SAUpdate(ConsultationObstetriqueUpdateBase):
    template_name = 'core/consultation_obs_echo_11SA_form.html'
    model = ConsultationEcho11SA
    form_class = ConsultationEcho11SAForm
    titre = 'Examen du 1er trimestre (< 11 SA)'


# -----------------------------------------------------------------------------------------------------
class ConsultationEchoPremierTrimestreCreate(ConsultationObstetriqueCreateBase):
    template_name = 'core/consultation_obs_echo_premier_trimestre_form.html'
    model = ConsultationEchoPremierTrimestre
    form_class = ConsultationEchoPremierTrimestreForm
    titre = 'Examen du 1er trimestre'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        motif = MotifConsultation.objects.filter(code='obs_echo_trimestre_1')
        context['motif'] = motif[0]
        context['doublon_consultation'] = context['patient'].check_doublon_consultation(motif=context['motif'],
                                                                                        date=date.today())
        templates = TemplateEdition.objects.filter(compte=self.request.user.profil.compte,
                                                   motif_consultation=motif[0])
        context['templates'] = templates
        templates_json = TemplateEditionSerializer(templates, many=True)
        context['templates_json'] = json.dumps(templates_json.data)
        return context


class ConsultationEchoPremierTrimestreUpdate(ConsultationObstetriqueUpdateBase):
    template_name = 'core/consultation_obs_echo_premier_trimestre_form.html'
    model = ConsultationEchoPremierTrimestre
    form_class = ConsultationEchoPremierTrimestreForm
    titre = 'Examen du 1er trimestre'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['motif'] = self.object.motif
        templates = TemplateEdition.objects.filter(compte=self.request.user.profil.compte,
                                                   motif_consultation=self.object.motif)
        context['templates'] = templates
        templates_json = TemplateEditionSerializer(templates, many=True)
        context['templates_json'] = json.dumps(templates_json.data)
        return context


# -----------------------------------------------------------------------------------------------------
class ConsultationEchoDeuxiemeTrimestreCreate(ConsultationObstetriqueCreateBase):
    template_name = 'core/consultation_obs_echo_deuxieme_trimestre_form.html'
    model = ConsultationEchoDeuxiemeTrimestre
    form_class = ConsultationEchoDeuxiemeTrimestreForm
    titre = 'Examen du 2ème trimestre'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        motif = MotifConsultation.objects.filter(code='obs_echo_trimestre_2')
        context['motif'] = motif[0]
        context['doublon_consultation'] = context['patient'].check_doublon_consultation(motif=context['motif'],
                                                                                        date=date.today())
        templates = TemplateEdition.objects.filter(compte=self.request.user.profil.compte,
                                                   motif_consultation=motif[0])
        context['templates'] = templates
        templates_json = TemplateEditionSerializer(templates, many=True)
        context['templates_json'] = json.dumps(templates_json.data)
        return context


class ConsultationEchoDeuxiemeTrimestreUpdate(ConsultationObstetriqueUpdateBase):
    template_name = 'core/consultation_obs_echo_deuxieme_trimestre_form.html'
    model = ConsultationEchoDeuxiemeTrimestre
    form_class = ConsultationEchoDeuxiemeTrimestreForm
    titre = 'Examen du 2ème trimestre'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['motif'] = self.object.motif
        templates = TemplateEdition.objects.filter(compte=self.request.user.profil.compte,
                                                   motif_consultation=self.object.motif)
        context['templates'] = templates
        templates_json = TemplateEditionSerializer(templates, many=True)
        context['templates_json'] = json.dumps(templates_json.data)
        return context


# -----------------------------------------------------------------------------------------------------
class ConsultationEchoTroisiemeTrimestreCreate(ConsultationObstetriqueCreateBase):
    template_name = 'core/consultation_obs_echo_troisieme_trimestre_form.html'
    model = ConsultationEchoTroisiemeTrimestre
    form_class = ConsultationEchoTroisiemeTrimestreForm
    titre = 'Examen du 3ème trimestre'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        motif = MotifConsultation.objects.filter(code='obs_echo_trimestre_3')
        context['motif'] = motif[0]
        context['doublon_consultation'] = context['patient'].check_doublon_consultation(motif=context['motif'],
                                                                                        date=date.today())
        templates = TemplateEdition.objects.filter(compte=self.request.user.profil.compte,
                                                   motif_consultation=motif[0])
        context['templates'] = templates
        templates_json = TemplateEditionSerializer(templates, many=True)
        context['templates_json'] = json.dumps(templates_json.data)
        return context


class ConsultationEchoTroisiemeTrimestreUpdate(ConsultationObstetriqueUpdateBase):
    template_name = 'core/consultation_obs_echo_troisieme_trimestre_form.html'
    model = ConsultationEchoTroisiemeTrimestre
    form_class = ConsultationEchoTroisiemeTrimestreForm
    titre = 'Examen du 3ème trimestre'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['motif'] = self.object.motif
        templates = TemplateEdition.objects.filter(compte=self.request.user.profil.compte,
                                                   motif_consultation=self.object.motif)
        context['templates'] = templates
        templates_json = TemplateEditionSerializer(templates, many=True)
        context['templates_json'] = json.dumps(templates_json.data)
        return context


# -----------------------------------------------------------------------------------------------------
class ConsultationEchoCroissanceCreate(ConsultationObstetriqueCreateBase):
    template_name = 'core/consultation_obs_echo_croissance_form.html'
    model = ConsultationEchoCroissance
    form_class = ConsultationEchoCroissanceForm
    titre = 'Echo de croissance'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        motif = MotifConsultation.objects.filter(code='obs_echo_croissance')
        context['motif'] = motif[0]
        context['doublon_consultation'] = context['patient'].check_doublon_consultation(motif=context['motif'],
                                                                                        date=date.today())
        templates = TemplateEdition.objects.filter(compte=self.request.user.profil.compte,
                                                   motif_consultation=motif[0])
        context['templates'] = templates
        templates_json = TemplateEditionSerializer(templates, many=True)
        context['templates_json'] = json.dumps(templates_json.data)
        return context


class ConsultationEchoCroissanceUpdate(ConsultationObstetriqueUpdateBase):
    template_name = 'core/consultation_obs_echo_croissance_form.html'
    model = ConsultationEchoCroissance
    form_class = ConsultationEchoCroissanceForm
    titre = 'Echo de croissance'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['motif'] = self.object.motif
        templates = TemplateEdition.objects.filter(compte=self.request.user.profil.compte,
                                                   motif_consultation=self.object.motif)
        context['templates'] = templates
        templates_json = TemplateEditionSerializer(templates, many=True)
        context['templates_json'] = json.dumps(templates_json.data)
        return context


# -----------------------------------------------------------------------------------------------------
class ConsultationEchoColCreate(ConsultationObstetriqueCreateBase):
    template_name = 'core/consultation_obs_echo_col_form.html'
    model = ConsultationEchoCol
    form_class = ConsultationEchoColForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        motif = MotifConsultation.objects.filter(code='obs_echo_col')
        context['motif'] = motif[0]
        context['doublon_consultation'] = context['patient'].check_doublon_consultation(motif=context['motif'],
                                                                                        date=date.today())
        return context


class ConsultationEchoColUpdate(ConsultationObstetriqueUpdateBase):
    template_name = 'core/consultation_obs_echo_col_form.html'
    model = ConsultationEchoCol
    form_class = ConsultationEchoColForm


# -----------------------------------------------------------------------------------------------------
class ConsultationEchoCardiofoetaleCreate(ConsultationObstetriqueCreateBase):
    template_name = 'core/consultation_obs_echo_cardiofoetale_form.html'
    model = ConsultationEchoCardiofoetale
    form_class = ConsultationEchoCardiofoetaleForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        motif = MotifConsultation.objects.filter(code='obs_echo_cardiofoetale')
        context['motif'] = motif[0]
        context['doublon_consultation'] = context['patient'].check_doublon_consultation(motif=context['motif'],
                                                                                        date=date.today())
        return context


class ConsultationEchoCardiofoetaleUpdate(ConsultationObstetriqueUpdateBase):
    template_name = 'core/consultation_obs_echo_cardiofoetale_form.html'
    model = ConsultationEchoCardiofoetale
    form_class = ConsultationEchoCardiofoetaleForm


# -----------------------------------------------------------------------------------------------------
class ConsultationGrossesseCreate(ConsultationObstetriqueCreateBase):
    template_name = 'core/consultation_obs_grossesse_form.html'
    model = ConsultationGrossesse
    form_class = ConsultationGrossesseForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        motif = MotifConsultation.objects.filter(code='obs_grossesse')
        context['motif'] = motif[0]
        context['doublon_consultation'] = context['patient'].check_doublon_consultation(motif=context['motif'],
                                                                                        date=date.today())
        return context


class ConsultationGrossesseUpdate(ConsultationObstetriqueUpdateBase):
    template_name = 'core/consultation_obs_grossesse_form.html'
    model = ConsultationGrossesse
    form_class = ConsultationGrossesseForm

# -----------------------------------------------------------------------------------------------------
