from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):

    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@example.com'
        password = 'admin'
        User = get_user_model()
        u = User.objects.filter(username=username)
        if u:
            return
        admin = User.objects.create_superuser(username, email, password)
        print('Creating account for %s (%s)' % (username, email))
        admin.is_active = True
        admin.is_admin = True
        admin.save()
