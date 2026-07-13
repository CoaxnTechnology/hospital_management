import datetime
import json
import logging
import os
import re

logger = logging.getLogger('dicom.storage')

from django.contrib.auth.decorators import login_required, permission_required
from django.core.files import File
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from apps.core.models import WorklistItem, ImageConsultation, repertoire_images_utilisateur, SRConsultation, \
    Consultation, Device, Patient
from apps.core.serializers import WorklistItemSerializer, SRConsultationSerializer
from django.db import models
from django.db.models import Q


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
        from apps.core.models import Device, Medecin
        device_obj = Device.objects.filter(ae_title=request.POST['device']).first()
        if device_obj:
            device_doctors = Medecin.objects.filter(default_device=device_obj).values_list('id', flat=True)
            if device_doctors:
                items = items.filter(consultation__praticien__in=device_doctors)
                print(f'Filtered by device doctors: {list(device_doctors)}')

    #items = items.filter(mpps_status__in=[WorklistItem.MPPS_STATUS_PENDING, WorklistItem.MPPS_STATUS_INPROGRESS])
    # Deduplicate: only the most recent WorklistItem per patient (handles double-click duplicates)
    items = items.order_by('consultation__patient_id', '-id').distinct('consultation__patient_id')
    print('Items found', items)
    data = WorklistItemSerializer(items, many=True)
    resp = {
        'items': json.dumps(data.data),
    }
    return JsonResponse(resp)


@csrf_exempt
def modifier_worklist_statut(request):
    if 'study_uid' in request.POST:
        study_uid = request.POST['study_uid']
        item = WorklistItem.objects.get(study_instance_uid=study_uid)
        if 'status' in request.POST:
            item.mpps_status = request.POST['status']
            item.save()
    resp = {
        'status': 'success',
    }
    return JsonResponse(resp)


@csrf_exempt
def ajouter_image(request):
    consultation = None
    study_uid = request.POST.get('study_uid', '')
    calling_aet = request.POST.get('calling_aet', '')
    patient_name = request.POST.get('patient_name', '')

    if study_uid:
        logger.info(f'ajouter_image: searching WorklistItem by study_uid={study_uid}')
        item = WorklistItem.objects.filter(study_instance_uid=study_uid).first()
        if item:
            logger.info(f'Found WorklistItem {item.id} for consultation {item.consultation.id}')
            consultation = item.consultation
        else:
            logger.info(f'WorklistItem with UID {study_uid} not found')

    if consultation is None and calling_aet:
        device = Device.objects.filter(ae_title=calling_aet).first()
        if device:
            today = datetime.datetime.now().date()
            from apps.core.models import Medecin
            device_doctors = Medecin.objects.filter(default_device=device).values_list('id', flat=True)
            item = WorklistItem.objects.filter(
                Q(device=device) | Q(device__isnull=True),
                consultation__date__date=today,
                consultation__praticien__in=device_doctors,
                mpps_status__in=[WorklistItem.MPPS_STATUS_PENDING, WorklistItem.MPPS_STATUS_INPROGRESS]
            ).order_by('-id').first()
            if item:
                consultation = item.consultation
                logger.info(f'Found consultation {item.consultation.id} by WorklistItem for device={calling_aet} (doctors={list(device_doctors)})')
            else:
                logger.info(f'No WorklistItem found for device={calling_aet} today with doctors={list(device_doctors)}')

    if consultation is None and patient_name:
        logger.info(f'ajouter_image: trying patient name fallback: {patient_name}')
        try:
            if '^' in patient_name:
                parts = patient_name.split('^')
                nom_dcm = parts[0].strip()
                prenom_dcm = parts[1].strip() if len(parts) > 1 else ''
            else:
                nom_dcm = patient_name.strip()
                prenom_dcm = ''
            patient_qs = Patient.objects.filter(nom__iexact=nom_dcm, prenom__iexact=prenom_dcm)
            if not patient_qs:
                patient_qs = Patient.objects.filter(nom__icontains=nom_dcm, prenom__icontains=prenom_dcm)
            if patient_qs:
                patient = patient_qs.first()
                today = datetime.datetime.now().date()
                jour_min = datetime.datetime.combine(today, datetime.time.min)
                jour_max = datetime.datetime.combine(today, datetime.time.max)
                cons_qs = Consultation.objects.filter(patient=patient, date__gte=jour_min, date__lte=jour_max)
                if calling_aet:
                    device = Device.objects.filter(ae_title=calling_aet).first()
                    if device:
                        from apps.core.models import Medecin
                        device_doctors = Medecin.objects.filter(default_device=device).values_list('id', flat=True)
                        cons_qs = cons_qs.filter(praticien__in=device_doctors)
                        logger.info(f'Restricted patient name fallback to device doctors={list(device_doctors)}')
                cons = cons_qs.order_by('-id').first()
                if cons:
                    logger.info(f'Found consultation {cons.id} for patient {patient.id} via name+date fallback')
                    consultation = cons
        except Exception as e:
            logger.error(f'ajouter_image patient name fallback failed: {e}', exc_info=True)

    if consultation is None:
        logger.info(f'ajouter_image: no matching consultation found for study={study_uid} patient={patient_name}')
        return JsonResponse({'message': 'No matching consultation found'}, status=404)

    if 'path' in request.POST:
        path = request.POST['path']
        if not os.path.exists(path):
            logger.warning(f"Image file not found: {path}")
            return JsonResponse({'message': 'Image file not found'}, status=404)
        device = Device.objects.filter(ae_title=calling_aet).first() if calling_aet else None
        ic = ImageConsultation(type=ImageConsultation.IMG_ECHO, consultation=consultation,
                               device=device,
                               date=datetime.datetime.now(), impression=False)
        patient = consultation.patient
        out_path = repertoire_images_utilisateur(patient.compte.pk, patient.pk, os.path.basename(path))
        ic.image.save(out_path, File(open(path, 'rb')))
    resp = {
        'status': 'success',
    }
    return JsonResponse(resp)


@csrf_exempt
def ajouter_sr(request):
    consultation = None
    study_uid = request.POST.get('study_uid', '')
    patient_name = request.POST.get('patient_name', '')
    calling_aet = request.POST.get('calling_aet', '')
    logger.info(f"ajouter_sr called: study_uid={study_uid}, patient_name={patient_name}, calling_aet={calling_aet}")

    if study_uid:
        logger.info(f'Searching WorklistItem by study_uid={study_uid}')
        item = WorklistItem.objects.filter(study_instance_uid=study_uid).first()
        if item:
            logger.info(f'Found WorklistItem {item.id} for consultation {item.consultation.id}')
            consultation = item.consultation
        else:
            logger.info(f'WorklistItem with UID {study_uid} not found')

    if consultation is None and calling_aet:
        device = Device.objects.filter(ae_title=calling_aet).first()
        if device:
            today = datetime.datetime.now().date()
            from apps.core.models import Medecin
            device_doctors = Medecin.objects.filter(default_device=device).values_list('id', flat=True)
            item = WorklistItem.objects.filter(
                Q(device=device) | Q(device__isnull=True),
                consultation__date__date=today,
                consultation__praticien__in=device_doctors,
                mpps_status__in=[WorklistItem.MPPS_STATUS_PENDING, WorklistItem.MPPS_STATUS_INPROGRESS]
            ).order_by('-id').first()
            if item:
                logger.info(f'Found consultation {item.consultation.id} by WorklistItem for device={calling_aet} (doctors={list(device_doctors)})')
                consultation = item.consultation
            else:
                logger.info(f'No WorklistItem found for device={calling_aet} today with doctors={list(device_doctors)}')

    if consultation is None and patient_name:
        logger.info(f'Trying patient name fallback: patient_name={patient_name}')
        try:
            if '^' in patient_name:
                parts = patient_name.split('^')
                nom_dcm = parts[0].strip()
                prenom_dcm = parts[1].strip() if len(parts) > 1 else ''
            else:
                nom_dcm = patient_name.strip()
                prenom_dcm = ''
            from apps.core.models import Patient
            patient_qs = Patient.objects.filter(nom__iexact=nom_dcm, prenom__iexact=prenom_dcm)
            if not patient_qs:
                patient_qs = Patient.objects.filter(nom__icontains=nom_dcm, prenom__icontains=prenom_dcm)
            if patient_qs:
                patient = patient_qs.first()
                today = datetime.datetime.now().date()
                jour_min = datetime.datetime.combine(today, datetime.time.min)
                jour_max = datetime.datetime.combine(today, datetime.time.max)
                cons_qs = Consultation.objects.filter(patient=patient, date__gte=jour_min, date__lte=jour_max)
                if calling_aet:
                    device = Device.objects.filter(ae_title=calling_aet).first()
                    if device:
                        from apps.core.models import Medecin
                        device_doctors = Medecin.objects.filter(default_device=device).values_list('id', flat=True)
                        cons_qs = cons_qs.filter(praticien__in=device_doctors)
                        logger.info(f'Restricted patient name fallback to device doctors={list(device_doctors)}')
                cons = cons_qs.order_by('-id').first()
                if cons:
                    logger.info(f'Found consultation {cons.id} for patient {patient.id} via name+date fallback')
                    consultation = cons
                else:
                    logger.info(f'No consultation today for patient {patient.id} (nom={nom_dcm} prenom={prenom_dcm})')
            else:
                logger.info(f'No patient found matching name: {nom_dcm} {prenom_dcm}')
        except Exception as e:
            logger.error(f'Patient name fallback failed: {e}', exc_info=True)

    if consultation is None:
        logger.error('No matching consultation found for SR - returning 404')
        return JsonResponse({'message': 'No matching consultation found'}, status=404)

    if 'data' in request.POST:
        data = request.POST['data']
        logger.info(f'Saving SRConsultation for consultation {consultation.id}')
        sr = SRConsultation(consultation=consultation, date=datetime.datetime.now(), data=data)
        sr.save()
        logger.info(f'SRConsultation saved id={sr.id}')
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
        data = {'data': 'null'}
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