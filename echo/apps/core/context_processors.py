import json

from django.conf import settings
from django.utils import translation

from apps.core.serializers import ParametresCompteSerializer


def global_settings(request):
    lang = translation.get_language() or "fr"
    ret = {
        "APP_VERSION": settings.APP_VERSION,
        "LANGUAGE_CODE": lang,
    }

    if hasattr(request.user, "profil"):
        ret["PARAMETRES_COMPTE"] = json.dumps(
            ParametresCompteSerializer(request.user.profil.compte.parametrescompte).data
        )
    return ret
