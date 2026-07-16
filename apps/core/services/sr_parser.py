import traceback
import logging as _logging

import pydicom
from apps.core.services.utils import *

_logger = _logging.getLogger('dicom.storage')


def _val(el, tag):
    return el[tag].value


code_val_tag = 0x00080100
code_val_meaning = 0x00080104
c_name_code_seq = 0x0040A043
c_code_seq = 0x0040A168
c_content_sequence = 0x0040A730

codes_concept_label = {
    '11781-2': 'date_accouchement',
    '11955-2': 'ddr',
    '11865-3': 'uterus_largeur',
    '11842-2': 'uterus_longueur',
    '11859-6': 'uterus_hauteur',
    '33192-6': 'uterus_volume',
    '12145-9': 'endometre_epaisseur',
    '11961-0': 'col_longueur',  # cervix length
    '99005-02': 'col_hauteur',  # cervix height
    '99005-03': 'col_largeur',  # cervix width
    '99005-04': 'col_volume',  # cervix volume
    '11829-9': 'ovaire_gauche_largeur',
    '11840-6': 'ovaire_gauche_longueur',
    '11857-0': 'ovaire_gauche_hauteur',
    '12164-0': 'ovaire_gauche_volume',
    '11830-7': 'ovaire_droit_largeur',
    '11841-4': 'ovaire_droit_longueur',
    '11858-8': 'ovaire_droit_hauteur',
    '12165-7': 'ovaire_droit_volume',
    '11726-7': 'peak_systolic_velocity',
    '11665-7': 'minimum_systolic_velocity',
    '11653-3': 'doppler_diastole', # Champ liste dans l'interface mais ce champ existe dans le doppler foetus et doppler maternel
    '20352-1': 'mean_systolic_velocity',
    '20247-3': 'peak_gradient',
    '20256-4': 'mean_gradient',
    '12023-8': 'doppler_cordon_ir',
    '12008-9': 'doppler_cordon_ip',
    '11654-1': 'time_averaged_maximum_velocity',  # TAmax
    '20217-8': 'acceleration_time',  # AccT
    '20218-6': 'acceleration_index',  # Acc
    '20219-4': 'deceleration_time',  # DecT
    '12022-0': 's_d_ratio',  # ED/PS S/D ratio
    '11850-5': 'sac_gestationnel_diametre',
    '18185-9': 'age_gestationnel',
    '8867-4': 'fc',
    '11957-8': 'lcc',
    '11979-2': 'pa',  # Abdominal circumference (pa)
    '11820-8': 'bip',  # Biparetal diameter (bip)
    '11963-6': 'femur',  # Femur length (bip)
    '99000-11': 'femur',  # Femur length (Samsung MEDISON vendor code)
    '11965-1': 'pied',  # Foot length
    '11984-2': 'pc',  # Head circumference (pa)
    '11851-3': 'dof',  # Occipitial-frontal diameter (DOF)
    '11862-0': 'dat',  # Transverse abdominal diameter (DAT)
    '11988-3': 'ct',  # Thoracic circumference (CT)
    '99001-04': 'oreille',  # Ear length (DAT)
    '99001-05': 'phalanx',  # Middle phalanx (DAT)
    '99005-14': 'bassinet_gauche',  # Left pelvis
    '99005-13': 'bassinet_droit',  # Right pelvis
    '11818-2': 'Anterior-Posterior Abdominal Diameter', # Anterior-Posterior Abdominal Diameter
    '11819-0': 'Anterior-Posterior Trunk Diameter',  # Anterior-Posterior Trunk Diameter
    '11824-0': 'BPD area corrected', # BPD area corrected
    '11860-4': 'cervelet_2', # Cisterna Magna
    #'11863-8': 'Trans Cerebellar Diameter',  # Trans Cerebellar Diameter
    '11863-8': 'cervelet',  # Trans Cerebellar Diameter
    '11864-6': 'Transverse Thoracic Diameter',  # Transverse Thoracic Diameter
    '11853-9': 'Left Kidney thickness',
    '11834-9': 'rein_gauche', # Left Kidney length
    '11825-7': 'Left Kidney width',
    '11855-4': 'Right Kidney thickness',
    '11836-4': 'rein_droite', # Right Kidney length
    '11827-3': 'Right Kidney width',
    '33191-8': 'APAD * TAD',
    '11966-9': 'humerus',  # Humerus length
    '11967-7': 'radius',  # Radius length
    '11969-3': 'cubitus',  # Ulna length
    '11968-5': 'tibia',  # Tibia length
    '11964-4': 'perone',  # Fibula length
    '11962-8': 'clavicule',  # Clavicle length

    '12171-5': 'Lateral Ventrical width',  # Lateral Ventrical width
    #'12146-7': 'Nuchal Fold thickness',  # Nuchal Fold thickness
    '12146-7': 'epn',  # Nuchal Fold thickness
    '33070-4': 'dio',  # Inner Orbital Diameter
    '11629-3': 'do',  # Outer Orbital Diameter
    '33069-6': 'cn',  # Nuchal Translucency
    '33197-5': 'Anterior Horn Lateral ventricular width',  # Anterior Horn Lateral ventricular width
    '33196-7': 'Posterior Horn Lateral ventricular width',  # Posterior Horn Lateral ventricular width
    '12170-7': 'Width of Hemisphere',  # Width of Hemisphere

    '99508-0': 'opn', # Nasal bone length
    'T-11149': 'opn',  # Nasal bone length

}

allowed_codes = codes_concept_label.keys()


def parse_pelvis_uterus(seq, result):
    for it in seq:
        cd = it[c_name_code_seq][0][code_val_tag].value

        if cd == 'T-83000':
            # Uterus section
            if 0x0040A730 in it:
                c_seq = it[0x0040A730]
                for seq_item in c_seq:
                    sub_seq = seq_item[c_name_code_seq][0]
                    # print(sub_seq[code_val_tag])
                    for cd in allowed_codes:
                        if sub_seq[code_val_tag].value == cd:
                            measured_val_seq = seq_item[0x0040A300]
                            units_seq = measured_val_seq[0][0x004008EA]
                            unit = units_seq[0][code_val_tag].value
                            value = measured_val_seq[0][0x0040A30A].value
                            result[codes_concept_label[cd]] = value

        if cd in ['12145-9', '11961-0', '99005-02', '99005-03', '99005-04']:
            if 0x0040A300 in it:
                c_seq = it[0x0040A300]
                for seq_item in c_seq:
                    #print(seq_item)
                    units_seq = seq_item[0x004008EA]
                    unit = units_seq[0][code_val_tag].value
                    #print('Unit', unit)
                    value = seq_item[0x0040A30A].value
                    #print('Value', value)
                    result[codes_concept_label[cd]] = value


def parse_ovary(seq, result):
    for it in seq:
        cd = it[c_name_code_seq][0][code_val_tag].value

        if cd in ['11829-9', '11840-6', '11857-0', '12164-0', '11830-7', '11841-4', '11858-8', '12165-7']:
            c_seq = it[0x0040A300]
            for seq_item in c_seq:
                #print(seq_item)
                units_seq = seq_item[0x004008EA]
                unit = units_seq[0][code_val_tag].value
                #print('Unit', unit)
                value = seq_item[0x0040A30A].value
                #print('Value', value)
                result[codes_concept_label[cd]] = value


def parse_umbilical_artery(seq, result):
    _logger.info('parse_umbilical_artery ===================')
    for it in seq:
        cd = it[c_name_code_seq][0][code_val_tag].value
        _logger.info(cd)

        foetus = None
        # print(_c)
        if cd == '11951-1':
            # Foetus ID
            id = it[0x0040A160].value
            _logger.info('Foetus ID', id)
            foetus = get_foetus(id, result)
            foetus['arteres'] = {}
            _logger.info(foetus)
        try:
            c_seq = it[0x0040A300]
            for seq_item in c_seq:
                units_seq = seq_item[0x004008EA]
                unit = units_seq[0][code_val_tag].value
                _logger.info('Unit', unit)
                value = seq_item[0x0040A30A].value
                if foetus is not None and cd in codes_concept_label:
                    cpt = codes_concept_label[cd]
                    foetus['arteres'][cpt] = value
        except Exception as e:
            _logger.info(f'parse_umbilical_artery error: {e}')
    _logger.info('===========================================')


def parse_follicule(seq, result):
    for it in seq:
        cd = it[c_name_code_seq][0][code_val_tag].value
        _logger.info(cd)
        _logger.info('************************')

        if cd in ['11829-9', '11840-6', '11857-0', '12164-0', '11830-7', '11841-4', '11858-8', '12165-7']:
            c_seq = it[0x0040A300]
            for seq_item in c_seq:
                #print(seq_item)
                units_seq = seq_item[0x004008EA]
                unit = units_seq[0][code_val_tag].value
                #print('Unit', unit)
                value = seq_item[0x0040A30A].value
                #print('Value', value)
                result[codes_concept_label[cd]] = value


def parse_doppler_samsung(dataset, result):

    if "ConceptNameCodeSequence" in dataset:
        cncs = dataset.ConceptNameCodeSequence[0].CodeValue
        if cncs == "121070":
            # Findings
            if "ContentSequence" in dataset:
                cs = dataset.ContentSequence
                for innerds in cs:
                    if "ConceptNameCodeSequence" in innerds:
                        innercncs = innerds.ConceptNameCodeSequence[0].CodeValue
                        #############################################################################
                        if innercncs == "T-46820":
                            _logger.info('<<<<< Uterine Artery >>>>>>')
                            doppler_uterin = {}
                            if 'doppler_uterin' in result:
                                doppler_uterin = result['doppler_uterin']

                            if "ContentSequence" in innerds:
                                for _ds in innerds.ContentSequence:
                                    if "ConceptNameCodeSequence" in _ds:
                                        _cv = _ds.ConceptNameCodeSequence[0].CodeValue
                                        if _cv == "G-C171":
                                            # Laterality
                                            if "ConceptCodeSequence" in _ds:
                                                if _ds.ConceptCodeSequence[0].CodeValue == "G-A100":
                                                    laterality = "droit"
                                                else:
                                                    laterality = "gauche"
                                                _logger.info("Laterality", laterality)
                                        else:
                                            # print(_cv)
                                            if "ConceptNameCodeSequence" in _ds:
                                                _ccs = _ds.ConceptNameCodeSequence[0]
                                                if "MeasuredValueSequence" in _ds:
                                                    for valitem in _ds.MeasuredValueSequence:
                                                        val = valitem.NumericValue
                                                        _logger.info(f"{_ccs.CodeValue} ({_ccs.CodeMeaning}) = {val}")
                                                        key = _ccs.CodeMeaning.lower().replace(' ', '_').replace('-', '_')
                                                        doppler_uterin[key + '_' + laterality] = val
                                                        # Also store with standard names
                                                        if _ccs.CodeValue == '12023-8':
                                                            doppler_uterin['ir_' + laterality] = val
                                                        if _ccs.CodeValue == '12008-9':
                                                            doppler_uterin['ip_' + laterality] = val

                            _logger.info('Doppler utérin', doppler_uterin)
                            result['doppler_uterin'] = doppler_uterin

                            #############################################################################

                        if innercncs == "T-F1810":
                            _logger.info('<<<<< Umbilical Artery >>>>>>')
                            doppler_ombilical = {}
                            foetusId = None
                            if "ContentSequence" in innerds:
                                for _ds in innerds.ContentSequence:
                                    if "ConceptNameCodeSequence" in _ds:
                                        _cv = _ds.ConceptNameCodeSequence[0].CodeValue
                                        if _cv == "11951-1":
                                            foetusId = _ds.TextValue
                                            _logger.info("Foetus ID", foetusId)
                                        else:
                                            if not foetusId:
                                                _logger.info("No foetus ID")
                                                continue
                                            f = get_foetus(foetusId, result)
                                            if "ConceptNameCodeSequence" in _ds:
                                                _ccs = _ds.ConceptNameCodeSequence[0]
                                                if "MeasuredValueSequence" in _ds:
                                                    for valitem in _ds.MeasuredValueSequence:
                                                        val = valitem.NumericValue
                                                        _logger.info(f"{_ccs.CodeValue} ({_ccs.CodeMeaning}) = {val}")
                                                        key = _ccs.CodeMeaning.lower().replace(' ', '_').replace('-', '_')
                                                        doppler_ombilical[key] = val
                                                        if _ccs.CodeValue == '12023-8':
                                                            doppler_ombilical['doppler_cordon_ir'] = val
                                                        if _ccs.CodeValue == '12008-9':
                                                            doppler_ombilical['doppler_cordon_ip'] = val
                                            if f:
                                                if 'doppler_ombilical' in f:
                                                    f['doppler_ombilical'] = {**f['doppler_ombilical'], **doppler_ombilical}
                                                else:
                                                    f['doppler_ombilical'] = doppler_ombilical
                            _logger.info('Doppler ombilical', doppler_ombilical)

                            #############################################################################


def get_foetus(id, result):
    if 'foetus' not in result:
        result['foetus'] = []

    for f in result['foetus']:
        if f['id'] == id:
            return f
    foetus = {'id': id}
    result['foetus'].append(foetus)
    return foetus


def print_attrib(code, sub):
    count = 0
    for i in sub[c_name_code_seq]:
        _logger.info(i[code_val_tag].value)
    _logger.info(count)
    param = sub[c_name_code_seq][0][code_val_tag].value
    meaning = sub[c_name_code_seq][0][code_val_meaning].value
    seq = safe_get(sub, 0x0040A300)
    if seq:
        val = seq[0][0x0040A30A].value
        #print(f'Code {code} - Param {param} ({meaning}) = {val}')


def parse_ds(ds):
    result = {}
    concept_name_code_sequence = safe_get(ds, c_name_code_seq)
    report_type = None
    if concept_name_code_sequence:
        report_type = _val(concept_name_code_sequence[0], 0x00080104)
        _logger.info('Report type ', report_type)
    content_sequence = safe_get(ds, 0x0040A730)

    if content_sequence:
        for seq in content_sequence:
            c_name_seq = seq.get(c_name_code_seq)
            if c_name_seq is None:
                continue

            parse_doppler_samsung(seq, result)

            for item in seq:
                try:
                    if item.VR != 'SQ':
                        continue

                    if (0x0008, 0x0100) not in item[0]:
                        continue

                    code = item[0][code_val_tag].value

                    if code == '121111':
                        if 0x0040A730 in seq:
                            _logger.info('Summary section')
                            c_seq = seq[0x0040A730]
                            for it in c_seq:
                                if c_name_code_seq not in it:
                                    continue
                                cd = it[c_name_code_seq][0][code_val_tag].value
                                if cd in ['11781-2', '11779-6']:
                                    result[codes_concept_label['11781-2']] = it[0x0040A121].value
                                if cd == '11955-2':
                                    result[codes_concept_label['11955-2']] = it[0x0040A121].value
                                if cd == '11878-6':
                                    if 0x0040A300 in it:
                                        result['nombre_foetus'] = it[0x0040A300][0][0x0040A30A].value
                                if cd == '125008':
                                    if 0x0040A730 in it:
                                        content = it[0x0040A730]
                                        foetus = {}
                                        for c in content:
                                            _c = c.get(c_name_code_seq)
                                            if _c is None:
                                                continue
                                            _c = _c[0]
                                            v = safe_get(_c, code_val_tag)
                                            if v:
                                                if v == '11951-1':
                                                    foetus['id'] = c[0x0040A160].value
                                                if v == '11888-5':
                                                    foetus['age_gest'] = c.get(0x0040A300, [None])[0].get(0x0040A30A, None) if c.get(0x0040A300) else None
                                                if v == '11727-5':
                                                    foetus['poids'] = c.get(0x0040A300, [None])[0].get(0x0040A30A, None) if c.get(0x0040A300) else None
                                                if v == '11884-4':
                                                    foetus['age_gest_ultrasound'] = c.get(0x0040A300, [None])[0].get(0x0040A30A, None) if c.get(0x0040A300) else None
                                                if v == '11885-1':
                                                    foetus['age_gest_lmp'] = c.get(0x0040A300, [None])[0].get(0x0040A30A, None) if c.get(0x0040A300) else None
                                                if v == '11781-2':
                                                    foetus['date_accouchement'] = c[0x0040A121].value
                                        if 'foetus' not in result:
                                            result['foetus'] = []
                                        result['foetus'].append(foetus)

                    if code == '125008':
                        if 0x0040A730 in seq:
                            content = seq[0x0040A730]
                            foetus = {}
                            for c in content:
                                _c = c.get(c_name_code_seq)
                                if _c is None:
                                    continue
                                _c = _c[0]
                                v = safe_get(_c, code_val_tag)
                                if v:
                                    try:
                                        if v == '11951-1':
                                            foetus['id'] = c[0x0040A160].value
                                        if v == '11888-5':
                                            mvs = c.get(0x0040A300)
                                            if mvs:
                                                foetus['age_gest'] = mvs[0].get(0x0040A30A, None) if hasattr(mvs[0], 'get') else mvs[0][0x0040A30A].value
                                        if v == '11727-5':
                                            mvs = c.get(0x0040A300)
                                            if mvs:
                                                foetus['poids'] = mvs[0].get(0x0040A30A, None) if hasattr(mvs[0], 'get') else mvs[0][0x0040A30A].value
                                        if v == '11884-4':
                                            mvs = c.get(0x0040A300)
                                            if mvs:
                                                foetus['age_gest_ultrasound'] = mvs[0].get(0x0040A30A, None) if hasattr(mvs[0], 'get') else mvs[0][0x0040A30A].value
                                        if v == '11885-1':
                                            mvs = c.get(0x0040A300)
                                            if mvs:
                                                foetus['age_gest_lmp'] = mvs[0].get(0x0040A30A, None) if hasattr(mvs[0], 'get') else mvs[0][0x0040A30A].value
                                        if v == '11781-2':
                                            foetus['date_accouchement'] = c[0x0040A121].value
                                        if v == '11948-7':
                                            foetus['fc'] = c[0x0040A121].value
                                    except:
                                        _logger.info("Error reading foetus summary data")
                            if 'foetus' not in result:
                                result['foetus'] = []
                            result['foetus'].append(foetus)

                    if code == '125001':
                        if 0x0040A730 in seq:
                            c_seq = safe_get(seq, 0x0040A730)
                            if not c_seq:
                                continue
                            id = None
                            ratios = {}
                            for it in c_seq:
                                _c = safe_get(it, c_name_code_seq)
                                if _c is None:
                                    continue
                                _c = _c[0]
                                _cv = safe_get(_c, code_val_tag)
                                if _cv == '11951-1':
                                    id = it[0x0040A160].value
                                mvs = safe_get(it, 0x0040A300)
                                if mvs and len(mvs) > 0:
                                    mv = mvs[0].get(0x0040A30A, None) if hasattr(mvs[0], 'get') else mvs[0][0x0040A30A].value
                                    if _cv == '11947-9':
                                        ratios['hc_ac'] = mv
                                    if _cv == '11871-1':
                                        ratios['fl_ac'] = mv
                                    if _cv == '11872-9':
                                        ratios['fl_bpd'] = mv
                                    if _cv == '11823-2':
                                        ratios['cephalic_index'] = mv
                                    if _cv == '11873-7':
                                        ratios['fl_hc'] = mv
                                    if _cv == '99000-01':
                                        ratios['fl_foot'] = mv
                            f = get_foetus(id, result)
                            if f:
                                f['ratios'] = ratios

                    if code == '99001':
                        _logger.info("Doppler section 99001 (uterine) found in SR")
                        if 0x0040A730 in seq:
                            c_seq = safe_get(seq, 0x0040A730)
                            if not c_seq:
                                _logger.info("Doppler 99001: empty content sequence, no data")
                                continue
                            dop = {}
                            for it in c_seq:
                                _c = safe_get(it, c_name_code_seq)
                                if _c is None:
                                    continue
                                _c = _c[0]
                                _cv = safe_get(_c, code_val_tag)
                                if (0x0040, 0xA168) in it:
                                    cd = safe_get(it[0x0040A168][0], code_val_tag)
                                    _logger.info(cd)
                                if _cv == '99100':
                                    cs99001 = safe_get(it, 0x0040A730)
                                    if cs99001:
                                        for el in cs99001:
                                            lat = None
                                            cs99001el = safe_get(el, 0x0040A730)
                                            if cs99001el:
                                                for item in cs99001el:
                                                    v = None
                                                    item_cncs = safe_get(item, c_name_code_seq)
                                                    if item_cncs:
                                                        v = safe_get(item_cncs[0], code_val_tag)
                                                    if v == "G-C0E3":
                                                        try:
                                                            inner = safe_get(item, 0x0040A730)
                                                            if inner and len(inner) > 0:
                                                                inner2 = safe_get(inner[0], c_name_code_seq)
                                                                if inner2 and len(inner2) > 0:
                                                                    if 'G-C171' == safe_get(inner2[0], code_val_tag):
                                                                        inner3 = safe_get(inner[0], 0x0040A168)
                                                                        if inner3 and len(inner3) > 0:
                                                                            lat = safe_get(inner3[0], code_val_tag)
                                                                            if lat == 'G-A101':
                                                                                lat = 'gauche'
                                                                            if lat == 'G-A100':
                                                                                lat = 'droit'
                                                        except Exception as e:
                                                            _logger.info(f"Uterus laterality can't be evaluated: {e}")
                                            if lat:
                                                param = safe_get(el, c_name_code_seq)
                                                if param:
                                                    param = param[0]
                                                    pv = safe_get(param, code_val_tag)
                                                    mvs = safe_get(el, 0x0040A300)
                                                    if mvs and len(mvs) > 0:
                                                        mv = mvs[0].get(0x0040A30A, None) if hasattr(mvs[0], 'get') else mvs[0][0x0040A30A].value
                                                        if pv in allowed_codes:
                                                            dop[codes_concept_label[pv] + '_' + lat] = mv
                                                        else:
                                                            meaning = safe_get(param, code_val_meaning)
                                                            if meaning:
                                                                key = meaning.lower().replace(' ', '_').replace('-', '_') + '_' + lat
                                                                dop[key] = mv
                                                        if pv == '12023-8':
                                                            dop['ir_' + lat] = mv
                                                        if pv == '12008-9':
                                                            dop['ip_' + lat] = mv
                            if dop:
                                _logger.info("Doppler 99001: extracted uterine doppler %s", dop)
                            else:
                                _logger.info("Doppler 99001: no uterine doppler values found")
                            result['doppler_uterin'] = dop

                    if code == '99000':
                        _logger.info("Doppler section 99000 (fetal) found in SR")
                        if 0x0040A730 in seq:
                            c_seq = safe_get(seq, 0x0040A730)
                            if not c_seq:
                                _logger.info("Doppler 99000: empty content sequence, no data")
                                continue
                            dop = {}
                            id = None
                            for it in c_seq:
                                _c = safe_get(it, c_name_code_seq)
                                if _c is None:
                                    continue
                                _cv = safe_get(_c[0], code_val_tag)
                                if _cv == '11951-1':
                                    id = it[0x0040A160].value
                                    _logger.info('Foetus', id)
                                if _cv == '99100':
                                    cs99000 = safe_get(it, 0x0040A730)
                                    if cs99000:
                                        for el in cs99000:
                                            cs = safe_get(el, c_content_sequence)
                                            if not cs or len(cs) == 0:
                                                continue
                                            ccs = safe_get(cs[0], c_code_seq)
                                            if not ccs or len(ccs) == 0:
                                                continue
                                            site = safe_get(ccs[0], code_val_tag)
                                            _logger.info("Doppler 99000: site code %s for foetus %s", site, id)
                                            if site == "T-F1810":
                                                f = get_foetus(id, result)
                                                try:
                                                    param = safe_get(el, c_name_code_seq)
                                                    if param:
                                                        param = param[0]
                                                        pv = safe_get(param, code_val_tag)
                                                        mvs = safe_get(el, 0x0040A300)
                                                        if mvs and len(mvs) > 0:
                                                            param_val = mvs[0].get(0x0040A30A, None) if hasattr(mvs[0], 'get') else mvs[0][0x0040A30A].value
                                                            if pv in allowed_codes:
                                                                dop[codes_concept_label[pv]] = param_val
                                                                if pv == '12023-8':
                                                                    dop['doppler_cordon_ir'] = param_val
                                                                if pv == '12008-9':
                                                                    dop['doppler_cordon_ip'] = param_val
                                                                if pv == '11653-3':
                                                                    dop['doppler_cordon_diastole_num'] = param_val
                                                                if pv == '8867-4' and f:
                                                                    f['fc'] = param_val
                                                            else:
                                                                meaning = safe_get(param, code_val_meaning)
                                                                if meaning:
                                                                    key = meaning.lower().replace(' ', '_').replace('-', '_')
                                                                    dop[key] = param_val
                                                        if f:
                                                            if 'doppler_ombilical' in f:
                                                                f['doppler_ombilical'] = {**f['doppler_ombilical'], **dop}
                                                            else:
                                                                f['doppler_ombilical'] = dop
                                                        _logger.info("Doppler 99000: umbilical (T-F1810) result for foetus %s: %s", id, dop if dop else "no data")
                                                except Exception as e:
                                                    _logger.error("Doppler 99000: error parsing umbilical doppler for foetus %s: %s", id, e)

                                            if site == "T-45600":
                                                f = get_foetus(id, result)
                                                try:
                                                    param = safe_get(el, c_name_code_seq)
                                                    if param:
                                                        param = param[0]
                                                        pv = safe_get(param, code_val_tag)
                                                        mvs = safe_get(el, 0x0040A300)
                                                        if mvs and len(mvs) > 0:
                                                            param_val = mvs[0].get(0x0040A30A, None) if hasattr(mvs[0], 'get') else mvs[0][0x0040A30A].value
                                                            if pv in allowed_codes:
                                                                dop[codes_concept_label[pv]] = param_val
                                                                if pv == '12023-8':
                                                                    dop['doppler_acm_ir'] = param_val
                                                                if pv == '12008-9':
                                                                    dop['doppler_acm_ip'] = param_val
                                                                if pv == '8867-4' and f:
                                                                    f['fc'] = param_val
                                                            else:
                                                                meaning = safe_get(param, code_val_meaning)
                                                                if meaning:
                                                                    key = meaning.lower().replace(' ', '_').replace('-', '_')
                                                                    dop[key] = param_val
                                                        if f:
                                                            if 'doppler_acm' in f:
                                                                f['doppler_acm'] = {**f['doppler_acm'], **dop}
                                                            else:
                                                                f['doppler_acm'] = dop
                                                        _logger.info("Doppler 99000: ACM (T-45600) result for foetus %s: %s", id, dop if dop else "no data")
                                                except Exception as e:
                                                    _logger.error("Doppler 99000: error parsing ACM doppler for foetus %s: %s", id, e)

                                            if site == "VP-0001":
                                                f = get_foetus(id, result)
                                                try:
                                                    param = safe_get(el, c_name_code_seq)
                                                    if param:
                                                        param = param[0]
                                                        pv = safe_get(param, code_val_tag)
                                                        mvs = safe_get(el, 0x0040A300)
                                                        if mvs and len(mvs) > 0:
                                                            param_val = mvs[0].get(0x0040A30A, None) if hasattr(mvs[0], 'get') else mvs[0][0x0040A30A].value
                                                            if pv in allowed_codes:
                                                                dop[codes_concept_label[pv]] = param_val
                                                                if pv == '12023-8':
                                                                    dop['doppler_dv_ir'] = param_val
                                                                if pv == '12008-9':
                                                                    dop['doppler_dv_ip'] = param_val
                                                                if pv == '8867-4' and f:
                                                                    f['fc'] = param_val
                                                            else:
                                                                meaning = safe_get(param, code_val_meaning)
                                                                if meaning:
                                                                    key = meaning.lower().replace(' ', '_').replace('-', '_')
                                                                    dop[key] = param_val
                                                        if f:
                                                            if 'doppler_dv' in f:
                                                                f['doppler_dv'] = {**f['doppler_dv'], **dop}
                                                            else:
                                                                f['doppler_dv'] = dop
                                                        _logger.info("Doppler 99000: DV (VP-0001) result for foetus %s: %s", id, dop if dop else "no data")
                                                except Exception as e:
                                                    _logger.error("Doppler 99000: error parsing DV doppler for foetus %s: %s", id, e)

                    if code == '125002' or code == '125009':
                        c_seq = safe_get(seq, 0x0040A730)
                        if c_seq:
                            bio = {}
                            id = None
                            for it in c_seq:
                                _c = safe_get(it, c_name_code_seq)
                                if _c is None:
                                    continue
                                _cv = safe_get(_c[0], code_val_tag)
                                if _cv == '11951-1':
                                    id = it[0x0040A160].value
                                if _cv == '125005':
                                    sub_seq = safe_get(it, 0x0040A730)
                                    if sub_seq:
                                        sub = sub_seq[0]
                                        param = safe_get(sub, c_name_code_seq)
                                        if param:
                                            param = param[0]
                                            pv = safe_get(param, code_val_tag)
                                            mvs = safe_get(sub, 0x0040A300)
                                            if mvs and len(mvs) > 0:
                                                mv = mvs[0].get(0x0040A30A, None) if hasattr(mvs[0], 'get') else mvs[0][0x0040A30A].value
                                                for v in allowed_codes:
                                                    if pv == v:
                                                        bio[codes_concept_label[v]] = mv
                            f = get_foetus(id, result)
                            if f:
                                if 'biometrie' in f:
                                    f['biometrie'] = {**f['biometrie'], **bio}
                                else:
                                    f['biometrie'] = bio

                    if code == '125003':
                        c_seq = safe_get(seq, 0x0040A730)
                        if c_seq:
                            bones = {}
                            id = None
                            for it in c_seq:
                                _c = safe_get(it, c_name_code_seq)
                                if _c is None:
                                    continue
                                _cv = safe_get(_c[0], code_val_tag)
                                if _cv == '11951-1':
                                    id = it[0x0040A160].value
                                if _cv == '125005':
                                    sub_seq = safe_get(it, 0x0040A730)
                                    if sub_seq:
                                        sub = sub_seq[0]
                                        param = safe_get(sub, c_name_code_seq)
                                        if param:
                                            param = param[0]
                                            pv = safe_get(param, code_val_tag)
                                            mvs = safe_get(sub, 0x0040A300)
                                            if mvs and len(mvs) > 0:
                                                mv = mvs[0].get(0x0040A30A, None) if hasattr(mvs[0], 'get') else mvs[0][0x0040A30A].value
                                                for v in allowed_codes:
                                                    if pv == v:
                                                        bones[codes_concept_label[v]] = mv
                            f = get_foetus(id, result)
                            if f:
                                f['os'] = bones

                    if code == '125004':
                        c_seq = safe_get(seq, 0x0040A730)
                        if c_seq:
                            cranium = {}
                            id = None
                            for it in c_seq:
                                _c = safe_get(it, c_name_code_seq)
                                if _c is None:
                                    continue
                                _cv = safe_get(_c[0], code_val_tag)
                                if _cv == '11951-1':
                                    id = it[0x0040A160].value
                                if _cv == '125005':
                                    sub_seq = safe_get(it, 0x0040A730)
                                    if sub_seq:
                                        sub = sub_seq[0]
                                        param = safe_get(sub, c_name_code_seq)
                                        if param:
                                            param = param[0]
                                            pv = safe_get(param, code_val_tag)
                                            mvs = safe_get(sub, 0x0040A300)
                                            if mvs and len(mvs) > 0:
                                                mv = mvs[0].get(0x0040A30A, None) if hasattr(mvs[0], 'get') else mvs[0][0x0040A30A].value
                                                for v in allowed_codes:
                                                    if pv == v:
                                                        cranium[codes_concept_label[v]] = mv
                            f = get_foetus(id, result)
                            if f:
                                f['crane'] = cranium

                    if code == '125011':
                        if 0x0040A730 in seq:
                            parse_pelvis_uterus(seq[0x0040A730], result)

                    if code == '121070' or code == '125070':
                        if 0x0040A730 in seq:
                            c_seq = seq[0x0040A730]
                            section = None
                            fol_num = -1
                            for it in c_seq:
                                _c = it.get(c_name_code_seq)
                                if _c is None:
                                    continue
                                cd = safe_get(_c[0], code_val_tag)
                                if cd == 'T-87000':
                                    _logger.info('Parse ovary')
                                    if 0x0040A730 in it:
                                        parse_ovary(it[0x0040A730], result)
                                        continue
                                if cd == 'T-F1810':
                                    continue
                                if cd == '125007':
                                    fol_num += 1
                                    parse_follicule(it, result)
                                    if section in ['follicule_left', 'follicule_right']:
                                        loc = 'gauche' if section == 'follicule_left' else 'droit'
                                        cncs = it.get(c_name_code_seq)
                                        if cncs and safe_get(cncs[0], code_val_tag) == '125007':
                                            if 0x0040A730 in it:
                                                c_seq2 = it[0x0040A730]
                                                for seq_item in c_seq2:
                                                    sub_seq = seq_item.get(c_name_code_seq)
                                                    if sub_seq is None:
                                                        continue
                                                    sub_cd = safe_get(sub_seq[0], code_val_tag)
                                                    mvs = seq_item.get(0x0040A300)
                                                    if mvs is None:
                                                        continue
                                                    us = mvs[0].get(0x004008EA)
                                                    unit = us[0][code_val_tag].value if us else None
                                                    mv = mvs[0].get(0x0040A30A, None) if hasattr(mvs[0], 'get') else mvs[0][0x0040A30A].value
                                                    if sub_cd == 'G-D705':
                                                        k = f'ovaire_{loc}_fol'
                                                        if k not in result:
                                                            result[k] = {}
                                                        if fol_num not in result[k]:
                                                            result[k][fol_num] = {}
                                                        result[k][fol_num]['vol'] = mv
                                                    if sub_cd == '11793-7':
                                                        k = f'ovaire_{loc}_fol'
                                                        if k not in result:
                                                            result[k] = {}
                                                        if fol_num not in result[k]:
                                                            result[k][fol_num] = {}
                                                        if 'diam' not in result[k][fol_num]:
                                                            result[k][fol_num]['diam'] = []
                                                        result[k][fol_num]['diam'].append(float(mv))

                                if section == 'follicule_laterality':
                                    cd2 = it.get(c_name_code_seq)
                                    if cd2:
                                        cd2v = safe_get(cd2[0], code_val_tag)
                                        if cd2v == 'G-C171':
                                            _c = it.get(0x0040A168)
                                            if _c:
                                                _cv = safe_get(_c[0], code_val_tag)
                                                if _cv == 'G-A101':
                                                    section = 'follicule_left'
                                                if _cv == 'G-A100':
                                                    section = 'follicule_right'

                                if (0x0040, 0xA168) in it:
                                    cd3 = it[0x0040A168][0][code_val_tag].value
                                    if cd3 == 'T-87600':
                                        section = 'follicule_laterality'
                                if (0x0040, 0xA168) in it:
                                    cd3 = it[0x0040A168][0][code_val_tag].value
                                    if cd3 == 'T-D6007':
                                        pass

                except Exception as e:
                    _logger.info(f"Error parsing SR item: {e}")
                    continue

    if not result:
        _logger.info("SR parsed but no measurements found")
    _logger.info('*******************************')
    _logger.info(result)
    _logger.info('*******************************')
    return result


if __name__ == '__main__':
    #ds = pydicom.dcmread('./data/obstetrique/sr_ip_ir.dcm')
    #ds = pydicom.dcmread('./data/obstetrique/sr_93978109 to test.dcm')
    ds = pydicom.dcmread('./data/obstetrique/sr_dop_omb_acm_mat.dcm')
    #ds = pydicom.dcmread('./data/sr_follicules.dcm')
    #ds = pydicom.dcmread('./data/drsidhom/sr_75454533.dcm')
    #ds = pydicom.dcmread('./data/sr_dop_dv.dcm')
    #ds = pydicom.dcmread('./data/gyneco/sr_55852573.dcm')
    #ds = pydicom.dcmread('./data/obstetrique/sr_77634075.dcm')
    #ds = pydicom.dcmread('./data/obstetrique/sr_88393973.dcm')
    _logger.info(parse_ds(ds))
