import traceback

import pydicom
from apps.core.services.utils import *


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
    '11850-5': 'sac_gestationnel_diametre',
    '18185-9': 'age_gestationnel',
    '8867-4': 'fc',
    '11957-8': 'lcc',
    '11979-2': 'pa',  # Abdominal circumference (pa)
    '11820-8': 'bip',  # Biparetal diameter (bip)
    '11963-6': 'femur',  # Femur length (bip)
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
    print('parse_umbilical_artery ===================')
    for it in seq:
        cd = it[c_name_code_seq][0][code_val_tag].value
        print(cd)

        foetus = None
        # print(_c)
        if cd == '11951-1':
            # Foetus ID
            id = it[0x0040A160].value
            print('Foetus ID', id)
            foetus = get_foetus(id, result)
            foetus['arteres'] = {}
            print(foetus)
        try:
            c_seq = it[0x0040A300]
            for seq_item in c_seq:
                units_seq = seq_item[0x004008EA]
                unit = units_seq[0][code_val_tag].value
                print('Unit', unit)
                value = seq_item[0x0040A30A].value
                # print('Value', value)
                #if foetus is not None:
                cpt = codes_concept_label[cd]
                #print(, value)
                foetus['arteres'].cpt = value
        except:
            pass
    print('===========================================')


def parse_follicule(seq, result):
    #print(seq)
    return
    for it in seq:
        cd = it[c_name_code_seq][0][code_val_tag].value
        print(cd)
        print('************************')

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
                            print('<<<<< Uterine Artery >>>>>>')
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
                                                print("Laterality", laterality)
                                        else:
                                            # print(_cv)
                                            if "ConceptNameCodeSequence" in _ds:
                                                _ccs = _ds.ConceptNameCodeSequence[0]
                                                if "MeasuredValueSequence" in _ds:
                                                    for valitem in _ds.MeasuredValueSequence:
                                                        val = valitem.NumericValue
                                                        print(f"{_ccs.CodeValue} ({_ccs.CodeMeaning}) = {val}")
                                                    if _ccs.CodeValue == '12023-8':
                                                        doppler_uterin['ir_' + laterality] = val
                                                    if _ccs.CodeValue == '12008-9':
                                                        doppler_uterin['ip_' + laterality] = val

                            print('Doppler utérin', doppler_uterin)
                            result['doppler_uterin'] = doppler_uterin

                            #############################################################################

                        if innercncs == "T-F1810":
                            print('<<<<< Umbilical Artery >>>>>>')
                            doppler_ombilical = {}
                            if "ContentSequence" in innerds:
                                for _ds in innerds.ContentSequence:
                                    if "ConceptNameCodeSequence" in _ds:
                                        _cv = _ds.ConceptNameCodeSequence[0].CodeValue
                                        if _cv == "11951-1":
                                            foetusId = _ds.TextValue
                                            print("Foetus ID", foetusId)
                                        else:
                                            if not foetusId:
                                                print("No foetus ID")
                                                continue
                                            f = get_foetus(foetusId, result)
                                            if "ConceptNameCodeSequence" in _ds:
                                                _ccs = _ds.ConceptNameCodeSequence[0]
                                                if "MeasuredValueSequence" in _ds:
                                                    for valitem in _ds.MeasuredValueSequence:
                                                        val = valitem.NumericValue
                                                        print(f"{_ccs.CodeValue} ({_ccs.CodeMeaning}) = {val}")
                                                    if _ccs.CodeValue == '12023-8':
                                                        doppler_ombilical['doppler_cordon_ir'] = val
                                                    if _ccs.CodeValue == '12008-9':
                                                        doppler_ombilical['doppler_cordon_ip'] = val
                                            if f:
                                                if 'doppler_ombilical' in f:
                                                    f['doppler_ombilical'] = {**f['doppler_ombilical'], **doppler_ombilical}
                                                else:
                                                    f['doppler_ombilical'] = doppler_ombilical
                            print('Doppler ombilical', doppler_ombilical)

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
        print(i[code_val_tag].value)
    print(count)
    param = sub[c_name_code_seq][0][code_val_tag].value
    meaning = sub[c_name_code_seq][0][code_val_meaning].value
    seq = safe_get(sub, 0x0040A300)
    if seq:
        val = seq[0][0x0040A30A].value
        #print(f'Code {code} - Param {param} ({meaning}) = {val}')


def parse_ds(ds):
    result = {}
    concept_name_code_sequence = safe_get(ds, c_name_code_seq)
    report_type = _val(concept_name_code_sequence[0], 0x00080104)
    print('Report type ', report_type)
    # print(v.tag, v.VR, v.value)
    # print('Concept Name Code Sequence Attribute', concept_name_code_sequence)
    content_template_sequence = safe_get(ds, 0x0040A504)
    # print('Content Template Sequence', content_template_sequence)
    content_sequence = safe_get(ds, 0x0040A730)

    for seq in content_sequence:
        c_name_seq = seq[c_name_code_seq]
        for item in seq:

            if item.VR != 'SQ':
                continue

            if (0x0008, 0x0100) not in item[0]:
                continue

            code = item[0][code_val_tag].value
            # print(code)

            parse_doppler_samsung(seq, result)

            if code == '121111':
                if 0x0040A730 in seq:
                    print('Summary section')
                    # Next sequence is summary
                    c_seq = seq[0x0040A730]
                    for it in c_seq:
                        cd = it[c_name_code_seq][0][code_val_tag].value
                        if cd in ['11781-2', '11779-6']:
                            # EDD from average ultrasound age
                            result[codes_concept_label['11781-2']] = it[0x0040A121].value
                        if cd == '11955-2':
                            # DDR from average ultrasound age
                            result[codes_concept_label['11955-2']] = it[0x0040A121].value

                        if cd == '125008':
                            # Fetus summary
                            if 0x0040A730 in it:
                                content = it[0x0040A730]
                                foetus = {}
                                for c in content:
                                    _c = c[c_name_code_seq][0]
                                    v = safe_get(_c, code_val_tag)
                                    if v:
                                        if v == '11951-1':
                                            foetus['id'] = c[0x0040A160].value
                                        if v == '11888-5':
                                            foetus['age_gest'] = c[0x0040A300][0][0x0040A30A].value
                                        if v == '11727-5':
                                            foetus['poids'] = c[0x0040A300][0][0x0040A30A].value
                                        if v == '11781-2':
                                            foetus['date_accouchement'] = c[0x0040A121].value
                                    #print(f">> {_c[code_val_tag].value} - {c[0x0040A300][0][0x0040A30A].value}")
                                #print('Foetus', foetus)
                                if 'foetus' not in result:
                                    result['foetus'] = []
                                result['foetus'].append(foetus)

            if code == '125008':
                if 0x0040A730 in seq:
                    # Fetus summary
                    content = seq[0x0040A730]
                    foetus = {}
                    for c in content:
                        _c = c[c_name_code_seq][0]
                        v = safe_get(_c, code_val_tag)
                        if v:
                            try:
                                if v == '11951-1':
                                    foetus['id'] = c[0x0040A160].value
                                if v == '99005-4':
                                    foetus['age_gest'] = c[0x0040A300][0][0x0040A30A].value
                                if v == '11727-5':
                                    foetus['poids'] = c[0x0040A300][0][0x0040A30A].value
                                if v == '11781-2':
                                    foetus['date_accouchement'] = c[0x0040A121].value
                                if v == '11948-7':
                                    foetus['fc'] = c[0x0040A121].value
                            except:
                                print("Error reading foetus summary data")

                    #print('Foetus', foetus)
                    if 'foetus' not in result:
                        result['foetus'] = []
                    result['foetus'].append(foetus)

            if code == '125001':
                if 0x0040A730 in seq:
                    # Fetal biometry ratios
                    c_seq = seq[0x0040A730]
                    id = None
                    ratios = {}
                    for it in c_seq:
                        _c = it[c_name_code_seq][0][code_val_tag].value
                        # print(_c)
                        if _c == '11951-1':
                            # Foetus ID
                            id = it[0x0040A160].value
                        if _c == '11947-9':
                            # HC/AC
                            ratios['hc_ac'] = it[0x0040A300][0][0x0040A30A].value
                        if _c == '11871-1':
                            # FL/AC
                            ratios['fl_ac'] = it[0x0040A300][0][0x0040A30A].value
                        if _c == '11872-9':
                            # FL/BPD
                            ratios['fl_bpd'] = it[0x0040A300][0][0x0040A30A].value
                        if _c == '11823-2':
                            # Cephalic index
                            ratios['cephalic_index'] = it[0x0040A300][0][0x0040A30A].value
                        if _c == '11873-7':
                            # FL/HC
                            ratios['fl_hc'] = it[0x0040A300][0][0x0040A30A].value
                        if _c == '99000-01':
                            # FL/FOOT
                            ratios['fl_foot'] = it[0x0040A300][0][0x0040A30A].value
                    # print('Foetus', ratios)

                    f = get_foetus(id, result)
                    if f:
                        f['ratios'] = ratios

            # DEBUG CODE
            if code != None:
                if 0x0040A730 in seq:
                    # Fetal biometry
                    c_seq = seq[0x0040A730]
                    id = None
                    for it in c_seq:
                        _c = it[c_name_code_seq][0][code_val_tag].value
                        if 0x0040A730 in it:
                            for el in it[0x0040A730]:
                                pass
                                #print(_c)
                                #print_attrib(code, el)
                                #print('--------')

            if code == '99001':
                if 0x0040A730 in seq:
                    # Doppler uterin/maternel
                    c_seq = seq[0x0040A730]
                    dop = {}
                    counter = 0
                    for it in c_seq:
                        _c = it[c_name_code_seq][0][code_val_tag].value
                        # print('Code', _c)
                        if (0x0040, 0xA168) in it:
                            cd = it[0x0040A168][0][code_val_tag].value
                            print(cd)
                        if _c == '99100':
                            if 0x0040A730 in it:
                                # print('Group not empty')
                                for el in it[0x0040A730]:
                                    lat = None
                                    if 0x0040A730 in el:
                                        for item in el[0x0040A730]:
                                            v = safe_get(item[c_name_code_seq][0], code_val_tag)
                                            if v == "G-C0E3":
                                                # Finding site
                                                try:
                                                    if 'G-C171' == safe_get(item[0x0040A730][0][c_name_code_seq][0], code_val_tag):
                                                        lat = safe_get(item[0x0040A730][0][0x0040A168][0], code_val_tag)
                                                        if lat == 'G-A101':
                                                            # Ovaire gauche
                                                            lat = 'gauche'
                                                        if lat == 'G-A100':
                                                            # Ovaire droit
                                                            lat = 'droit'
                                                        #print(v)
                                                except :
                                                    print("Uterus laterality can't be evaluated")


                                    if lat:
                                        param = el[c_name_code_seq][0][code_val_tag].value
                                        # print_attrib(code, el)
                                        for v in allowed_codes:
                                            if param == v:
                                                if param == '12023-8':
                                                    dop['ir_' + lat] = el[0x0040A300][0][0x0040A30A].value
                                                if param == '12008-9':
                                                    dop['ip_' + lat] = el[0x0040A300][0][0x0040A30A].value

                        print('Doppler utérin', dop)
                        result[f'doppler_uterin'] = dop

            if code == '99000':
                if 0x0040A730 in seq:
                    # Doppler foetus (ombilical/ACM)
                    c_seq = seq[0x0040A730]
                    dop = {}
                    id = None
                    for it in c_seq:
                        _c = it[c_name_code_seq][0][code_val_tag].value
                        # print('Code', _c)
                        if _c == '11951-1':
                            # Foetus ID
                            id = it[0x0040A160].value
                            print('Foetus', id)
                        if _c == '99100':
                            if 0x0040A730 in it:
                                print('Group not empty')
                                for el in it[0x0040A730]:
                                    # el[0x0040A730][0][c_name_code_seq][0][code_val_tag].value
                                    site = el[c_content_sequence][0][c_code_seq][0][code_val_tag].value
                                    #print("Site", site)
                                    if site == "T-F1810":
                                        # Ombilical
                                        f = get_foetus(id, result)
                                        try:
                                            param = el[c_name_code_seq][0][code_val_tag].value
                                            #print_attrib(code, sub)
                                            for v in allowed_codes:
                                                if param == v:
                                                    param_val = el[0x0040A300][0][0x0040A30A].value
                                                    dop[codes_concept_label[v]] = param_val
                                                    if param == '12023-8':
                                                        dop['doppler_cordon_ir'] = param_val
                                                    if param == '12008-9':
                                                        dop['doppler_cordon_ip'] = param_val
                                                    if param == '11653-3':
                                                        dop['doppler_cordon_diastole_num'] = param_val
                                                    if param == '8867-4':
                                                        if f:
                                                            f['fc'] = param_val
                                            if f:
                                                if 'doppler_ombilical' in f:
                                                    f['doppler_ombilical'] = {**f['doppler_ombilical'], **dop}
                                                else:
                                                    f['doppler_ombilical'] = dop
                                            print('Doppler ombilical', dop)
                                        except:
                                            print("Problem parsing ombilical doppler")
                                    if site == "T-45600":
                                        # ACM
                                        f = get_foetus(id, result)
                                        try:
                                            param = el[c_name_code_seq][0][code_val_tag].value
                                            #print_attrib(code, sub)
                                            for v in allowed_codes:
                                                if param == v:
                                                    param_val = el[0x0040A300][0][0x0040A30A].value
                                                    dop[codes_concept_label[v]] = param_val
                                                    if param == '12023-8':
                                                        dop['doppler_acm_ir'] = param_val
                                                    if param == '12008-9':
                                                        dop['doppler_acm_ip'] = param_val
                                                    if param == '8867-4':
                                                        if f:
                                                            f['fc'] = param_val
                                                    #if param == '11653-3':
                                                    #    dop['doppler_acm_diastole'] = param_val
                                            if f:
                                                if 'doppler_acm' in f:
                                                    f['doppler_acm'] = {**f['doppler_acm'], **dop}
                                                else:
                                                    f['doppler_acm'] = dop
                                            print('Doppler acm', dop)
                                        except:
                                            print("Problem parsing acm doppler")

                                    if site == "VP-0001":
                                        # DV
                                        f = get_foetus(id, result)
                                        try:
                                            param = el[c_name_code_seq][0][code_val_tag].value
                                            #print_attrib(code, sub)
                                            for v in allowed_codes:
                                                if param == v:
                                                    param_val = el[0x0040A300][0][0x0040A30A].value
                                                    dop[codes_concept_label[v]] = param_val
                                                    if param == '12023-8':
                                                        dop['doppler_dv_ir'] = param_val
                                                    if param == '12008-9':
                                                        dop['doppler_dv_ip'] = param_val
                                                    if param == '8867-4':
                                                        if f:
                                                            f['fc'] = param_val
                                                    #if param == '11653-3':
                                                    #    dop['doppler_acm_diastole'] = param_val
                                            if f:
                                                if 'doppler_dv' in f:
                                                    f['doppler_dv'] = {**f['doppler_dv'], **dop}
                                                else:
                                                    f['doppler_dv'] = dop
                                            print('Doppler DV', dop)
                                        except:
                                            print("Problem parsing DV doppler")

            if code == '125002' or code == '125009':
                if 0x0040A730 in seq:
                    # Fetal biometry
                    c_seq = seq[0x0040A730]
                    bio = {}
                    id = None
                    for it in c_seq:
                        _c = it[c_name_code_seq][0][code_val_tag].value
                        #print('Code', _c)
                        if _c == '11951-1':
                            # Foetus ID
                            id = it[0x0040A160].value
                            #print('Foetus', id)
                        if _c == '125005':
                            # Biometry group
                            if 0x0040A730 in it:
                                #print('Group not empty')
                                sub = it[0x0040A730][0]
                                param = sub[c_name_code_seq][0][code_val_tag].value
                                #print_attrib(code, sub)
                                for v in allowed_codes:
                                    if param == v:
                                        bio[codes_concept_label[v]] = sub[0x0040A300][0][0x0040A30A].value
                            else:
                                #print('Group empty')
                                pass

                        # print('Biométrie', bio)

                    f = get_foetus(id, result)
                    if f:
                        if 'biometrie' in f:
                            f['biometrie'] = {**f['biometrie'], **bio}
                        else:
                            f['biometrie'] = bio

            if code == '125003':
                # Fetal long bones
                if 0x0040A730 in seq:
                    c_seq = seq[0x0040A730]
                    bones = {}
                    id = None
                    for it in c_seq:
                        _c = it[c_name_code_seq][0][code_val_tag].value
                        #print('Code', _c)
                        if _c == '11951-1':
                            # Foetus ID
                            id = it[0x0040A160].value
                            #print('Foetus', id)

                        if _c == '125005':
                            if 0x0040A730 in it:
                            # Biometry group
                                sub = it[0x0040A730][0]
                                param = sub[c_name_code_seq][0][code_val_tag].value
                                for v in allowed_codes:
                                    if param == v:
                                        bones[codes_concept_label[v]] = sub[0x0040A300][0][0x0040A30A].value

                        #print('--------------------------------------')
                        #print('Bones', bones)
                        f = get_foetus(id, result)
                        if f:
                            f['os'] = bones

            if code == '125004':
                if 0x0040A730 in seq:
                    # Fetal cranium
                    c_seq = seq[0x0040A730]
                    cranium = {}
                    id = None
                    for it in c_seq:
                        _c = it[c_name_code_seq][0][code_val_tag].value
                        #print('Code', _c)
                        if _c == '11951-1':
                            # Foetus ID
                            id = it[0x0040A160].value
                            #print('Foetus', id)

                        if _c == '125005':
                            # Biometry group
                            if 0x0040A730 in it:
                                sub = it[0x0040A730][0]
                                param = sub[c_name_code_seq][0][code_val_tag].value
                                for v in allowed_codes:
                                    if param == v:
                                        cranium[codes_concept_label[v]] = sub[0x0040A300][0][0x0040A30A].value

                        #print('--------------------------------------')
                        #print('Crane', cranium)
                        f = get_foetus(id, result)
                        if f:
                            f['crane'] = cranium

            # print(f'----------------- Sequence item code {code} ------------------')
            if code == '125011':
                # print('*************** Pelvis and Uterus')
                if 0x0040A730 in seq:
                    parse_pelvis_uterus(seq[0x0040A730], result)

            if code == '121070' or code == '125070':
                # Findings
                if 0x0040A730 in seq:
                    #print('Findings')
                    c_seq = seq[0x0040A730]
                    section = None
                    seq_count = 0
                    fol_num = -1
                    for it in c_seq:
                        seq_count += 1
                        cd = it[c_name_code_seq][0][code_val_tag].value
                        #print('Seq code', cd)
                        # print('Sequence count', seq_count)
                        if cd == 'T-87000':
                            print('Parse ovary')
                            if 0x0040A730 in it:
                                parse_ovary(it[0x0040A730], result)
                                continue

                        if cd == 'T-F1810':
                            #print('Parse Umbilical Artery')
                            #parse_umbilical_artery(it[0x0040A730], result)
                            continue

                        if cd == '125007':
                            # Measurement group
                            fol_num += 1
                            #print('Parse follicule')
                            parse_follicule(it, result)

                            if section in ['follicule_left', 'follicule_right']:
                                loc = 'gauche' if section == 'follicule_left' else 'droit'
                                # print(it)
                                if it[c_name_code_seq][0][code_val_tag].value == '125007':
                                    # Measurement group
                                    # print('Measurement group')
                                    if 0x0040A730 in it:
                                        c_seq = it[0x0040A730]
                                        for seq_item in c_seq:
                                            sub_seq = seq_item[c_name_code_seq][0]
                                            cd = sub_seq[code_val_tag].value
                                            if cd == 'G-D705':
                                                # Volume
                                                measured_val_seq = seq_item[0x0040A300]
                                                # print(sub_seq[code_val_tag].value)
                                                units_seq = measured_val_seq[0][0x004008EA]
                                                unit = units_seq[0][code_val_tag].value
                                                value = measured_val_seq[0][0x0040A30A].value
                                                if f'ovaire_{loc}_fol' not in result:
                                                    result[f'ovaire_{loc}_fol'] = {}
                                                if fol_num not in result[f'ovaire_{loc}_fol']:
                                                    result[f'ovaire_{loc}_fol'][fol_num] = {}
                                                result[f'ovaire_{loc}_fol'][fol_num]['vol'] = value

                                            if cd == '11793-7':
                                                # Diameter
                                                measured_val_seq = seq_item[0x0040A300]
                                                # print(sub_seq[code_val_tag].value)
                                                units_seq = measured_val_seq[0][0x004008EA]
                                                unit = units_seq[0][code_val_tag].value
                                                value = measured_val_seq[0][0x0040A30A].value
                                                # print(measured_val_seq[0][0x0040A30A])
                                                if f'ovaire_{loc}_fol' not in result:
                                                    result[f'ovaire_{loc}_fol'] = {}
                                                if fol_num not in result[f'ovaire_{loc}_fol']:
                                                    result[f'ovaire_{loc}_fol'][fol_num] = {}
                                                if 'diam' not in result[f'ovaire_{loc}_fol'][fol_num]:
                                                    result[f'ovaire_{loc}_fol'][fol_num]['diam'] = []
                                                result[f'ovaire_{loc}_fol'][fol_num]['diam'].append(float(value))

                        if section == 'follicule_laterality':
                            cd = it[c_name_code_seq][0][code_val_tag].value
                            # print(it)
                            if cd == 'G-C171':
                                _c = it[0x0040A168][0][code_val_tag].value
                                if _c == 'G-A101':
                                    # Ovaire gauche
                                    section = 'follicule_left'

                                if _c == 'G-A100':
                                    # Ovaire droit
                                    section = 'follicule_right'

                                # print(it[0x0040A168][0][code_val_tag].value)
                            # 'G-A101'

                        if (0x0040, 0xA168) in it:
                            cd = it[0x0040A168][0][code_val_tag].value
                            if cd == 'T-87600':
                                section = 'follicule_laterality'
                        if (0x0040, 0xA168) in it:
                            cd = it[0x0040A168][0][code_val_tag].value
                            if cd == 'T-D6007':
                                # print('Pelvic Vascular Structure X4')
                                pass

            """
            for it in item:
                if (0x0040, 0xA010) in it:
                    if it[0x0040A010].value == 'CONTAINS':
                        if it[0x0040A040].value == 'DATE':
                            # print('Date sequence')
                            sub_items = it[c_name_code_seq]
                            cd = sub_items[0][code_val_tag].value
                            if cd == '11781-2':
                                # EDD from average ultrasound age
                                result[codes_concept_label['11781-2']] = it[0x0040A121].value
                            if cd == '11955-2':
                                # DDR from average ultrasound age
                                result[codes_concept_label['11955-2']] = it[0x0040A121].value
                        else:
                            # print(it[c_name_code_seq][0][code_val_tag].value)
                            cd = it[c_name_code_seq][0][code_val_tag].value

                            if cd == '125005':
                                # Biometry group
                                c_seq = it[0x0040A730]
                                for seq_item in c_seq:
                                    measured_val_seq = seq_item[0x0040A300]
                                    sub_seq = seq_item[c_name_code_seq][0]
                                    # print(sub_seq[code_val_tag].value)
                                    for cd in allowed_codes:
                                        if sub_seq[code_val_tag].value == cd:
                                            measured_val_seq = seq_item[0x0040A300]
                                            units_seq = measured_val_seq[0][0x004008EA]
                                            unit = units_seq[0][code_val_tag].value
                                            value = measured_val_seq[0][0x0040A30A].value
                                            result[codes_concept_label[cd]] = value
                                    # print('-------------------------------')

                            # sub_items = it[c_name_code_seq]
"""
    print('*******************************')
    print(result)
    print('*******************************')
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
    print(parse_ds(ds))
