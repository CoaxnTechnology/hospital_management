from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.urls import reverse


class ProfilRequiredMiddleware:
    """
    Catches RelatedObjectDoesNotExist when a logged-in user has no Profil,
    and returns a clear error page instead of a 500 crash.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
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
