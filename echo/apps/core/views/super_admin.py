import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from apps.core.models import Compte, SuperAdminProfile
from apps.core.services.doctor_setup import create_doctor_compte


def super_admin_required(view_func):
    """Decorator: user must be authenticated and have SuperAdminProfile."""
    @login_required(login_url='/accounts/login')
    def wrapper(request, *args, **kwargs):
        if not SuperAdminProfile.objects.filter(user=request.user).exists():
            return redirect('/')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


@super_admin_required
def dashboard(request):
    comptes = (
        Compte.objects
        .select_related('parametrescompte', 'responsable')
        .order_by('-id')
    )
    return render(request, 'super_admin/dashboard.html', {'comptes': comptes})


@super_admin_required
@require_POST
def create_doctor(request):
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        specialty = data.get('specialty', '').strip()
        distribution = data.get('distribution', 'gyneco')
        password = data.get('password', '').strip()

        if not name or not email:
            return JsonResponse({'error': 'Name and email are required.'}, status=400)

        result = create_doctor_compte(name=name, email=email, specialty=specialty, distribution=distribution, password=password)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@super_admin_required
@require_POST
def delete_compte(request, pk):
    try:
        compte = Compte.objects.get(pk=pk)
        compte.delete()
        return JsonResponse({'status': 'deleted'})
    except Compte.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
