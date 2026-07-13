from django.db import migrations

# Translations for antecedent_obstetrique, consultation_echo_pelvienne_myome, consultation_obstetrique
TRANSLATIONS = {
    # === antecedent_obstetrique: grossesse ===
    16: ('Normal', 'طبيعية', 'Normal'),
    17: ('IUGR-detected', 'تأخر نمو داخل الرحم مكتشف', 'RCIU detectado'),
    18: ('IUGR-undetected', 'تأخر نمو داخل الرحم غير مكتشف', 'RCIU no detectado'),
    19: ('Hypertension', 'ارتفاع ضغط الدم', 'Hipertensión'),
    20: ('Preterm labour threat', 'تهديد بالولادة المبكرة', 'Amenaza de parto prematuro'),
    21: ('Pre-eclampsia', 'ما قبل تسمم الحمل', 'Preeclampsia'),
    22: ('Amniocentesis for ultrasound sign', 'بزل السلى لعلامة إيكوغرافية', 'Amniocentesis por signo ecográfico'),
    23: ('Chorioamnionitis', 'التهاب المشيمة والسلى', 'Corioamnionitis'),
    24: ('Twin pregnancy', 'حمل توأم', 'Embarazo gemelar'),
    25: ('IUGR', 'تأخر النمو داخل الرحم', 'RCIU'),
    26: ('PPROM', 'تمزق الأغشية المبكر', 'RPDE'),
    27: ('Early', 'مبكر', 'Precoz'),
    578: ('IUI', 'تلقيح اصطناعي', 'IAC'),
    579: ('IVF', 'أطفال أنابيب', 'FIV'),
    # === antecedent_obstetrique: analgesie ===
    28: ('General anaesthesia', 'تخدير عام', 'Anestesia general'),
    29: ('Epidural', 'تخدير فوق الجافية', 'Epidural'),
    30: ('None', 'لا شيء', 'Ninguna'),
    31: ('Pudendal nerve block', 'تخدير الأعصاب العجانية', 'Bloqueo nervio pudendo'),
    32: ('Spinal anaesthesia', 'تخدير شوكي', 'Raquianestesia'),
    33: ('No anaesthesia', 'بدون تخدير', 'Sin anestesia'),
    # === antecedent_obstetrique: mise_en_travail ===
    34: ('Spontaneous', 'تلقائي', 'Espontáneo'),
    35: ('Induced', 'مُحفَّز', 'Inducido'),
    36: ('Cervical ripening', 'إنضاج عنق الرحم', 'Maduración cervical'),
    37: ('Directed', 'موجَّه', 'Dirigido'),
    38: ('No labour', 'بدون مخاض', 'Sin trabajo de parto'),
    # === antecedent_obstetrique: indications ===
    39: ('FHR anomaly', 'شذوذ معدل ضربات قلب الجنين', 'Anomalía RCF'),
    40: ('IUGR-detected', 'تأخر نمو مكتشف', 'RCIU detectado'),
    41: ('IUGR-undetected', 'تأخر نمو غير مكتشف', 'RCIU no detectado'),
    42: ('Dystocia', 'عسر الولادة', 'Distocia'),
    43: ('Macrosomia', 'ضخامة الجنين', 'Macrosomía'),
    44: ('IUFD', 'وفاة الجنين داخل الرحم', 'MFIU'),
    45: ('Oligohydramnios', 'قلة السائل الأمنيوسي', 'Oligohidramnios'),
    46: ('Pre-eclampsia', 'ما قبل تسمم الحمل', 'Preeclampsia'),
    47: ('Pre-eclampsia', 'ما قبل تسمم الحمل', 'Preeclampsia'),
    48: ('IUGR', 'تأخر النمو داخل الرحم', 'RCIU'),
    49: ('PPROM', 'تمزق الأغشية المبكر', 'RPDE'),
    50: ('Post-term', 'تجاوز الموعد المحدد', 'Embarazo postérmino'),
    # === antecedent_obstetrique: etat_sante ===
    51: ('Healthy', 'بصحة جيدة', 'Sano'),
    52: ('Malformation', 'تشوه خلقي', 'Malformación'),
    53: ('Chromosomal anomaly', 'شذوذ كروموسومي', 'Anomalía cromosómica'),
    54: ('Deceased', 'متوفى', 'Fallecido'),
    # === antecedent_obstetrique: perinee ===
    55: ('Intact', 'سليم', 'Íntegro'),
    56: ('Episiotomy', 'فصل العجان', 'Episiotomía'),
    57: ('Simple tear', 'تمزق بسيط', 'Desgarro simple'),
    58: ('Complex tear', 'تمزق معقد', 'Desgarro complejo'),
    # === antecedent_obstetrique: suite_couche_type ===
    59: ('Pathological', 'مرضية', 'Patológicas'),
    60: ('Physiological', 'طبيعية', 'Fisiológicas'),
    # === antecedent_obstetrique: suite_couche_detail ===
    61: ('Abscess following operated engorgement', 'خراج بعد احتقان مُعالَج', 'Absceso tras ingurgitación operada'),
    62: ('Anaemia', 'فقر الدم', 'Anemia'),
    63: ('Scalp detachment', 'انفصال فروة الرأس', 'Desprendimiento de cuero cabelludo'),
    64: ('Neonatal with antibiotics', 'حديث الولادة مع مضادات حيوية', 'Neonatal con antibióticos'),
    65: ('Neonate for low weight', 'حديث الولادة لانخفاض الوزن', 'Neonato por bajo peso'),
    66: ('Group A streptococcal sepsis', 'تعفن الدم بالمكورات العقدية أ', 'Sepsis por estreptococo A'),
    67: ('Thrombus', 'خثرة', 'Trombo'),
    # === antecedent_obstetrique: evacuation_grossesse ===
    576: ('Aspiration', 'شفط', 'Aspiración'),
    577: ('Medical', 'دوائي', 'Medicamentoso'),
    # === antecedent_obstetrique: issue_grossesse ===
    1000: ('Breech delivery', 'ولادة مقعدية', 'Parto en nalgas'),
    1001: ('Vaginal delivery', 'ولادة طبيعية', 'Parto vaginal'),
    1002: ('Caesarean section', 'قيصرية', 'Cesárea'),
    1003: ('Spontaneous miscarriage', 'إجهاض تلقائي', 'Aborto espontáneo'),
    1004: ('Late miscarriage', 'إجهاض متأخر', 'Aborto tardío'),
    1005: ('Ectopic pregnancy', 'حمل خارج الرحم', 'Embarazo ectópico'),
    1006: ('Molar pregnancy', 'حمل عنقودي', 'Embarazo molar'),
    1007: ('Medical termination of pregnancy', 'إنهاء الحمل الطبي', 'Interrupción médica del embarazo'),
    1008: ('Late medical termination', 'إنهاء الحمل الطبي المتأخر', 'Interrupción tardía del embarazo'),
    1009: ('Voluntary termination', 'إنهاء الحمل الطوعي', 'Interrupción voluntaria del embarazo'),
    1010: ('Intrauterine foetal death', 'وفاة الجنين داخل الرحم', 'Muerte fetal intrauterina'),
    # === consultation_echo_pelvienne_myome: situation ===
    337: ('Fundal', 'قاعي', 'Fúndico'),
    338: ('Cornual', 'قرني', 'Cornual'),
    339: ('Corporeal', 'جسمي', 'Corporal'),
    340: ('Isthmic', 'برزخي', 'Ístmico'),
    341: ('Cervical', 'عنقي', 'Cervical'),
    342: ('Supra-isthmic', 'فوق البرزخ', 'Supraístmico'),
    # === consultation_echo_pelvienne_myome: type_figo ===
    343: ('0 (pedunculated submucosal intracavitary)', '0 (تحت المخاطية مُعنَّق داخل التجويف)', '0 (submucoso pediculado intracavitario)'),
    344: ('1 (submucosal < 50% intramural)', '1 (تحت المخاطية < 50% داخل العضل)', '1 (submucoso < 50% intramural)'),
    345: ('2 (submucosal > 50% intramural)', '2 (تحت المخاطية > 50% داخل العضل)', '2 (submucoso > 50% intramural)'),
    346: ('3 (100% intramural adjacent to endometrium)', '3 (100% داخل العضل مجاور لبطانة الرحم)', '3 (100% intramural adyacente al endometrio)'),
    347: ('4 (100% intramural distant from endometrium)', '4 (100% داخل العضل بعيد عن بطانة الرحم)', '4 (100% intramural distante del endometrio)'),
    348: ('5 (subserosal > 50% intramural)', '5 (تحت المصلية > 50% داخل العضل)', '5 (subseroso > 50% intramural)'),
    349: ('6 (subserosal < 50% intramural)', '6 (تحت المصلية < 50% داخل العضل)', '6 (subseroso < 50% intramural)'),
    350: ('8 (other: cervical, round ligament, broad ligament)', '8 (أخرى: عنقي، رباط مستدير، رباط عريض)', '8 (otro: cervical, ligamento redondo, ligamento ancho)'),
    351: ('7 (pedunculated subserosal)', '7 (تحت المصلية مُعنَّق)', '7 (subseroso pediculado)'),
    352: ('2-5 (hybrid submucosal class 2 and subserosal class 5)', '2-5 (هجين تحت المخاطية 2 وتحت المصلية 5)', '2-5 (híbrido submucoso clase 2 y subseroso clase 5)'),
    # === consultation_echo_pelvienne_myome: situation_coupe_longitudinale ===
    353: ('Anterior', 'أمامي', 'Anterior'),
    354: ('Central', 'مركزي', 'Central'),
    355: ('Posterior', 'خلفي', 'Posterior'),
    # === consultation_echo_pelvienne_myome: situation_coupe_transversale ===
    356: ('Right', 'يمين', 'Derecho'),
    357: ('Left', 'يسار', 'Izquierdo'),
    358: ('Median', 'وسطي', 'Mediano'),
    # === consultation_echo_pelvienne_myome: contours ===
    359: ('Regular', 'منتظمة', 'Regular'),
    360: ('Irregular', 'غير منتظمة', 'Irregular'),
    # === consultation_echo_pelvienne_myome: structure ===
    361: ('Homogeneous', 'متجانس', 'Homogéneo'),
    362: ('Heterogeneous', 'غير متجانس', 'Heterogéneo'),
    363: ('Heterogeneous', 'غير متجانس', 'Heterogéneo'),
    364: ('Necrosis', 'نخر', 'Necrosis'),
    365: ('Multiple', 'متعددة', 'Múltiples'),
    366: ('Calcified', 'متكلس', 'Calcificado'),
    # === consultation_echo_pelvienne_myome: calcifications ===
    367: ('Absent', 'غائبة', 'Ausentes'),
    368: ('Present', 'موجودة', 'Presentes'),
    # === consultation_echo_pelvienne_myome: vascularisation ===
    369: ('Absent', 'غائبة', 'Ausente'),
    370: ('Peripheral', 'محيطية', 'Periférica'),
    371: ('Peripheral and central', 'محيطية ومركزية', 'Periférica y central'),
    372: ('Hypervascularisation', 'فرط التروية الدموية', 'Hipervascularización'),
    # === consultation_obstetrique: notch ===
    558: ('No', 'لا', 'No'),
    559: ('Yes', 'نعم', 'Sí'),
    560: ('Possible', 'محتمل', 'Posible'),
    561: ('Early notch', 'نقشة مبكرة', 'Muesca incipiente'),
    # === consultation_obstetrique: col_entonnoir ===
    598: ('No', 'لا', 'No'),
    599: ('Yes', 'نعم', 'Sí'),
    600: ('Uterine scar', 'ندبة رحمية', 'Cicatriz uterina'),
    601: ('Cerclage in place', 'خياطة عنق الرحم في مكانها', 'Cerclaje en posición'),
    602: ('Tape in place', 'شريط في مكانه', 'Cinta en posición'),
}


def apply_translations(apps, schema_editor):
    ListeChoix = apps.get_model('core', 'ListeChoix')
    for pk, (en, ar, es) in TRANSLATIONS.items():
        ListeChoix.objects.filter(pk=pk).update(
            libelle_en=en,
            libelle_ar=ar,
            libelle_es=es,
        )


def reverse_translations(apps, schema_editor):
    ListeChoix = apps.get_model('core', 'ListeChoix')
    pks = list(TRANSLATIONS.keys())
    ListeChoix.objects.filter(pk__in=pks).update(libelle_en='', libelle_ar='', libelle_es='')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0211_listechoix_translations_data'),
    ]

    operations = [
        migrations.RunPython(apply_translations, reverse_translations),
    ]
