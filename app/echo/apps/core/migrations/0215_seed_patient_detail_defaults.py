from django.db import migrations


CONSULTATION_CATEGORIES = [
    (1, "Obstétrique"),
    (2, "Gynécologie"),
    (3, "PMA"),
    (4, "Examen libre"),
    (5, "Cardiologie"),
    (6, "Vasculaire"),
    (7, "Compte-rendu opératoire"),
]


CONSULTATION_MOTIFS = [
    ("gynecologique-defaut", "Consultation gynécologique", 2, True),
    ("colposcopie", "Coloposcopie", 2, False),
    ("echo-pelvienne", "Echographie pelvienne", 2, False),
    ("gyneco-libre", "Consultation gynécologique libre", 2, True),
    ("obs_echo_11SA", "Echo < 11 SA", 1, True),
    ("obs_echo_trimestre_1", "Echo 1er trimestre", 1, True),
    ("obs_echo_trimestre_2", "Echo 2ème trimestre", 1, True),
    ("obs_echo_trimestre_3", "Echo 3ème trimestre", 1, True),
    ("obs_echo_croissance", "Echo de croissance", 1, True),
    ("obs-libre", "Consultation obstétrique libre", 1, True),
    ("libre-defaut", "Consultation libre", 4, True),
    ("cr_op", "Compte-rendu opératoire", 7, True),
]


DISTRIBUTION_DEFAULT_CATEGORIES = {
    "gyneco": [1, 2, 4, 7],
    "cardio": [5, 6, 4, 7],
    "general": [4, 7],
}


ANTECEDENT_CATEGORIES = [
    (1, "Antécédents familiaux", "Family History", "التاريخ العائلي", "Antecedentes familiares"),
    (2, "Antécédents médico-chirurgicaux", "Medical-Surgical History", "التاريخ الطبي والجراحي", "Antecedentes médico-quirúrgicos"),
    (3, "Antécédents gynécologiques", "Gynecological History", "التاريخ النسائي", "Antecedentes ginecológicos"),
    (4, "Antécédents obstétricaux", "Obstetric History", "التاريخ التوليدي", "Antecedentes obstétricos"),
    (5, "Autres", "Other", "أخرى", "Otros"),
    (6, "Allergies", "Allergies", "الحساسية", "Alergias"),
]


SOUS_CATEGORIES_ANTECEDENTS = [
    (1, "Antécédents familiaux", 1),
    (2, "Antécédents médico-chirurgicaux", 2),
    (3, "Antécédents gynécologiques", 3),
    (4, "Accouchement du siège", 4),
    (5, "Accouchement voie basse", 4),
    (6, "Accouchement voie basse instrumentale", 4),
    (7, "Césarienne", 4),
    (8, "FCS", 4),
    (9, "FCT", 4),
    (10, "GEU", 4),
    (11, "Grossesse molaire", 4),
    (12, "IMG", 4),
    (13, "ISG", 4),
    (14, "IVG", 4),
    (15, "MFIU", 4),
    (16, "FCV", 5),
    (17, "Mammographie", 5),
    (18, "Echo Mammaire", 5),
    (19, "Non définie", 4),
]


PHRASIERS_ANTECEDENTS = [
    ("Antécédents familiaux", "Diabète", "Diabète familial (préciser le type et le degré)", "Family history of diabetes (specify type and degree)", "تاريخ عائلي للسكري (تحديد النوع والدرجة)", "Diabetes familiar (especificar tipo y grado)"),
    ("Antécédents familiaux", "Hypertension artérielle", "HTA dans la famille", "Family history of hypertension", "ارتفاع ضغط الدم العائلي", "Hipertensión arterial familiar"),
    ("Antécédents familiaux", "Cardiopathie", "Cardiopathie familiale", "Family history of heart disease", "أمراض القلب العائلية", "Cardiopatía familiar"),
    ("Antécédents familiaux", "Cancer du sein", "Cancer du sein dans la famille", "Family history of breast cancer", "سرطان الثدي في العائلة", "Cáncer de mama familiar"),
    ("Antécédents familiaux", "Cancer de lovaire", "Cancer de lovaire dans la famille", "Family history of ovarian cancer", "سرطان المبيض في العائلة", "Cáncer de ovario familiar"),
    ("Antécédents familiaux", "Maladie thromboembolique", "Antécédent de maladie thromboembolique familiale", "Family history of thromboembolic disease", "تاريخ عائلي للجلطات الوريدية", "Enfermedad tromboembólica familiar"),
    ("Antécédents médico-chirurgicaux", "Appendicectomie", "Appendicectomie à lâge de ...", "Appendectomy at age...", "استئصال الزائدة في سن...", "Apendicectomía a la edad de..."),
    ("Antécédents médico-chirurgicaux", "Chirurgie ovarienne", "Chirurgie ovarienne (préciser)", "Ovarian surgery (specify)", "جراحة المبيض (تحديد)", "Cirugía ovárica (especificar)"),
    ("Antécédents médico-chirurgicaux", "Myomectomie", "Myomectomie", "Myomectomy", "استئصال الورم الليفي", "Miomectomía"),
    ("Antécédents médico-chirurgicaux", "Conisation", "Conisation", "Conization", "استئصال مخروطي", "Conización"),
    ("Antécédents médico-chirurgicaux", "Hystéroscopie", "Hystéroscopie diagnostique/opératoire", "Diagnostic/operative hysteroscopy", "تنظير الرحم التشخيصي/الجراحي", "Histeroscopia diagnóstica/operatoria"),
    ("Antécédents gynécologiques", "Grossesse extra-utérine", "Antécédent de GEU", "History of ectopic pregnancy", "تاريخ حمل خارج الرحم", "Antecedente de embarazo ectópico"),
    ("Antécédents gynécologiques", "Kyste ovarien", "Kyste ovarien droit/gauche", "Right/left ovarian cyst", "كيس مبيضي أيمن/أيسر", "Quiste ovárico derecho/izquierdo"),
    ("Antécédents gynécologiques", "Syndrome des ovaires polykystiques", "SOPK", "Polycystic ovary syndrome (PCOS)", "تعدد كيسات المبيض", "Síndrome de ovario poliquístico"),
    ("Antécédents gynécologiques", "Endométriose", "Endométriose (préciser le stade)", "Endometriosis (specify stage)", "بطانة رحميه مهاجره (تحديد المرحلة)", "Endometriosis (especificar estadio)"),
    ("Antécédents gynécologiques", "Ménopause précoce", "Ménopause précoce familiale", "Family history of premature menopause", "انقطاع الطمث المبكر العائلي", "Menopausia precoce familiar"),
    ("Allergies", "Allergie aux antibiotiques", "Allergie à la pénicilline / autres antibiotiques", "Allergy to penicillin / other antibiotics", "حساسية من البنسلين / مضادات حيوية أخرى", "Alergia a la penicilina / otros antibióticos"),
    ("Allergies", "Allergie à lodothérapie", "Allergie à liode", "Allergy to iodine", "حساسية من اليود", "Alergia al yodo"),
    ("Allergies", "Allergie aux antiseptiques", "Allergie aux antiseptiques", "Allergy to antiseptics", "حساسية من المطهرات", "Alergia a los antisépticos"),
    ("Allergies", "Allergie au latex", "Allergie au latex", "Latex allergy", "حساسية من اللاتكس", "Alergia al látex"),
]


LISTE_CHOIX_ANTECEDENTS = [
    ("FCV", "Normal", "Normal", "طبيعي", "Normal", True),
    ("FCV", "Anormal", "Abnormal", "غير طبيعي", "Anormal", False),
    ("FCV", "ASC-H", "ASC-H", "ASC-H", "ASC-H", False),
    ("FCV", "ASC-US", "ASC-US", "ASC-US", "ASC-US", False),
    ("FCV", "LSIL", "LSIL", "LSIL", "LSIL", False),
    ("FCV", "HSIL", "HSIL", "HSIL", "HSIL", False),
    ("FCV", "AGC", "AGC", "AGC", "AGC", False),
    ("FCV", "Échantillon insatisfaisant", "Unsatisfactory sample", "عينة غير مرضية", "Muestra insatisfactoria", False),
    ("FCV", "Néonatalogie positive", "Positive neonatology", "نيوناتولوجيا إيجابية", "Neonatología positiva", False),
    ("Mammographie", "Normal", "Normal", "طبيعي", "Normal", True),
    ("Mammographie", "Anormal", "Abnormal", "غير طبيعي", "Anormal", False),
    ("Mammographie", "Calcifications", "Calcifications", "تكلسات", "Calcificaciones", False),
    ("Mammographie", "Masse", "Mass", "كتلة", "Masa", False),
    ("Mammographie", "Distorsion architecturale", "Architectural distortion", "تشوه معماري", "Distorsión arquitectónica", False),
    ("Mammographie", "Asymétrie", "Asymmetry", "عدم تماثل", "Asimetría", False),
    ("Mammographie", "BI-RADS 0", "BI-RADS 0", "BI-RADS 0", "BI-RADS 0", False),
    ("Mammographie", "BI-RADS 3", "BI-RADS 3 - Probably Benign", "BI-RADS 3 - حميد على الأرجح", "BI-RADS 3 - Probablemente benigno", False),
    ("Mammographie", "BI-RADS 4", "BI-RADS 4 - Suspicious", "BI-RADS 4 - مشبوه", "BI-RADS 4 - Sospechoso", False),
    ("Mammographie", "BI-RADS 5", "BI-RADS 5 - Highly Suspicious", "BI-RADS 5 - مشبوه جداً", "BI-RADS 5 - Altamente sospechoso", False),
    ("Echo Mammaire", "Normal", "Normal", "طبيعي", "Normal", True),
    ("Echo Mammaire", "Anormal", "Abnormal", "غير طبيعي", "Anormal", False),
    ("Echo Mammaire", "Kyste simple", "Simple cyst", "كيس بسيط", "Quiste simple", False),
    ("Echo Mammaire", "Kyste complexe", "Complex cyst", "كيس معقد", "Quiste complejo", False),
    ("Echo Mammaire", "Fibroadénome", "Fibroadenoma", "ورم ليفية", "Fibroadenoma", False),
    ("Echo Mammaire", "Nodule solide", "Solid nodule", "عقدة صلبة", "Nódulo sólido", False),
    ("Echo Mammaire", "Dilatation canalaire", "Ductal dilatation", "توسع قناة", "Dilatación ductal", False),
    ("Echo Mammaire", "Lipome", "Lipoma", "ورم شحمي", "Lipoma", False),
]


def seed_patient_detail_defaults(apps, schema_editor):
    CategorieConsultation = apps.get_model("core", "CategorieConsultation")
    MotifConsultation = apps.get_model("core", "MotifConsultation")
    Compte = apps.get_model("core", "Compte")
    CatgeorieAntecedent = apps.get_model("core", "CatgeorieAntecedent")
    SousCatgeorieAntecedent = apps.get_model("core", "SousCatgeorieAntecedent")
    PhrasierAntecedent = apps.get_model("core", "PhrasierAntecedent")
    ListeChoix = apps.get_model("core", "ListeChoix")

    for pk, libelle in CONSULTATION_CATEGORIES:
        CategorieConsultation.objects.update_or_create(
            pk=pk,
            defaults={"libelle": libelle},
        )

    for code, libelle, categorie_id, actif in CONSULTATION_MOTIFS:
        MotifConsultation.objects.update_or_create(
            code=code,
            defaults={
                "libelle": libelle,
                "categorie_id": categorie_id,
                "actif": actif,
            },
        )

    for compte in Compte.objects.all():
        if compte.categories_consultations.exists():
            continue
        cat_ids = DISTRIBUTION_DEFAULT_CATEGORIES.get(
            compte.distribution, DISTRIBUTION_DEFAULT_CATEGORIES["gyneco"]
        )
        compte.categories_consultations.set(
            CategorieConsultation.objects.filter(pk__in=cat_ids)
        )

    for pk, libelle, en, ar, es in ANTECEDENT_CATEGORIES:
        CatgeorieAntecedent.objects.update_or_create(
            pk=pk,
            defaults={
                "libelle": libelle,
                "libelle_en": en,
                "libelle_ar": ar,
                "libelle_es": es,
            },
        )

    for pk, libelle, categorie_id in SOUS_CATEGORIES_ANTECEDENTS:
        SousCatgeorieAntecedent.objects.update_or_create(
            pk=pk,
            defaults={"libelle": libelle, "categorie_id": categorie_id},
        )

    categories_by_label = {
        c.libelle: c for c in CatgeorieAntecedent.objects.filter(
            libelle__in=[x[1] for x in ANTECEDENT_CATEGORIES]
        )
    }
    for categorie_libelle, libelle, text, text_en, text_ar, text_es in PHRASIERS_ANTECEDENTS:
        categorie = categories_by_label.get(categorie_libelle)
        if not categorie:
            continue
        PhrasierAntecedent.objects.update_or_create(
            libelle=libelle,
            defaults={
                "categorie_id": categorie.pk,
                "text": text,
                "text_en": text_en,
                "text_ar": text_ar,
                "text_es": text_es,
            },
        )

    for champ, libelle, libelle_en, libelle_ar, libelle_es, normale in LISTE_CHOIX_ANTECEDENTS:
        ListeChoix.objects.update_or_create(
            formulaire="antecedents",
            champ=champ,
            libelle=libelle,
            defaults={
                "libelle_en": libelle_en,
                "libelle_ar": libelle_ar,
                "libelle_es": libelle_es,
                "normale": normale,
                "actif": True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0214_add_categorie_translations"),
    ]

    operations = [
        migrations.RunPython(seed_patient_detail_defaults, migrations.RunPython.noop),
    ]
