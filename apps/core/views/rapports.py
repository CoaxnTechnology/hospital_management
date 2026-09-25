import datetime as dt
import json
import logging
logger = logging.getLogger(__name__)

from dateutil.parser import *
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core import serializers
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView

import json

from apps.core.models import (
    Consultation,
    ImageConsultation,
    SRConsultation,
    MesuresConsultation,
    WaveformConsultation,
    CategorieConsultation,
    MotifConsultation,
    Praticien,
    Medecin,
    Grossesse,
    ConsultationObstetrique,
    DonneesFoetus,
    ConsultationEchoPelvienne,
)
from apps.core.serializers import (
    ConsultationSerializer,
    MotifSerializer,
    PraticienSerializer,
    GrossesseSerializer,
    ConsultationRapportSerializer,
    GrossesseRapportSerializer,
)


class RapportConsultationList(PermissionRequiredMixin, View):
    template_name = "core/rapport_consultation.html"
    permission_required = "core.view_patient"

    def get(self, request):
        # consultations = json.dumps(ConsultationRapportSerializer(qs, many=True).data)
        consultations = []
        categories = self.request.user.profil.compte.categories_consultations.all()
        motifs = MotifConsultation.objects.all().select_related("categorie")
        motifs_json = json.dumps(MotifSerializer(motifs, many=True).data)
        lst = []
        """for q in qs:
            if q.patient.mot_cle and q.patient.mot_cle is not None:
                mots = json.loads(q.patient.mot_cle)
                cles = map(lambda m: m['value'], mots)
                lst.extend(cles)
        mots_cles = list(set(lst))
        mot_patient = mots_cles
        """
        mot_patient = []
        praticiens_corresp = Praticien.objects.filter(
            compte=self.request.user.profil.compte
        )
        praticiens = Medecin.objects.filter(compte=self.request.user.profil.compte)

        return render(
            request,
            self.template_name,
            {
                "object_list": consultations,
                "categories": categories,
                "motifs": motifs,
                "motifs_json": motifs_json,
                "mots_patients": mot_patient,
                "praticiens_corresp": praticiens_corresp,
                "praticiens": praticiens,
            },
        )


@login_required
@permission_required("core.view_patient", raise_exception=True)
def rechercher_consultation(request):
    objects = (
        Consultation.objects.filter(patient__compte=request.user.profil.compte)
        .select_related("patient")
        .select_related("praticien")
        .select_related("motif")
        .select_related("motif__categorie")
    )

    # Data table request
    draw = request.POST.get("draw", None)
    start = int(request.POST.get("start", None))
    length = int(request.POST.get("length", None))
    order_col = int(request.POST.get("order[0][column]", None))
    order_col_name = request.POST.get("columns[{}][data]".format(order_col)).replace(
        ".", "__"
    )
    if order_col == 9:
        order_col_name = "praticien__user"
    order_dir = request.POST.get("order[0][dir]", None)
    dir = ""
    if order_dir == "desc":
        dir = "-"

    """
    print("---------------------------")
    for i in range(0, 15):
        val = request.POST.get(f'columns[{i}][search][value]')
        print(f'Col {i}', val)
    print("---------------------------")
    """
    filtered = objects
    ipp = request.POST.get("columns[0][search][value]")
    if ipp:
        filtered = filtered.filter(patient__id=ipp)
    gouvernorat = request.POST.get("columns[1][search][value]")
    if gouvernorat:
        filtered = filtered.filter(patient__adresse__gouvernorat__icontains=gouvernorat)
    prat_corresp = request.POST.get("columns[2][search][value]")
    if prat_corresp:
        filtered = filtered.filter(
            patient__praticiens_correspondants__nom__icontains=prat_corresp
        )
    nom = request.POST.get("columns[4][search][value]")
    if nom:
        filtered = filtered.filter(patient__nom__icontains=nom)
    nom_naissance = request.POST.get("columns[5][search][value]")
    if nom_naissance:
        filtered = filtered.filter(patient__nom_naissance__icontains=nom_naissance)
    prenom = request.POST.get("columns[6][search][value]")
    if prenom:
        filtered = filtered.filter(patient__prenom__icontains=prenom)
    praticien = request.POST.get("columns[9][search][value]")
    if praticien:
        filtered = filtered.filter(praticien_id=praticien)
    categorie = request.POST.get("columns[7][search][value]")
    if categorie:
        filtered = filtered.filter(motif__categorie_id=categorie)
    motif = request.POST.get("columns[8][search][value]")
    if motif:
        filtered = filtered.filter(motif_id=motif)
    mots_cles = request.POST.get("columns[10][search][value]")
    if mots_cles:
        mots_parsed = json.loads(mots_cles)  # [{"value":"diabète"}]
        for m in mots_parsed:
            filtered = filtered.filter(patient__mot_cle__icontains=m["value"])
    debut = request.POST.get("columns[11][search][value]")
    if debut and debut != "":
        print("Debut", debut)
        filtered = filtered.filter(date__gte=debut)
    fin = request.POST.get("columns[12][search][value]")
    if fin and fin != "":
        filtered = filtered.filter(date__lte=fin)

    print("Order col name", order_col_name)
    filtered = filtered.order_by(dir + order_col_name)
    # filtered = objects.filter(patient__pk__icontains=ipp).order_by(dir + order_col_name)
    total = objects.count()
    filtered_count = filtered.count()
    objs = filtered[start : start + length - 1]
    objs_json = ConsultationRapportSerializer(objs, many=True)
    resp = {
        "draw": draw,
        "recordsTotal": total,
        "recordsFiltered": filtered_count,
        "data": objs_json.data,
    }
    return JsonResponse(resp)


class RapportAccouchementList(PermissionRequiredMixin, View):
    template_name = "core/rapport_accouchement.html"
    permission_required = "core.view_patient"

    def get(self, request):
        qs = (
            Grossesse.objects.filter(
                patient__compte=self.request.user.profil.compte, encours=True
            )
            .select_related("patient")
            .select_related("lieu_accouchement")
            .order_by("pk")
        )
        accouchements = json.dumps(GrossesseRapportSerializer(qs, many=True).data)

        return render(request, self.template_name, {"accouchements": accouchements})


# Alias for URL backward compatibility
RapportAccouchementList = RapportAccouchementList


class ConsultationView(PermissionRequiredMixin, DetailView):
    model = Consultation
    template_name = "core/consultation_detail.html"
    permission_required = "core.view_patient"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def _get_measurements(consultation):
    """
    Returns the final measurement dict for a consultation.
    Priority: MesuresConsultation (manual edits) > SRConsultation (raw DICOM, date-based) > Database consultation models.
    """
    # 1. Try manual overrides first
    try:
        m = consultation.mesures
        if m and m.data:
            data = json.loads(m.data)
            if data:
                return data, 'manual'
    except Exception as e:
        logger.warning(f"_get_measurements (manual) failed for consultation {consultation.id}: {e}")
        pass

    # 2. Fall back to raw DICOM SR (date-based — same day, any consultation for this patient)
    try:
        if consultation.date:
            sr = SRConsultation.objects.filter(
                consultation__patient=consultation.patient,
                date__date=consultation.date.date()
            ).last()
        else:
            sr = None
        if sr and sr.data:
            data = json.loads(sr.data)
            if data:
                return data, 'dicom'
    except Exception as e:
        logger.warning(f"_get_measurements (SR) failed for consultation {consultation.id}: {e}")
        pass

    # 3. Fall back to data saved directly in consultation models
    try:
        # Check ConsultationEchoPelvienne
        try:
            pelv = consultation.consultationechopelvienne
            pelv_data = {}
            if pelv.longueur: pelv_data['uterus_longueur'] = pelv.longueur
            if pelv.largeur: pelv_data['uterus_largeur'] = pelv.largeur
            if pelv.hauteur: pelv_data['uterus_hauteur'] = pelv.hauteur
            if pelv.volume_uterin: pelv_data['uterus_volume'] = pelv.volume_uterin
            if pelv.endometre_epaisseur: pelv_data['endometre_epaisseur'] = pelv.endometre_epaisseur
            if pelv_data:
                return pelv_data, 'form'
        except Exception:
            pass

        # Check ConsultationObstetrique
        try:
            obs = consultation.consultationobstetrique
            foetus_qs = obs.donneesfoetus_set.all()
            if foetus_qs.exists():
                obs_data = {'foetus': []}
                for f in foetus_qs:
                    f_dict = {
                        'poids': f.poids or f.poids_estime,
                        'fc': f.fc,
                        'biometrie': {},
                        'os': {},
                        'crane': {},
                    }
                    if f.bip: f_dict['biometrie']['bip'] = f.bip
                    if f.pc: f_dict['biometrie']['pc'] = f.pc
                    if f.pa: f_dict['biometrie']['pa'] = f.pa
                    if f.femur: f_dict['biometrie']['femur'] = f.femur
                    if f.lcc: f_dict['biometrie']['lcc'] = f.lcc
                    if f.cn: f_dict['biometrie']['cn'] = f.cn
                    if f.epn: f_dict['biometrie']['epn'] = f.epn
                    if f.dat: f_dict['biometrie']['dat'] = f.dat
                    if f.humerus: f_dict['os']['humerus'] = f.humerus
                    if f.radius: f_dict['os']['radius'] = f.radius
                    if f.cubitus: f_dict['os']['cubitus'] = f.cubitus
                    if f.tibia: f_dict['os']['tibia'] = f.tibia
                    if f.perone: f_dict['os']['perone'] = f.perone
                    if f.pied: f_dict['os']['pied'] = f.pied
                    if f.cervelet: f_dict['crane']['cervelet'] = f.cervelet
                    if f.dio: f_dict['crane']['dio'] = f.dio

                    if f.doppler_cordon_ip or f.doppler_cordon_ir:
                        f_dict['doppler_ombilical'] = {
                            'doppler_cordon_ip': f.doppler_cordon_ip,
                            'doppler_cordon_ir': f.doppler_cordon_ir,
                        }
                    if f.doppler_acm_ip or f.doppler_acm_ir:
                        f_dict['doppler_acm'] = {
                            'doppler_acm_ip': f.doppler_acm_ip,
                            'doppler_acm_ir': f.doppler_acm_ir,
                        }

                    obs_data['foetus'].append(f_dict)

                if obs.col_long:
                    obs_data['col_longueur'] = obs.col_long
                if obs.ir_droit or obs.ir_gauche or obs.ip_droit or obs.ip_gauche:
                    obs_data['doppler_uterin'] = {
                        'ir_droit': obs.ir_droit,
                        'ir_gauche': obs.ir_gauche,
                        'ip_droit': obs.ip_droit,
                        'ip_gauche': obs.ip_gauche,
                    }

                has_any_val = any(bool(f_dict['biometrie'] or f_dict['os'] or f_dict['crane'] or f_dict['poids'] or f_dict['fc']) for f_dict in obs_data['foetus'])
                if has_any_val or obs.col_long:
                    return obs_data, 'form'
        except Exception:
            pass
    except Exception as e:
        logger.warning(f"_get_measurements (form fallback) failed: {e}")

    return None, None


def _fk_label(value):
    """Display label for a ListeChoix FK (localized via __str__), None when empty."""
    if value is None or value == '':
        return None
    try:
        label = str(value).strip()
    except Exception:
        return None
    return label or None


def _get_examen_resume(consultation):
    """
    Qualitative exam selections (dropdowns) for the printed report.
    Reads live from ConsultationObstetrique + DonneesFoetus rows so the report
    always reflects the exam form. Returns None when nothing was recorded.
    Structure: {'maternel': [{'label':..,'value':..}], 'clinique': [...],
                'foetus': [{'titre':.., 'vitalite': [...], 'morpho': [...], 'doppler': [...]}]}
    """
    from apps.core.models import ConsultationObstetrique

    try:
        obs = ConsultationObstetrique.objects.filter(pk=consultation.pk).first()
    except Exception:
        return None
    if obs is None:
        return None

    def item(label, value, unit=''):
        if value is None or value == '':
            return None
        return {'label': label, 'value': str(value) + (f' {unit}' if unit else '')}

    def fk_item(label, fk):
        label_value = _fk_label(fk)
        if not label_value:
            return None
        return {'label': label, 'value': label_value}

    maternel = [
        x for x in [
            fk_item('Notch droit', obs.notch_droit),
            fk_item('Notch gauche', obs.notch_gauche),
            item('Col — longueur', obs.col_long, 'mm'),
            item('Col — orifice interne', obs.col_orifice_interne, 'mm'),
            fk_item('Col — entonnoir', obs.col_entonnoir),
            fk_item('Pelvis maternel', obs.pelvis_maternel),
            fk_item('LMC', obs.lmc),
        ] if x
    ]

    leuco_values = []
    try:
        for choice in obs.leuco.all():
            label_value = _fk_label(choice)
            if label_value:
                leuco_values.append(label_value)
    except Exception:
        pass
    clinique = [
        x for x in [
            fk_item('Seins', obs.seins),
            fk_item('Examen sous spéculum', obs.examen_sous_speculum),
            ({'label': 'Leucorrhées', 'value': ', '.join(leuco_values)} if leuco_values else None),
            item('TV', obs.tv),
            item('Poids', obs.poids, 'kg'),
            item('TA', obs.ta),
            item('Température', obs.temperature, '°C'),
            item('Albuminurie', obs.alb),
            item('Glycémie', obs.gly),
            item('Commentaires cliniques', obs.commentaires_cliniques),
        ] if x
    ]

    foetus_list = []
    try:
        donnees = list(obs.donneesfoetus_set.all().order_by('id'))
    except Exception:
        donnees = []
    morpho_labels = [
        ('morpho_crane', 'Boîte crânienne'),
        ('morpho_struct', 'Structure cérébrale'),
        ('morpho_face', 'Face'),
        ('morpho_cou', 'Cou'),
        ('morpho_thorax', 'Thorax'),
        ('morpho_coeur', 'Cœur'),
        ('morpho_abdo', 'Paroi abdominale'),
        ('morpho_digest', 'Appareil digestif'),
        ('morpho_urine', 'Appareil urinaire'),
        ('morpho_rachis', 'Rachis'),
        ('morpho_membres', 'Membres'),
        ('morpho_oge', 'OGE'),
        ('morpho_pole_cepha', 'Pôle céphalique'),
        ('morpho_lmc', 'LMC'),
        ('morpho_liquide_amnio', 'Liquide amniotique'),
        ('morpho_placenta', 'Placenta'),
        ('morpho_cordon', 'Cordon'),
        ('morpho_trophoblaste_localisation', 'Trophoblaste — localisation'),
        ('morpho_trophoblaste_aspect', 'Trophoblaste — aspect'),
        ('morpho_decol', 'Décollement'),
    ]
    for idx, df in enumerate(donnees, start=1):
        vitalite = [
            x for x in [
                fk_item('Présentation', df.presentation),
                fk_item('Activité cardiaque', df.activite_cardiaque),
                fk_item('Mobilité', df.mobilite),
            ] if x
        ]
        morpho = []
        for field_name, field_label in morpho_labels:
            try:
                entry = fk_item(field_label, getattr(df, field_name))
            except Exception:
                entry = None
            if entry:
                morpho.append(entry)
        doppler = [
            x for x in [
                fk_item('Flux en diastole (ombilical)', df.doppler_cordon_diastole),
                fk_item('Onde A (ductus veineux)', df.doppler_dv_onde),
            ] if x
        ]
        commentaires = (df.commentaires or '').strip() if hasattr(df, 'commentaires') else ''
        if vitalite or morpho or doppler or commentaires:
            foetus_list.append({
                'titre': f'FŒTUS {idx}' if len(donnees) > 1 else 'FŒTUS',
                'vitalite': vitalite,
                'morpho': morpho,
                'doppler': doppler,
                'commentaires': commentaires or None,
            })

    sac = []
    try:
        from apps.core.models import ConsultationEcho11SA
        echo11 = ConsultationEcho11SA.objects.filter(pk=consultation.pk).first()
    except Exception:
        echo11 = None
    if echo11 is not None:
        sac = [
            x for x in [
                fk_item('Sac — localisation', echo11.sac_gestationnel_localisation),
                fk_item('Sac — tonicité', echo11.sac_gestationnel_tonicite),
                fk_item('Sac — trophoblaste', echo11.sac_gestationnel_trophoblaste),
                fk_item('Sac — décollement', echo11.sac_gestationnel_decollement),
                fk_item('Extrémité céphalique', getattr(echo11, 'morpho_extremite_cephalique', None)),
                fk_item('Membres (11SA)', getattr(echo11, 'morpho_membres', None)),
                fk_item('Activité cardiaque (11SA)', getattr(echo11, 'activite_cardiaque', None)),
            ] if x
        ]

    if not maternel and not clinique and not foetus_list and not sac:
        return None
    has_extra = bool(sac) or bool(maternel) or bool(clinique) or any(
        f.get('doppler') for f in foetus_list
    )
    return {
        'maternel': maternel,
        'clinique': clinique,
        'foetus': foetus_list,
        'sac': sac,
        'has_extra': has_extra,
    }


class ConsultationRapportView(PermissionRequiredMixin, DetailView):
    model = Consultation
    template_name = "core/consultation_rapport.html"
    permission_required = "core.view_patient"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consultation = self.get_object()
        context['patient'] = consultation.patient
        try:
            context['parametres'] = self.request.user.profil.compte.parametrescompte
        except:
            context['parametres'] = None
        context['praticien'] = consultation.praticien

        if consultation.date:
            cons_date = consultation.date.date()
            images_qs = ImageConsultation.objects.filter(
                consultation__patient=consultation.patient,
                date__date=cons_date
            ).order_by('-date')
            context['images_echo'] = images_qs.filter(type=ImageConsultation.IMG_ECHO)
            context['images_graph'] = images_qs.filter(type=ImageConsultation.IMG_GRAPH)
            context['waveforms'] = WaveformConsultation.objects.filter(
                consultation__patient=consultation.patient,
                created_at__date=cons_date
            )
        else:
            context['images_echo'] = ImageConsultation.objects.none()
            context['images_graph'] = ImageConsultation.objects.none()
            context['waveforms'] = WaveformConsultation.objects.none()

        obs = None
        try:
            obs = consultation.consultationobstetrique
        except Exception:
            pass
        context['consultation_obs'] = obs

        foetus_list = []
        if obs:
            foetus_list = list(obs.donneesfoetus_set.all().select_related(
                'presentation', 'activite_cardiaque', 'mobilite',
                'morpho_crane', 'morpho_struct', 'morpho_face', 'morpho_cou',
                'morpho_thorax', 'morpho_coeur', 'morpho_pole_cepha',
                'morpho_abdo', 'morpho_digest', 'morpho_urine', 'morpho_rachis',
                'morpho_membres', 'morpho_oge', 'morpho_liquide_amnio',
                'morpho_trophoblaste_localisation', 'morpho_trophoblaste_aspect',
                'morpho_decol', 'morpho_placenta', 'morpho_cordon',
                'doppler_cordon_diastole', 'doppler_dv_onde'
            ))
        context['foetus_db_list'] = foetus_list

        pelvienne = None
        try:
            pelvienne = consultation.consultationechopelvienne
        except Exception:
            pass
        context['consultation_pelvienne'] = pelvienne

        data, source = _get_measurements(consultation)
        context['sr'] = data
        context['sr_source'] = source
        try:
            context['examen'] = _get_examen_resume(consultation)
        except Exception as e:
            logger.warning(f"_get_examen_resume failed for consultation {consultation.id}: {e}")
            context['examen'] = None
        return context


class MesuresEditView(PermissionRequiredMixin, View):
    """
    GET  /consultation/<pk>/mesures/  — edit form pre-filled with DICOM/manual data
    POST /consultation/<pk>/mesures/  — save manual overrides
    """
    permission_required = "core.view_patient"

    def get(self, request, pk):
        consultation = get_object_or_404(Consultation, pk=pk)
        data, source = _get_measurements(consultation)
        return render(request, "core/mesures_consultation.html", {
            'consultation': consultation,
            'patient': consultation.patient,
            'mesures_json': json.dumps(data or {}),
            'sr_source': source,
        })

    def post(self, request, pk):
        consultation = get_object_or_404(Consultation, pk=pk)
        raw = request.POST.get('mesures_data', '{}')
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            parsed = {}

        obj, _ = MesuresConsultation.objects.get_or_create(consultation=consultation)
        obj.data = json.dumps(parsed)
        obj.updated_by = request.user
        obj.save()

        return JsonResponse({'status': 'ok', 'redirect': f'/consultation/{pk}/rapport'})
