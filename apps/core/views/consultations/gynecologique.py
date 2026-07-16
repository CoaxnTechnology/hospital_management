import json
from datetime import datetime, date

from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView

from apps.core.forms import ConsultationGynecologiqueForm, ConsultationColposcopieForm, \
    ConsultationEchoPelvienneForm, MyomeForm
from apps.core.models import Patient, MotifConsultation, ConsultationGynecologique, \
    ConsultationColposcopie, ConsultationEchoPelvienne, ListeChoix, DossierFichiersPatient, FichierPatient, Myome
from apps.core.serializers import ListeChoixSerializer
from apps.core.views import patients
from apps.core.views.consultations.base import AjaxableResponseMixin, ConsultationCreateBase, ConsultationUpdateBase
from apps.core import utils


class ConsultationGynecologiqueCreate(AjaxableResponseMixin, ConsultationCreateBase):
    template_name = 'core/consultation_gynecologique_form.html'
    model = ConsultationGynecologique
    form_class = ConsultationGynecologiqueForm
    success_url = reverse_lazy('accueil')
    titre = 'Consultation gynécologique'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editor_only'] = False
        motif = MotifConsultation.objects.filter(code='gynecologique-defaut')
        context['motif'] = motif[0]
        context['titre'] = self.titre
        MyomeFormset = inlineformset_factory(ConsultationGynecologique, Myome, form=MyomeForm, fields='__all__', extra=1, can_delete=True)
        if self.request.POST:
            context["myomes_formset"] = MyomeFormset(self.request.POST)
        else:
            context["myomes_formset"] = MyomeFormset()

        figo = ListeChoix.objects.filter(champ='type_figo')
        context['types_figo'] = json.dumps(ListeChoixSerializer(figo, many=True).data)
        listes = ListeChoix.objects.filter(formulaire='consultation_gynecologique')
        context['listes_choix_json'] = json.dumps(ListeChoixSerializer(listes, many=True).data)
        context['doublon_consultation'] = context['patient'].check_doublon_consultation(motif=context['motif'],
                                                                                        date=date.today())
        return context

    def get_initial(self):
        init = super().get_initial()
        init['patient'] = self.kwargs['pk']
        init['praticien'] = self.request.user.profil
        patient = get_object_or_404(Patient, pk=self.kwargs['pk'])
        if patient.mesures_jour:
            init['poids'] = patient.mesures_jour.poids
            init['ta'] = patient.mesures_jour.ta
            init['temperature'] = patient.mesures_jour.temperature
            init['gly'] = patient.mesures_jour.gly
        return init

    def form_valid(self, form):
        context = self.get_context_data()
        data = {}
        myomes_formset = context["myomes_formset"]
        if form.is_valid():
            with transaction.atomic():
                try:
                    self.object = form.save()
                except Exception as x:
                    print(x)
                print('form valid')
                if myomes_formset.is_valid():
                    print('formset valid')
                    myomes_formset.instance = self.object
                    myomes_formset.save()

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


class ConsultationGynecologiqueUpdate(AjaxableResponseMixin, ConsultationUpdateBase):
    template_name = 'core/consultation_gynecologique_form.html'
    model = ConsultationGynecologique
    form_class = ConsultationGynecologiqueForm
    success_url = reverse_lazy('accueil')
    titre = 'Consultation gynécologique'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editor_only'] = False
        context['motif'] = self.object.motif
        extra = 1
        if self.object.myome_set.count() > 0:
            extra = 0
        MyomeFormset = inlineformset_factory(ConsultationGynecologique, Myome,
                                             form=MyomeForm, fields='__all__',
                                             extra=extra, can_delete=True)
        if self.request.POST:
            context["myomes_formset"] = MyomeFormset(self.request.POST, instance=self.object)
        else:
            context["myomes_formset"] = MyomeFormset(instance=self.object)
        figo = ListeChoix.objects.filter(champ='type_figo')
        context['types_figo'] = json.dumps(ListeChoixSerializer(figo, many=True).data)
        listes = ListeChoix.objects.filter(formulaire='consultation_gynecologique')
        context['listes_choix_json'] = json.dumps(ListeChoixSerializer(listes, many=True).data)
        return context

    def form_valid(self, form):
        print('form_valid called')
        context = self.get_context_data()
        data = {}
        myomes_formset = context["myomes_formset"]
        if form.is_valid():
            print('form valid')
            self.object = form.save()
            if myomes_formset.is_valid():
                print('formset valid')
                myomes_formset.instance = self.object
                myomes_formset.save()

            if utils.is_ajax(self.request):
                data = {
                    'consultation_pk': self.object.pk,
                    'date': self.object.date,
                    'status': 'ok'
                }
        else:
            data = {
                'errors': form.errors,
                'consultation_pk': self.object.pk,
                'status': 'error'
            }

        response = super().form_valid(form)

        if utils.is_ajax(self.request):
            return JsonResponse(data)
        else:
            return response


class ConsultationColposcopieCreate(AjaxableResponseMixin, ConsultationCreateBase):
    template_name = 'core/consultation_colposcopie_form.html'
    model = ConsultationColposcopie
    form_class = ConsultationColposcopieForm
    success_url = reverse_lazy('accueil')
    titre = 'Colposcopie'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editor_only'] = False
        motif = MotifConsultation.objects.filter(code='colposcopie')
        context['motif'] = motif[0]
        listes = ListeChoix.objects.filter(formulaire='consultation_colposcopie')
        context['listes_choix_json'] = json.dumps(ListeChoixSerializer(listes, many=True).data)
        context['doublon_consultation'] = context['patient'].check_doublon_consultation(motif=context['motif'],
                                                                                        date=date.today())
        return context

    def get_initial(self):
        init = super().get_initial()
        init['patient'] = self.kwargs['pk']
        init['praticien'] = self.request.user.profil
        return init


class ConsultationColposcopieUpdate(AjaxableResponseMixin, ConsultationUpdateBase):
    template_name = 'core/consultation_colposcopie_form.html'
    model = ConsultationColposcopie
    form_class = ConsultationColposcopieForm
    success_url = reverse_lazy('accueil')
    titre = 'Colposcopie'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editor_only'] = False
        context['motif'] = self.object.motif
        listes = ListeChoix.objects.filter(formulaire='consultation_colposcopie')
        context['listes_choix_json'] = json.dumps(ListeChoixSerializer(listes, many=True).data)
        return context


class ConsultationEchoPelvienneCreate(ConsultationCreateBase):
    template_name = 'core/consultation_echo_pelvienne_form.html'
    model = ConsultationEchoPelvienne
    form_class = ConsultationEchoPelvienneForm
    success_url = reverse_lazy('accueil')
    titre = 'Echo pelvienne'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editor_only'] = False
        motif = MotifConsultation.objects.filter(code='echo-pelvienne')
        context['motif'] = motif[0]
        MyomeFormset = inlineformset_factory(ConsultationEchoPelvienne, Myome, form=MyomeForm, fields='__all__', extra=1, can_delete=True)
        if self.request.POST:
            context["myomes_formset"] = MyomeFormset(self.request.POST)
        else:
            context["myomes_formset"] = MyomeFormset()

        figo = ListeChoix.objects.filter(champ='type_figo')
        context['types_figo'] = json.dumps(ListeChoixSerializer(figo, many=True).data)
        listes = ListeChoix.objects.filter(formulaire='consultation_echo_pelvienne')
        context['listes_choix_json'] = json.dumps(ListeChoixSerializer(listes, many=True).data)
        context['doublon_consultation'] = context['patient'].check_doublon_consultation(motif=context['motif'],
                                                                                        date=date.today())
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
        myomes_formset = context["myomes_formset"]
        if form.is_valid():
            with transaction.atomic():
                self.object = form.save()
                print('form valid')
                if myomes_formset.is_valid():
                    print('formset valid')
                    myomes_formset.instance = self.object
                    myomes_formset.save()

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


class ConsultationEchoPelvienneUpdate(AjaxableResponseMixin, ConsultationUpdateBase):
    template_name = 'core/consultation_echo_pelvienne_form.html'
    model = ConsultationEchoPelvienne
    form_class = ConsultationEchoPelvienneForm
    success_url = reverse_lazy('accueil')
    titre = 'Echo pelvienne'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editor_only'] = False
        context['motif'] = self.object.motif
        extra = 1
        if self.object.myome_set.count() > 0:
            extra = 0
        MyomeFormset = inlineformset_factory(ConsultationEchoPelvienne, Myome,
                                             form=MyomeForm, fields='__all__',
                                             extra=extra, can_delete=True)
        if self.request.POST:
            context["myomes_formset"] = MyomeFormset(self.request.POST, instance=self.object)
        else:
            context["myomes_formset"] = MyomeFormset(instance=self.object)
        figo = ListeChoix.objects.filter(champ='type_figo')
        context['types_figo'] = json.dumps(ListeChoixSerializer(figo, many=True).data)
        listes = ListeChoix.objects.filter(formulaire='consultation_echo_pelvienne')
        context['listes_choix_json'] = json.dumps(ListeChoixSerializer(listes, many=True).data)
        return context

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if utils.is_ajax(self.request):
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        print('form_valid called')
        context = self.get_context_data()
        data = {}
        myomes_formset = context["myomes_formset"]
        if form.is_valid():
            print('form valid')
            self.object = form.save()
            if myomes_formset.is_valid():
                print('formset valid')
                myomes_formset.instance = self.object
                myomes_formset.save()

            if utils.is_ajax(self.request):
                data = {
                    'consultation_pk': self.object.pk,
                    'date': self.object.date,
                    'status': 'ok'
                }
        else:
            data = {
                'errors': form.errors,
                'consultation_pk': self.object.pk,
                'status': 'error'
            }

        response = super().form_valid(form)

        if utils.is_ajax(self.request):
            return JsonResponse(data)
        else:
            return response
