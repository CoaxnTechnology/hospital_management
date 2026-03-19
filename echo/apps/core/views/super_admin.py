import json
import os

from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from apps.core.models import Compte, SuperAdminProfile, DoctorSignupRequest
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
    signup_requests = DoctorSignupRequest.objects.filter(
        status=DoctorSignupRequest.STATUS_PENDING
    ).order_by('-created_at')
    storage_port = os.environ.get('EE_STORE_SCP_PORT', '11113')
    mwl_port = os.environ.get('EE_WL_MPPS_SCP_PORT', '11112')
    return render(request, 'super_admin/dashboard.html', {
        'comptes': comptes,
        'active_count': active_count,
        'signup_requests': signup_requests,
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


@super_admin_required
@require_POST
def approve_signup(request, pk):
    try:
        signup = DoctorSignupRequest.objects.get(pk=pk, status=DoctorSignupRequest.STATUS_PENDING)
    except DoctorSignupRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found or already processed.'}, status=404)

    try:
        result = create_doctor_compte(
            name=signup.full_name,
            email=signup.email,
            hashed_password=signup.password,
        )
        signup.status = DoctorSignupRequest.STATUS_APPROVED
        signup.save(update_fields=['status'])

        login_url = f"{request.scheme}://{request.get_host()}/accounts/login/"
        body = render_to_string('core/signup_approved_email.txt', {
            'full_name': signup.full_name,
            'username': result['username'],
            'login_url': login_url,
        })
        send_mail(
            subject='Your CabinetPro access has been approved',
            message=body,
            from_email=None,
            recipient_list=[signup.email],
            fail_silently=True,
        )
        return JsonResponse({
            'status': 'approved',
            'username': result['username'],
            'ae_title': result['ae_title'],
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@super_admin_required
@require_POST
def reject_signup(request, pk):
    try:
        signup = DoctorSignupRequest.objects.get(pk=pk, status=DoctorSignupRequest.STATUS_PENDING)
    except DoctorSignupRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found or already processed.'}, status=404)

    signup.status = DoctorSignupRequest.STATUS_REJECTED
    signup.save(update_fields=['status'])

    body = render_to_string('core/signup_rejected_email.txt', {
        'full_name': signup.full_name,
    })
    send_mail(
        subject='Your CabinetPro access request',
        message=body,
        from_email=None,
        recipient_list=[signup.email],
        fail_silently=True,
    )
    return JsonResponse({'status': 'rejected'})


def doctor_signup(request):
    """Public page for doctors to submit a signup request."""
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        errors = {}
        if not full_name:
            errors['full_name'] = 'Full name is required.'
        if not email:
            errors['email'] = 'Email address is required.'
        elif DoctorSignupRequest.objects.filter(email=email).exists():
            errors['email'] = 'A request with this email already exists.'
        if not password:
            errors['password'] = 'Password is required.'
        elif len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters.'
        elif password != password2:
            errors['password2'] = 'Passwords do not match.'

        if errors:
            return render(request, 'core/doctor_signup.html', {
                'errors': errors,
                'form_data': {'full_name': full_name, 'email': email, 'phone': phone},
            })

        DoctorSignupRequest.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            password=make_password(password),
        )
        return render(request, 'core/doctor_signup.html', {'submitted': True})

    return render(request, 'core/doctor_signup.html', {})
