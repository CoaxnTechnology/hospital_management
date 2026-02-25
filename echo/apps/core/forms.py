from pprint import pprint

import pytz
from bootstrap_modal_forms.forms import BSModalForm
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User, Group
from django.forms import inlineformset_factory, BaseInlineFormSet, Select, ModelMultipleChoiceField
from django_select2 import forms as s2forms
from apps.core.data import adresses
from django.forms.formsets import BaseFormSet, formset_factory
from apps.core.models import *

ProfilFormset = inlineformset_factory(
    User, Profil,
    fields=(
        'titre', 'date_naissance', 'telephone_principal', 'telephone_secondaire', 'signature', 'code_securite_sociale',
        'code_conventionnel','ajouter_signature_edition', 'default_device'
    ),
    labels={"date_naissance": "Date de naissance"},
    extra=1
)


class UserForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True)

    class Meta:
        model = User
        fields = ['is_active', 'first_name', 'last_name', 'email', 'group', 'username', 'password']
        labels = {'group': 'Profil'}


class UserUpdateForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True)

    class Meta:
        model = User
        fields = ['is_active', 'first_name', 'last_name', 'email', 'group', 'username']
        labels = {'group': 'Profil'}


class MdpForm(BSModalForm):
    class Meta:
        model = User
        fields = ['password']
        widgets = {
            'password': forms.PasswordInput()
        }


class RdvForm(forms.ModelForm):
    date_debut = forms.DateField(required=True)
    heure_debut = forms.TimeField(required=True)
    heure_fin = forms.TimeField(required=True)
    observation = forms.CharField(widget=forms.Textarea, required=False)
    patient = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Rdv
        fields = ['prenom', 'nom', 'nom_naissance', 'telephone', 'cp', 'ville', 'gouvernorat', 'motif', 'date_debut',
                  'heure_debut', 'heure_fin', 'praticien', 'observation', 'nouveau']

    def __init__(self, *args, **kwargs):
        compte = kwargs.pop('compte')
        super().__init__(*args, **kwargs)
        self.fields['praticien'].queryset = Medecin.objects.filter(compte=compte)


class ProgrammeOperatoireForm(forms.ModelForm):
    debut = forms.DateField(required=True)
    heure_debut = forms.TimeField(required=True)
    heure_fin = forms.TimeField(required=True)

    class Meta:
        model = ProgrammeOperatoire
        fields = ['debut', 'patient', 'type_acte', 'lieu_accouchement', 'heure_debut', 'heure_fin', 'praticien',
                  'observation']

    def __init__(self, *args, **kwargs):
        compte = kwargs.pop('compte')
        super().__init__(*args, **kwargs)
        self.fields['praticien'].queryset = Medecin.objects.filter(compte=compte)


class RdvDispoForm(forms.ModelForm):
    class Meta:
        model = Rdv
        fields = ['prenom', 'nom', 'telephone', 'motif', 'debut', 'praticien', 'nouveau', 'patient']
        widgets = {
            'debut': forms.HiddenInput(),
            'fin': forms.HiddenInput(),
            'patient': forms.HiddenInput(),
            'nom': forms.HiddenInput(),
            'prenom': forms.HiddenInput(),
            'telephone': forms.HiddenInput(),
            'nouveau': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        compte = kwargs.pop('compte')
        super().__init__(*args, **kwargs)
        self.fields['praticien'].queryset = Medecin.objects.filter(compte=compte)


class AbsenceMedecinForm(forms.ModelForm):
    date_debut = forms.DateField(required=True)
    heure_debut = forms.TimeField(required=True)
    date_fin = forms.DateField(required=True)
    heure_fin = forms.TimeField(required=True)

    class Meta:
        model = AbsenceMedecin
        fields = ['date_debut','heure_debut','date_fin','heure_fin', 'motif', 'praticien','praticien_remplacant']

    def __init__(self, *args, **kwargs):
        compte = kwargs.pop('compte')
        super().__init__(*args, **kwargs)
        self.fields['praticien'].queryset = Medecin.objects.filter(compte=compte)
        self.fields['praticien_remplacant'].queryset = Medecin.objects.filter(compte=compte)


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['civilite', 'sexe', 'prenom', 'nom', 'nom_naissance', 'date_naissance', 'numero_identite',
                  'code_securite_sociale', 'adresse', 'email', 'telephone', 'telephone_secondaire','telephone_autre',
                  'observation', 'profession', 'praticien_principal',
                  'taille', 'poids', 'groupe_sanguin', 'fumeur', 'nombre_cigarettes', 'origine', 'ancien_numero',
                  'date_mariage', 'nom_conjoint', 'prenom_conjoint', 'date_naissance_conjoint', 'telephone_conjoint',
                  'groupe_sanguin_conjoint', 'consanguinite_conjoint', 'etat_sante_conjoint', 'profession_conjoint','mutuelle',
                  'designation','caisse_affectation','regime','lien_parente','num_carnet_soin','code_medecin_famille',
                  'date_validite_mutuelle','code_apci']

    def __init__(self, *args, **kwargs):
        compte = kwargs.pop('compte')
        super().__init__(*args, **kwargs)
        self.fields['praticien_principal'].queryset = Medecin.objects.filter(compte=compte)
        self.fields['praticien_principal'].required = True


class AdresseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AdresseForm, self).__init__(*args, **kwargs)
        # self.fields['cp'].queryset = adresses

    class Meta:
        model = Adresse
        fields = ['numero', 'rue', 'cite', 'ville', 'cp', 'gouvernorat', 'pays']
        widgets = {
            'cp': forms.TextInput()
        }


class ParametresGenerauxForm(forms.ModelForm):
    h_deb_mat_lundi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_fin_mat_lundi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_deb_mat_mardi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_fin_mat_mardi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_deb_mat_mercredi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_fin_mat_mercredi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_deb_mat_jeudi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_fin_mat_jeudi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_deb_mat_vendredi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_fin_mat_vendredi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_deb_mat_samedi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_fin_mat_samedi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_deb_am_lundi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_fin_am_lundi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_deb_am_mardi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_fin_am_mardi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_deb_am_mercredi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_fin_am_mercredi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_deb_am_jeudi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_fin_am_jeudi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_deb_am_vendredi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_fin_am_vendredi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_deb_am_samedi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    h_fin_am_samedi = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))

    class Meta:
        model = ParametresCompte
        fields = '__all__'
        widgets = {
            'compte': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        compte = kwargs.pop('compte')
        super().__init__(*args, **kwargs)
        self.fields['praticien_defaut'].queryset = Medecin.objects.filter(compte=compte)


class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['motif', 'praticien', 'text', 'patient', 'date']

    def __init__(self, *args, **kwargs):
        compte = kwargs.pop('compte')
        super().__init__(*args, **kwargs)
        self.fields['praticien'].queryset = Medecin.objects.filter(compte=compte)
        self.fields['date'].required = False


class PraticienForm(BSModalForm):
    class Meta:
        model = Praticien
        fields = ['titre', 'nom', 'prenom', 'specialite', 'telephone', 'email', 'notes']


class EtablissementForm(forms.ModelForm):
    class Meta:
        model = Etablissement
        fields = ['nom', 'telephone']


class OrdonnanceForm(forms.ModelForm):
    traitement = forms.CharField(required=False)
    prescription = forms.CharField(required=False)

    class Meta:
        model = Ordonnance
        fields = ['date', 'patient', 'praticien', 'text', 'traitement', 'prescription', 'type']
        widgets = {
            'patient': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        compte = kwargs.pop('compte')
        super().__init__(*args, **kwargs)
        self.fields['praticien'].queryset = Medecin.objects.filter(compte=compte)
        self.fields['type'].queryset = TypeOrdonnance.objects.filter(compte=compte).order_by('libelle')


class CertificatForm(forms.ModelForm):
    class Meta:
        model = Certificat
        fields = ['date', 'patient', 'praticien', 'text', 'duree', 'type']
        widgets = {
            'patient': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        compte = kwargs.pop('compte')
        super().__init__(*args, **kwargs)
        self.fields['praticien'].queryset = Medecin.objects.filter(compte=compte)


class TraitementForm(forms.ModelForm):
    class Meta:
        model = Traitement
        fields = ['libelle', 'forme', 'text']


class PrestationForm(forms.ModelForm):
    class Meta:
        model = Prestation
        fields = ['prestation', 'code', 'prix_ttc', 'prix_pec','par_defaut']

class MotifAbsenceForm(forms.ModelForm):
    class Meta:
        model = MotifAbsence
        fields = ['motif']

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['libelle', 'text', 'categorie']


class GrossesseWidget(s2forms.Select2MultipleWidget):
    search_fields = [
        "libelle__icontains",
        "valeur__icontains"
    ]


class AntecedentObstetriqueForm(forms.ModelForm):
    sous_categorie = forms.ModelChoiceField(
        queryset=SousCatgeorieAntecedent.objects.filter(categorie=4).order_by('libelle'), required=False)
    # grossesse = forms.MultipleChoiceField(choices=[item for item in ListeChoixActif.objects.filter(champ="grossesse").values_list('id', 'valeur')], required=False)
    grossesse = forms.ModelMultipleChoiceField(queryset=None, widget=GrossesseWidget)
    mise_en_travail = forms.ModelChoiceField(queryset=None, required=False)
    issue_grossesse = forms.ModelChoiceField(queryset=None, required=False)
    analgesie = forms.ModelChoiceField(queryset=None, required=False)
    indications = forms.ModelChoiceField(queryset=None, required=False)
    etat_sante_1 = forms.ModelChoiceField(queryset=None, required=False)
    etat_sante_2 = forms.ModelChoiceField(queryset=None, required=False)
    etat_sante_3 = forms.ModelChoiceField(queryset=None, required=False)
    perinee = forms.ModelChoiceField(queryset=None, required=False)
    suite_couche_type = forms.ModelChoiceField(queryset=None, required=False)
    suite_couche_detail = forms.ModelChoiceField(queryset=None, required=False)
    evacuation_grossesse = forms.ModelChoiceField(queryset=None, required=False)

    class Meta:
        model = AntecedentObstetrique
        fields = '__all__'
        widgets = {
            'patient': forms.HiddenInput(),
            'grossesse_patient': forms.HiddenInput(),
            'lieu_accouchement': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grossesse'].queryset = ListeChoixActif.objects.filter(champ="grossesse")
        self.fields['mise_en_travail'].queryset = ListeChoixActif.objects.filter(champ='mise_en_travail')
        self.fields['issue_grossesse'].queryset = ListeChoixActif.objects.filter(champ='issue_grossesse')
        self.fields['analgesie'].queryset = ListeChoixActif.objects.filter(champ='analgesie')
        self.fields['indications'].queryset = ListeChoixActif.objects.filter(champ='indications')
        self.fields['etat_sante_1'].queryset = ListeChoixActif.objects.filter(champ='etat_sante')
        self.fields['etat_sante_2'].queryset = ListeChoixActif.objects.filter(champ='etat_sante')
        self.fields['etat_sante_3'].queryset = ListeChoixActif.objects.filter(champ='etat_sante')
        self.fields['perinee'].queryset = ListeChoixActif.objects.filter(champ='perinee')
        self.fields['suite_couche_type'].queryset = ListeChoixActif.objects.filter(champ='suite_couche_type')
        self.fields['suite_couche_detail'].queryset = ListeChoixActif.objects.filter(champ='suite_couche_detail')
        self.fields['evacuation_grossesse'].queryset = ListeChoixActif.objects.filter(champ='evacuation_grossesse')


class ConsultationColposcopieForm(ConsultationForm):
    indications = forms.ModelChoiceField(queryset=None, required=False)
    test_hpv = forms.ModelChoiceField(queryset=None, required=False)
    examen_sans_preparation = forms.ModelChoiceField(queryset=None, required=False)
    acide_acetique = forms.ModelChoiceField(queryset=None, required=False)
    tag = forms.ModelChoiceField(queryset=None, required=False)
    localisation = forms.ModelChoiceField(queryset=None, required=False)
    lugol = forms.ModelChoiceField(queryset=None, required=False)

    class Meta:
        model = ConsultationColposcopie
        fields = '__all__'
        widgets = {
            'patient': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['indications'].queryset = ListeChoixActif.objects.filter(champ='indications_colposcopie')
        self.fields['test_hpv'].queryset = ListeChoixActif.objects.filter(champ='test_hpv')
        self.fields['examen_sans_preparation'].queryset = ListeChoixActif.objects.filter(champ='examen_sans_preparation')
        self.fields['acide_acetique'].queryset = ListeChoixActif.objects.filter(champ='acide_acetique')
        self.fields['tag'].queryset = ListeChoixActif.objects.filter(champ='tag')
        self.fields['localisation'].queryset = ListeChoixActif.objects.filter(champ='localisation')
        self.fields['lugol'].queryset = ListeChoixActif.objects.filter(champ='lugol')


class MyomeForm(forms.ModelForm):
    situation = forms.ModelChoiceField(queryset=None, required=False)
    type_figo = forms.ModelChoiceField(queryset=None, required=False)
    situation_coupe_longitudinale = forms.ModelChoiceField(queryset=None, required=False)
    situation_coupe_transversale = forms.ModelChoiceField(queryset=None, required=False)
    contours = forms.ModelChoiceField(queryset=None, required=False)
    structure = forms.ModelChoiceField(queryset=None, required=False)
    calcifications = forms.ModelChoiceField(queryset=None, required=False)
    vascularisation = forms.ModelChoiceField(queryset=None,  required=False)

    class Meta:
        model = Myome
        exclude = ('id',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['situation'].queryset = ListeChoixActif.objects.filter(champ='situation')
        self.fields['type_figo'].queryset = ListeChoixActif.objects.filter(champ='type_figo')
        self.fields['situation_coupe_longitudinale'].queryset = ListeChoixActif.objects.filter(champ='situation_coupe_longitudinale')
        self.fields['situation_coupe_transversale'].queryset = ListeChoixActif.objects.filter(champ='situation_coupe_transversale')
        self.fields['contours'].queryset = ListeChoixActif.objects.filter(champ='contours')
        self.fields['structure'].queryset = ListeChoixActif.objects.filter(champ='structure')
        self.fields['calcifications'].queryset = ListeChoixActif.objects.filter(champ='calcifications')
        self.fields['vascularisation'].queryset = ListeChoixActif.objects.filter(champ='vascularisation')


class EchoPelvienneBaseForm(ConsultationForm):
    titre_echo_pelvienne = forms.ModelChoiceField(queryset=None, required=False)
    position_uterus = forms.ModelChoiceField(queryset=None, required=False)
    lateralisation = forms.ModelChoiceField(queryset=None, required=False)
    volume_uterin_commentaire = forms.ModelChoiceField(queryset=None, required=False)
    asymetrie = forms.ModelChoiceField(queryset=None, required=False)
    mobilite = forms.ModelChoiceField(queryset=None, required=False)
    structures = forms.ModelChoiceField(queryset=None, required=False)
    cavite = forms.ModelChoiceField(queryset=None, required=False)
    malformation = forms.ModelChoiceField(queryset=None, required=False)
    ligne_cavitaire = forms.ModelChoiceField(queryset=None, required=False)
    type_dispositif_intra_uterin = forms.ModelChoiceField(queryset=None, required=False)
    localisation_dispositif_intra_uterin = forms.ModelChoiceField(queryset=None, required=False)
    anomalies_dispositif_intra_uterin = forms.ModelChoiceField(queryset=None, required=False)
    endometre_visualisation = forms.ModelChoiceField(queryset=None, required=False)
    endometre_echogenicite = forms.ModelChoiceField(queryset=None, required=False)
    col_aspect = forms.ModelChoiceField(queryset=None, required=False)
    col_vascularisation = forms.ModelChoiceField(queryset=None, required=False)
    ovaire_gauche_visibilite = forms.ModelChoiceField(queryset=None, required=False)
    ovaire_gauche_aspect = forms.ModelChoiceField(queryset=None, required=False)
    ovaire_gauche_mobilite = forms.ModelChoiceField(queryset=None, required=False)
    ovaire_gauche_accessibilite = forms.ModelChoiceField(queryset=None, required=False)
    ovaire_gauche_follicules = forms.ModelChoiceField(queryset=None, required=False)
    ovaire_droit_visibilite = forms.ModelChoiceField(queryset=None, required=False)
    ovaire_droit_aspect = forms.ModelChoiceField(queryset=None, required=False)
    ovaire_droit_mobilite = forms.ModelChoiceField(queryset=None, required=False)
    ovaire_droit_accessibilite = forms.ModelChoiceField(queryset=None, required=False)
    ovaire_droit_follicules = forms.ModelChoiceField(queryset=None, required=False)
    cul_de_sac_latero = forms.ModelChoiceField(queryset=None, required=False)
    adenomyose = forms.MultipleChoiceField(choices=[], required=False)
    adenomyose_conclusion = forms.MultipleChoiceField(choices=[], required=False)

    class Meta:
        model = ConsultationEchoPelvienneBase
        fields = '__all__'
        widgets = {
            'patient': forms.HiddenInput(),
            'ovaire_gauche_follicules_list': forms.HiddenInput(),
            'ovaire_droit_follicules_list': forms.HiddenInput(),
            'dispositif_intra_tubaire': forms.CheckboxInput(),

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['titre_echo_pelvienne'].queryset = ListeChoixActif.objects.filter(champ='titre_echo_pelvienne')
        self.fields['position_uterus'].queryset = ListeChoixActif.objects.filter(champ='position_uterus')
        self.fields['lateralisation'].queryset = ListeChoixActif.objects.filter(champ='lateralisation')
        self.fields['volume_uterin_commentaire'].queryset = ListeChoixActif.objects.filter(champ='volume_uterin_commentaire')
        self.fields['asymetrie'].queryset = ListeChoixActif.objects.filter(champ='asymetrie')
        self.fields['mobilite'].queryset = ListeChoixActif.objects.filter(champ='mobilite')
        self.fields['structures'].queryset = ListeChoixActif.objects.filter(champ='structures')
        self.fields['cavite'].queryset = ListeChoixActif.objects.filter(champ='cavite')
        self.fields['malformation'].queryset = ListeChoixActif.objects.filter(champ='malformation')
        self.fields['ligne_cavitaire'].queryset = ListeChoixActif.objects.filter(champ='ligne_cavitaire')
        self.fields['type_dispositif_intra_uterin'].queryset = ListeChoixActif.objects.filter(champ='type_dispositif_intra_uterin')
        self.fields['localisation_dispositif_intra_uterin'].queryset = ListeChoixActif.objects.filter(champ='localisation_dispositif_intra_uterin')
        self.fields['anomalies_dispositif_intra_uterin'].queryset = ListeChoixActif.objects.filter(champ='anomalies_dispositif_intra_uterin')
        self.fields['endometre_visualisation'].queryset = ListeChoixActif.objects.filter(champ='endometre_visualisation')
        self.fields['endometre_echogenicite'].queryset = ListeChoixActif.objects.filter(champ='endometre_echogenicite')
        self.fields['col_aspect'].queryset = ListeChoixActif.objects.filter(champ='col_aspect')
        self.fields['col_vascularisation'].queryset = ListeChoixActif.objects.filter(champ='col_vascularisation')
        self.fields['cul_de_sac_latero'].queryset = ListeChoixActif.objects.filter(champ='cul_de_sac_latero')
        self.fields['ovaire_gauche_visibilite'].queryset = ListeChoixActif.objects.filter(champ='ovaire_visibilite')
        self.fields['ovaire_gauche_aspect'].queryset = ListeChoixActif.objects.filter(champ='ovaire_aspect')
        self.fields['ovaire_gauche_mobilite'].queryset = ListeChoixActif.objects.filter(champ='ovaire_mobilite')
        self.fields['ovaire_gauche_accessibilite'].queryset = ListeChoixActif.objects.filter(champ='ovaire_accessibilite')
        self.fields['ovaire_gauche_follicules'].queryset = ListeChoixActif.objects.filter(champ='ovaire_follicules')
        self.fields['ovaire_droit_visibilite'].queryset = ListeChoixActif.objects.filter(champ='ovaire_visibilite')
        self.fields['ovaire_droit_aspect'].queryset = ListeChoixActif.objects.filter(champ='ovaire_aspect')
        self.fields['ovaire_droit_mobilite'].queryset = ListeChoixActif.objects.filter(champ='ovaire_mobilite')
        self.fields['ovaire_droit_accessibilite'].queryset = ListeChoixActif.objects.filter(champ='ovaire_accessibilite')
        self.fields['ovaire_droit_follicules'].queryset = ListeChoixActif.objects.filter(champ='ovaire_follicules')


class ConsultationEchoPelvienneForm(EchoPelvienneBaseForm):

    class Meta(EchoPelvienneBaseForm.Meta):
        model = ConsultationEchoPelvienne
        fields = '__all__'


class ConsultationGynecologiqueForm(EchoPelvienneBaseForm):
    motif_consultation = forms.ModelChoiceField(queryset=ListeChoixActif.objects.filter(champ='motif_consultation'),
                                                required=False)
    partenaire = forms.ModelChoiceField(queryset=ListeChoixActif.objects.filter(champ='partenaire'), required=False)
    cycles = forms.ModelChoiceField(queryset=ListeChoixActif.objects.filter(champ='cycles'), required=False)
    syndrome_premenstruel = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(champ='syndrome_premenstruel'),
        required=False)
    abondance = forms.ModelChoiceField(queryset=ListeChoixActif.objects.filter(champ='abondance'), required=False)
    douleur = forms.ModelChoiceField(queryset=ListeChoixActif.objects.filter(champ='douleur'), required=False)
    mode_contraception = forms.ModelChoiceField(queryset=ListeChoixActif.objects.filter(champ='mode_contraception'),
                                                required=False)
    observance = forms.ModelChoiceField(queryset=ListeChoixActif.objects.filter(champ='observance'), required=False)
    satisfaction = forms.ModelChoiceField(queryset=ListeChoixActif.objects.filter(champ='satisfaction'), required=False)
    effets_indesirables = forms.ModelChoiceField(queryset=ListeChoixActif.objects.filter(champ='effets_indesirables'),
                                                 required=False)
    examen_sous_speculum = forms.ModelChoiceField(queryset=ListeChoixActif.objects.filter(champ='examen_sous_speculum'),
                                                  required=False)
    seins = forms.ModelChoiceField(queryset=ListeChoixActif.objects.filter(champ='seins'), required=False)
    leuco = forms.MultipleChoiceField(
                required=False)
    presence_rapports_sexuels = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(champ='presence_rapports_sexuels'), required=False)

    class Meta(EchoPelvienneBaseForm.Meta):
        model = ConsultationGynecologique
        fields = '__all__'
        widgets = {
            'patient': forms.HiddenInput(),
            'ovaire_gauche_follicules_list': forms.HiddenInput(),
            'ovaire_droit_follicules_list': forms.HiddenInput(),
            'dispositif_intra_tubaire': forms.CheckboxInput(),
            'adenomyose': forms.CheckboxSelectMultiple(
                ),
            'adenomyose_conclusion': forms.CheckboxSelectMultiple(
                ),
            'traitements': forms.HiddenInput(),
            'examens': forms.HiddenInput(),
            'leuco': forms.CheckboxSelectMultiple(
                ),
        }


class GrossesseForm(forms.ModelForm):
    caryotype_type = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='grossesse', champ='caryotype'), required=False)
    conception_v2 = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='grossesse', champ='conception'), required=False)
    type_grossesse_v2 = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='grossesse', champ='type_grossesse'), required=False)
    score_herman_1_v2 = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='grossesse', champ='score_herman'), required=False)
    score_herman_2_v2 = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='grossesse', champ='score_herman'), required=False)
    score_herman_3_v2 = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='grossesse', champ='score_herman'), required=False)
    msres_1_type_v2 = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='grossesse', champ='msres_1_type'), required=False)
    msres_2_type_v2 = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='grossesse', champ='msres_2_type'), required=False)
    diabete_v2 = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='grossesse', champ='diabete'), required=False)

    class Meta:
        model = Grossesse
        exclude = ('encours',)
        widgets = {
            'patient': forms.HiddenInput(),
            'lieu_accouchement': forms.HiddenInput(),
            'tabac': forms.CheckboxInput(),
            'listeria': forms.CheckboxInput(),
            'toxoplasmose': forms.CheckboxInput(),
            'cmv': forms.CheckboxInput(),
            'alcool': forms.CheckboxInput(),
            'epp': forms.CheckboxInput(),
            'ppo': forms.CheckboxInput(),
            'adp': forms.CheckboxInput(),
            'aspegic': forms.CheckboxInput(),
            'allaitement_maternel': forms.CheckboxInput(),
            'allaitement_artificiel': forms.CheckboxInput(),
        }


class DonneesFoetusForm(forms.ModelForm):
    presentation = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='presentation'),
        required=False)
    activite_cardiaque = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='activite_cardiaque'),
        required=False)
    mobilite = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='mobilite'), required=False)
    doppler_cordon_diastole = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='doppler_cordon_diastole'),
        required=False)
    doppler_dv_onde = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='doppler_dv_onde'),
        required=False)
    morpho_crane = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='morpho_crane'),
        required=False)
    morpho_struct = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='morpho_struct'),
        required=False)
    morpho_face = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='morpho_face'),
        required=False)
    morpho_cou = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='morpho_cou'),
        required=False)
    morpho_thorax = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='morpho_thorax'),
        required=False)
    morpho_coeur = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='morpho_coeur'),
        required=False)
    morpho_abdo = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='morpho_abdo'),
        required=False)
    morpho_digest = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='morpho_digest'),
        required=False)
    morpho_urine = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='morpho_urine'),
        required=False)
    morpho_rachis = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='morpho_rachis'),
        required=False)
    morpho_membres = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='morpho_membres'),
        required=False)
    morpho_oge = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='morpho_oge'),
        required=False)
    morpho_pole_cepha = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='morpho_pole_cepha'),
        required=False)
    morpho_lmc = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='morpho_lmc'),
        required=False)
    morpho_liquide_amnio = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='morpho_liquide_amnio'),
        required=False)
    morpho_placenta = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='morpho_placenta'),
        required=False)
    morpho_cordon = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='morpho_cordon'),
        required=False)
    morpho_trophoblaste_localisation = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus',
                                                champ='morpho_trophoblaste_localisation'), required=False)
    morpho_trophoblaste_aspect = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus',
                                                champ='morpho_trophoblaste_aspect'), required=False)
    morpho_decol = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_foetus', champ='morpho_decol'),
        required=False)

    class Meta:
        model = DonneesFoetus
        #fields = '__all__'
        exclude = ('id',)


DonneesFoetusFormset = inlineformset_factory(ConsultationObstetrique, DonneesFoetus, DonneesFoetusForm,
                                             fields='__all__', extra=3, max_num=3, min_num=3)


class ConsultationObstetriqueForm(ConsultationForm):
    col_entonnoir = forms.ModelChoiceField(queryset=ListeChoixActif.objects.filter(champ='col_entonnoir'),
                                           required=False)
    pelvis_maternel = forms.ModelChoiceField(queryset=ListeChoixActif.objects.filter(champ='pelvis_maternel'),
                                           required=False)
    notch_droit = forms.ModelChoiceField(queryset=ListeChoixActif.objects.filter(champ='notch'), required=False)
    notch_gauche = forms.ModelChoiceField(queryset=ListeChoixActif.objects.filter(champ='notch'), required=False)

    examen_sous_speculum = forms.ModelChoiceField(queryset=ListeChoixActif.objects.filter(champ='examen_sous_speculum'),
                                                  required=False)
    seins = forms.ModelChoiceField(queryset=ListeChoixActif.objects.filter(champ='seins'), required=False)
    leuco = forms.MultipleChoiceField(

        required=False)

    class Meta:
        model = ConsultationObstetrique
        fields = '__all__'
        widgets = {
            'patient': forms.HiddenInput(),
            'grossesse': forms.HiddenInput(),
            'rdv_suivant_apres': forms.HiddenInput(),
            'rdv_suivant_avant': forms.HiddenInput(),
        }


class ConsultationEcho11SAForm(ConsultationObstetriqueForm):
    sac_gestationnel_localisation = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_11SA',
                                                champ='sac_gestationnel_localisation'), required=False)
    sac_gestationnel_tonicite = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_11SA', champ='sac_gestationnel_tonicite'),
        required=False)
    sac_gestationnel_trophoblaste = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_11SA',
                                                champ='sac_gestationnel_trophoblaste'), required=False)
    sac_gestationnel_decollement = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_11SA',
                                                champ='sac_gestationnel_decollement'), required=False)
    morpho_extremite_cephalique = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_11SA',
                                                champ='morpho_extremite_cephalique'), required=False)
    morpho_membres = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_11SA', champ='morpho_membres'),
        required=False)
    activite_cardiaque = forms.ModelChoiceField(
        queryset=ListeChoixActif.objects.filter(formulaire='consultation_obs_11SA', champ='activite_cardiaque'),
        required=False)
    embryon_visible = forms.BooleanField(widget=forms.CheckboxInput, initial=True, required=False)

    class Meta(ConsultationObstetriqueForm.Meta):
        model = ConsultationEcho11SA
        fields = '__all__'


class ConsultationEchoPremierTrimestreForm(ConsultationObstetriqueForm):
    class Meta(ConsultationObstetriqueForm.Meta):
        model = ConsultationEchoPremierTrimestre
        fields = '__all__'


class ConsultationEchoDeuxiemeTrimestreForm(ConsultationObstetriqueForm):
    class Meta(ConsultationObstetriqueForm.Meta):
        model = ConsultationEchoDeuxiemeTrimestre
        fields = '__all__'


class ConsultationEchoTroisiemeTrimestreForm(ConsultationObstetriqueForm):
    class Meta(ConsultationObstetriqueForm.Meta):
        model = ConsultationEchoTroisiemeTrimestre
        fields = '__all__'


class ConsultationEchoCroissanceForm(ConsultationObstetriqueForm):
    class Meta(ConsultationObstetriqueForm.Meta):
        model = ConsultationEchoCroissance
        fields = '__all__'


class ConsultationEchoColForm(ConsultationForm):
    pass


class ConsultationEchoCardiofoetaleForm(ConsultationForm):
    pass


class ConsultationGrossesseForm(ConsultationForm):
    pass


class ReglementForm(forms.ModelForm):
    total = forms.FloatField(required=False)

    class Meta:
        model = Reglement
        fields = ['admission', 'patient', 'praticien', 'note', 'mutuelle', 'nom_mutuelle', 'espece_payment', 'cheque_payment',
                  'cb_payment', 'cheque_number', 'titulaire', 'date_cheque', 'total']
        widgets = {
            'admission': forms.HiddenInput(),
            'patient': forms.HiddenInput(),
            'praticien': forms.HiddenInput(),
        }


class LigneReglementForm(forms.ModelForm):
    class Meta:
        model = LigneReglement
        fields = ['prestation', 'code', 'prix_ttc', 'reglement', 'prix_initial']


class PrescriptionAnalyseBiologiqueForm(forms.ModelForm):
    class Meta:
        model = PrescriptionAnalyseBiologique
        fields = '__all__'


class AnalyseBiologiqueForm(forms.ModelForm):
    class Meta:
        model = AnalyseBiologique
        fields = ['code', 'libelle', 'type', 'unite', 'modele_resultat', 'ordre']


class CollectionAnalyseBiologiqueForm(forms.ModelForm):
    ordre = forms.CharField(required=False)

    class Meta:
        model = CollectionAnalyseBiologique
        fields = ['nom', 'analyses', 'ordre']
        widgets = {
            'ordre': forms.HiddenInput()
        }


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        exclude = ('compte',)


class ListeChoixForm(forms.ModelForm):
    class Meta:
        model = ListeChoix
        exclude = ('actif',)
        widgets = {
            'formulaire': forms.HiddenInput(),
            'champ': forms.HiddenInput()
        }


class TemplateEditionForm(forms.ModelForm):
    class Meta:
        model = TemplateEdition
        fields = ['libelle', 'categorie_consultation', 'motif_consultation', 'contenu']


class InterrogatoirePMAForm(forms.ModelForm):
    class Meta:
        model = InterrogatoirePMA
        fields = '__all__'
        widgets = {
            'sperme_congenalation_clinique': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        compte = kwargs.pop('compte')
        super().__init__(*args, **kwargs)
        self.fields['praticien'].queryset = Medecin.objects.filter(compte=compte)
        self.fields['date'].required = False


class TentativesHistoriquesPMAForm(forms.ModelForm):
    class Meta:
        model = TentativesHistoriquesPMA
        fields = '__all__'


class BilanEndocrinienPMAFemininForm(forms.ModelForm):
    class Meta:
        model = BilanEndocrinienPMAFeminin
        fields = '__all__'


class BilanEndocrinienPMAMasculinForm(forms.ModelForm):
    class Meta:
        model = BilanEndocrinienPMAMasculin
        fields = '__all__'


class SpermogrammePMAForm(forms.ModelForm):
    class Meta:
        model = SpermogrammePMA
        fields = '__all__'


class TentativePMAForm(forms.ModelForm):
    class Meta:
        model = TentativePMA
        exclude = ('encours',)

    def __init__(self, *args, **kwargs):
        compte = kwargs.pop('compte')
        super().__init__(*args, **kwargs)
        self.fields['praticien'].queryset = Medecin.objects.filter(compte=compte)


class TentativePMAClotureForm(forms.ModelForm):
    class Meta:
        model = TentativePMA
        fields = ['reussie', 'commentaires', 'encours']
        widgets = {
            'encours': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)


class TraitementPMAForm(forms.ModelForm):
    class Meta:
        model = TraitementPMA
        fields = ['libelle']


class TraitementValeurPMAForm(forms.ModelForm):
    class Meta:
        model = TraitementValeurPMA
        fields = ['traitement', 'valeur']
        widgets = {
            'traitement': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['traitement'].required = False


class SuiviTraitementPMAForm(forms.ModelForm):
    class Meta:
        model = SuiviTraitementPMA
        fields = ['date', 'traitments_valeurs', 'oestradiol', 'lh', 'progesterone', 'ovaire_droit', 'ovaire_gauche',
                  'endometre']


class BaseTraitementValeurFormset(BaseInlineFormSet):

    def save(self, commit=True):
        for form in self.forms:
            obj = form.save()
            #pprint(obj.__dict__)


TraitementValeurPMACreateFormset = inlineformset_factory(SuiviTraitementPMA, TraitementValeurPMA,
                                                         form=TraitementValeurPMAForm,
                                                         max_num=7, min_num=7,
                                                         can_delete=False,
                                                         formset=BaseTraitementValeurFormset,
                                                         extra=7)

TraitementValeurPMAUpdateFormset = inlineformset_factory(SuiviTraitementPMA, TraitementValeurPMA,
                                                         form=TraitementValeurPMAForm,
                                                         can_delete=False,
                                                         formset=BaseTraitementValeurFormset,
                                                         extra=0)


class BaseSuiviTraitementFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = True
            if hasattr(form, 'nested'):
                form.nested.empty_permitted = True

    def is_valid(self):
        result = super().is_valid()

        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    if not form.nested.is_valid():
                        print(form.nested.errors)
                    result = result and form.nested.is_valid()

        return result

    def save(self, commit=True):
        result = super().save(commit=commit)
        for form in self.forms:
            if hasattr(form, 'nested'):
                #if not self._should_delete_form(form):
                form.nested.save(commit=commit)

        return result


class BaseSuiviTraitementCreateFormSet(BaseSuiviTraitementFormSet):

    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.nested = TraitementValeurPMACreateFormset(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix='%s-%s' % (
                form.prefix,
                TraitementValeurPMACreateFormset.get_default_prefix())
        )


class BaseSuiviTraitementUpdateFormSet(BaseSuiviTraitementFormSet):

    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.nested = TraitementValeurPMAUpdateFormset(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix='%s-%s' % (
                form.prefix,
                TraitementValeurPMAUpdateFormset.get_default_prefix())
        )


class MesuresPatientForm(forms.ModelForm):

    class Meta:
        model = MesuresPatient
        exclude = ('date',)
        widgets = {
            'patient': forms.HiddenInput(),
        }
