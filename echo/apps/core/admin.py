import csv
from io import TextIOWrapper

from django.contrib import admin

# Register your models here.
from django.forms import forms
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import path

from apps.core.models import *


class BaseModelAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return self.model.objects_with_deleted.all()


admin.site.register(Compte)
admin.site.register(Profil)
admin.site.register(Adresse)
admin.site.register(Consultation, BaseModelAdmin)
admin.site.register(Rdv)
admin.site.register(MotifRdv)
admin.site.register(ParametresCompte)
admin.site.register(MotifConsultation)
admin.site.register(CategorieConsultation)
admin.site.register(FormulaireConsultation)
admin.site.register(CatgeorieAntecedent)
admin.site.register(SousCatgeorieAntecedent)
admin.site.register(Antecedent)
admin.site.register(DossierFichiersPatient)
admin.site.register(FichierPatient)
admin.site.register(Admission)
admin.site.register(PhrasierAntecedent)
admin.site.register(Ordonnance)
admin.site.register(Prestation)
admin.site.register(Reglement)
admin.site.register(LigneReglement)
admin.site.register(Facture)
admin.site.register(Cloture)
# admin.site.register(Traitement)
# admin.site.register(Prescription)
admin.site.register(Certificat)
admin.site.register(Etablissement)
admin.site.register(AntecedentObstetrique)
admin.site.register(ConsultationGynecologique)
admin.site.register(ConsultationColposcopie)
admin.site.register(ConsultationEchoPelvienne)
admin.site.register(Grossesse)
admin.site.register(ConsultationEcho11SA)
admin.site.register(ConsultationEchoPremierTrimestre)
admin.site.register(ConsultationEchoDeuxiemeTrimestre)
admin.site.register(ConsultationEchoTroisiemeTrimestre)
admin.site.register(ConsultationEchoCroissance)
admin.site.register(DonneesFoetus)
admin.site.register(ImageConsultation)
#admin.site.register(AnalyseBiologique)
admin.site.register(CollectionAnalyseBiologique)
admin.site.register(PrescriptionAnalyseBiologique)
admin.site.register(Device)
admin.site.register(WorklistItem)
admin.site.register(TemplateEdition)
admin.site.register(Myome)
admin.site.register(InterrogatoirePMA)
admin.site.register(TentativePMA)
admin.site.register(SuiviTraitementPMA)
admin.site.register(TraitementValeurPMA)
admin.site.register(AbsenceMedecin)
admin.site.register(ProgrammeOperatoire)
admin.site.register(TypeOrdonnance)
admin.site.register(ResultatAnalyseBiologique)
admin.site.register(MesuresPatient)
admin.site.register(MotifAbsence)
admin.site.register(SRConsultation)
admin.site.register(Bordereau)

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


@admin.register(Traitement)
class TraitementAdmin(admin.ModelAdmin):
    change_list_template = "core/admin/traitment_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='cp1252', errors='replace')
            reader = csv.DictReader(csv_file, delimiter=',')
            entries = []
            compte_pk = -1
            compte = None
            for row in reader:
                if compte_pk != int(row['compte']):
                    compte_pk = int(row['compte'])
                    compte = get_object_or_404(Compte, pk=compte_pk)
                libelle = row['libelle']
                text = row['text']
                forme = row['forme']
                entries.append(Traitement(compte=compte, libelle=libelle, text=text, forme=forme))

            Traitement.objects.bulk_create(entries)
            self.message_user(request, "Fichier csv importé avec succès")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "core/admin/csv_form.html", payload
        )


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    change_list_template = "core/admin/traitment_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='cp1252', errors='replace')
            reader = csv.DictReader(csv_file, delimiter=';')
            entries = []
            compte_pk = -1
            compte = None
            for row in reader:
                if compte_pk != int(row['compte']):
                    compte_pk = int(row['compte'])
                    compte = get_object_or_404(Compte, pk=compte_pk)
                libelle = row['libelle']
                text = row['text']
                categorie = row['categorie']
                entries.append(Prescription(compte=compte, libelle=libelle, text=text, categorie=categorie))

            Prescription.objects.bulk_create(entries)
            self.message_user(request, "Fichier csv importé avec succès")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "core/admin/csv_form.html", payload
        )


@admin.register(AnalyseBiologique)
class AnalyseBiologiqueAdmin(admin.ModelAdmin):
    change_list_template = "core/admin/analyse_biologique_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='cp1252', errors='replace')
            reader = csv.DictReader(csv_file, delimiter=';')
            entries = []
            compte_pk = -1
            compte = None
            for row in reader:
                if compte_pk != int(row['compte']):
                    compte_pk = int(row['compte'])
                    compte = get_object_or_404(Compte, pk=compte_pk)
                libelle = row['libelle']
                code = row['code']
                type = row['type']
                unite = row['unite']
                entries.append(AnalyseBiologique(compte=compte, libelle=libelle, code=code, type=type, unite=unite))

            AnalyseBiologique.objects.bulk_create(entries)
            self.message_user(request, "Fichier csv importé avec succès")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "core/admin/csv_form.html", payload
        )


@admin.register(Patient)
class PatientAdmin(BaseModelAdmin):
    change_list_template = "core/admin/patient_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='cp1252', errors='replace')
            reader = csv.DictReader(csv_file, delimiter=';')
            entries = []
            compte_pk = -1
            compte = None

            count = 0

            for row in reader:
                if compte_pk != int(row['compte']):
                    compte_pk = int(row['compte'])
                    compte = get_object_or_404(Compte, pk=compte_pk)

                p = Patient()
                p.compte = compte
                p.nom = row['nom_marital']
                p.nom_naissance = row['nom_naissance']
                p.prenom = row['prenom']
                try:
                    p.date_naissance = datetime.datetime.strptime(row['date_naissance'], '%d/%m/%Y').strftime('%Y-%m-%d')
                except Exception:
                    p.date_naissance = '1900-01-01'
                try:
                    p.telephone = row['telephone']
                except Exception:
                    pass
                try:
                    p.telephone_secondaire = row['telephone_secondaire']
                except Exception:
                    pass
                try:
                    p.ancien_numero = row['ancien_numero']
                except Exception:
                    pass

                count = count + 1
                entries.append(p)
                if count == 1000:
                    Patient.objects.bulk_create(entries)
                    entries = []
                    count = 0

            Patient.objects.bulk_create(entries)
            self.message_user(request, "Fichier csv importé avec succès")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "core/admin/csv_form.html", payload
        )
