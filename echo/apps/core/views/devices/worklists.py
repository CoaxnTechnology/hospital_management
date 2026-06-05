import datetime
import json
import os
import re

from django.contrib.auth.decorators import login_required, permission_required
from django.core.files import File
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from apps.core.models import WorklistItem, ImageConsultation, repertoire_images_utilisateur, SRConsultation, \
    Consultation, Device, Patient, Admission
from apps.core.serializers import WorklistItemSerializer, SRConsultationSerializer
from django.db import models


@csrf_exempt
def rechercher_worklists(request):
    items = WorklistItem.objects.filter().order_by('consultation__patient__nom')
    if 'patient_name' in request.POST:
        patient_name = request.POST.get('patient_name').replace('*', '')
        name = re.split('[\^]', patient_name)
        print('Chercher worklist patient name', name)
        if len(name) == 2:
            items = items.filter(consultation__patient__prenom__icontains=name[1],
                                 consultation__patient__nom__icontains=name[0])
        else:
            items = items.filter(consultation__patient__prenom__icontains=name[0],
                                 consultation__patient__nom__icontains=name[0])
    if 'date' in request.POST:
        date = datetime.datetime.strptime(request.POST.get('date'), '%Y%m%d')
        print('Recherche worklist par date', date)
        items = items.filter(consultation__date__day=date.day,
                             consultation__date__month=date.month,
                             consultation__date__year=date.year)

    if 'device' in request.POST:
        items = items.filter(device__ae_title=request.POST['device'])

    items = items.filter(mpps_status__in=[WorklistItem.MPPS_STATUS_PENDING, WorklistItem.MPPS_STATUS_INPROGRESS])
    print('Items found', items)
    data = WorklistItemSerializer(items, many=True)
    resp = {
        'items': json.dumps(data.data),
    }
    return JsonResponse(resp)


@csrf_exempt
def modifier_worklist_statut(request):
    from datetime import date
    if 'study_uid' in request.POST:
        study_uid = request.POST['study_uid']
        item = WorklistItem.objects.get(study_instance_uid=study_uid)
        if 'status' in request.POST:
            item.mpps_status = request.POST['status']
            item.save()
            if request.POST['status'] == WorklistItem.MPPS_STATUS_COMPLETED:
                today = date.today()
                item.consultation.patient.admission_set.filter(
                    date__day=today.day,
                    date__month=today.month,
                    date__year=today.year,
                    statut='2'
                ).update(statut='3')
    resp = {
        'status': 'success',
    }
    return JsonResponse(resp)


@csrf_exempt
def ajouter_image(request):
    consultation = None
    if 'study_uid' in request.POST:
        study_uid = request.POST['study_uid']
        print(f'Requesting worklist item with study id {study_uid}')
        try:
            item = WorklistItem.objects.get(study_instance_uid=study_uid)
            print(f'Found item {item}')
            consultation = item.consultation
        except WorklistItem.DoesNotExist:
            print(f'WorklistItem with UID {study_uid} not found, trying fallback by patient name')

    if consultation is None and 'patient_name' in request.POST:
        patient_name = request.POST['patient_name']
        parts = patient_name.split('^')
        if len(parts) >= 2:
            last_name = parts[0]
            first_name = parts[1]
            today = datetime.datetime.now().date()
            from apps.core.models import Consultation as ConsultationModel
            match = ConsultationModel.objects.filter(
                patient__nom__iexact=last_name,
                patient__prenom__iexact=first_name,
                date__date=today,
            ).order_by('-id').first()
            if match:
                consultation = match
                print(f'Found consultation by patient name: {match.id}')

    if consultation is None:
        return JsonResponse({'message': 'No matching consultation found'}, status=404)

    if 'path' in request.POST:
        path = request.POST['path']
        ic = ImageConsultation(type=ImageConsultation.IMG_ECHO, consultation=consultation,
                               date=datetime.datetime.now(), impression=False)
        ic.save()
        patient = consultation.patient
        out_path = repertoire_images_utilisateur(patient.compte.pk, patient.pk, os.path.basename(path))
        ic.image.save(out_path, File(open(path, 'rb')))
        today = datetime.date.today()
        patient.admission_set.filter(
            date__day=today.day,
            date__month=today.month,
            date__year=today.year,
            statut='2'
        ).update(statut='3')
    resp = {
        'status': 'success',
    }
    return JsonResponse(resp)


@csrf_exempt
def ajouter_sr(request):
    consultation = None
    if 'study_uid' in request.POST:
        study_uid = request.POST['study_uid']
        print(f'Requesting worklist item with study id {study_uid}')
        try:
            item = WorklistItem.objects.get(study_instance_uid=study_uid)
            print(f'Found item {item}')
            consultation = item.consultation
        except WorklistItem.DoesNotExist:
            print(f'WorklistItem with UID {study_uid} not found, trying fallback by patient name')

    if consultation is None and 'patient_name' in request.POST:
        patient_name = request.POST['patient_name']
        parts = patient_name.split('^')
        if len(parts) >= 2:
            last_name = parts[0]
            first_name = parts[1]
            today = datetime.datetime.now().date()
            from apps.core.models import Consultation as ConsultationModel
            match = ConsultationModel.objects.filter(
                patient__nom__iexact=last_name,
                patient__prenom__iexact=first_name,
                date__date=today,
            ).order_by('-id').first()
            if match:
                consultation = match
                print(f'Found consultation by patient name: {match.id}')

    if consultation is None:
        return JsonResponse({'message': 'No matching consultation found'}, status=404)

    if 'data' in request.POST:
        data = request.POST['data']
        sr = SRConsultation(consultation=consultation, date=datetime.datetime.now(), data=data)
        sr.save()
    resp = {
        'status': 'success',
    }
    return JsonResponse(resp)


@csrf_exempt
def ajouter_waveform(request):
    """Handle DICOM Waveform upload."""
    from apps.core.models import WaveformConsultation
    
    consultation = None
    if 'study_uid' in request.POST:
        study_uid = request.POST['study_uid']
        print(f'Requesting worklist item with study id {study_uid}')
        try:
            item = WorklistItem.objects.get(study_instance_uid=study_uid)
            print(f'Found item {item}')
            consultation = item.consultation
        except WorklistItem.DoesNotExist:
            print(f'WorklistItem with UID {study_uid} not found, trying fallback by patient name')

    if consultation is None and 'patient_name' in request.POST:
        patient_name = request.POST['patient_name']
        parts = patient_name.split('^')
        if len(parts) >= 2:
            last_name = parts[0]
            first_name = parts[1]
            today = datetime.datetime.now().date()
            from apps.core.models import Consultation as ConsultationModel
            match = ConsultationModel.objects.filter(
                patient__nom__iexact=last_name,
                patient__prenom__iexact=first_name,
                date__date=today,
            ).order_by('-id').first()
            if match:
                consultation = match
                print(f'Found consultation by patient name: {match.id}')

    if consultation is None:
        return JsonResponse({'message': 'No matching consultation found'}, status=404)

    sop_uid = request.POST.get('sop_uid', '')
    
    if 'path' in request.POST:
        path = request.POST['path']
        wf = WaveformConsultation(
            consultation=consultation,
            sop_instance_uid=sop_uid,
            description=f"Waveform from {request.POST.get('called_aet', 'Unknown')}"
        )
        patient = consultation.patient
        out_path = repertoire_images_utilisateur(
            patient.compte.pk, patient.pk, 
            os.path.basename(path)
        )
        wf.image_preview.save(out_path, File(open(path, 'rb')))
        wf.save()
        print(f'Waveform saved: {wf.id}')
    
    resp = {
        'status': 'success',
    }
    return JsonResponse(resp)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def consultation_sr(request, pk):
    consult = get_object_or_404(Consultation, pk=pk)
    srs = SRConsultation.objects.filter(consultation=consult)
    print(srs)
    sr = consult.srconsultation_set.last()
    if sr:
        data = {'data': json.dumps(SRConsultationSerializer(sr).data)}
    else:
        data = {'data': '{}'}
    return JsonResponse(data)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def modifier_worklist(request, pk):
    print('********************************')
    #consultation = get_object_or_404(Consultation, pk=pk)
    #item = consultation.worklistitem_set.first()
    item = WorklistItem.objects.filter(consultation=pk).first()
    if item:
        device_id = request.POST.get('device', None)
        if device_id:
            device = get_object_or_404(Device, pk=device_id)
            item.device = device
            item.save()
    data = {}
    return JsonResponse(data)


@login_required
@permission_required('core.view_patient', raise_exception=True)
def send_patient_to_worklist(request, patient_pk):
    from apps.core.models import Patient, Admission, Consultation, Device
    from django.utils import timezone
    from pydicom.uid import generate_uid

    try:
        patient = get_object_or_404(Patient, pk=patient_pk)
        today = timezone.now().date()

        admission = Admission.objects.filter(
            patient=patient,
            date__day=today.day,
            date__month=today.month,
            date__year=today.year,
            statut='2'
        ).first()

        if not admission:
            from django.db.models import Max
            completed = Admission.objects.filter(
                patient=patient,
                date__day=today.day,
                date__month=today.month,
                date__year=today.year,
                statut='3'
            ).first()
            if completed:
                completed.statut = '2'
                completed.debut_consultation = timezone.now()
                completed.save()
                admission = completed
            else:
                return JsonResponse({'status': 'error', 'message': 'Patient non trouvé en consultation'}, status=400)

        consultation = Consultation.objects.filter(
            patient=patient,
            date__day=today.day,
            date__month=today.month,
            date__year=today.year
        ).order_by('-id').first()

        if not consultation:
            from apps.core.models import MotifConsultation
            motif = MotifConsultation.objects.first()
            consultation = Consultation.objects.create(
                patient=patient,
                motif=motif,
                date=timezone.now(),
                praticien=request.user.profil.medecin if hasattr(request.user.profil, 'medecin') else None,
            )

        existing = WorklistItem.objects.filter(
            consultation=consultation,
            mpps_status__in=[WorklistItem.MPPS_STATUS_PENDING, WorklistItem.MPPS_STATUS_INPROGRESS]
        )
        if existing.exists():
            existing.update(mpps_status=WorklistItem.MPPS_STATUS_DISCONTINUED)

        default_device = Device.objects.first()

        worklist_item = WorklistItem.objects.create(
            consultation=consultation,
            study_instance_uid=generate_uid(),
            mpps_status=WorklistItem.MPPS_STATUS_PENDING,
            device=default_device
        )

        return JsonResponse({
            'status': 'success',
            'message': f'Patient {patient.nom_complet} envoyé vers la machine DICOM',
            'worklist_id': worklist_item.id
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def terminer_consultation_patient(request, patient_pk):
    from django.db.models import Q
    from datetime import date
    try:
        patient = get_object_or_404(Patient, pk=patient_pk)
        today = date.today()
        consultation = Consultation.objects.filter(
            patient=patient,
            date__day=today.day,
            date__month=today.month,
            date__year=today.year,
        ).order_by('-id').first()
        if not consultation:
            return JsonResponse({'status': 'error', 'message': 'Aucune consultation en cours'}, status=400)
        consultation.worklistitem_set.all().update(mpps_status=WorklistItem.MPPS_STATUS_COMPLETED)
        patient.admission_set.filter(
            Q(date__day=today.day) & Q(date__month=today.month) & Q(date__year=today.year)
        ).update(statut='3')
        patient.rdv_set.filter(
            debut__day=today.day, debut__month=today.month, debut__year=today.year
        ).update(statut=3)
        return JsonResponse({'status': 'success', 'message': 'Consultation terminée'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)