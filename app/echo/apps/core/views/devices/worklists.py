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
    Consultation, Device
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

    #items = items.filter(mpps_status__in=[WorklistItem.MPPS_STATUS_PENDING, WorklistItem.MPPS_STATUS_INPROGRESS])
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
    if 'study_uid' in request.POST:
        study_uid = request.POST['study_uid']
        print(f'Requesting worklist item with study id {study_uid}')
        try:
            item = WorklistItem.objects.get(study_instance_uid=study_uid)
            print(f'Found item {item}')
        except WorklistItem.DoesNotExist:
            return JsonResponse({'message': f'Study with ID {study_uid} not found'}, status=404)
        if 'path' in request.POST:
            path = request.POST['path']
            ic = ImageConsultation(type=ImageConsultation.IMG_ECHO, consultation=item.consultation,
                                   date=datetime.datetime.now(), impression=False)
            ic.save()
            patient = item.consultation.patient
            out_path = repertoire_images_utilisateur(patient.compte.pk, patient.pk, os.path.basename(path))
            ic.image.save(out_path, File(open(path, 'rb')))
    resp = {
        'status': 'success',
    }
    return JsonResponse(resp)


@csrf_exempt
def ajouter_sr(request):
    if 'study_uid' in request.POST:
        study_uid = request.POST['study_uid']
        print(f'Requesting worklist item with study id {study_uid}')
        try:
            item = WorklistItem.objects.get(study_instance_uid=study_uid)
            print(f'Found item {item}')
            if 'data' in request.POST:
                data = request.POST['data']
                sr = SRConsultation(consultation=item.consultation, date=datetime.datetime.now(), data=data)
                sr.save()
        except WorklistItem.DoesNotExist:
            return JsonResponse({'message': f'Study with ID {study_uid} not found'}, status=404)
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