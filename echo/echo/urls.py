"""echo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, re_path, include

from apps.core import debug
from apps.core.debug import test
from apps.core.views import profils, rdvs, accueil, patients, parametres_compte, praticiens, admissions, \
    ordonnances, traitements, prescriptions, certificats, prestations, etablissements, utils, reglements, grossesses, \
    consultations, analyses_biologiques, listes_choix, templates_edition, rapports,motifs, absence, mutuelle


from django.conf import settings

from apps.core.views.consultations import base, gynecologique, obstetrique, images, pma
from apps.core.views.devices import worklists, devices

urlpatterns = [
    # Toolbar
    path('__debug__/', include(debug_toolbar.urls)),

    # Admin
    re_path(r'^admin/clearcache/', include('clearcache.urls')),
    path('admin/', admin.site.urls),

    re_path(r'^', include('apps.chat.urls')),

    # Authentification
    path('accounts/login/', auth_views.LoginView.as_view(template_name='core/login_v2.html'), name='login'),
    path('accounts/password_reset/', auth_views.LoginView.as_view(template_name='core/login.html'),
         name='password_reset'),
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='core/login.html')),

    # Module tableau de bord
    path('accueil/', accueil.Accueil.as_view(), name='accueil-1'),
    path('', accueil.Accueil.as_view(), name='accueil'),

    # Module utilisateurs/profils
    path('utilisateurs/', profils.ProfilList.as_view(), name='profils_list'),
    path('utilisateurs/ajouter', profils.ProfilCreate.as_view(), name='profil_form'),
    path('utilisateurs/<int:pk>/modifier/', profils.ProfilUpdate.as_view(), name='profil_modifier'),
    path('utilisateurs/<int:pk>/supprimer', profils.supprimer_profil, name='profil_supprimer'),
    path('utilisateurs/<int:pk>/mdp/', profils.MotDePasseUpdate.as_view(), name='profil_modifier_mdp'),

    # Module paramètres
    path('parametres/<int:pk>', parametres_compte.ParametresGeneraux.as_view(), name='parametres_generaux'),

    # Module rendez-vous
    path('rdvs/', rdvs.RdvList.as_view(), name='rdvs_list'),
    re_path(r'rdvs/ajouter/$', rdvs.RdvCreate.as_view(), name='rdv_form'),
    path('rdvs/<int:pk>/modifier/', rdvs.RdvUpdate.as_view(), name='rdv_modifier'),
    path('rdvs/<int:pk>/modifier_horaire/', rdvs.modifier_horaire, name='rdv_modifier_horaire'),
    path('rdvs/<int:pk>/supprimer/', rdvs.supprimer_rdv, name='rdv_supprimer'),
    path('rdvs/<int:pk>/rappel/', rdvs.rappel_rdv, name='rdv_rappel'),
    re_path(r'rdvs/dispo/ajouter/$', rdvs.RdvDispoCreate.as_view(), name='rdv_dispo'),
    path('absence/ajouter/', absence.AbsenceCreate.as_view(), name='absence_form'),
    path('absences/<int:pk>/modifier/', absence.AbsenceUpdate.as_view(), name='absence_modifier'),
    path('programme_operatoire/ajouter/', absence.ProgrammeOperatoireCreate.as_view(), name='programme_operatoire_form'),
    path('programme_operatoire/<int:pk>/modifier/', absence.ProgrammeOperatoireUpdate.as_view(), name='programme_operatoire_modifier'),
    # Module patients
    path('patients/', patients.PatientList.as_view(), name='patients_list'),
    re_path(r'patients/recherche/$', patients.PatientList.as_view(), name='patients_list1'),
    re_path(r'patients/recherche_async/$', patients.rechercher_patient, name='patients_list2'),
    #path('patients/recherche/', patients.rechercher_patient, name='patients_recherche'),
    path('patients/<int:pk>/admission/', patients.admission_patient, name='patient_admission'),
    path('patients/<int:pk>/admissions/', patients.liste_admissions_patient, name='patient_admissions_list'),
    path('patients/<int:pk>/fichiers/', patients.fichiers_list, name='patient_fichiers_list'),
    path('patients/<int:pk>/telecharger/', patients.fichiers_telecharger, name='patient_fichiers_telecharger'),
    path('patients/ajouter/', patients.PatientCreate.as_view(), name='patient_form'),
    path('patients/<int:pk>/modifier', patients.PatientUpdate.as_view(), name='patient_modifier'),
    path('patients/<int:pk>/', patients.PatientView.as_view(), name='patient_afficher'),
    path('patients/<int:pk>/infos/', patients.infos_patient, name='patient_infos'),
    path('patients/<int:pk>/supprimer', patients.supprimer_patient, name='patient_supprimer'),
    path('patients/<int:pk>/antecedents', patients.enregistrer_antecedents, name='patient_enregistrer_antecedents'),
    path('patients/<int:pk>/antecedents/ajouter', patients.ajouter_antecedent, name='patient_ajouter_antecedent'),
    path('antecedent/<int:pk>/supprimer/', patients.supprimer_antecedent, name='patient_supprimer_antecedent'),
    path('patients/<int:pk>/notes', patients.enregistrer_notes, name='patient_enregistrer_notes'),
    path('patients/<int:pk>/consultation/ajouter/', consultations.base.ConsultationCreate.as_view(),
         name='consultation_form'),
    path('patients/<int:patient_pk>/consultations/', consultations.base.ConsultationList.as_view(),
         name='consultation_form'),
    path('patients/<int:pk>/consultation/enregistrer/', base.enregistrer_consultation, name='consultation_enregistrer'),
    path('patients/<int:pk>/consultation/terminer/', base.terminer_consultation, name='consultation_terminer'),
    path('patients/<int:patient_pk>/consultation/<int:pk>/modifier/', base.ConsultationUpdate.as_view(),
         name='consultation_modifier'),
    path('patients/<int:pk>/praticien/ajouter/', patients.ajouter_praticien, name='patient_praticien_ajouter'),
    path('patients/<int:pk>/fichier/ajouter/', patients.ajouter_fichier, name='patient_fichier_ajouter'),
    path('patients/<int:pk>/fichier/<int:fichier_pk>/deplacer/', patients.deplacer_fichier,
         name='patient_fichier_daplacer'),
    path('patients/<int:pk>/fichier/<int:fichier_pk>/supprimer/', patients.supprimer_fichier,
         name='patient_fichier_supprimer'),
    path('patients/<int:pk>/mot_cle/ajouter/', patients.ajouter_mot_cle, name='patient_mot_cle_ajouter'),
    path('patients/<int:pk>/mot_cle/supprimer/', patients.supprimer_mot_cle, name='patient_mot_cle_supprimer'),
    path('patients/<int:pk>/antecedent_obstetrique/ajouter/', patients.AntecedentObstetriqueCreate.as_view(), name='patient_antecedent_obstetrique_ajouter'),
    path('antecedent_obstetrique/<int:pk>/modifier', patients.AntecedentObstetriqueUpdate.as_view(), name='patient_antecedent_obstetrique_modifier'),
    path('antecedent_obstetrique/<int:pk>/supprimer/', patients.supprimer_antecedent_obstetrique, name='patient_antecedent_obstetrique_supprimer'),
    path('patients/<int:pk>/grossesse/ajouter', grossesses.GrossesseCreate.as_view(), name='patient_grossesse_ajouter'),
    path('grossesse/<int:pk>/modifier', grossesses.GrossesseUpdate.as_view(), name='patient_grossesse_modifier'),
    path('patients/<int:pk>/mesures/ajouter', patients.MesuresPatientCreate.as_view(), name='patient_mesures_ajouter'),
    path('mesures/<int:pk>/modifier', patients.MesuresPatientUpdate.as_view(), name='patient_mesures_modifier'),
    path('grossesses/<int:pk>/calendrier', grossesses.CalendrierGrossesseDetail.as_view(), name='grossesse_calendrier'),
    path('grossesses/<int:pk>/mesures/', grossesses.mesures, name='grossesse_mesures'),
    path('patients/<int:pk>/alerte/', patients.ajouter_alerte, name='patient_alerte_ajouter'),
    path('alertes/<int:pk>/supprimer/', patients.supprimer_alerte, name='patient_alerte_supprimer'),
    path('patient/<int:pk>/consultation/rechercher/', patients.rechercher_consultation, name='patient_consultation_rechercher'),

    # Analyses biologiques
    path('patients/<int:pk>/analyses/ajouter/', analyses_biologiques.PrescriptionCreate.as_view(), name='patient_analyses_ajouter'),
    path('patients/<int:pk>/analyses/', analyses_biologiques.prescriptions, name='patient_analyses_liste'),
    path('analyses/<int:pk>/modifier/', analyses_biologiques.PrescriptionUpdate.as_view(), name='patient_analyses_modifier'),
    path('analyses/<int:pk>/supprimer/', analyses_biologiques.supprimer_prescription, name='patient_analyses_supprimer'),
    path('analyses/enregistrer/', analyses_biologiques.enregistrer_prescription, name='patient_analyses_enregistrer'),
    path('analyses-biologiques/', analyses_biologiques.AnalyseBiologiqueList.as_view(), name='analyses_biologiques_liste'),
    path('analyses-biologiques/ajouter/', analyses_biologiques.AnalyseBiologiqueCreate.as_view(), name='analyses_biologiques_form'),
    path('analyses-biologiques/<int:pk>/modifier', analyses_biologiques.AnalyseBiologiqueUpdate.as_view(), name='analyses_biologiques_modifier'),
    path('analyses-biologiques/<int:pk>/supprimer', analyses_biologiques.supprimer_analyse_biologique, name='analyses_biologiques_supprimer'),
    path('analyses-biologiques/recherche/', analyses_biologiques.rechercher_analyse, name='analyses_biologiques_recherche'),
    path('collection-analyses/', analyses_biologiques.CollectionAnalyseBiologiqueList.as_view(), name='collection_analyses_liste'),
    path('collection-analyses/ajouter/', analyses_biologiques.CollectionAnalyseBiologiqueCreate.as_view(), name='collection_analyses_form'),
    path('collection-analyses/<int:pk>/modifier', analyses_biologiques.CollectionAnalyseBiologiqueUpdate.as_view(), name='collection_analyses_modifier'),
    path('collection-analyses/<int:pk>/supprimer', analyses_biologiques.supprimer_collection_analyse_biologique, name='collection_analyses_supprimer'),
    path('collection-analyses/recherche/', analyses_biologiques.rechercher_collection, name='collection_analyses_recherche'),
    path('resultats-analyses', analyses_biologiques.ajouter_resultats_analyses, name='resultats_analyses_ajouter'),
    path('resultats-analyses/<int:pk>', analyses_biologiques.modifier_resultats_analyses, name='resultats_analyses_modifier'),

    # Etablissements
    path('etablissements/', etablissements.EtablissementList.as_view(), name='etablissements_liste'),
    path('etablissements/ajouter/', etablissements.EtablissementCreate.as_view(), name='etablissement_ajouter'),
    path('etablissements/<int:pk>/modifier/', etablissements.EtablissementUpdate.as_view(),
         name='etablissement_modifier'),
    path('etablissements/<int:pk>/supprimer/', etablissements.supprimer_etablissement, name='etablissement_supprimer'),
    path('patients/<int:pk>/etablissement/associer/', etablissements.associer_etablissement,
         name='patient_associer_etablissement'),
    path('patients/<int:pk>/etablissement/dissocier/', etablissements.dissocier_etablissement,
         name='patient_dissocier_etablissement'),

    path('consultation/<int:pk>/cloturer/', base.terminer_consultation, name='consultation_cloturer'),
    path('consultation/<int:pk>/supprimer/', base.supprimer_consultation, name='consultation_supprimer'),
    path('patients/<int:pk>/consultation_gynecologique/ajouter/', gynecologique.ConsultationGynecologiqueCreate.as_view(),
         name='consultation_gynecologique_ajouter'),
    path('consultation_gynecologique/<int:pk>/modifier/', gynecologique.ConsultationGynecologiqueUpdate.as_view(),
         name='consultation_gynecologique_modifier'),
    path('patients/<int:pk>/consultation_colposcopie/ajouter/', gynecologique.ConsultationColposcopieCreate.as_view(),
         name='consultation_colposcopie_ajouter'),
    path('consultation_colposcopie/<int:pk>/modifier/', gynecologique.ConsultationColposcopieUpdate.as_view(),
         name='consultation_colposcopie_modifier'),
    path('patients/<int:pk>/consultation_echo_pelvienne/ajouter/', gynecologique.ConsultationEchoPelvienneCreate.as_view(),
         name='consultation_echo_pelvienne_ajouter'),
    path('consultation_echo_pelvienne/<int:pk>/modifier/', gynecologique.ConsultationEchoPelvienneUpdate.as_view(),
         name='consultation_echo_pelvienne_modifier'),

    # Liste de choix
    path('listes/', listes_choix.ListeChoixList.as_view(), name='liste_choix_liste'),
    path('listes/ajouter/', listes_choix.ListeChoixCreate.as_view(), name='liste_choix_ajouter'),
    path('listes/<int:pk>/modifier/', listes_choix.ListeChoixUpdate.as_view(), name='liste_choix_modifier'),
    path('listes/<int:pk>/supprimer/', listes_choix.supprimer_liste_choix, name='liste_choix_supprimer'),
    path('listes/<int:pk>/desactiver/', listes_choix.desactiver_liste_choix, name='liste_choix_desactiver'),

    # Consultations obstétriques
    # Echo < 11 SA
    path('patients/<int:pk>/consultation_obs_echo_11SA/ajouter/', obstetrique.ConsultationEcho11SACreate.as_view(), name='consultation_obs_echo_11SA_ajouter'),
    path('consultation_obs_echo_11SA/<int:pk>/modifier/', obstetrique.ConsultationEcho11SAUpdate.as_view(), name='consultation_obs_echo_11SA_modifier'),
    # Echo 1er trimestre
    path('patients/<int:pk>/consultation_obs_echo_premier_trimestre/ajouter/', obstetrique.ConsultationEchoPremierTrimestreCreate.as_view(), name='consultation_obs_echo_premier_trimestre_ajouter'),
    path('consultation_obs_echo_premier_trimestre/<int:pk>/modifier/', obstetrique.ConsultationEchoPremierTrimestreUpdate.as_view(), name='consultation_obs_echo_premier_trimestre_modifier'),
    # Echo 2eme trimestre
    path('patients/<int:pk>/consultation_obs_echo_deuxieme_trimestre/ajouter/', obstetrique.ConsultationEchoDeuxiemeTrimestreCreate.as_view(), name='consultation_obs_echo_deuxieme_trimestre_ajouter'),
    path('consultation_obs_echo_deuxieme_trimestre/<int:pk>/modifier/', obstetrique.ConsultationEchoDeuxiemeTrimestreUpdate.as_view(), name='consultation_obs_echo_deuxieme_trimestre_modifier'),
    # Echo 3eme trimestre
    path('patients/<int:pk>/consultation_obs_echo_troisieme_trimestre/ajouter/', obstetrique.ConsultationEchoTroisiemeTrimestreCreate.as_view(), name='consultation_obs_echo_troisieme_trimestre_ajouter'),
    path('consultation_obs_echo_troisieme_trimestre/<int:pk>/modifier/', obstetrique.ConsultationEchoTroisiemeTrimestreUpdate.as_view(), name='consultation_obs_echo_troisieme_trimestre_modifier'),
    # Echo de croissance
    path('patients/<int:pk>/consultation_obs_echo_croissance/ajouter/', obstetrique.ConsultationEchoCroissanceCreate.as_view(), name='consultation_obs_echo_croissance_ajouter'),
    path('consultation_obs_echo_croissance/<int:pk>/modifier/', obstetrique.ConsultationEchoCroissanceUpdate.as_view(), name='consultation_obs_echo_croissance_modifier'),
    # Echo du col
    path('patients/<int:pk>/consultation_obs_echo_col/ajouter/', obstetrique.ConsultationEchoColCreate.as_view(), name='consultation_obs_echo_col_ajouter'),
    path('consultation_obs_echo_col/<int:pk>/modifier/', obstetrique.ConsultationEchoColUpdate.as_view(), name='consultation_obs_echo_col_modifier'),
    # Echo de cardiofoetale
    path('patients/<int:pk>/consultation_obs_echo_cardio_foetale/ajouter/', obstetrique.ConsultationEchoCardiofoetaleCreate.as_view(), name='consultation_obs_echo_cardio_foetale_ajouter'),
    path('consultation_obs_echo_cardio_foetale/<int:pk>/modifier/', obstetrique.ConsultationEchoCardiofoetaleUpdate.as_view(), name='consultation_obs_echo_cardio_foetale_modifier'),
    # Consult. grossesse
    path('patients/<int:pk>/consultation_obs_grossesse/ajouter/', obstetrique.ConsultationGrossesseCreate.as_view(), name='consultation_obs_grossesse_ajouter'),
    path('consultation_obs_grossesse/<int:pk>/modifier/', obstetrique.ConsultationGrossesseUpdate.as_view(), name='consultation_obs_grossesse_modifier'),

    # PMA
    path('patients/<int:pk>/interrogatoire-pma/ajouter/', pma.InterrogatoirePMACreate.as_view(), name='interrogatoire_pma_ajouter'),
    path('interrogatoire-pma/<int:pk>/modifier/', pma.InterrogatoirePMAUpdate.as_view(), name='interrogatoire_pma_modifier'),
    path('patients/<int:pk>/tentative-pma/ajouter/', pma.creer_tentative, name='tentative_pma_ajouter'),
    path('tentative-pma/<int:pk>/modifier/', pma.TentativePMAUpdate.as_view(), name='tentative_pma_modifier'),
    path('tentative-pma/<int:pk>/cloturer/', pma.TentativePMACloture.as_view(), name='tentative_pma_cloturer'),
    path('tentative-pma/<int:pk>/supprimer/', pma.supprimer_tentative, name='tentative_pma_supprimer'),
    path('tentative-pma/chercher/<int:consultation_pk>/', pma.rechercher_tentative, name='tentative_pma_rechercher'),

    path('consultations/<int:pk>/images/', images.consultation_images, name='consultation_images'),
    path('consultations/<int:pk>/images/ajouter/', images.ajouter_image, name='consultation_image_ajouter'),
    path('images/<int:pk>/supprimer/', images.supprimer_image, name='consultation_image_supprimer'),
    path('images/<int:pk>/modifier/', images.modifier_image, name='consultation_image_modifier'),

    # Worklists
    path('worklists/', worklists.rechercher_worklists, name='worklists_chercher'),
    path('worklists/statut/', worklists.modifier_worklist_statut, name='worklists_modifier_status'),
    path('worklists/image/', worklists.ajouter_image, name='worklists_ajouter_image'),
    path('worklists/sr/', worklists.ajouter_sr, name='worklists_ajouter_sr'),
    path('consultations/<int:pk>/sr/', worklists.consultation_sr, name='consultation_sr'),
    path('worklists/<int:pk>/modifier/', worklists.modifier_worklist, name='worklists_modifier'),

    # Devices
    path('devices/', devices.DeviceList.as_view(), name='devices_list'),
    path('devices/ajouter/', devices.DeviceCreate.as_view(), name='device_creer'),
    path('devices/<int:pk>/modifier', devices.DeviceUpdate.as_view(), name='device__modifier'),
    path('devices/<int:pk>/supprimer', devices.supprimer_device, name='device_supprimer'),

    # Admissions
    path('admissions/<int:pk>/ordre/', admissions.modifier_ordre, name='patient_ordre_modifier'),
    path('admissions/<int:pk>/modifier/', admissions.modifier_admission, name='admission_modifier'),
    path('admissions/<int:pk>/supprimer/', admissions.supprimer_admission, name='admission_supprimer'),

    # Module praticiens
    path('praticiens/ajouter/', praticiens.PraticienCreate.as_view(), name='praticien_form'),
    path('praticiens/<int:pk>/modifier/', praticiens.PraticienUpdate.as_view(), name='praticien_update_form'),
    path('praticiens/<int:pk>/supprimer', praticiens.supprimer_praticien, name='praticien_supprimer'),

    # Module ordonnances
    path('patients/<int:patient_pk>/ordonnances', ordonnances.OrdonnanceList.as_view(), name='ordonnances_list'),
    path('patients/<int:patient_pk>/ordonnances/ajouter/', ordonnances.OrdonnanceCreate.as_view(),
         name='ordonnance_creer'),
    path('ordonnances/<int:pk>', ordonnances.OrdonnanceView.as_view(), name='ordonnance_afficher'),
    path('ordonnances/<int:pk>/modifier', ordonnances.OrdonnanceUpdate.as_view(), name='ordonnance_modifier'),
    path('ordonnances/<int:pk>/supprimer', ordonnances.supprimer_ordonnance, name='ordonnance_supprimer'),

    path('traitements/', traitements.TraitementList.as_view(), name='traitements_list'),
    path('traitements/recherche/', traitements.rechercher_traitement, name='traitements_recherche'),
    path('traitements/ajouter/', traitements.TraitementCreate.as_view(), name='traitement_creer'),
    path('traitements/<int:pk>/modifier', traitements.TraitementUpdate.as_view(), name='traitement__modifier'),
    path('traitements/<int:pk>/supprimer', traitements.supprimer_traitement, name='traitement_supprimer'),

    path('traitements-pma/', pma.TraitementPMAList.as_view(), name='traitements_pma_list'),
    path('traitements-pma/ajouter/', pma.TraitementPMACreate.as_view(), name='traitement_pma_creer'),
    path('traitements-pma/<int:pk>/modifier', pma.TraitementPMAUpdate.as_view(), name='traitement_pma_modifier'),
    path('traitements-pma/<int:pk>/supprimer', pma.supprimer_traitement, name='traitement_pma_supprimer'),

    path('prescriptions/', prescriptions.PrescriptionList.as_view(), name='prescriptions_list'),
    path('prescriptions/recherche/', prescriptions.rechercher_prescription, name='prescriptions_recherche'),
    path('prescriptions/ajouter/', prescriptions.PrescriptionCreate.as_view(), name='prescription_creer'),
    path('prescriptions/<int:pk>/modifier', prescriptions.PrescriptionUpdate.as_view(), name='prescription__modifier'),
    path('prescriptions/<int:pk>/supprimer', prescriptions.supprimer_prescription, name='prescription_supprimer'),

    # Module template edition
    path('templates-edition/', templates_edition.TemplateEditionList.as_view(), name='templates_edition_list'),
    path('templates-edition/ajouter/', templates_edition.TemplateEditionCreate.as_view(), name='template_edition_creer'),
    path('templates-edition/<int:pk>/modifier', templates_edition.TemplateEditionUpdate.as_view(), name='template_edition_modifier'),
    path('templates-edition/<int:pk>/supprimer', templates_edition.supprimer_template_edition, name='template_edition_supprimer'),

    # Module comptabilité
    path('prestations/', prestations.PrestationList.as_view(), name='prestations_list'),
    path('prestations/ajouter/', prestations.PrestationCreate.as_view(), name='prestation_creer'),
    path('prestations/<int:pk>/modifier', prestations.PrestationUpdate.as_view(), name='prestation_modifier'),
    path('prestations/<int:pk>/supprimer', prestations.supprimer_prestation, name='prestation_supprimer'),
    # Module motif absence
    path('motifs_absence/', motifs.MotifList.as_view(), name='motifs_list'),
    path('motifs_absence/ajouter/', motifs.MotifCreate.as_view(), name='motif_creer'),
    path('motifs_absence/<int:pk>/modifier', motifs.MotifUpdate.as_view(), name='motif_modifier'),
    path('motifs_absence/<int:pk>/supprimer', motifs.supprimer_motif, name='motif_supprimer'),
    # Module certificats
    path('patients/<int:patient_pk>/certificats', certificats.CertificatList.as_view(), name='certificats_list'),
    path('patients/<int:patient_pk>/certificats/ajouter/', certificats.CertificatCreate.as_view(),
         name='certificat_creer'),
    path('certificats/<int:pk>', certificats.CertificatView.as_view(), name='certificat_afficher'),
    path('certificats/<int:pk>/modifier', certificats.CertificatUpdate.as_view(), name='certificat_modifier'),
    path('certificats/<int:pk>/supprimer', certificats.supprimer_certificat, name='certificat_supprimer'),

    path('reglements/', reglements.ReglementList.as_view(), name='reglements_list'),
    path('reglements/rapport/', reglements.ReglementRapportList.as_view(), name='reglements_rapport_list'),
    path('reglements/<int:pk>/ajouter/', reglements.ReglementCreate.as_view(), name='reglements_creer'),
    path('reglements/<int:pk>/modifier/', reglements.ReglementUpdate.as_view(), name='reglement_modifier'),
    path('caisse/cloturer', reglements.caisse_cloture, name='caisse_cloturer'),
    path('cloture/<int:pk>/detail', reglements.ClotureDetail.as_view(), name='cloture_detail'),
    path('reglement/<int:pk>/facture', reglements.facture_create, name='reglement_facture'),

    path('utils/fermer/', utils.FermerFenetre.as_view(), name='fermer_fenetre'),

    #module rapports
    path('rapports/consultation/', rapports.RapportConsultationList.as_view(), name='rapports_consultation_list'),
    path('rapports/consultation/rechercher/', rapports.rechercher_consultation, name='rapports_consultation_rechercher'),
    path('rapports/accouchement/', rapports.RapportAccouchementList.as_view(), name='rapports_accouchement_list'),
    path('consultation/<int:pk>', rapports.ConsultationView.as_view(), name='consultation_afficher'),

    #module mutuelle
    path('mutuelle/', mutuelle.List.as_view(), name='mutuelle_list'),
    path('bordereau/creation', mutuelle.bordereau_creation, name='bordereau_creation'),
    path('bordereau/<int:pk>/detail', mutuelle.BordereauDetail.as_view(), name='bordereau_detail'),
    path('bordereau/<int:pk>/rapport', mutuelle.telecharger_rapport, name='bordereau_rapport'),
    path('bordereau/<int:pk>/supprimer', mutuelle.supprimer_bordereau, name='bordereau_supprimer'),

    # Utils
    path('utils/fermer_noreload/', utils.FermerFenetreNoReload.as_view(), name='fermer_fenetre_noreload'),
    path('utils/email/', utils.envoyer_email, name='envoyer_email'),
    path('utils/log/', utils.log, name='log_ajouter'),

    # Plugins
    path("select2/", include("django_select2.urls")),
    path('tinymce/', include('tinymce.urls')),

    # Debug
    path('error', test.error_404, name='certificat_supprimer'),

]

# if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
