import datetime as dt
import json

from dateutil.parser import *
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core import serializers
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView

from apps.core.models import Consultation, CategorieConsultation, MotifConsultation, Praticien, Medecin, Grossesse
from apps.core.serializers import ConsultationSerializer, MotifSerializer, PraticienSerializer, GrossesseSerializer, \
    ConsultationRapportSerializer, GrossesseRapportSerializer


class RapportConsultationList(PermissionRequiredMixin, View):
    template_name = 'core/rapport_consultation.html'
    permission_required = 'core.view_patient'

    def get(self, request):
        #consultations = json.dumps(ConsultationRapportSerializer(qs, many=True).data)
        consultations = []
        categories = self.request.user.profil.compte.categories_consultations.all()
        motifs = MotifConsultation.objects.all().select_related('categorie')
        motifs_json = json.dumps(MotifSerializer(motifs, many=True).data)
        lst = []
        """for q in qs:
            if q.patient.mot_cle and q.patient.mot_cle is not None:
                mots = json.loads(q.patient.mot_cle)
                cles = map(lambda m: m['value'], mots)
                lst.extend(cles)
        mots_cles = list(set(lst))
        mot_patient = mots_cles
        """
        mot_patient = []
        praticiens_corresp = Praticien.objects.filter(compte=self.request.user.profil.compte)
        praticiens = Medecin.objects.filter(compte=self.request.user.profil.compte)

        return render(request, self.template_name,
                      {'object_list': consultations, 'categories': categories,
                       'motifs': motifs, 'motifs_json': motifs_json,
                       'mots_patients': mot_patient,
                       'praticiens_corresp': praticiens_corresp,
                       'praticiens': praticiens
                       })


@login_required
@permission_required('core.view_patient', raise_exception=True)
def rechercher_consultation(request):
    objects = Consultation.objects.filter(patient__compte=request.user.profil.compte) \
            .select_related('patient') \
            .select_related('praticien') \
            .select_related('motif') \
            .select_related('motif__categorie')

    # Data table request
    draw = request.POST.get('draw', None)
    start = int(request.POST.get('start', None))
    length = int(request.POST.get('length', None))
    order_col = int(request.POST.get('order[0][column]', None))
    order_col_name = request.POST.get('columns[{}][data]'.format(order_col)).replace('.','__')
    if order_col == 9:
        order_col_name = 'praticien__user'
    order_dir = request.POST.get('order[0][dir]', None)
    dir = ''
    if order_dir == 'desc':
        dir = '-'

    """
    print("---------------------------")
    for i in range(0, 15):
        val = request.POST.get(f'columns[{i}][search][value]')
        print(f'Col {i}', val)
    print("---------------------------")
    """
    filtered = objects
    ipp = request.POST.get('columns[0][search][value]')
    if ipp:
        filtered = filtered.filter(patient__id=ipp)
    gouvernorat = request.POST.get('columns[1][search][value]')
    if gouvernorat:
        filtered = filtered.filter(patient__adresse__gouvernorat__icontains=gouvernorat)
    prat_corresp = request.POST.get('columns[2][search][value]')
    if prat_corresp:
        filtered = filtered.filter(patient__praticiens_correspondants__nom__icontains=prat_corresp)
    nom = request.POST.get('columns[4][search][value]')
    if nom:
        filtered = filtered.filter(patient__nom__icontains=nom)
    nom_naissance = request.POST.get('columns[5][search][value]')
    if nom_naissance:
        filtered = filtered.filter(patient__nom_naissance__icontains=nom_naissance)
    prenom = request.POST.get('columns[6][search][value]')
    if prenom:
        filtered = filtered.filter(patient__prenom__icontains=prenom)
    praticien = request.POST.get('columns[9][search][value]')
    if praticien:
        filtered = filtered.filter(praticien_id=praticien)
    categorie = request.POST.get('columns[7][search][value]')
    if categorie:
        filtered = filtered.filter(motif__categorie_id=categorie)
    motif = request.POST.get('columns[8][search][value]')
    if motif:
        filtered = filtered.filter(motif_id=motif)
    mots_cles = request.POST.get('columns[10][search][value]')
    if mots_cles:
        mots_parsed = json.loads(mots_cles) #[{"value":"diabète"}]
        for m in mots_parsed:
            filtered = filtered.filter(patient__mot_cle__icontains=m["value"])
    debut = request.POST.get('columns[11][search][value]')
    if debut and debut != "":
        print('Debut', debut)
        filtered = filtered.filter(date__gte=debut)
    fin = request.POST.get('columns[12][search][value]')
    if fin and fin != "":
        filtered = filtered.filter(date__lte=fin)

    print('Order col name', order_col_name)
    filtered = filtered.order_by(dir + order_col_name)
    #filtered = objects.filter(patient__pk__icontains=ipp).order_by(dir + order_col_name)
    total = objects.count()
    filtered_count = filtered.count()
    objs = filtered[start:start + length - 1]
    objs_json = ConsultationRapportSerializer(objs, many=True)
    resp = {
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': filtered_count,
        'data': objs_json.data
    }
    return JsonResponse(resp)


class RapportAccouchementList(PermissionRequiredMixin, View):
    template_name = 'core/rapport_accouchement.html'
    permission_required = 'core.view_patient'

    def get(self, request):
        qs = Grossesse.objects.filter(patient__compte=self.request.user.profil.compte, encours=True) \
                .select_related('patient')\
                .select_related('lieu_accouchement').order_by('pk')
        accouchements = json.dumps(GrossesseRapportSerializer(qs, many=True).data)

        return render(request, self.template_name, {'accouchements': accouchements})


class ConsultationView(PermissionRequiredMixin, DetailView):
    model = Consultation
    template_name = 'core/consultation_detail.html'
    permission_required = 'core.view_patient'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
