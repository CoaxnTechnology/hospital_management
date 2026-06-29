from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from apps.core.models import (
    Compte, Patient, Grossesse, ConsultationObstetrique,
    ConsultationEchoTroisiemeTrimestre, MotifConsultation,
    CategorieConsultation, Medecin,
)
from apps.core.views.patients import PatientView


class AutoInitiateTest(TestCase):
    def setUp(self):
        self.compte = Compte.objects.create(
            raison_sociale="Test Compte",
        )
        self.user = User.objects.create_user("testdoctor", password="testpass123")
        medecin_group, _ = Group.objects.get_or_create(name="Médecin")
        self.user.groups.add(medecin_group)

        self.medecin = Medecin.objects.create(
            user=self.user,
            compte=self.compte,
            titre="dr",
        )

        ctype = ContentType.objects.get_for_model(Patient)
        perm = Permission.objects.get(content_type=ctype, codename="view_patient")
        self.user.user_permissions.add(perm)
        self.user.save()

        self.cat_consult = CategorieConsultation.objects.create(libelle="Obstétrique")
        self.compte.categories_consultations.add(self.cat_consult)

        self.motif = MotifConsultation.objects.create(
            libelle="Écho 3e trimestre",
            code="obs_echo_trimestre_3",
            categorie=self.cat_consult,
        )

        self.patient = Patient.objects.create(
            compte=self.compte,
            civilite="mme",
            prenom="Jeanne",
            nom="Testing",
            sexe="F",
            date_naissance="1990-01-01",
        )
        self.grossesse = Grossesse.objects.create(
            patient=self.patient,
            encours=True,
        )

        self.factory = RequestFactory()

    def _get_response_context(self):
        request = self.factory.get(f"/patients/{self.patient.pk}/")
        request.user = self.user
        request.user.profil = self.medecin
        view = PatientView()
        view.setup(request, pk=self.patient.pk)
        response = view.get(request, pk=self.patient.pk)
        return response.context_data if hasattr(response, 'context_data') else None

    def test_pregnant_no_consultation_auto_initiates(self):
        context = self._get_response_context()
        self.assertIsNotNone(context)
        self.assertTrue(context['is_new_consultation'],
                        "Should auto-initiate for pregnant patient with no consultation")
        self.assertIsNotNone(context['consultation_tabs_form'],
                             "Should have consultation form set")

    def test_non_typed_consultation_triggers_auto_initiate(self):
        ConsultationObstetrique.objects.create(
            patient=self.patient,
            praticien=self.medecin,
            motif=self.motif,
            grossesse=self.grossesse,
            date=timezone.now(),
        )
        context = self._get_response_context()
        self.assertIsNotNone(context)
        self.assertTrue(context['is_new_consultation'],
                        "Should auto-initiate when latest consultation is not a known typed subclass")

    def test_typed_consultation_loads_normally(self):
        ConsultationEchoTroisiemeTrimestre.objects.create(
            patient=self.patient,
            praticien=self.medecin,
            motif=self.motif,
            grossesse=self.grossesse,
            date=timezone.now(),
        )
        context = self._get_response_context()
        self.assertIsNotNone(context)
        self.assertFalse(context['is_new_consultation'],
                         "Should NOT auto-initiate when a typed consultation exists")
        self.assertIsNotNone(context['consultation_tabs_form'],
                             "Should have loaded the existing typed consultation form")
        self.assertIsNotNone(context['consultation_active'],
                             "consultation_active should be set to the existing consultation")

    def test_auto_initiate_form_type_and_initial(self):
        context = self._get_response_context()
        self.assertTrue(context['is_new_consultation'])
        form = context['consultation_tabs_form']
        self.assertIsNotNone(form)
        from apps.core.forms import ConsultationEchoTroisiemeTrimestreForm
        self.assertIsInstance(form, ConsultationEchoTroisiemeTrimestreForm)
        self.assertIn('patient', form.initial)
        self.assertEqual(form.initial['patient'], self.patient.pk)
        self.assertIn('grossesse', form.initial)
        self.assertEqual(form.initial['grossesse'], self.grossesse.pk)
