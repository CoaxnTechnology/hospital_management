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
from apps.core.forms import RdvForm, RdvDispoForm, AbsenceMedecinForm, ProgrammeOperatoireForm
from apps.core.models import Rdv, Patient, Praticien, AbsenceMedecin, MotifAbsence, ProgrammeOperatoire, \
    ParametresCompte
from apps.core.serializers import PatientSerializer, DateTimeEncoder, PraticienSerializer, MotifAbsenceSerializer, \
    ProgrammeOperatoireSerializer
from apps.core.services.rdvs import *


class AbsenceCreate(PermissionRequiredMixin, CreateView):
    model = AbsenceMedecin
    form_class = AbsenceMedecinForm
    template_name = 'core/absence_medecin_form.html'
    permission_required = 'core.add_absencemedecin'
    success_url = reverse_lazy('fermer_fenetre')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        praticiens = json.dumps(
            PraticienSerializer(Praticien.objects.filter(compte=self.request.user.profil.compte), many=True).data)
        context['praticiens_json'] = praticiens
        motifs = json.dumps(
            MotifAbsenceSerializer(MotifAbsence.objects.filter(compte=self.request.user.profil.compte), many=True).data)
        context['motifs_absence'] = motifs
        prog = ProgrammeOperatoire.objects.filter(compte=self.request.user.profil.compte) \
            .select_related('patient') \
            .select_related('praticien') \
            .select_related('lieu_accouchement')
        programme_operatoire = json.dumps(ProgrammeOperatoireSerializer(prog, many=True).data)
        context['programme_operatoire_json'] = programme_operatoire

        return context

    def get_initial(self):
        initial_base = super(AbsenceCreate, self).get_initial()

        praticien = get_object_or_404(ParametresCompte.objects.select_related('praticien_defaut'),
                                      compte=self.request.user.profil.compte)
        initial_base['praticien'] = praticien.praticien_defaut

        return initial_base

    def form_valid(self, form):
        if form.is_valid():
            debut = dt.datetime.combine(form.cleaned_data['date_debut'], form.cleaned_data['heure_debut'])
            fin = dt.datetime.combine(form.cleaned_data['date_fin'], form.cleaned_data['heure_fin'])
            print(debut, fin)
            # if debut < dt.datetime.now():
            #    form.add_error('heure_debut', "La date sélectionnée est dans le passé")
            #    return super().form_invalid(form)

            if debut > fin:
                form.add_error('heure_fin', "L'heure de fin doit être ultérieure à l'heure de début")
                return super().form_invalid(form)

            absence_meme_jour = AbsenceMedecin.objects.filter(date_debut__day=debut.day, date_debut__month=debut.month,
                                                              date_debut__year=debut.year)
            print(absence_meme_jour)
            if absence_meme_jour:
                form.add_error('date_debut', "Une autre absence est planifié à la même date")
                return super().form_invalid(forAbsenceUpdatem)

            self.object = form.save(commit=False)
            self.object.date_debut = debut
            self.object.date_fin = fin
            self.object.save()
            return super().form_valid(form)


class AbsenceUpdate(PermissionRequiredMixin, UpdateView):
    model = AbsenceMedecin
    form_class = AbsenceMedecinForm
    template_name = 'core/absence_medecin_form.html'
    permission_required = 'core.change_absencemedecin'
    success_url = reverse_lazy('fermer_fenetre')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AbsenceUpdate, self).get_context_data(**kwargs)
        praticiens = json.dumps(
            PraticienSerializer(Praticien.objects.filter(compte=self.request.user.profil.compte), many=True).data)
        context['praticiens_json'] = praticiens
        return context

    def get_initial(self):
        initial_base = super(AbsenceUpdate, self).get_initial()
        initial_base['date_debut'] = self.object.date_debut
        initial_base['heure_debut'] = self.object.date_debut.strftime("%H:%M")
        initial_base['date_fin'] = self.object.date_fin
        initial_base['heure_fin'] = self.object.date_fin.strftime("%H:%M")
        return initial_base

    def form_valid(self, form):
        debut = dt.datetime.combine(form.cleaned_data['date_debut'], form.cleaned_data['heure_debut'])
        fin = dt.datetime.combine(form.cleaned_data['date_fin'], form.cleaned_data['heure_fin'])
        print(debut, fin)
        # if debut < dt.datetime.now():
        #    form.add_error('heure_debut', "La date sélectionnée est dans le passé")
        #    return super().form_invalid(form)

        if debut > fin:
            form.add_error('heure_fin', "L'heure de fin doit être ultérieure à l'heure de début")
            return super().form_invalid(form)

        absence_meme_jour = AbsenceMedecin.objects.filter(date_debut__day=debut.day, date_debut__month=debut.month,
                                                          date_debut__year=debut.year)
        for absence in absence_meme_jour:
            if self.object.pk != absence.pk:
                form.add_error('date_debut', "Une autre absence est planifié à la même date")
                return super().form_invalid(form)
        self.object = form.save(commit=False)
        self.object.date_debut = debut
        self.object.date_fin = fin
        self.object.save()
        return super().form_valid(form)


class ProgrammeOperatoireCreate(PermissionRequiredMixin, CreateView):
    model = ProgrammeOperatoire
    form_class = ProgrammeOperatoireForm
    template_name = 'core/programme_operatoire_form.html'
    permission_required = 'core.add_programmeoperatoire'
    success_url = reverse_lazy('fermer_fenetre')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patients = json.dumps(
            PatientSerializer(Patient.objects.filter(compte=self.request.user.profil.compte), many=True).data)
        context['patients_json'] = patients
        return context

    def get_initial(self):
        initial_base = super().get_initial()

        praticien = get_object_or_404(ParametresCompte.objects.select_related('praticien_defaut'),
                                      compte=self.request.user.profil.compte)
        initial_base['praticien'] = praticien.praticien_defaut

        return initial_base

    def form_valid(self, form):
        if form.is_valid():
            debut = dt.datetime.combine(form.cleaned_data['debut'], form.cleaned_data['heure_debut'])
            fin = dt.datetime.combine(form.cleaned_data['debut'], form.cleaned_data['heure_fin'])
            # if debut < dt.datetime.now():
            #    form.add_error('heure_debut', "La date sélectionnée est dans le passé")
            #    return super().form_invalid(form)

            if debut > fin:
                form.add_error('heure_fin', "L'heure de fin doit être ultérieure à l'heure de début")
                return super().form_invalid(form)

            operation_meme_jour = ProgrammeOperatoire.objects.filter(debut__day=debut.day, debut__month=debut.month,
                                                                     debut__year=debut.year,
                                                                     praticien=form.cleaned_data['praticien'],
                                                                     patient=form.cleaned_data['patient'])

            self.object = form.save(commit=False)
            self.object.debut = debut
            self.object.fin = fin

            return super().form_valid(form)


class ProgrammeOperatoireUpdate(PermissionRequiredMixin, UpdateView):
    model = ProgrammeOperatoire
    form_class = ProgrammeOperatoireForm
    template_name = 'core/programme_operatoire_form.html'
    permission_required = 'core.change_programmeoperatoire'
    success_url = reverse_lazy('fermer_fenetre')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ProgrammeOperatoireUpdate, self).get_context_data(**kwargs)
        patients = json.dumps(
            PatientSerializer(Patient.objects.filter(compte=self.request.user.profil.compte), many=True).data)
        context['patients_json'] = patients
        return context

    def get_initial(self):
        initial_base = super(ProgrammeOperatoireUpdate, self).get_initial()
        initial_base['debut'] = self.object.debut
        initial_base['heure_debut'] = self.object.debut.strftime("%H:%M")
        initial_base['heure_fin'] = self.object.fin.strftime("%H:%M")
        return initial_base

    def form_valid(self, form):
        if form.is_valid():
            debut = dt.datetime.combine(form.cleaned_data['debut'], form.cleaned_data['heure_debut'])
            fin = dt.datetime.combine(form.cleaned_data['debut'], form.cleaned_data['heure_fin'])
            # if debut < dt.datetime.now():
            #    form.add_error('heure_debut', "La date sélectionnée est dans le passé")
            #    return super().form_invalid(form)

            if debut > fin:
                form.add_error('heure_fin', "L'heure de fin doit être ultérieure à l'heure de début")
                return super().form_invalid(form)

            operation_meme_jour = ProgrammeOperatoire.objects.filter(debut__day=debut.day, debut__month=debut.month,
                                                                     debut__year=debut.year,
                                                                     praticien=form.cleaned_data['praticien'],
                                                                     patient=form.cleaned_data['patient'])

            self.object = form.save(commit=False)
            self.object.debut = debut
            self.object.fin = fin

            return super().form_valid(form)
