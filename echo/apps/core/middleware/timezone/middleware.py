import pytz

from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.session.get('django_timezone')
        return self.get_response(request)
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            # Charger le timezone des parametres du compte
            if hasattr(request.user, 'profil'):
                tzname = request.user.profil.compte.parametrescompte.timezone
                request.session['django_timezone'] = tzname
                timezone.activate(pytz.timezone(tzname))
        return self.get_response(request)
