import json
import logging
import os

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
import requests


class FermerFenetre(TemplateView):
    template_name = 'core/fermer_fenetre.html'


class FermerFenetreNoReload(TemplateView):
    template_name = 'core/fermer_fenetre_noreload.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'event' in self.request.GET:
            context['event'] = self.request.GET['event']
        return context


def envoyer_email(request):
    subject = request.POST.get('subject', 'Contact')
    body = request.POST.get('body', '')
    api_key = os.environ.get('SENDINBLUE_API_KEY', '')
    post_data = {
        "sender": {
            "name": "Utilisateur Gyneasy",
            "email": "arbi.benali@aims-consult.com"
        },
        "to": [
            {
                "email": "adel.ayadi@gmail.com",
                "name": "Adel Ayadi"
            }
        ],
        "cc": [
            {
                "email": "arbi.ben.ali@gmail.com",
                "name": "Arbi Ben Ali"
            }
        ],
        "subject": subject,
        "htmlContent": body
    }
    url = 'https://api.sendinblue.com/v3/smtp/email'
    headers = {'content-type': 'application/json', 'accept': 'application/json', 'api-key': api_key}
    resp = requests.post(f'{url}', json=post_data, headers=headers)
    data = {'message': "Message envoyé"}
    return JsonResponse(data)


def log(request):
    logger = logging.getLogger('client')
    body = json.loads(request.body)
    logs = body['logs']
    for log in logs:
        logger.log(getattr(logging, log['level'].upper()), log['message'])
    data = {'message': "Message sent"}
    return JsonResponse(data)
