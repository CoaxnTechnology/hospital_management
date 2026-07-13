from json import JSONEncoder

from rest_framework import serializers
from apps.core.models import *


class ParametresCompteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParametresCompte
        fields = '__all__'
        depth = 0


class ProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profil
        fields = ['pk', 'titre_nom', 'initiales', 'groupe', 'enligne']
        depth = 1


class PraticienSerializer(serializers.ModelSerializer):

    class Meta:
        model = Praticien
        fields = ['id', 'nom', 'prenom', 'nom_complet', 'specialite', 'telephone', 'email']
        depth = 1


class EtablissementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etablissement
        fields = '__all__'
        depth = 0


class BaseGrossesseSerializer(serializers.ModelSerializer):
    nb_foetus = serializers.CharField(source='get_nb_foetus_display')
    terme = serializers.CharField(source='terme_disp')
    ddg = serializers.CharField(source='get_ddg')
    type_grossesse = serializers.CharField(source='get_type_grossesse_display')
    ddr = serializers.CharField(source='get_ddr')
    lieu_accouchement = EtablissementSerializer(read_only=True)

    class Meta:
        model = Grossesse
        fields = '__all__'
        depth = 1


class LigneReglementSerializer(serializers.ModelSerializer):
    class Meta:
        model = LigneReglement
        fields = '__all__'
        depth = 1


class LigneReglementRapportSerializer(serializers.ModelSerializer):
    class Meta:
        model = LigneReglement
        fields = ['prestation', 'prix_ttc']
        depth = 1


class FactureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facture
        fields = '__all__'
        depth = 0


class PatientSerializerBasic(serializers.ModelSerializer):
    lien_parente = serializers.CharField(source='get_lien_parente_display')
    nom_complet = serializers.ReadOnlyField()

    class Meta:
        model = Patient
        fields = '__all__'
        depth = 1


class ReglementSerializer(serializers.ModelSerializer):
    lignes_reglement = LigneReglementSerializer(many=True, read_only=True)
    factures = FactureSerializer(many=True, read_only=True)
    somme_payee = serializers.ReadOnlyField()
    patient = PatientSerializerBasic()
    total = serializers.ReadOnlyField()
    ticket_moderateur = serializers.ReadOnlyField()
    prise_en_charge = serializers.ReadOnlyField()

    class Meta:
        model = Reglement
        fields = '__all__'
        depth = 1


class PatientReglementRapportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = ['nom', 'nom_complet', 'mot_cle']
        depth = 0


class ReglementRapportSerializer(serializers.ModelSerializer):
    lignes_reglement = LigneReglementRapportSerializer(many=True, read_only=True)
    somme_payee = serializers.ReadOnlyField()
    patient = PatientReglementRapportSerializer()

    class Meta:
        model = Reglement
        fields = ['id', 'date_creation', 'somme_payee', 'lignes_reglement', 'patient', 'mutuelle', 'factures']
        depth = 1


class MesuresPatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = MesuresPatient
        fields = '__all__'
        depth = 0


class PatientSerializer(serializers.ModelSerializer):
    praticiens_correspondants = PraticienSerializer(many=True, read_only=True)
    origine = serializers.CharField(source='get_origine_display')
    grossesse_encours = BaseGrossesseSerializer()
    mesures_jour = MesuresPatientSerializer()
    reglement_set = ReglementSerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'identifiant_unique', 'civilite', 'prenom', 'nom', 'nom_naissance', 'date_naissance', 'age',
                  'sexe', 'adresse', 'telephone', 'nouveau', 'praticiens_correspondants', 'mot_cle', 'nom_complet',
                  'fumeur', 'groupe_sanguin', 'origine', 'taille', 'poids', 'imc', 'grossesse_encours', 'ancien_numero',
                  'mesures_jour', 'reglement_set', 'nom_complet']
        depth = 1


class GrossesseSerializer(BaseGrossesseSerializer):
    patient = PatientSerializer(read_only=True)


class PatientSerializerRapport(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'identifiant_unique', 'nom', 'nom_naissance', 'prenom']
        depth = 0


class GrossesseRapportSerializer(serializers.ModelSerializer):
    terme = serializers.CharField(source='terme_disp')
    type_grossesse = serializers.CharField(source='get_type_grossesse_display')
    ddr = serializers.CharField(source='get_ddr')
    lieu_accouchement = EtablissementSerializer(read_only=True)
    patient = PatientSerializerRapport(read_only=True)

    class Meta:
        model = Grossesse
        fields = ['patient', 'ddr', 'type_grossesse', 'lieu_accouchement', 'terme', 'cycle']
        depth = 1




class MotifSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotifConsultation
        fields = '__all__'
        depth = 1


class MotifRapportSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotifConsultation
        fields = ['code', 'libelle', 'categorie']
        depth = 1


class MedecinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medecin
        fields = ['id', 'nom', 'signature', 'ajouter_signature_edition']
        depth = 1


class MotifRdvSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotifRdv
        fields = '__all__'
        depth = 0


class AdmissionSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    praticien = MedecinSerializer(read_only=True)

    class Meta:
        model = Admission
        fields = ['id', 'numero', 'date', 'debut_consultation', 'patient', 'praticien', 'ordre', 'statut', 'reglements', 'motif']
        depth = 1


class PatientAdmissionReglementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['nom', 'nom_naissance', 'prenom', 'nom_complet']
        depth = 1


class AdmissionRapportSerializer(serializers.ModelSerializer):
    patient = PatientAdmissionReglementSerializer(read_only=True)
    reglements = ReglementRapportSerializer(required=True, many=True)

    class Meta:
        model = Admission
        fields = ['id', 'numero', 'date', 'patient', 'statut', 'nb_reglements', 'reglements']
        depth = 1


class ProgrammeOperatoireSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    praticien = MedecinSerializer(read_only=True)
    lieu_accouchement = EtablissementSerializer(read_only=True)

    class Meta:
        model = ProgrammeOperatoire
        fields = '__all__'
        depth = 1


class ConsultationSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    praticien = MedecinSerializer(read_only=True)

    class Meta:
        model = Consultation
        fields = '__all__'
        depth = 2


class ConsultationRapportSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    praticien = MedecinSerializer(read_only=True)
    motif = MotifRapportSerializer(read_only=True)

    class Meta:
        model = Consultation
        fields = ['id', 'date', 'patient', 'motif', 'praticien']
        depth = 1


class PhrasierSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhrasierAntecedent
        fields = '__all__'
        depth = 1


class OrdonnanceSerializer(serializers.ModelSerializer):
    praticien = MedecinSerializer(read_only=True)

    class Meta:
        model = Ordonnance
        fields = '__all__'
        depth = 1


class TraitementSerializer(serializers.ModelSerializer):
    forme = serializers.CharField(source='get_forme_display')

    class Meta:
        model = Traitement
        fields = '__all__'
        depth = 0


class PrestationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prestation
        fields = '__all__'
        depth = 1


class MotifAbsenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotifAbsence
        fields = '__all__'
        depth = 1


class PrescriptionSerializer(serializers.ModelSerializer):
    categorie = serializers.CharField(source='get_categorie_display')

    class Meta:
        model = Prescription
        fields = '__all__'
        depth = 0


class CertificatSerializer(serializers.ModelSerializer):
    praticien = MedecinSerializer(read_only=True)
    type = serializers.CharField(source='get_type_display')

    class Meta:
        model = Certificat
        fields = '__all__'
        depth = 1


class ListeChoixSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeChoix
        fields = '__all__'
        depth = 1


class SousCategorieAntecedentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SousCatgeorieAntecedent
        fields = '__all__'
        depth = 1


class AntecedentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Antecedent
        fields = '__all__'
        depth = 1


class AntecedentObstetriqueSerializer(serializers.ModelSerializer):

    class Meta:
        model = AntecedentObstetrique
        fields = '__all__'
        depth = 1


class ConsultationObstetriqueSerializer(ConsultationSerializer):
    grossesse = GrossesseSerializer(read_only=True)
    terme = serializers.CharField()

    class Meta:
        model = ConsultationObstetrique
        fields = '__all__'
        depth = 1


class ClotureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cloture
        fields = ['id', 'date_cloture', 'total', 'periode']
        depth = 1


class BordereauSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bordereau
        fields = ['id', 'bordereau_id', 'nom_medecin', 'code_conventionnel', 'date_bordereau', 'periode',
                  'num_bordereau', 'periode_format']
        depth = 1


class ImageConsultationSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ImageConsultation
        fields = '__all__'
        depth = 1

    def get_url(self, image):
        request = self.context.get('request')
        url = image.image.url
        return url


class ImageConsultationSerializerLight(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ImageConsultation
        fields = '__all__'
        depth = 0

    def get_url(self, image):
        request = self.context.get('request')
        url = ''
        try:
            url = image.image.url
        except:
            pass
        return url


class SRConsultationSerializer(serializers.ModelSerializer):

    class Meta:
        model = SRConsultation
        fields = '__all__'
        depth = 0


# subclass JSONEncoder
class DateTimeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


class AnalyseBiologiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyseBiologique
        fields = '__all__'
        depth = 0


class CollectionAnalyseBiologiqueSerializer(serializers.ModelSerializer):
    analyses_list = AnalyseBiologiqueSerializer(many=True, read_only=True)

    class Meta:
        model = CollectionAnalyseBiologique
        fields = '__all__'
        depth = 1


class ResultatAnalyseBiologiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultatAnalyseBiologique
        fields = '__all__'
        depth = 1


class WorklistItemSerializer(serializers.ModelSerializer):
    consultation = ConsultationSerializer(read_only=True)

    class Meta:
        model = WorklistItem
        fields = '__all__'
        depth = 1


class DeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = '__all__'
        depth = 0


class TemplateEditionSerializer(serializers.ModelSerializer):

    class Meta:
        model = TemplateEdition
        fields = '__all__'
        depth = 1


class TraitementPMASerializer(serializers.ModelSerializer):
    class Meta:
        model = TraitementPMA
        fields = '__all__'
        depth = 1


class TentativePMASerializer(serializers.ModelSerializer):
    praticien = MedecinSerializer(read_only=True)

    class Meta:
        model = TentativePMA
        fields = ['id', 'updated_at', 'praticien', 'reussie']
        depth = 1


class RdvSerializer(serializers.ModelSerializer):
    praticien = MedecinSerializer(read_only=True)
    statut = serializers.CharField(source='get_statut_display')

    class Meta:
        model = Rdv
        fields = '__all__'
        depth = 1

