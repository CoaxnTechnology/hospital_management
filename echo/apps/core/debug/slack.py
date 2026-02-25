import json
import os

import requests

from django.utils.log import AdminEmailHandler


class SlackHandler(AdminEmailHandler):
    def send_mail(self, subject, message, *args, **kwargs):
        data = {'text': message}
        webhook_url = os.environ.get('SLACK_WEBHOOK_URL', '')
        if webhook_url:
            requests.post(webhook_url,
                          data=json.dumps(data), headers={'Content-Type': 'application/json'})
