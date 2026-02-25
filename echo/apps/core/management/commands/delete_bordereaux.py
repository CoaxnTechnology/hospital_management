from django.contrib.auth.models import User, Group
from django.core.management import BaseCommand

from apps.core.models import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        Bordereau.objects.all().delete()

