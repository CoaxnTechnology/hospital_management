import datetime
import json
import logging
import os
import re

logger = logging.getLogger('dicom.storage')

from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import gettext as _
from django.utils import timezone
from django.core.files import File
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django.db.models import Max, Q

from apps.core.models import WorklistItem, ImageConsultation, repertoire_images_utilisateur, SRConsultation, \
    Consultation, Device, Patient, Admission, DonneesFoetus, MotifRdv, Medecin
from apps.core.serializers import WorklistItemSerializer, SRConsultationSerializer


def _complete_admission_if_mpps_done(consultation):
    """If the WorklistItem already has mpps_status=COMPLETED (MPPS ended before data arrived),
    complete the admission now."""
    if consultation.worklistitem_set.filter(mpps_status=WorklistItem.MPPS_STATUS_COMPLETED).exists():
        today = datetime.date.today()
        consultation.patient.admission_set.filter(
            date__day=today.day,
            date__month=today.month,
            date__year=today.year,
            statut='2'
        ).update(statut='3')


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
        device_ae_title = request.POST['device']
        print(f'Filtering worklist by device AE title: {device_ae_title}')
        try:
            device = Device.objects.filter(ae_title=device_ae_title).first()
            if device:
                items = items.filter(
                    Q(device=device) | Q(device__isnull=True),
                    consultation__patient__compte=device.compte
                )
                from apps.core.models import Medecin
                device_doctors = Medecin.objects.filter(default_device=device).values_list('id', flat=True)
                if device_doctors:
                    items = items.filter(consultation__praticien__in=device_doctors)
                    print(f'Filtered by device doctors: {list(device_doctors)}')
                else:
                    print(f'No doctors configured for device {device_ae_title}, returning all account items')
            else:
                print(f'No Device found with AE title {device_ae_title}')
        except Exception as e:
            print(f'Error filtering by device AE title: {e}')

    items = items.filter(mpps_status__in=[WorklistItem.MPPS_STATUS_PENDING, WorklistItem.MPPS_STATUS_INPROGRESS]).distinct()
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
        item = WorklistItem.objects.filter(study_instance_uid=study_uid).first()
        if not item:
            return JsonResponse({'status': 'success', 'message': 'study_uid not found, skipped'})

        if 'status' in request.POST:
            status = request.POST['status']
            item.mpps_status = status
            item.save()

            if status.upper() == 'COMPLETED':
                consultation = item.consultation
                today = datetime.date.today()
                consultation.patient.admission_set.filter(
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
    calling_aet = request.POST.get('calling_aet', '')
    study_uid = request.POST.get('study_uid', '')
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
            # Only match consultations for doctors who have this device as their default
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
                # If device info available, restrict to its doctors
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
        _complete_admission_if_mpps_done(consultation)
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
        _complete_admission_if_mpps_done(consultation)

        # Auto-create DonneesFoetus records from SR data
        try:
            sr_data = json.loads(data)
            from apps.core.models import ConsultationObstetrique
            try:
                obs_consult = ConsultationObstetrique.objects.get(id=consultation.id)
            except ConsultationObstetrique.DoesNotExist:
                obs_consult = None

            if obs_consult is not None:
                # Uterine Doppler -> ConsultationObstetrique fields
                ut = sr_data.get('doppler_uterin', {})
                changed = False
                if 'ir_gauche' in ut and ut['ir_gauche'] is not None:
                    obs_consult.ir_gauche = float(ut['ir_gauche'])
                    changed = True
                if 'ip_gauche' in ut and ut['ip_gauche'] is not None:
                    obs_consult.ip_gauche = float(ut['ip_gauche'])
                    changed = True
                if 'ir_droit' in ut and ut['ir_droit'] is not None:
                    obs_consult.ir_droit = float(ut['ir_droit'])
                    changed = True
                if 'ip_droit' in ut and ut['ip_droit'] is not None:
                    obs_consult.ip_droit = float(ut['ip_droit'])
                    changed = True
                if changed:
                    obs_consult.save()
                    logger.info(f'Updated ConsultationObstetrique {obs_consult.id} uterine Doppler')

                # Remove existing DonneesFoetus for this consultation to avoid duplicates
                obs_consult.donneesfoetus_set.all().delete()

                # Fetal data -> DonneesFoetus
                foetus_list = sr_data.get('foetus', [])
                for foetus in foetus_list:
                    df = DonneesFoetus(consultation=obs_consult)

                    # Weight
                    if foetus.get('poids') is not None:
                        df.poids = float(foetus['poids'])
                        df.poids_estime = float(foetus['poids'])

                    # Biometry
                    bio = foetus.get('biometrie', {})
                    if bio.get('bip') is not None:
                        df.bip = float(bio['bip'])
                    if bio.get('pc') is not None:
                        df.pc = float(bio['pc'])
                    if bio.get('pa') is not None:
                        df.pa = float(bio['pa'])
                    if bio.get('femur') is not None:
                        df.femur = float(bio['femur'])
                    if bio.get('lcc') is not None:
                        df.lcc = float(bio['lcc'])
                    if bio.get('dat') is not None:
                        df.dat = float(bio['dat'])
                    if bio.get('cn') is not None:
                        df.cn = float(bio['cn'])
                    if bio.get('humerus') is not None:
                        df.humerus = float(bio['humerus'])
                    if bio.get('cervelet') is not None:
                        df.cervelet = float(bio['cervelet'])

                    # Fetal Doppler
                    dop = foetus.get('doppler_ombilical', {})
                    if dop.get('doppler_cordon_ir') is not None:
                        df.doppler_cordon_ir = float(dop['doppler_cordon_ir'])
                    if dop.get('doppler_cordon_ip') is not None:
                        df.doppler_cordon_ip = float(dop['doppler_cordon_ip'])

                    dop_acm = foetus.get('doppler_acm', {})
                    if dop_acm.get('doppler_acm_ir') is not None:
                        df.doppler_acm_ir = float(dop_acm['doppler_acm_ir'])
                    if dop_acm.get('doppler_acm_ip') is not None:
                        df.doppler_acm_ip = float(dop_acm['doppler_acm_ip'])
                    if dop_acm.get('doppler_acm_vitesse') is not None:
                        df.doppler_acm_vitesse = float(dop_acm['doppler_acm_vitesse'])

                    dop_dv = foetus.get('doppler_dv', {})
                    if dop_dv.get('doppler_dv_ir') is not None:
                        df.doppler_dv_ir = float(dop_dv['doppler_dv_ir'])
                    if dop_dv.get('doppler_dv_ip') is not None:
                        df.doppler_dv_ip = float(dop_dv['doppler_dv_ip'])

                    df.save()
                    logger.info(f'Created DonneesFoetus id={df.id} for consultation {obs_consult.id} foetus index {foetus_list.index(foetus)}')
        except Exception as e:
            logger.error(f'Failed to auto-create DonneesFoetus from SR data: {e}', exc_info=True)
    else:
        logger.warning('No data field in SR POST')

    resp = {
        'status': 'success',
    }
    return JsonResponse(resp)


@csrf_exempt
def ajouter_waveform(request):
    """Handle DICOM Waveform upload."""
    from apps.core.models import WaveformConsultation
    
    consultation = None
    calling_aet = request.POST.get('calling_aet', '')
    study_uid = request.POST.get('study_uid', '')
    if study_uid:
        print(f'Requesting worklist item with study id {study_uid}')
        item = WorklistItem.objects.filter(study_instance_uid=study_uid).first()
        if item:
            print(f'Found item {item}')
            consultation = item.consultation
        else:
            print(f'WorklistItem with UID {study_uid} not found, trying fallbacks')

    if consultation is None and calling_aet:
        device = Device.objects.filter(ae_title=calling_aet).first()
        if device:
            today = datetime.datetime.now().date()
            item = WorklistItem.objects.filter(
                device=device,
                consultation__date__date=today,
                mpps_status__in=[WorklistItem.MPPS_STATUS_PENDING, WorklistItem.MPPS_STATUS_INPROGRESS]
            ).order_by('-id').first()
            if item:
                consultation = item.consultation
                print(f'Found consultation {item.consultation.id} by WorklistItem for device={calling_aet}')

    if consultation is None and 'patient_name' in request.POST:
        patient_name = request.POST['patient_name']
        parts = patient_name.split('^')
        if len(parts) >= 2 and parts[0] and parts[1]:
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
        from apps.core.models import Consultation as ConsultationModel
        today = datetime.datetime.now().date()
        active = ConsultationModel.objects.filter(
            date__date=today,
        ).order_by('-id').first()
        if active:
            consultation = active
            print(f'Found consultation by active admission fallback: {active.id}')

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
    if consult.date:
        srs = SRConsultation.objects.filter(
            consultation__patient=consult.patient,
            date__date=consult.date.date()
        )
        sr = srs.last()
    else:
        sr = None
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
        if consultation:
            items = consultation.worklistitem_set.all()
            items.filter(mpps_status=WorklistItem.MPPS_STATUS_INPROGRESS).update(
                mpps_status=WorklistItem.MPPS_STATUS_DISCONTINUED
            )
            items.filter(mpps_status=WorklistItem.MPPS_STATUS_PENDING).update(
                mpps_status=WorklistItem.MPPS_STATUS_DISCONTINUED
            )
        patient.admission_set.filter(
            Q(date__day=today.day) & Q(date__month=today.month) & Q(date__year=today.year)
        ).update(statut='3')
        patient.rdv_set.filter(
            debut__day=today.day, debut__month=today.month, debut__year=today.year
        ).update(statut=3)
        return JsonResponse({'status': 'success', 'message': 'Consultation terminée'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_POST
def demarrer_examen(request, patient_pk):
    from django.shortcuts import redirect
    from pydicom.uid import generate_uid
    try:
        patient = get_object_or_404(Patient, pk=patient_pk)
        compte = request.user.profil.compte
        today = datetime.date.today()
        jour_min = datetime.datetime.combine(today, datetime.time.min)
        jour_max = datetime.datetime.combine(today, datetime.time.max)

        consultation = Consultation.objects.filter(
            patient=patient,
            date__gte=jour_min,
            date__lte=jour_max,
        ).order_by('-id').first()

        if not consultation:
            return JsonResponse({'status': 'error', 'message': _('Aucune consultation trouvée pour ce patient aujourd\'hui')}, status=404)

        device = Device.objects.filter(compte=compte).first()
        if not device:
            return JsonResponse({'status': 'error', 'message': _('Aucun dispositif DICOM configuré')}, status=400)

        WorklistItem.objects.filter(
            consultation__patient=patient,
            mpps_status__in=[WorklistItem.MPPS_STATUS_PENDING, WorklistItem.MPPS_STATUS_INPROGRESS]
        ).exclude(consultation=consultation).update(mpps_status=WorklistItem.MPPS_STATUS_DISCONTINUED)

        item, created = WorklistItem.objects.get_or_create(
            consultation=consultation,
            defaults={
                'study_instance_uid': generate_uid(),
                'mpps_status': WorklistItem.MPPS_STATUS_PENDING,
                'device': device,
            },
        )
        if not created:
            item.mpps_status = WorklistItem.MPPS_STATUS_PENDING
            item.device = device
            item.save(update_fields=['mpps_status', 'device'])

        return JsonResponse({'status': 'success', 'redirect': f'/consultation/{consultation.pk}/rapport/'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_POST
def remettre_en_salle_patient(request, patient_pk):
    from django.db.models import Q
    from datetime import date
    import datetime as dt
    try:
        patient = get_object_or_404(Patient, pk=patient_pk)
        today = date.today()
        jour_min = dt.datetime.combine(today, dt.time.min)
        jour_max = dt.datetime.combine(today, dt.time.max)

        consultation = Consultation.objects.filter(
            patient=patient,
            date__gte=jour_min,
            date__lte=jour_max,
        ).order_by('-id').first()
        if consultation:
            consultation.worklistitem_set.filter(
                mpps_status__in=[WorklistItem.MPPS_STATUS_INPROGRESS, WorklistItem.MPPS_STATUS_PENDING]
            ).update(mpps_status=WorklistItem.MPPS_STATUS_DISCONTINUED)

        admission = Admission.objects.filter(
            patient=patient,
            date__gte=jour_min,
            date__lte=jour_max,
        ).order_by('-id').first()

        if admission:
            admission.statut = '1'
            admission.debut_consultation = None
            admission.save(update_fields=['statut', 'debut_consultation'])
        else:
            compte = request.user.profil.compte
            praticien = getattr(request.user, 'medecin', None) or Medecin.objects.filter(compte=compte).first()
            motif = MotifRdv.objects.first()
            ordre_max = Admission.objects.filter(
                Q(patient__compte=compte) & Q(date__gte=jour_min) & Q(date__lte=jour_max)
            ).aggregate(Max('ordre'))['ordre__max']
            ordre = 1 if ordre_max is None else ordre_max + 1
            numero_max = Admission.objects.filter(
                patient__compte=compte, date__year=today.year
            ).aggregate(Max('numero'))['numero__max']
            numero = 1 if numero_max is None else numero_max + 1
            Admission.objects.create(
                numero=numero, patient=patient, praticien=praticien,
                date=timezone.now(), ordre=ordre, statut='1', motif=motif,
            )

        return JsonResponse({'status': 'success', 'message': 'Patient renvoyé en salle d\'attente'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)