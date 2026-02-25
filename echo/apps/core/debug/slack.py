import json

import requests

from django.utils.log import AdminEmailHandler


class SlackHandler(AdminEmailHandler):
    def send_mail(self, subject, message, *args, **kwargs):
        data = {'text': message}
        requests.post("REDACTED",
                      data=json.dumps(data), headers={'Content-Type': 'application/json'})
