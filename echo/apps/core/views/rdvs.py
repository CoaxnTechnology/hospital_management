import datetime as dt
import json

from dateutil.parser import *
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core import serializers
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView
from datetimerange import DateTimeRange

from apps.core.data import adresses
from apps.core.forms import RdvForm, RdvDispoForm, AbsenceMedecinForm
from apps.core.models import Rdv, Patient, Praticien, AbsenceMedecin, MotifAbsence, ProgrammeOperatoire
from apps.core.serializers import PatientSerializer, DateTimeEncoder, PraticienSerializer, MotifAbsenceSerializer, \
    ProgrammeOperatoireSerializer
from apps.core.services.rdvs import *


class RdvList(PermissionRequiredMixin, View):
    permission_required = 'core.view_rdv'
    template_name = 'core/rdv_calendrier.html'

    def get(self, request):
        # , debut__gte=dt.date.today()) \
        qs = Rdv.objects.filter(compte=self.request.user.profil.compte) \
            .select_related('compte') \
            .select_related('motif') \
            .select_related('patient') \
            .prefetch_related('praticien') \
            .prefetch_related('praticien__user')
        data = serializers.serialize('json', list(qs), use_natural_foreign_keys=True)
        absence = AbsenceMedecin.objects.filter(praticien__compte=self.request.user.profil.compte)
        programme_operatoires = ProgrammeOperatoire.objects.filter(compte=self.request.user.profil.compte) \
            .select_related('patient') \
            .select_related('lieu_accouchement')

        data_absence = serializers.serialize('json', list(absence), use_natural_foreign_keys=True)
        data_programme = json.dumps(
            ProgrammeOperatoireSerializer(programme_operatoires, many=True).data)

        return render(request, self.template_name,
                      {'object_list': data, 'absence_list': data_absence, 'programme_operatoire': data_programme})


class RdvCreate(PermissionRequiredMixin, CreateView):
    model = Rdv
    form_class = RdvForm
    template_name = 'core/rdv_form_dialog.html'
    permission_required = 'core.add_rdv'
    success_url = reverse_lazy('fermer_fenetre')

    def get_context_data(self, **kwargs):
        context = super(RdvCreate, self).get_context_data(**kwargs)
        pays = "Tunisie"
        if self.request.user.profil.compte.adresse and self.request.user.profil.compte.adresse.pays:
            pays = self.request.user.profil.compte.adresse.pays
        context['codes_postaux'] = adresses.codes_postaux_json(pays)
        return context

    def get_initial(self):
        initial_base = super(RdvCreate, self).get_initial()
        initial_base['motif'] = 1
        initial_base['praticien'] = self.request.user.profil.compte.parametrescompte.praticien_defaut
        if 'debut' in self.request.GET:
            debut = self.request.GET['debut'].replace('%2b', '+')
            fin = self.request.GET['fin'].replace('%2b', '+')
            initial_base['date_debut'] = parse(debut)
            initial_base['heure_debut'] = parse(debut).strftime("%H:%M")
            initial_base['heure_fin'] = parse(fin).strftime("%H:%M")
        return initial_base

    def get_form_kwargs(self):
        kwargs = super(RdvCreate, self).get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def form_valid(self, form):
        if form.is_valid():
            debut = dt.datetime.combine(form.cleaned_data['date_debut'], form.cleaned_data['heure_debut'])
            fin = dt.datetime.combine(form.cleaned_data['date_debut'], form.cleaned_data['heure_fin'])
            # if debut < dt.datetime.now():
            #    form.add_error('heure_debut', "La date sélectionnée est dans le passé")
            #    return super().form_invalid(form)

            if debut > fin:
                form.add_error('heure_fin', "L'heure de fin doit être ultérieure à l'heure de début")
                return super().form_invalid(form)

            rdvs_meme_jour = Rdv.objects.filter(debut__day=debut.day, debut__month=debut.month, debut__year=debut.year)
            range = DateTimeRange(debut + dt.timedelta(seconds=30), fin - dt.timedelta(seconds=30))
            # print('Rdv jour: ', rdvs_meme_jour)
            for rdv in rdvs_meme_jour:
                range2 = DateTimeRange(rdv.debut, rdv.fin)
                if range.is_intersection(range2) and rdv.statut != '10':
                    form.add_error('heure_debut', "Un autre rendez-vous est planifié à la même heure")
                    return super().form_invalid(form)
            operation_meme_praticien = ProgrammeOperatoire.objects.filter(praticien=form.cleaned_data['praticien'])
            for operation in operation_meme_praticien:
                range2 = DateTimeRange(operation.debut, operation.fin)
                if range.is_intersection(range2):
                    form.add_error('praticien', "le praticien à un programme opératoire dans cet intervalle de date")
                    return super().form_invalid(form)
            self.object = form.save(commit=False)
            self.object.debut = debut
            self.object.fin = fin
            if form.cleaned_data['patient'] is not None:
                patient_pk = form.cleaned_data['patient']
                # print('Association au Patient', patient_pk)
                patient = get_object_or_404(Patient, pk=patient_pk)
                self.object.patient = patient
            self.object.save()
            return super().form_valid(form)


class RdvUpdate(PermissionRequiredMixin, UpdateView):
    model = Rdv
    form_class = RdvForm
    template_name = 'core/rdv_form_dialog.html'
    permission_required = 'core.change_rdv'
    success_url = reverse_lazy('fermer_fenetre')

    def get_context_data(self, **kwargs):
        context = super(RdvUpdate, self).get_context_data(**kwargs)
        pays = "Tunisie"
        if self.request.user.profil.compte.adresse and self.request.user.profil.compte.adresse.pays:
            pays = self.request.user.profil.compte.adresse.pays
        context['codes_postaux'] = adresses.codes_postaux_json(pays)
        context['statuts_confirmables'] = ['1', '10']
        return context

    def get_initial(self):
        initial_base = super(RdvUpdate, self).get_initial()
        initial_base['date_debut'] = self.object.debut
        initial_base['heure_debut'] = self.object.debut.strftime("%H:%M")
        initial_base['heure_fin'] = self.object.fin.strftime("%H:%M")
        return initial_base

    def get_form_kwargs(self):
        kwargs = super(RdvUpdate, self).get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def form_valid(self, form):
        context = self.get_context_data()
        if form.is_valid():
            ancien_debut = self.object.debut
            debut = dt.datetime.combine(form.cleaned_data['date_debut'], form.cleaned_data['heure_debut'])
            fin = dt.datetime.combine(form.cleaned_data['date_debut'], form.cleaned_data['heure_fin'])
            # if debut < dt.datetime.now():
            #    form.add_error('heure_debut', "La date sélectionnée est dans le passé")
            #    return super().form_invalid(form)
            if debut > fin:
                form.add_error('heure_fin', "L'heure de fin doit être ultérieure à l'heure de début")
                return super().form_invalid(form)

            rdvs_meme_jour = Rdv.objects.filter(debut__day=debut.day, debut__month=debut.month, debut__year=debut.year)
            range = DateTimeRange(debut + dt.timedelta(seconds=30), fin - dt.timedelta(seconds=30))
            # print('Rdv jour: ', rdvs_meme_jour)
            for rdv in rdvs_meme_jour:
                range2 = DateTimeRange(rdv.debut, rdv.fin)
                # Verifier qu'il n'y a pas un autre rdv planifié aux mêmes horaires
                if range.is_intersection(range2) and self.object.pk != rdv.pk and rdv.statut != '10':
                    form.add_error('heure_debut', "Un autre rendez-vous est planifié à la même heure")
                    return super().form_invalid(form)

            self.object = form.save(commit=False)
            self.object.debut = debut
            if ancien_debut != debut:
                self.object.ancien_debut = ancien_debut
            self.object.fin = fin
            self.object.statut = 1
            if form.cleaned_data['patient'] is not None:
                patient_pk = form.cleaned_data['patient']
                print('Association au Patient', patient_pk)
                patient = get_object_or_404(Patient, pk=patient_pk)
                self.object.patient = patient
            self.object.save()

        return super().form_valid(form)


@login_required
@permission_required('core.delete_rdv', raise_exception=True)
def supprimer_rdv(request, pk):
    rdv = get_object_or_404(Rdv, pk=pk)
    rdv.statut = 10
    rdv.save()
    if 'next' in request.GET:
        return redirect(request.GET['next'])
    else:
        return redirect(reverse_lazy('fermer_fenetre'))


@login_required
@permission_required('core.change_rdv', raise_exception=True)
def modifier_horaire(request, pk):
    debut = request.POST.get('debut', None)
    fin = request.POST.get('fin', None)
    rdv = get_object_or_404(Rdv, pk=pk)
    rdv.debut = debut
    rdv.fin = fin
    rdv.save()
    data = {'message': "Rendez-vous modifié"}
    return JsonResponse(data)


class RdvDispoCreate(PermissionRequiredMixin, CreateView):
    model = Rdv
    form_class = RdvDispoForm
    template_name = 'core/rdv_dispo_form_dialog.html'
    permission_required = 'core.add_rdv'
    success_url = reverse_lazy('fermer_fenetre_noreload')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        debut = dt.date.today() + dt.timedelta(days=1)
        if 'debut' in self.request.GET:
            debut = dt.datetime.strptime(self.request.GET['debut'], '%Y-%m-%d').date()
        if 'fin' in self.request.GET:
            fin = dt.datetime.strptime(self.request.GET['fin'], '%Y-%m-%d').date()
        else:
            fin = debut + dt.timedelta(days=7)
        rdvs = Rdv.objects.filter(debut__gte=debut, debut__lte=fin)
        params = self.request.user.profil.compte.parametrescompte
        opening_hours = ouvertures_par_jour(debut, fin, params)
        slots = []
        for hours in opening_hours:
            lst = list(
                filter(lambda rdv: rdv[0] >= hours[0] and rdv[1] < hours[1], list(rdvs.values_list('debut', 'fin'))))
            slot = get_slots(hours, lst, self.request.user.profil.compte.parametrescompte.duree_rdv_defaut)
            slots = slots + slot
        context['slots'] = json.dumps(slots, cls=DateTimeEncoder)
        context['date_debut'] = debut
        context['patient'] = self.request.GET['patient']
        return context

    def get_initial(self):
        init = super().get_initial()
        init['motif'] = 1
        if self.request.user.profil.is_medecin():
            init['praticien'] = self.request.user.profil
        else:
            init['praticien'] = self.request.user.profil.compte.parametrescompte.praticien_defaut

        patient_id = self.request.GET['patient']
        init['compte'] = self.request.user.profil.compte
        init['patient'] = patient_id
        patient = Patient.objects.get(pk=patient_id)
        init['nom_naissance'] = patient.nom_naissance
        init['nom'] = patient.nom
        init['prenom'] = patient.prenom
        init['telephone'] = patient.telephone
        init['nouveau'] = False
        return init

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def form_valid(self, form):
        if form.is_valid():
            fin = form.cleaned_data['debut'] + dt.timedelta(
                minutes=self.request.user.profil.compte.parametrescompte.duree_rdv_defaut)
            self.object = form.save(commit=False)
            if self.request.user.profil.is_medecin():
                praticien = self.request.user.profil
            else:
                praticien = self.request.user.profil.compte.parametrescompte.praticien_defaut
            self.object.praticien = praticien
            self.object.fin = fin
            self.object.save()
            return super().form_valid(form)


@login_required
@permission_required('core.add_rdv', raise_exception=True)
def disponibilites(request, pk):
    debut = request.POST.get('debut', None)
    fin = request.POST.get('fin', None)
    rdvs = Rdv.objects.filter(debut__gte=debut, debut__lte=fin)
    print(f"Found {len(rdvs)} rdvs planifiés");
    data = {'message': "Rendez-vous modifié"}
    return JsonResponse(data)


@login_required
@permission_required('core.add_rdv', raise_exception=True)
def rappel_rdv(request, pk):
    rappel = request.POST.get('rappel', None)
    if rappel is not None:
        rdv = get_object_or_404(Rdv, pk=pk)
        print('Rappel rdv', rappel)
        rdv.patient_rappele = rappel == '1'
        print(rdv.patient_rappele)
        rdv.save()
    data = {'message': "Rendez-vous modifié", 'id': pk, 'rappel': rappel}
    return JsonResponse(data)

