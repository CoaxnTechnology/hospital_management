from django.http import HttpResponseNotFound


def error_404(request):
    return HttpResponseNotFound('<h1>Page not found</h1>')
