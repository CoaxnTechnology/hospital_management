import os
from django.http import HttpResponseNotFound


class AdminHostMiddleware:
    """Only allow /admin/ access from the admin subdomain."""

    ADMIN_HOST = os.environ.get('ADMIN_SUBDOMAIN', 'admin.clinicalgynecologists.space')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]
        if request.path.startswith('/admin/') or request.path.startswith('/super-admin/'):
            if host != self.ADMIN_HOST:
                return HttpResponseNotFound()
        return self.get_response(request)
