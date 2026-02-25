import json

from django.conf import settings

from apps.core.serializers import ParametresCompteSerializer


def global_settings(request):
    ret = {
        'APP_VERSION': settings.APP_VERSION
    }

    if hasattr(request.user, 'profil'):
        ret['PARAMETRES_COMPTE'] = json.dumps(ParametresCompteSerializer(request.user.profil.compte.parametrescompte).data)
    return ret
