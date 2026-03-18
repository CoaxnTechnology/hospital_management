import json
import os

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
    active_count = sum(1 for c in comptes if c.responsable and c.responsable.is_active)
    storage_port = os.environ.get('EE_STORE_SCP_PORT', '11113')
    mwl_port = os.environ.get('EE_WL_MPPS_SCP_PORT', '11112')
    return render(request, 'super_admin/dashboard.html', {
        'comptes': comptes,
        'active_count': active_count,
        'storage_port': storage_port,
        'mwl_port': mwl_port,
    })


@super_admin_required
@require_POST
def create_doctor(request):
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        specialty = data.get('specialty', '').strip()
        password = data.get('password', '').strip()
        if not name or not email:
            return JsonResponse({'error': 'Name and email are required.'}, status=400)

        result = create_doctor_compte(name=name, email=email, specialty=specialty, password=password)
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


@super_admin_required
@require_POST
def toggle_compte(request, pk):
    try:
        compte = Compte.objects.select_related('responsable').get(pk=pk)
        user = compte.responsable
        if user:
            user.is_active = not user.is_active
            user.save(update_fields=['is_active'])
            return JsonResponse({'status': 'ok', 'is_active': user.is_active})
        return JsonResponse({'error': 'No user linked to this account.'}, status=400)
    except Compte.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
