import csv
import json
import logging
import os
import random
import string

from django.contrib.auth.hashers import is_password_usable
from django.contrib.auth.models import User, Group

from apps.core.models import (
    AnalyseBiologique,
    CategorieConsultation,
    Compte,
    MotifConsultation,
    ParametresCompte,
    Prescription,
    Profil,
    SuperAdminProfile,
    TemplateEdition,
    Traitement,
)

logger = logging.getLogger(__name__)

_DATA_DIR     = os.path.join(os.path.dirname(__file__), '..', 'data')
_FIXTURES_DIR = os.path.join(os.path.dirname(__file__), '..', 'fixtures')

# Category PKs per distribution
DISTRIBUTION_CATEGORIES = {
    'gyneco':  [1, 2, 4, 7],   # Obstétrique, Gynécologie, Examen libre, CR opératoire
    'cardio':  [5, 6, 4, 7],   # Cardiologie, Vasculaire, Examen libre, CR opératoire
    'general': [4, 7],          # Examen libre, CR opératoire
}


def generate_ae_title(name: str) -> str:
    """Generate a unique 16-char DICOM AE title from a doctor/clinic name."""
    base = ''.join(c for c in name.upper() if c.isalnum())[:10]
    while True:
        suffix = ''.join(random.choices(string.digits, k=4))
        ae = f"{base}{suffix}"[:16]
        if not ParametresCompte.objects.filter(ae_title=ae).exists():
            return ae


def generate_password(length: int = 14) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choices(chars, k=length))


def create_doctor_compte(name: str, email: str, specialty: str = '', distribution: str = 'gyneco', password: str = '', hashed_password: str = '') -> dict:
    """
    Create a fully isolated Compte for a new doctor.
    Pass hashed_password (from signup request) or plain password. Falls back to auto-generate.
    Returns credentials dict: username, ae_title.
    """
    import unicodedata
    normalized = unicodedata.normalize('NFD', name.lower())
    ascii_name = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    base_username = ''.join(c if c.isalnum() else '_' for c in ascii_name).strip('_')
    base_username = base_username or email.split('@')[0].lower().replace('.', '_')
    username = base_username
    suffix = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{suffix}"
        suffix += 1

    if hashed_password and is_password_usable(hashed_password):
        user = User.objects.create_user(username=username, email=email, password=None)
        user.password = hashed_password
        user.save(update_fields=['password'])
    else:
        plain = password or generate_password()
        user = User.objects.create_user(username=username, email=email, password=plain)
    user.first_name = name.split()[0] if name else ''
    user.last_name = ' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
    user.save()

    compte = Compte.objects.create(
        raison_sociale=name,
        email=email,
        telephone='',
        distribution=distribution,
        responsable=user,  # makes this user the account manager with full access
    )

    Profil.objects.create(user=user, compte=compte, titre='dr')

    try:
        medecin_group = Group.objects.get(name='Médecin')
        user.groups.add(medecin_group)
    except Group.DoesNotExist:
        pass

    # Assign consultation categories based on distribution
    category_pks = DISTRIBUTION_CATEGORIES.get(distribution, DISTRIBUTION_CATEGORIES['gyneco'])
    categories = CategorieConsultation.objects.filter(pk__in=category_pks)
    compte.categories_consultations.set(categories)

    ae_title = generate_ae_title(name)
    # ParametresCompte is auto-created by a post_save signal on Compte
    ParametresCompte.objects.filter(compte=compte).update(ae_title=ae_title)

    return {
        'username': username,
        'ae_title': ae_title,
        'compte_id': compte.pk,
    }


def load_default_templates(compte: Compte) -> dict:
    """
    Populate default templates (medications, lab tests, prescriptions, report templates)
    for a newly created Compte. Skips entries that already exist.
    Returns a summary dict with counts.
    """
    summary = {}

    # --- Traitements ---
    traitements_csv = os.path.join(_DATA_DIR, 'traitements.csv')
    if os.path.exists(traitements_csv):
        existing = set(Traitement.objects.filter(compte=compte).values_list('libelle', flat=True))
        entries = []
        with open(traitements_csv, encoding='cp1252', errors='replace') as f:
            for row in csv.DictReader(f, delimiter=';'):
                libelle = row['libelle'].strip()
                if not libelle or libelle in existing:
                    continue
                entries.append(Traitement(
                    compte=compte,
                    libelle=libelle,
                    text=row.get('text', '').strip(),
                    forme=row.get('forme', 'comprime').strip().lower() or 'comprime',
                ))
        Traitement.objects.bulk_create(entries, ignore_conflicts=True)
        summary['traitements'] = len(entries)
    else:
        logger.warning('load_default_templates: traitements.csv not found at %s', traitements_csv)
        summary['traitements'] = 0

    # --- Analyses biologiques ---
    analyses_csv = os.path.join(_DATA_DIR, 'analyses.csv')
    if os.path.exists(analyses_csv):
        existing = set(AnalyseBiologique.objects.filter(compte=compte).values_list('code', flat=True))
        entries = []
        with open(analyses_csv, encoding='cp1252', errors='replace') as f:
            for row in csv.DictReader(f, delimiter=';'):
                code = row.get('code', '').strip()
                if not code or code in existing:
                    continue
                entries.append(AnalyseBiologique(
                    compte=compte,
                    code=code,
                    libelle=row.get('libelle', '').strip() or code,
                    type=row.get('type', 'text').strip() or 'text',
                    unite=row.get('unite', '').strip(),
                ))
        AnalyseBiologique.objects.bulk_create(entries, ignore_conflicts=True)
        summary['analyses'] = len(entries)
    else:
        logger.warning('load_default_templates: analyses.csv not found at %s', analyses_csv)
        summary['analyses'] = 0

    # --- Prescriptions ---
    prescriptions_csv = os.path.join(_DATA_DIR, 'prescriptions.csv')
    if os.path.exists(prescriptions_csv):
        existing = set(Prescription.objects.filter(compte=compte).values_list('libelle', flat=True))
        entries = []
        with open(prescriptions_csv, encoding='cp1252', errors='replace') as f:
            for row in csv.DictReader(f, delimiter=';'):
                libelle = row.get('libelle', '').strip()
                if not libelle or libelle in existing:
                    continue
                categorie = row.get('categorie', '').strip()
                if categorie not in ('examen_complementaire',):
                    categorie = 'examen_complementaire'
                entries.append(Prescription(
                    compte=compte,
                    libelle=libelle,
                    categorie=categorie,
                    text=row.get('text', libelle).strip(),
                ))
        Prescription.objects.bulk_create(entries, ignore_conflicts=True)
        summary['prescriptions'] = len(entries)
    else:
        logger.warning('load_default_templates: prescriptions.csv not found at %s', prescriptions_csv)
        summary['prescriptions'] = 0

    # --- Report templates ---
    templates_json = os.path.join(_FIXTURES_DIR, 'templates_data.json')
    if os.path.exists(templates_json):
        with open(templates_json, encoding='utf-8') as f:
            data = json.load(f)
        templates = data.get('template_editions', [])
        existing = set(TemplateEdition.objects.filter(compte=compte).values_list('libelle', flat=True))
        created = 0
        for t in templates:
            libelle = t.get('libelle', '').strip()
            if not libelle or libelle in existing:
                continue
            cat_libelle = t.get('categorie_consultation__libelle')
            motif_code = t.get('motif_consultation__code')
            try:
                categorie = CategorieConsultation.objects.get(libelle=cat_libelle)
            except CategorieConsultation.DoesNotExist:
                logger.warning('load_default_templates: categorie "%s" not found, skipping "%s"', cat_libelle, libelle)
                continue
            motif = None
            if motif_code:
                try:
                    motif = MotifConsultation.objects.get(code=motif_code)
                except MotifConsultation.DoesNotExist:
                    pass
            TemplateEdition.objects.create(
                compte=compte,
                libelle=libelle,
                contenu=t.get('contenu', ''),
                categorie_consultation=categorie,
                motif_consultation=motif,
            )
            created += 1
        summary['report_templates'] = created
    else:
        logger.warning('load_default_templates: templates_data.json not found at %s', templates_json)
        summary['report_templates'] = 0

    return summary
