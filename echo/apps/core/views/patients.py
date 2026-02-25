import json
import logging
from datetime import date
from pprint import pformat

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Max, Q, F
# Create your views here.
from django.core import serializers
from django.forms import model_to_dict
from django.http import HttpResponseNotFound, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DetailView, FormView
from apps.core.forms import EtablissementForm, AntecedentObstetriqueForm, GrossesseForm, MesuresPatientForm
from apps.core.data import adresses
from apps.core.forms import PatientForm, AdresseForm, ConsultationForm
from apps.core.models import *
from apps.core.serializers import PhrasierSerializer, PatientSerializer, ListeChoixSerializer, \
    SousCategorieAntecedentSerializer, AntecedentSerializer, MedecinSerializer, ConsultationSerializer, \
    GrossesseSerializer, ConsultationObstetriqueSerializer, AntecedentObstetriqueSerializer, PraticienSerializer, \
    TentativePMASerializer, AdmissionSerializer, MotifSerializer, ConsultationRapportSerializer
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView

from apps.core.services.patients import get_grossesse_data

logger = logging.getLogger()


class PatientList(PermissionRequiredMixin, View):
    template_name = 'core/patient_list_v2.html'
    permission_required = 'core.view_patient'

    def get(self, request):
        if 'rdv' in request.GET:
            # Recherche patient pour admission
            rdv = get_object_or_404(Rdv, pk=request.GET['rdv'])
            return render(request, self.template_name, {'rdv': rdv})

        return render(request, self.template_name)


@login_required
@permission_required('core.view_patient', raise_exception=True)
def fichiers_list(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    dossiers = DossierFichiersPatient.objects.all()
    return render(request, 'core/patient_fichiers_list.html',
                  {'patient': patient, 'dossiers': dossiers })

@login_required
@permission_required('core.view_patient', raise_exception=True)
def fichiers_telecharger(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    dossiers = DossierFichiersPatient.objects.all()
    return render(request, 'core/patient_fichiers_telecharger.html',
                  {'patient': patient, 'dossiers': dossiers })


def charger_info_panel_context(request, context, patient):
    print("Mots clé patient", patient)
    context['patient_json'] = json.dumps(PatientSerializer(patient).data)
    praticiens = Praticien.objects.filter(compte=request.user.profil.compte)
    praticiens_json = PraticienSerializer(praticiens, many=True)
    context['praticiens_json'] = json.dumps(praticiens_json.data)
    patients = Patient.objects.exclude(pk=patient.pk)
    etablissement = serializers.serialize('json', Etablissement.objects.all(), use_natural_foreign_keys=True,
                                          fields=('pk', 'nom', 'adresse'))
    context['etablissements_json'] = etablissement
    lst = []
    for p in patients:
        if p.mot_cle and p.mot_cle is not None:
            mots = json.loads(p.mot_cle)
            cles = map(lambda m: m['value'], mots)
            lst.extend(cles)
    mots_cles = list(set(lst))
    print("Mots clés patient", mots_cles)
    context['mot_patient'] = mots_cles

    #logger.error('Mots cle patient %s', pformat(mots_cles))

    if patient.grossesse_encours is not None:
        context['grossesse_encours_json'] = json.dumps(GrossesseSerializer(patient.grossesse_encours).data)
        #logger.info('Grossesse en cours %s', model_to_dict(patient.grossesse_encours))
        context['grossesse_data'] = json.dumps(get_grossesse_data(patient))
    return context


class PatientView(PermissionRequiredMixin, DetailView):
    model = Patient
    form_class = PatientForm
    permission_required = 'core.view_patient'
    template_name = 'core/patient_detail_v2.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Patient.objects.select_related('compte'), pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        charger_info_panel_context(self.request, context, self.object)

        if 'msg' in self.request.GET:
            if self.request.GET['msg'] == 'admission_succes':
                context['msg'] = 'Patient admis avec succès'

        if self.object.taille and self.object.poids:
            taille = self.object.taille * 0.01
            IMC = self.object.poids / (taille * taille)
            context['IMC'] = round(IMC, 1)

        grossesse = self.object.grossesse_set.filter(encours=True)
        if len(grossesse):
            context['grossesse_encours_json'] = json.dumps(GrossesseSerializer(grossesse[0]).data)
            context['grossesse_encours'] = grossesse[0]

        consult_query = self.object.consultation_set.filter() \
            .select_related('patient') \
            .select_related('praticien') \
            .select_related('praticien__user') \
            .select_related('motif') \
            .order_by('-date')
        context['consultations'] = consult_query
        context['consultations_json'] = json.dumps(ConsultationSerializer(consult_query, many=True).data)

        consult_obs_query = ConsultationObstetrique.objects.filter(patient=self.object)
        context['consultations_obs_json'] = json.dumps(ConsultationObstetriqueSerializer(consult_obs_query, many=True).data)

        ord_query = self.object.ordonnance_set.all() \
            .select_related('patient') \
            .select_related('praticien') \
            .select_related('praticien__user') \
            .order_by('-date')
        ordonnances = serializers.serialize('json', ord_query, use_natural_foreign_keys=True,
                                            fields=('pk', 'date', 'type', 'text', 'praticien'))
        context['ordonnances_json'] = ordonnances

        motifs = serializers.serialize('json', MotifConsultation.objects.all(), use_natural_foreign_keys=True,
                                       fields=('pk', 'libelle', 'code', 'catgeorie'))
        context['motifs'] = motifs

        praticiens = json.dumps(PraticienSerializer(Praticien.objects.filter(compte=self.request.user.profil.compte), many=True).data)
        context['praticiens_json'] = praticiens

        dossiers = serializers.serialize('json', DossierFichiersPatient.objects.all(), use_natural_foreign_keys=True,
                                         fields=('pk', 'nom'))
        context['dossiers_json'] = dossiers

        # fichiers = serializers.serialize('json', object.fichiers(), use_natural_foreign_keys=True)
        context['fichiers'] = self.object.fichiers()

        phrasiers = PhrasierAntecedent.objects.all().prefetch_related('categorie')
        context['phrasiers_json'] = json.dumps(PhrasierSerializer(phrasiers, many=True).data)

        params_compte = self.request.user.profil.compte.parametrescompte
        context['antecedents_defaut'] = json.dumps([
            params_compte.antecedents_familiaux_defaut,
            params_compte.antecedents_medico_chirurgicaux_defaut,
            params_compte.antecedents_gynecologiques_defaut
        ])

        liste_choix = ListeChoix.objects.filter(formulaire='antecedents').order_by('valeur')
        context['formulaire_antecedents_liste_choix'] = json.dumps(ListeChoixSerializer(liste_choix, many=True).data)

        sous_categories_antecedents = SousCatgeorieAntecedent.objects.all().select_related('categorie')
        context['sous_categories_antecedents'] = json.dumps(
            SousCategorieAntecedentSerializer(sous_categories_antecedents, many=True).data)

        antecedents = Antecedent.objects.filter(patient=self.object) \
            .select_related('sous_categorie').select_related('patient').order_by('-date')
        context['antecedents_fcv'] = antecedents.filter(sous_categorie__libelle='FCV')
        context['antecedents_mammographie'] = antecedents.filter(sous_categorie__libelle='Mammographie')
        context['antecedents_echo_mammaire'] = antecedents.filter(sous_categorie__libelle='Echo Mammaire')

        ant_obs = AntecedentObstetrique.objects\
            .filter(patient=self.object, sous_categorie__categorie=4)\
            .order_by('-date_accouchement')
        context['antecedents_obstetriques_patient'] = ant_obs
        context['antecedents_obstetriques_patient_json'] = json.dumps(AntecedentObstetriqueSerializer(ant_obs, many=True).data)

        tentatives_pma = self.object.tentativepma_set.filter(encours=False)\
            .select_related('patient') \
            .select_related('praticien') \
            .select_related('praticien__user') \
            .order_by('-updated_at')
        context['tentatives_pma_json'] = json.dumps(TentativePMASerializer(tentatives_pma, many=True).data)

        categories = self.request.user.profil.compte.categories_consultations.all()
        motifs = MotifConsultation.objects.all().select_related('categorie')
        motifs_json = json.dumps(MotifSerializer(motifs, many=True).data)
        context['categories'] = categories
        context['motifs_'] = motifs
        context['motifs_json'] = motifs_json

        dossiers = DossierFichiersPatient.objects.all()
        context['dossiers'] = dossiers

        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        today = date.today()
        if 'action' in self.request.GET:
            if self.request.GET['action'] == 'demarrer_consultation':
                patient = self.object
                patient.admission_set.filter(Q(date__day=today.day)
                                             & Q(date__month=today.month)
                                             & Q(date__year=today.year)).update(statut='2')
                if not self.request.user.profil.is_medecin():
                    return redirect("/accueil?msg=consultation_demarree_succes#liste_en_consultation")

        return self.render_to_response(context)

@login_required
@permission_required('core.view_patient', raise_exception=True)
def infos_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return JsonResponse(json.dumps(PatientSerializer(patient).data), safe=False)

@login_required
@permission_required('core.view_patient', raise_exception=True)
def admission_patient(request, pk):
    # Recherche patient pour admission
    patient = get_object_or_404(Patient, pk=pk)
    praticien = patient.praticien_principal
    motif = MotifRdv.objects.all()[0]
    if 'rdv' in request.GET:
        rdv = get_object_or_404(Rdv, pk=request.GET['rdv'])
        rdv.patient = patient
        rdv.statut = 2
        praticien = rdv.praticien
        rdv.save()
        motif = rdv.motif

    today = date.today()
    ordre_max = Admission.objects.filter(Q(patient__compte=request.user.profil.compte)
                                         & Q(date__day=today.day)
                                         & Q(date__month=today.month)
                                         & Q(date__year=today.year)).aggregate(Max('ordre'))['ordre__max']
    if ordre_max is None:
        ordre = 1
    else:
        ordre = 1 + ordre_max

    # Chercher le numéro d'admission max sur l'année en cours
    numero_max = Admission.objects.filter(patient__compte=request.user.profil.compte, date__year=today.year) \
        .aggregate(Max('numero'))['numero__max']
    if numero_max is None:
        numero = 1
    else:
        numero = 1 + numero_max

    admission = Admission(numero=numero, patient=patient, praticien=praticien,
                          date=datetime.datetime.now(), ordre=ordre, statut='1', motif=motif)
    print(f'Admission à {datetime.datetime.now()}')
    admission.save()

    if patient.admission_set.count() > 1 and patient.nouveau:
        patient.nouveau = False
        patient.save()

    return redirect("/accueil?msg=admission_succes#liste_salle_attente")


class PatientCreate(PermissionRequiredMixin, View):
    template_name = 'core/patient_form_dialog.html'
    permission_required = 'core.add_patient'

    def get(self, request):
        context = {}
        initial_adresse = {}
        initial_patient = {}

        if 'rdv' in request.GET:
            # Recherche patient pour admission
            rdv = get_object_or_404(Rdv, pk=request.GET['rdv'])
            context['rdv'] = rdv
            initial_adresse = {
                'cp': rdv.cp,
                'ville': rdv.ville,
                'gouvernorat': rdv.gouvernorat
            }
            initial_patient = {
                'nom': rdv.nom,
                'nom_naissance': rdv.nom_naissance,
                'prenom': rdv.prenom,
                'telephone': rdv.telephone,
                'praticien_principal': rdv.praticien
            }
        else:
            if 'nom' in request.GET:
                initial_patient['nom'] = request.GET['nom']
                initial_patient['nom_naissance'] = request.GET['nom']
            if 'prenom' in request.GET:
                initial_patient['prenom'] = request.GET['prenom']
            if 'nom_naissance' in request.GET:
                initial_patient['nom_naissance'] = request.GET['nom_naissance']
            if 'date_naissance' in request.GET:
                initial_patient['date_naissance'] = request.GET['date_naissance']
            if 'ville' in request.GET:
                initial_adresse['ville'] = request.GET['ville']
            initial_patient['praticien_principal'] = self.request.user.profil.compte.parametrescompte.praticien_defaut

        if request.user.profil.compte.adresse and request.user.profil.compte.adresse.pays:
            initial_adresse['pays'] = request.user.profil.compte.adresse.pays
        if (not 'ville' in initial_adresse or initial_adresse['ville'] == '') and request.user.profil.compte.adresse and request.user.profil.compte.adresse.ville:
            initial_adresse['ville'] = request.user.profil.compte.adresse.ville
        if (not 'gouvernorat' in initial_adresse or initial_adresse['gouvernorat'] == '') and request.user.profil.compte.adresse and request.user.profil.compte.adresse.gouvernorat:
            initial_adresse['gouvernorat'] = request.user.profil.compte.adresse.gouvernorat

        adresse_form = AdresseForm(initial=initial_adresse)
        patient_form = PatientForm(initial=initial_patient, compte=self.request.user.profil.compte)
        context['adresse'] = adresse_form
        context['patient'] = patient_form
        pays = "Tunisie"
        if self.request.user.profil.compte.adresse and self.request.user.profil.compte.adresse.pays:
            pays = self.request.user.profil.compte.adresse.pays
        context['codes_postaux'] = adresses.codes_postaux_json(pays)

        return render(request, self.template_name, context)

    def post(self, request):
        adresse_form = AdresseForm(request.POST)
        patient_form = PatientForm(request.POST, compte=self.request.user.profil.compte)
        if patient_form.is_valid():
            patient = patient_form.save(commit=False)
            if patient_form.cleaned_data['nom'] is None:
                patient.nom = patient_form.cleaned_data['nom_naissance']
            if adresse_form.is_valid():
                adresse = adresse_form.save()
                patient.adresse = adresse
                patient.save()

            if 'action' in request.GET:
                if request.GET['action'] == 'admission':
                    if 'rdv' in request.GET:
                        redir = f"{reverse('patient_admission', kwargs={'pk': patient.pk})}?rdv={request.GET['rdv']}"
                    else:
                        redir = reverse("patient_admission", kwargs={'pk': patient.pk})
            else:
                redir = reverse("patient_afficher", kwargs={'pk': patient.pk})

            return redirect(f"{reverse('fermer_fenetre')}?next={redir}")

        pays = "Tunisie"
        if request.user.profil.compte.adresse and request.user.profil.compte.adresse.pays:
            pays = request.user.profil.compte.adresse.pays
        codes_postaux = adresses.codes_postaux_json(pays)

        context = {
            'adresse': adresse_form,
            'patient': patient_form,
            'codes_postaux': codes_postaux
        }
        return render(request, self.template_name, context)


class PatientUpdate(PermissionRequiredMixin, View):
    template_name = 'core/patient_form_dialog.html'
    permission_required = 'core.change_patient'

    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        patient_form = PatientForm(instance=patient, compte=self.request.user.profil.compte)
        adresse_form = AdresseForm(instance=patient.adresse)
        pays = "Tunisie"
        if request.user.profil.compte.adresse and request.user.profil.compte.adresse.pays:
            pays = request.user.profil.compte.adresse.pays
        codes_postaux = adresses.codes_postaux_json(pays)
        context = {
            'adresse': adresse_form,
            'patient': patient_form,
            'object': patient,
            'codes_postaux': codes_postaux
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        patient_form = PatientForm(request.POST, instance=patient, compte=self.request.user.profil.compte)
        adresse_form = AdresseForm(request.POST, instance=patient.adresse)
        if patient_form.is_valid():
            patient = patient_form.save(commit=False)
            if patient_form.cleaned_data['nom'] is None:
                patient.nom = patient_form.cleaned_data['nom_naissance']
            if adresse_form.is_valid():
                adresse = adresse_form.save()
                patient.adresse = adresse
                patient.save()

            return redirect(reverse_lazy('fermer_fenetre_noreload') + "?event=patient:updated")

        pays = "Tunisie"
        if request.user.profil.compte.adresse and request.user.profil.compte.adresse.pays:
            pays = request.user.profil.compte.adresse.pays
        codes_postaux = adresses.codes_postaux_json(pays)
        context = {
            'adresse': adresse_form,
            'patient': patient_form,
            'codes_postaux': codes_postaux
        }
        return render(request, self.template_name, context)


@login_required
@permission_required('core.delete_patient', raise_exception=True)
def supprimer_patient(request, pk):
    query = get_object_or_404(Patient, pk=pk)
    query.delete()
    return redirect('patients_list')


@login_required
@permission_required('core.change_patient', raise_exception=True)
def enregistrer_antecedents(request, pk):
    type = request.POST.get('type_antecedent', None)
    text = request.POST.get('text', None)
    print(f"Antecedent  {type} = {text}")
    patient = get_object_or_404(Patient, pk=pk)
    if type == None:
        return JsonResponse({'message': "Aucun type fourni".format(type)}, status=400)
    if type == '1':
        patient.antecedents_familiaux = text
    elif type == '2':
        patient.antecedents_medico_chirurgicaux = text
    elif type == '3':
        patient.antecedents_gynecologiques = text
    elif type == '4':
        patient.allergies = text
    else:
        return JsonResponse({'message': "Le type {} n'existe pas".format(type)}, status=400)

    patient.save()

    data = {
        'message': "Antécédent enregistré avec succès"
    }
    return JsonResponse(data)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def ajouter_antecedent(request, pk):
    sous_categorie_id = request.POST.get('sous_categorie', None)
    text = request.POST.get('text', None)
    date = request.POST.get('date', None)
    sous_categorie = get_object_or_404(SousCatgeorieAntecedent, pk=sous_categorie_id)
    patient = get_object_or_404(Patient, pk=pk)
    Antecedent.objects.create(sous_categorie=sous_categorie, date=date, text=text, patient=patient)
    data = {
        'message': "Antécédent enregistré avec succès"
    }
    return JsonResponse(data)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def supprimer_antecedent(request, pk):
    ant = get_object_or_404(Antecedent, pk=pk)
    ant.delete()
    data = {
        'message': "Antécédent supprimé avec succès"
    }
    return JsonResponse(data)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def enregistrer_notes(request, pk):
    text = request.POST.get('text', None)
    patient = get_object_or_404(Patient, pk=pk)
    patient.notes = text
    patient.save()
    data = {
        'message': "Notes enregistrées avec succès"
    }
    return JsonResponse(data)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def ajouter_praticien(request, pk):
    praticien_pk = request.POST.get('praticien', None)
    patient = get_object_or_404(Patient, pk=pk)
    praticien = get_object_or_404(Praticien, pk=praticien_pk)
    patient.praticiens_correspondants.add(praticien)
    patient.save()

    data = {'message': "Praticien ajouté avec succès", "particien": json.dumps(PraticienSerializer(praticien).data)}
    return JsonResponse(data)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def ajouter_fichier(request, pk):
    print('Ajouter fichier patient')
    patient = get_object_or_404(Patient, pk=pk)
    print(patient)
    id_dossier = request.POST.get('dossier', None)
    print(id_dossier)
    dossier = get_object_or_404(DossierFichiersPatient, id=id_dossier)
    fichier = FichierPatient(nom=request.FILES['file'].name, fichier=request.FILES['file'], dossier=dossier,
                             date=datetime.datetime.now(),
                             patient=patient)
    fichier.save()
    patient.fichierpatient_set.add(fichier)
    patient.save()
    data = {
        'pk': fichier.pk,
        'nom': fichier.nom,
        'dossier': dossier.nom,
        'dossierId': dossier.id,
        'chemin': fichier.fichier.url,
        'message': "Fichier ajouté"
    }
    return JsonResponse(data)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def deplacer_fichier(request, pk, fichier_pk):
    if request.method == "GET":
        fichier = get_object_or_404(FichierPatient, pk=fichier_pk)
        dossier_patient = DossierFichiersPatient.objects.exclude(id=fichier.dossier.id)
        context = {'dossier_patient': dossier_patient}
        return render(request, "core/fichier_form.html", context)
    else:
        patient = get_object_or_404(Patient, pk=pk)
        fichier = get_object_or_404(FichierPatient, pk=fichier_pk)
        id_dossier = request.POST.get('dossier_fichier_patient', None)
        dossier = get_object_or_404(DossierFichiersPatient, id=id_dossier)
        fichier.dossier = dossier
        fichier.save()
        return redirect(reverse("patient_afficher", kwargs={'pk': patient.pk}) + '#fichiers')


@login_required
@permission_required('core.delete_patient', raise_exception=True)
def supprimer_fichier(request, pk, fichier_pk):
    patient = get_object_or_404(Patient, pk=pk)
    fichier = get_object_or_404(FichierPatient, pk=fichier_pk)
    fichier.delete()

    # data = {'message': "Fichier supprimé"}
    # return JsonResponse(data)
    return redirect(reverse("patient_afficher", kwargs={'pk': patient.pk}) + '#fichiers')


# ajouter_mot_cle_patient
@login_required
@permission_required('core.change_patient', raise_exception=True)
def ajouter_mot_cle(request, pk):
    mot_cle = request.POST.get('mot_cle', None)
    patient = get_object_or_404(Patient, pk=pk)
    print("Ajout des mots clé", mot_cle)
    patient.mot_cle = mot_cle
    patient.save()
    data = {
        'message': "mot clé enregistré avec succès"
    }
    return JsonResponse(data)


# supprimer_mot_cle_patient
@login_required
@permission_required('core.change_patient', raise_exception=True)
def supprimer_mot_cle(request, pk):
    mot_cle = request.POST.get('mot_cle', None)
    patient = get_object_or_404(Patient, pk=pk)
    patient.mot_cle = mot_cle
    patient.save()
    data = {
        'message': "mot clé supprimé avec succès"
    }
    return JsonResponse(data)


class AntecedentObstetriqueCreate(PermissionRequiredMixin, CreateView):
    model = AntecedentObstetrique
    form_class = AntecedentObstetriqueForm
    template_name = 'core/antecedent_obstetrique_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('fermer_fenetre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = get_object_or_404(Patient, pk=self.kwargs['pk'])
        context['patient'] = patient
        if 'action' in self.request.GET:
            if self.request.GET['action'] == 'cloturer_grossesse':
                grossesse = Grossesse.objects.filter(patient=self.kwargs['pk'], encours=True)
                if len(grossesse):
                    nb_foetus = 1
                    if grossesse[0].nb_foetus == 'gemellaire':
                        nb_foetus = 2
                    if grossesse[0].nb_foetus == 'triple':
                        nb_foetus = 3
                    context['nb_foetus'] = nb_foetus
                    context['ddr'] = grossesse[0].ddr
        return context

    def get_initial(self):
        init = super().get_initial()
        init['patient'] = self.kwargs['pk']
        init['sous_categorie'] = 19  # Sous catégorie par défaut
        if 'action' in self.request.GET:
            if self.request.GET['action'] == 'cloturer_grossesse':
                grossesse = Grossesse.objects.filter(patient=self.kwargs['pk'], encours=True)
                if len(grossesse):
                    init['grossesse_patient'] = grossesse[0].pk
                    nb_foetus = 1
                    if grossesse[0].nb_foetus == 'gemellaire':
                        nb_foetus = 2
                    if grossesse[0].nb_foetus == 'triple':
                        nb_foetus = 3
                    init['nb_foetus'] = nb_foetus
        return init

    def form_valid(self, form):
        if form.is_valid():
            if 'action' in self.request.GET:
                if self.request.GET['action'] == 'cloturer_grossesse':
                    patient = get_object_or_404(Patient, pk=self.kwargs['pk'])
                    grossesse = patient.grossesse_set.filter(encours=True)
                    if len(grossesse):
                        grossesse[0].encours = False
                        grossesse[0].save()
            o = form.save(commit=False)
            if not o.sous_categorie_id:
                o.sous_categorie_id = 19
            o.save()
        return super().form_valid(form)


class AntecedentObstetriqueUpdate(PermissionRequiredMixin, UpdateView):
    model = AntecedentObstetrique
    form_class = AntecedentObstetriqueForm
    template_name = 'core/antecedent_obstetrique_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('fermer_fenetre')

    def form_valid(self, form):
        if form.is_valid():
            o = form.save(commit=False)
            if not o.sous_categorie_id:
                o.sous_categorie_id = 19
            o.save()
        return super().form_valid(form)


@login_required
@permission_required('core.delete_patient', raise_exception=True)
def supprimer_antecedent_obstetrique(request, pk):
    ant = get_object_or_404(AntecedentObstetrique, pk=pk)
    patientId = ant.patient.id
    ant.delete()
    return redirect(reverse("patient_afficher", kwargs={'pk': patientId}))


@login_required
@permission_required('core.view_patient', raise_exception=True)
def liste_admissions_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    today = date.today()
    admissions = patient.admission_set.filter(date__day=today.day, date__month=today.month, date__year=today.year)
    adm = json.dumps(AdmissionSerializer(admissions, many=True).data)
    return JsonResponse({'admissions': adm})


class MesuresPatientCreate(PermissionRequiredMixin, CreateView):
    model = MesuresPatient
    form_class = MesuresPatientForm
    template_name = 'core/mesures_patient_form.html'
    permission_required = 'core.change_patient'
    success_url = reverse_lazy('fermer_fenetre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = get_object_or_404(Patient, pk=self.kwargs['pk'])
        context['patient'] = patient
        return context

    def get_initial(self):
        init = super().get_initial()
        init['patient'] = self.kwargs['pk']
        return init

    def form_valid(self, form):
        if form.is_valid():
            mesures = form.save()
            if mesures.poids:
                mesures.patient.poids = mesures.poids
                mesures.patient.save()
        return super().form_valid(form)


class MesuresPatientUpdate(PermissionRequiredMixin, UpdateView):
    model = MesuresPatient
    form_class = MesuresPatientForm
    template_name = 'core/mesures_patient_form.html'
    permission_required = 'core.change_patient'
    success_url = '/utils/fermer_noreload/?event=grossesse:updated'

    def form_valid(self, form):
        if form.is_valid():
            mesures = form.save()
            if mesures.poids:
                mesures.patient.poids = mesures.poids
                mesures.patient.save()
        return super().form_valid(form)



@login_required
@permission_required('core.change_patient', raise_exception=True)
def ajouter_alerte(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    text = request.POST.get('text', None)
    alerte = AlertePatient.objects.create(text=text, patient=patient)
    data = {'message': "Alerte ajoutée", 'id': alerte.id, 'date': alerte.created_at}
    return JsonResponse(data, safe=False)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def supprimer_alerte(request, pk):
    print('Supprimer alerte')
    alerte = get_object_or_404(AlertePatient, pk=pk)
    alerte.delete()
    data = {'message': "Alerte supprimée", 'id': pk}
    return JsonResponse(data, safe=False)


@permission_required('core.view_patient', raise_exception=True)
def rechercher_patient(request):
    objects = Patient.objects.filter(compte=request.user.profil.compte)
    total = objects.count()

    if request.body is not None:
        try:
            fltr = {}
            body = json.loads(request.body)
            if 'nom' in body:
                fltr['nom__icontains'] = body['nom']
            if 'nom_naissance' in body:
                fltr['nom_naissance__icontains'] = body['nom_naissance']
            if 'prenom' in body:
                fltr['prenom__icontains'] = body['prenom']
            # Typeahead autocomplete request
            filtered = objects.filter(**fltr).order_by('nom_naissance')[:20]
            resp = PatientSerializer(filtered, many=True)
            return JsonResponse(json.dumps(resp.data), safe=False)
        except:
            pass

    # Data table request
    draw = request.POST.get('draw', None)
    start = int(request.POST.get('start', None))
    length = int(request.POST.get('length', None))
    order_col = int(request.POST.get('order[0][column]', None))
    order_col_name = request.POST.get('columns[{}][data]'.format(order_col))
    print('Order col', order_col, order_col_name)
    if order_col_name == 'identifiant_unique':
        order_col_name = 'id'
    order_dir = request.POST.get('order[0][dir]', None)
    dir = ''
    if order_dir == 'desc':
        dir = '-'

    fltr = {}
    for c in range(1, 10):
        col_name = request.POST.get(f'columns[{c}][data]')
        sv = request.POST.get(f'columns[{c}][search][value]')
        print('Filter ', col_name, sv)
        if col_name and sv and sv != "":
            if col_name == 'adresse':
                fltr['adresse__ville__icontains'] = sv
            else:
                fltr[col_name + '__icontains'] = sv

    objects = objects.filter(**fltr)
    #filtered = objects.filter(libelle__icontains=libelle).order_by(dir + order_col_name)
    filtered = objects.order_by(dir + order_col_name)
    filtered_count = filtered.count()
    objs = filtered[start:start + length - 1]
    objs_json = PatientSerializer(objs, many=True)
    resp = {
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': filtered_count,
        'data': objs_json.data
    }
    return JsonResponse(resp)


@login_required
@permission_required('core.view_patient', raise_exception=True)
def rechercher_consultation(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    objects = Consultation.objects.filter(patient=patient) \
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