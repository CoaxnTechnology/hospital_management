import random
import string

from django.contrib.auth.models import User, Group

from apps.core.models import Compte, ParametresCompte, Profil, SuperAdminProfile


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


def create_doctor_compte(name: str, email: str, specialty: str = '', distribution: str = 'gyneco', password: str = '') -> dict:
    """
    Create a fully isolated Compte for a new doctor.
    Returns credentials dict: username, password, ae_title.
    """
    base_username = email.split('@')[0].lower().replace('.', '_')
    username = base_username
    suffix = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{suffix}"
        suffix += 1

    password = password or generate_password()
    user = User.objects.create_user(username=username, email=email, password=password)
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

    ae_title = generate_ae_title(name)
    # ParametresCompte is auto-created by a post_save signal on Compte
    ParametresCompte.objects.filter(compte=compte).update(ae_title=ae_title)

    return {
        'username': username,
        'password': password,
        'ae_title': ae_title,
        'compte_id': compte.pk,
    }
