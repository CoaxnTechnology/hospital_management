from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse

ADMIN_DOMAIN = getattr(settings, 'ADMIN_DOMAIN', 'admin.clinicalgynecologists.space')


def _is_super_admin(user):
    if not user.is_authenticated:
        return False
    try:
        return user.super_admin_profile is not None
    except ObjectDoesNotExist:
        return False


class ProfilRequiredMiddleware:
    """
    Catches RelatedObjectDoesNotExist when a logged-in user has no Profil,
    and returns a clear error page instead of a 500 crash.
    Super-admin users (with SuperAdminProfile) are allowed through without a Profil.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Block /super-admin/ from non-admin subdomain entirely (return 404)
        if request.path.startswith('/super-admin/'):
            host = request.get_host().split(':')[0]  # strip port if any
            if host != ADMIN_DOMAIN:
                raise Http404

        # Super-admin users have no Profil — only allow /super-admin/ and /admin/ and /accounts/
        if _is_super_admin(request.user):
            allowed = ('/super-admin/', '/admin/', '/accounts/', '/i18n/', '/__debug__/')
            if not any(request.path.startswith(p) for p in allowed):
                return HttpResponseRedirect('/super-admin/')
            return self.get_response(request)

        # Block /super-admin/ for non-super-admin users
        if request.path.startswith('/super-admin/'):
            return HttpResponseRedirect('/')

        try:
            response = self.get_response(request)
        except ObjectDoesNotExist as e:
            if request.user.is_authenticated and 'profil' in str(e).lower():
                return HttpResponse(
                    """
                    <html><body style="font-family:sans-serif;padding:40px;">
                    <h2>Compte incomplet</h2>
                    <p>Votre compte utilisateur n'a pas de profil associé.</p>
                    <p>Veuillez contacter l'administrateur pour créer votre profil.</p>
                    <p><a href="/accounts/logout">Se déconnecter</a></p>
                    </body></html>
                    """,
                    status=200,
                )
            raise
        return response
