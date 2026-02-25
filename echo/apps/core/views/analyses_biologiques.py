import json
from pprint import pprint

from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView, UpdateView

from apps.core.forms import PrescriptionAnalyseBiologiqueForm, AnalyseBiologiqueForm, CollectionAnalyseBiologiqueForm
from apps.core.models import *
from apps.core.serializers import AnalyseBiologiqueSerializer, CollectionAnalyseBiologiqueSerializer, PatientSerializer, \
    ResultatAnalyseBiologiqueSerializer


class PrescriptionBaseView(PermissionRequiredMixin, TemplateView):
    template_name = 'core/prescription_analyse_form.html'
    permission_required = 'core.change_patient'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        analyses = AnalyseBiologique.objects.filter(compte=self.request.user.profil.compte).order_by('ordre')
        collections = CollectionAnalyseBiologique.objects.filter(compte=self.request.user.profil.compte)
        context['analyses'] = analyses
        context['collections'] = collections
        analyses_json = AnalyseBiologiqueSerializer(analyses, many=True)
        context['analyses_json'] = json.dumps(analyses_json.data)
        collections_json = CollectionAnalyseBiologiqueSerializer(collections, many=True)
        context['collections_json'] = json.dumps(collections_json.data)
        return context


class PrescriptionCreate(PrescriptionBaseView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = get_object_or_404(Patient, pk=self.kwargs['pk'])
        context['patient_json'] = json.dumps(PatientSerializer(patient).data)
        return context


class PrescriptionUpdate(PrescriptionBaseView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prescription = get_object_or_404(PrescriptionAnalyseBiologique, pk=self.kwargs['pk'])
        context['prescription'] = prescription
        patient = prescription.patient
        context['patient_json'] = json.dumps(PatientSerializer(patient).data)
        resultats = prescription.resultatanalysebiologique_set.all()
        context['resultats_json'] = json.dumps(ResultatAnalyseBiologiqueSerializer(resultats, many=True).data)
        return context


@login_required
@permission_required('core.change_patient', raise_exception=True)
def enregistrer_prescription(request):
    id = int(request.POST.get('id', None))
    if id == -1:
        if 'patient' not in request.POST:
            return JsonResponse({'msg': "Patient est obligatoire"}, status=400)
        patient_id = int(request.POST.get('patient', None))
        presc = PrescriptionAnalyseBiologique(date_prescription=datetime.datetime.now(), patient_id=patient_id)
        presc.save()
    else:
        presc = get_object_or_404(PrescriptionAnalyseBiologique, pk=id)
        if 'date_prescription' in request.POST:
            presc.date_prescription = request.POST.get('date_prescription', None)
        if 'date_resultat' in request.POST:
            presc.date_resultat = request.POST.get('date_resultat', None)
        presc.save()

    data = {
        'id': presc.id,
        'message': "Prescription enregistrée avec succès"
    }
    return JsonResponse(data)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def ajouter_resultats_analyses(request):
    if 'prescription' not in request.POST:
        return JsonResponse({'msg': "Prescription est obligatoire"}, status=400)
    prescId = int(request.POST.get('prescription', None))
    presc = get_object_or_404(PrescriptionAnalyseBiologique, pk=prescId)
    resultats = list()
    analyses = request.POST.get('analyses', None)
    if analyses is None:
        return JsonResponse({'msg': "Au moins un résultat est obligatoire"}, status=400)
    for analyse in json.loads(analyses):
        analyse_bio = AnalyseBiologique.objects.get(pk=analyse['id'])
        res = ResultatAnalyseBiologique.objects.create(prescription=presc, analyse=analyse_bio,
                                                       valeur=analyse_bio.modele_resultat)
        resultats.append(res)
    # resultats = presc.resultatanalysebiologique_set.all()
    resultats_json = ResultatAnalyseBiologiqueSerializer(resultats, many=True).data
    data = {
        'id': presc.id,
        'resultats': resultats_json,
        'message': "Prescription enregistrée avec succès"
    }
    return JsonResponse(data)


def creer_alerte(resultat):
    patient = resultat.prescription.patient
    text = f"Anomalie dans l'analyse <strong>{resultat.analyse.libelle}</strong> de valeur <strong>{resultat.valeur}</strong>"
    lien = f"dialog:analyses:{resultat.prescription.id}"
    AlertePatient.objects.create(text=text, patient=patient, lien=lien)

@login_required
@permission_required('core.change_patient', raise_exception=True)
def modifier_resultats_analyses(request, pk):
    res = get_object_or_404(ResultatAnalyseBiologique, pk=pk)
    if request.method == 'PUT':
        body = json.loads(request.body)
        if 'valeur' in body:
            res.valeur = body['valeur']
            res.date = datetime.datetime.now()
        if 'observation' in body:
            res.observation = body['observation']
        if 'valeur_anormale' in body:
            res.valeur_anormale = body['valeur_anormale']
            if res.valeur_anormale:
                creer_alerte(res)
        res.save()
        data = {
            'id': res.id,
            'message': "Résultat modifié avec succès"
        }

    elif request.method == 'DELETE':
        res.delete()
        data = {
            'id': pk,
            'message': "Résultat supprimé avec succès"
        }
    else:
        return JsonResponse({'msg': "Méthode non autorisée"}, status=405)

    return JsonResponse(data)


class AnalyseBiologiqueList(PermissionRequiredMixin, ListView):
    model = AnalyseBiologique
    template_name = 'core/analyse_biologique_list.html'
    permission_required = 'core.view_patient'

    def get_queryset(self):
        return AnalyseBiologique.objects.filter(compte=self.request.user.profil.compte)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # analyses_json = AnalyseBiologiqueSerializer(self.get_queryset(), many=True)
        # context['analyses_json'] = json.dumps(analyses_json.data)
        return context


class AnalyseBiologiqueCreate(PermissionRequiredMixin, CreateView):
    model = AnalyseBiologique
    form_class = AnalyseBiologiqueForm
    template_name = 'core/analyse_biologique_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('analyses_biologiques_liste')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        analyses = AnalyseBiologique.objects.filter(compte=self.request.user.profil.compte);
        analyses_json = AnalyseBiologiqueSerializer(analyses, many=True)
        context['analyses_json'] = json.dumps(analyses_json.data)
        return context


class AnalyseBiologiqueUpdate(PermissionRequiredMixin, UpdateView):
    model = AnalyseBiologique
    form_class = AnalyseBiologiqueForm
    template_name = 'core/analyse_biologique_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('analyses_biologiques_liste')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        analyses = AnalyseBiologique.objects.filter(compte=self.request.user.profil.compte);
        analyses_json = AnalyseBiologiqueSerializer(analyses, many=True)
        context['analyses_json'] = json.dumps(analyses_json.data)
        return context

@login_required
@permission_required('core.change_patient', raise_exception=True)
def supprimer_analyse_biologique(request, pk):
    query = get_object_or_404(AnalyseBiologique, pk=pk)
    query.delete()
    return redirect(reverse("analyses_biologiques_liste"))


@login_required
@permission_required('core.view_patient', raise_exception=True)
def rechercher_analyse(request):
    objects = AnalyseBiologique.objects.filter(compte=request.user.profil.compte)
    if request.body is not None:
        try:
            body = json.loads(request.body)
            query = body['libelle']
            # Typeahead autocomplete request
            if query is not None:
                filtered = objects.filter(libelle__icontains=query).order_by('libelle')[:20]
                resp = AnalyseBiologiqueSerializer(filtered, many=True)
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
    objs_json = AnalyseBiologiqueSerializer(objs, many=True)
    resp = {
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': filtered_count,
        'data': objs_json.data
    }
    return JsonResponse(resp)


class CollectionAnalyseBiologiqueList(PermissionRequiredMixin, ListView):
    model = CollectionAnalyseBiologique
    template_name = 'core/collection_analyse_list.html'
    permission_required = 'core.view_patient'

    def get_queryset(self):
        return CollectionAnalyseBiologique.objects.filter(compte=self.request.user.profil.compte)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # analyses_json = CollectionAnalyseBiologiqueSerializer(self.get_queryset(), many=True)
        # context['analyses_json'] = json.dumps(analyses_json.data)
        return context


class CollectionAnalyseBiologiqueCreate(PermissionRequiredMixin, CreateView):
    model = CollectionAnalyseBiologique
    form_class = CollectionAnalyseBiologiqueForm
    template_name = 'core/collection_analyse_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('collection_analyses_liste')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        if form.is_valid():
            ordre = form.cleaned_data.get('ordre').split()
            #print('Ordre', ordre)
            collection = form.save()
            analyses = form.cleaned_data.get('analyses')
            for item in ordre:
                a = next((x for x in analyses if x.id == int(item)), None)
                if a:
                    #print('Ajouter', a.id)
                    collection.analyses.add(a)
                else:
                    print(f'Analyse with id {item} not found')
        return super().form_valid(form)


class CollectionAnalyseBiologiqueUpdate(PermissionRequiredMixin, UpdateView):
    model = CollectionAnalyseBiologique
    form_class = CollectionAnalyseBiologiqueForm
    template_name = 'core/collection_analyse_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('collection_analyses_liste')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['analyses_ajoutees'] = json.dumps(AnalyseBiologiqueSerializer(self.object.analyses_list, many=True).data)
        return context

    def form_valid(self, form):
        if form.is_valid():
            ordre = form.cleaned_data.get('ordre').split()
            #print('Ordre', ordre)
            collection = form.save()
            collection.analyses.clear()
            analyses = form.cleaned_data.get('analyses')
            for item in ordre:
                a = next((x for x in analyses if x.id == int(item)), None)
                if a:
                    #print('Ajouter', a.id)
                    collection.analyses.add(a)
                else:
                    print(f'Analyse with id {item} not found')
        return super().form_valid(form)



@login_required
@permission_required('core.change_patient', raise_exception=True)
def supprimer_collection_analyse_biologique(request, pk):
    query = get_object_or_404(CollectionAnalyseBiologique, pk=pk)
    query.delete()
    return redirect(reverse("collection_analyses_liste"))


@login_required
@permission_required('core.view_patient', raise_exception=True)
def rechercher_collection(request):
    objects = CollectionAnalyseBiologique.objects.filter(compte=request.user.profil.compte)
    if request.body is not None:
        try:
            body = json.loads(request.body)
            query = body['nom']
            # Typeahead autocomplete request
            if query is not None:
                filtered = objects.filter(nom__icontains=query).order_by('nom')[:20]
                resp = CollectionAnalyseBiologiqueSerializer(filtered, many=True)
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
    nom = request.POST.get('columns[0][search][value]')

    filtered = objects.filter(nom__icontains=nom).order_by(dir + order_col_name)
    total = objects.count()
    filtered_count = filtered.count()
    objs = filtered[start:start + length - 1]
    objs_json = CollectionAnalyseBiologiqueSerializer(objs, many=True)
    resp = {
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': filtered_count,
        'data': objs_json.data
    }
    return JsonResponse(resp)


@login_required
@permission_required('core.view_patient', raise_exception=True)
def prescriptions(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    prescr = patient.prescriptionanalysebiologique_set.all()[:4]
    return render(request, "core/partials/prescription_list.html", {'prescriptions': prescr})


@login_required
@permission_required('core.change_patient', raise_exception=True)
def supprimer_prescription(request, pk):
    presc = get_object_or_404(PrescriptionAnalyseBiologique, pk=pk)
    presc.delete()
    data = {
        'id': pk,
        'message': "Prescription supprimée avec succès"
    }
    return JsonResponse(data)
