"""
Create permission groups
Create permissions (read only) to models for a set of groups
"""
import logging

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission

groups = {
    'Médecin': {
        'user': ['view'],
        'adresse': ['view', 'add', 'change', 'delete'],
        'profil': ['view', 'add', 'change', 'delete'],
        'patient': ['view', 'add', 'change', 'delete'],
        'antecedent': ['view', 'add', 'change', 'delete'],
        'consultation': ['view', 'add', 'change', 'delete'],
        'motif rdv': ['view', 'add', 'change', 'delete'],
        'rdv': ['view', 'add', 'change', 'delete'],
        'parametres compte': ['view', 'add', 'change', 'delete'],
        'reglement': ['view', 'add', 'change'],
        'cloture': ['view', 'add', 'change'],
        'facture': ['view', 'add', 'change', 'delete'],
        'prestation': ['view', 'add', 'change', 'delete'],
        'absence medecin': ['view', 'add', 'change'],
        'programme operatoire': ['view', 'add', 'change'],
    },
    'Assistant': {
        'adresse': ['view', 'add', 'change', 'delete'],
        'profil': ['view'],
        'patient': ['view', 'add', 'change', 'delete'],
        'motif rdv': ['view', 'add', 'change', 'delete'],
        'rdv': ['view', 'add', 'change', 'delete'],
        'reglement': ['view', 'add', 'change'],
        'facture': ['view', 'add', 'change'],
        'prestation': ['view', 'add', 'change'],
        'absence medecin': ['view', 'add', 'change'],
        'programme operatoire': ['view', 'add', 'change'],
    }
}


class Command(BaseCommand):
    help = 'Creates default permission groups for users'

    def handle(self, *args, **options):
        for group in groups:
            new_group, created = Group.objects.get_or_create(name=group)
            models = groups[group]
            for model in models:
                for permission in models[model]:
                    name = 'Can {} {}'.format(permission, model)
                    print("Creating {}".format(name))
                    try:
                        model_add_perm = Permission.objects.get(name=name)
                    except Permission.DoesNotExist:
                        print("Permission not found with name '{}'.".format(name))
                        continue

                    new_group.permissions.add(model_add_perm)

        print("Created default group and permissions.")
