import json
import os

from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from apps.core.models import Compte, Profil, SuperAdminProfile, DoctorSignupRequest, Device
from django.contrib.auth.models import User
from apps.core.services.doctor_setup import create_doctor_compte, load_default_templates


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

        try:
            compte = Compte.objects.get(pk=result['compte_id'])
            load_default_templates(compte)
        except Exception as tmpl_err:
            import logging
            logging.getLogger(__name__).warning('load_default_templates failed: %s', tmpl_err)

        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@super_admin_required
@require_POST
def delete_compte(request, pk):
    try:
        compte = Compte.objects.get(pk=pk)
        # Hard-delete all users of this compte before deleting it
        user_ids = Profil.objects_with_deleted.filter(compte=compte).values_list('user_id', flat=True)
        User.objects.filter(pk__in=list(user_ids)).delete()
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

        # Load default templates (medications, labs, prescriptions, report templates)
        try:
            compte = Compte.objects.get(pk=result['compte_id'])
            load_default_templates(compte)
        except Exception as tmpl_err:
            import logging
            logging.getLogger(__name__).warning('load_default_templates failed: %s', tmpl_err)

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


@super_admin_required
def list_devices(request, pk):
    try:
        compte = Compte.objects.get(pk=pk)
    except Compte.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
    devices = Device.all_objects.filter(compte=compte, deleted_at__isnull=True).values(
        'id', 'marque', 'modele', 'ae_title', 'ip', 'port'
    )
    return JsonResponse({'devices': list(devices)})


@super_admin_required
@require_POST
def add_device(request, pk):
    try:
        compte = Compte.objects.get(pk=pk)
    except Compte.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
    try:
        data = json.loads(request.body)
        ae_title = data.get('ae_title', '').strip()
        if not ae_title:
            return JsonResponse({'error': 'AE Title is required.'}, status=400)
        created = Device.all_objects.bulk_create([Device(
            compte=compte,
            marque=data.get('marque', '').strip(),
            modele=data.get('modele', '').strip(),
            ae_title=ae_title,
            ip=data.get('ip', '').strip(),
            port=int(data.get('port') or 104),
        )])
        device = created[0]
        return JsonResponse({
            'id': device.id,
            'marque': device.marque,
            'modele': device.modele,
            'ae_title': device.ae_title,
            'ip': device.ip,
            'port': device.port,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@super_admin_required
@require_POST
def delete_device(request, pk):
    try:
        deleted_count, _ = Device.all_objects.filter(pk=pk).delete()
        if not deleted_count:
            return JsonResponse({'error': 'Not found'}, status=404)
        return JsonResponse({'status': 'deleted'})
    except Device.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)


@super_admin_required
def poll_stats(request):
    comptes = list(
        Compte.objects
        .select_related('parametrescompte', 'responsable')
        .order_by('-id')
    )
    active_count = sum(1 for c in comptes if c.responsable and c.responsable.is_active)
    pending_count = DoctorSignupRequest.objects.filter(
        status=DoctorSignupRequest.STATUS_PENDING
    ).count()
    doctors = []
    for c in comptes:
        try:
            ae = c.parametrescompte.ae_title or ''
        except Exception:
            ae = ''
        doctors.append({
            'pk': c.pk,
            'name': c.raison_sociale or '',
            'email': (c.responsable.email if c.responsable else None) or c.email or '',
            'ae_title': ae,
            'username': c.responsable.username if c.responsable else '',
            'is_active': c.responsable.is_active if c.responsable else False,
            'has_responsable': bool(c.responsable),
        })
    return JsonResponse({
        'total': len(comptes),
        'active': active_count,
        'pending': pending_count,
        'doctors': doctors,
    })


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
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'A user with this email already exists.'
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
