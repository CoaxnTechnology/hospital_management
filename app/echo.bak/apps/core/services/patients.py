# Données de grossesse pour reporting et edition
import math
import re
from html import escape

from django.template.loader import render_to_string

from apps.core.models import ConsultationEcho11SA, ResultatAnalyseBiologique, ConsultationEchoPremierTrimestre, \
    ConsultationEchoDeuxiemeTrimestre, ConsultationEchoTroisiemeTrimestre


def get_last_value_analyse(patient, code):
    res = ResultatAnalyseBiologique.objects.filter(analyse__code=code, prescription__patient=patient) \
        .order_by('-prescription__date_resultat')
    if len(res) > 0:
        res = res[0].valeur.replace('\n', '\\n').replace('\r', '\\r') if res[0].valeur is not None else ''
        return res
    return ''


def get_grossesse_data(patient):
    data = {
        'atcd': '',
        'ddr': '',
        'poids_avant_gross': '',
        'var_poids_gross': '',
        'terme': '',
        'date_accouchement': '',
        'test_t21_fait': '',
        'fiv': '',
        'date_echo_t1': '',
        'resultat_exam_morpho': '',
        'date_prev_echo_morpho': '',
        'resultat_echo_t3': '',
        'risque_t21': '',
        'diabete': 'Non',
        'caryotype_val': '',
        'tabac': '',
        'tv': '',
        'ta': '',
        'alb': '',
        'gly': '',
        'temperature': '',
        'lcc': '',
        'cn': '',
        'opn': '',
        'opn_presence': '',
        'gs': '',
        'nfs': '',
        'hb': '',
        'pq': '',
        'ag': '',
        'tpha': '',
        'toxo': '',
        'rub': '',
        'rai': '',
        'tsh': '',
        'creat': '',
        'gp75': '',
        'ecbu': '',
        'bw': '',
        'hvc': '',
        'hiv': '',
        'pv': '',
        'dpni': '',
        'tp': '',
        'fib': '',
        'uree': '',
        'ionos': '',
        'acideu': '',
        'asat': '',
        'cpk': '',
        'btc': '',
        'prot': '',
        'ca125': '',
        'ca19': '',
        'ft4': '',
        'bhcg': '',
        'fsh': '',
        'lh': '',
        'prl': '',
        'amh': '',
        'oestr': '',
        'proges': '',
        'amyl': '',
        'lip': '',
        'he4': '',
    }
    atcd = re.sub(r"\s+", " ", render_to_string("core/partials/antecedents_lettre.html", {'patient': patient}))
    data['atcd'] = atcd.replace('\"','\\"')
    if patient.grossesse_encours is None:
        return data
    g = patient.grossesse_encours
    if g.get_ddr():
        data['ddr'] = g.get_ddr().strftime("%d/%m/%Y")
    diff_poids = 0
    if g.poids_avant_grossesse:
        data['poids_avant_gross'] = g.poids_avant_grossesse
        if patient.poids:
            diff_poids = patient.poids - g.poids_avant_grossesse

    data['var_poids_gross'] = "{}{:.1f} Kg".format('+' if diff_poids > 0 else '-', diff_poids) if diff_poids != 0 else ''
    data['terme'] = g.terme_disp
    data['date_accouchement'] = g.date_accouch_disp
    data['test_t21_fait'] = g.test_t21_fait
    data['risque_t21'] = "1/{:.0f}".format(g.risque) if g.risque else ""
    data['dpni'] = g.dpni if g.dpni else ""
    data['diabete'] = g.diabete_v2.valeur if g.diabete_v2 else "Non"
    data['caryotype_val'] = g.caryotype_val if g.caryotype_val else ""
    data['tabac'] = patient.fumeur if patient.fumeur else "Non"
    if g.conception_v2:
        data['fiv'] = 'Oui' if g.conception_v2.valeur == 'FIV' else 'Non'
    data['date_prev_echo_morpho'] = g.date_echo_morpho()

    exams = g.consultationobstetrique_set.all().order_by('-id')
    if len(exams) > 0:
        dernier_exam = exams[0]
        data['tv'] = dernier_exam.tv if dernier_exam.tv else ""
        data['ta'] = dernier_exam.ta if dernier_exam.ta else ""
        #print('TA/TV', data['ta'], data['tv'])
        data['alb'] = dernier_exam.alb if dernier_exam.alb else ""
        data['gly'] = dernier_exam.gly if dernier_exam.gly else ""
        data['temperature'] = dernier_exam.temperature if dernier_exam.temperature else ""
        if isinstance(dernier_exam, ConsultationEcho11SA):
            data['lcc'] = dernier_exam.lcc if dernier_exam.lcc else ""
        else:
            fs = dernier_exam.donneesfoetus_set.all()
            for f in fs:
                """
                if data['lcc'] == '':
                    data['lcc'] = f.lcc if f.lcc else ""
                elif f.lcc and f.lcc != "":
                    data['lcc'] = "{}/{}".format(data['lcc'], (f.lcc if f.lcc else "")).replace('.', ',')
                if data['cn'] == '':
                    data['cn'] = f.cn if f.cn else ""
                else:
                    data['cn'] = "{}/{}".format(data['cn'], (f.cn if f.cn else "")).replace('.', ',')
                """
                opn = ""
                if f.opn_presence:
                    opn = f.get_opn_presence_display()
                if f.opn:
                    opn = f"{f.opn}".replace('.', ',')
                if opn != '':
                    if data['opn'] == '':
                        data['opn'] = opn
                    else:
                        data['opn'] = f"{data['opn']}/{opn}".replace('.', ',')

        exam_t1 = ConsultationEchoPremierTrimestre.objects.filter(grossesse=g).order_by('-date')
        if len(exam_t1) > 0:
            dernier_exam_t1 = exam_t1[0]
            data['date_echo_t1'] = dernier_exam_t1.date.strftime("%d/%m/%Y")
            fs = dernier_exam_t1.donneesfoetus_set.all()
            print('=====================================')
            for f in fs:
                print('Foetus')
                if data['lcc'] == '':
                    data['lcc'] = f.lcc if f.lcc else ""
                elif f.lcc and f.lcc != "":
                    data['lcc'] = "{}/{}".format(data['lcc'], (f.lcc if f.lcc else "")).replace('.', ',')
                if data['cn'] == '':
                    data['cn'] = f.cn if f.cn else ""
                elif f.cn and f.cn != "":
                    data['cn'] = "{}/{}".format(data['cn'], (f.cn if f.cn else "")).replace('.', ',')
            print('=====================================')

        exam_t2 = ConsultationEchoDeuxiemeTrimestre.objects.filter(grossesse=g).order_by('-date')
        if len(exam_t2) > 0:
            data['resultat_exam_morpho'] = exam_t2[0].echo_morpho

        exam_t3 = ConsultationEchoTroisiemeTrimestre.objects.filter(grossesse=g).order_by('-date')
        if len(exam_t3) > 0:
            data['resultat_echo_t3'] = exam_t3[0].echo_t3

    # Biologie
    data['gs'] = get_last_value_analyse(patient, 'Groupe sanguin Rhésus')
    data['nfs'] = get_last_value_analyse(patient, 'NFS')
    data['rai'] = get_last_value_analyse(patient, 'RAI')
    data['tsh'] = get_last_value_analyse(patient, 'TSH')
    data['creat'] = get_last_value_analyse(patient, 'Créat')
    data['gp75'] = get_last_value_analyse(patient, 'GP75')
    data['ecbu'] = get_last_value_analyse(patient, 'ECBU')
    data['toxo'] = get_last_value_analyse(patient, 'Toxoplasmose')
    data['rub'] = get_last_value_analyse(patient, 'Rubéole')
    data['ag'] = get_last_value_analyse(patient, 'AgHbs')
    data['bw'] = get_last_value_analyse(patient, 'BW')
    data['tpha'] = get_last_value_analyse(patient, 'TPHA-VDRL')
    data['hvc'] = get_last_value_analyse(patient, 'HVC')
    data['hiv'] = get_last_value_analyse(patient, 'HIV')
    data['pv'] = get_last_value_analyse(patient, 'PV')
    data['gly'] = get_last_value_analyse(patient, 'Glycémie à Jeun')
    data['tp'] = get_last_value_analyse(patient, 'TP')
    data['fib'] = get_last_value_analyse(patient, 'Fibrinémie')
    data['uree'] = get_last_value_analyse(patient, 'Urée')
    data['ionos'] = get_last_value_analyse(patient, 'Ionogramme sanguin')
    data['acideu'] = get_last_value_analyse(patient, 'Acide Urique')
    data['asat'] = get_last_value_analyse(patient, 'ASAT/ALAT')
    data['cpk'] = get_last_value_analyse(patient, 'CPK/LDH')
    data['btc'] = get_last_value_analyse(patient, 'BT/C')
    data['prot'] = get_last_value_analyse(patient, 'Protéinurie de 24h')
    data['ca125'] = get_last_value_analyse(patient, 'CA125')
    data['ca19'] = get_last_value_analyse(patient, 'CA19-9')
    data['ft4'] = get_last_value_analyse(patient, 'FT4')
    data['bhcg'] = get_last_value_analyse(patient, 'bHCG')
    data['fsh'] = get_last_value_analyse(patient, 'FSH')
    data['lh'] = get_last_value_analyse(patient, 'LH')
    data['prl'] = get_last_value_analyse(patient, 'PRL')
    data['amh'] = get_last_value_analyse(patient, 'AMH')
    data['oestr'] = get_last_value_analyse(patient, 'Oestradiolémie')
    data['proges'] = get_last_value_analyse(patient, 'Progestéronémie')
    data['amyl'] = get_last_value_analyse(patient, 'Amylase')
    data['lip'] = get_last_value_analyse(patient, 'Lipase')
    data['he4'] = get_last_value_analyse(patient, 'HE4')

    return data



"""
    Retourne les valeurs historiques d'une mesure liée à la grossesse pour tous les foetus
    Resultat = {'Foetus 1' : {'bip': [[12, 43.5], [13, 49.5]]}, 
                'Foetus 2': {'bip': [[12, 43.5], [13, 49.5]]}
                }
"""
def get_obs_measure_history(attr, grossesse):
    result = {}
    for c in grossesse.consultationobstetrique_set.all().order_by('id'):
        fs = c.donneesfoetus_set.all()
        for idx, foetus_data in enumerate(fs):
            f_idx = 'Foetus ' + str(idx+1)
            if f_idx not in result:
                result[f_idx] = {}

            if attr not in result[f_idx]:
                result[f_idx][attr] = []

            val = getattr(foetus_data, attr)
            if val:
                result[f_idx][attr].append([
                    c.terme_sa(),
                    val])

    return result


def get_all_obs_measure_history(grossesse):
    result = {}
    attrs = ["poids", "lcc", "dat", "cn", "fc", "bip", "pc", "pa", "femur", ]
    for a in attrs:
        res = get_obs_measure_history(a, grossesse)
        for key, value in res.items():
            if key in result:
                result[key] = {**result[key], **value}
            else:
                result[key] = value
    print('>>>>>>>>> resultat', result)
    return result