from django.core.management.base import BaseCommand
from apps.core.models import CatgeorieAntecedent, PhrasierAntecedent, ListeChoix


class Command(BaseCommand):
    help = (
        "Load sample antecedent data for dropdown menus with all language translations"
    )

    def handle(self, *args, **options):
        self.stdout.write("Loading antecedent data with translations...")

        categories_data = [
            {
                "libelle": "Antécédents familiaux",
                "libelle_en": "Family History",
                "libelle_ar": "التاريخ العائلي",
                "libelle_es": "Antecedentes familiares",
            },
            {
                "libelle": "Antécédents médico-chirurgicaux",
                "libelle_en": "Medical-Surgical History",
                "libelle_ar": "التاريخ الطبي والجراحي",
                "libelle_es": "Antecedentes médico-quirúrgicos",
            },
            {
                "libelle": "Antécédents gynécologiques",
                "libelle_en": "Gynecological History",
                "libelle_ar": "التاريخ النسائي",
                "libelle_es": "Antecedentes ginecológicos",
            },
            {
                "libelle": "Allergies",
                "libelle_en": "Allergies",
                "libelle_ar": "الحساسية",
                "libelle_es": "Alergias",
            },
        ]

        categories = {}
        categories_by_libelle = {}
        for cat_data in categories_data:
            cat, created = CatgeorieAntecedent.objects.get_or_create(
                libelle=cat_data["libelle"]
            )
            cat.libelle_en = cat_data["libelle_en"]
            cat.libelle_ar = cat_data["libelle_ar"]
            cat.libelle_es = cat_data["libelle_es"]
            cat.save()
            categories[cat.id] = cat
            categories_by_libelle[cat.libelle] = cat
            if created:
                self.stdout.write(f"  Created category: {cat.libelle} (ID: {cat.id})")
            else:
                self.stdout.write(f"  Updated translations for: {cat.libelle}")

        phrases_data = [
            {
                "categorie": "Antécédents familiaux",
                "libelle": "Diabète",
                "text": "Diabète familial (préciser le type et le degré)",
                "text_en": "Family history of diabetes (specify type and degree)",
                "text_ar": "تاريخ عائلي للسكري (تحديد النوع والدرجة)",
                "text_es": "Diabetes familiar (especificar tipo y grado)",
            },
            {
                "categorie": "Antécédents familiaux",
                "libelle": "Hypertension artérielle",
                "text": "HTA dans la famille",
                "text_en": "Family history of hypertension",
                "text_ar": "ارتفاع ضغط الدم العائلي",
                "text_es": "Hipertensión arterial familiar",
            },
            {
                "categorie": "Antécédents familiaux",
                "libelle": "Cardiopathie",
                "text": "Cardiopathie familiale",
                "text_en": "Family history of heart disease",
                "text_ar": "أمراض القلب العائلية",
                "text_es": "Cardiopatía familiar",
            },
            {
                "categorie": "Antécédents familiaux",
                "libelle": "Cancer du sein",
                "text": "Cancer du sein dans la famille",
                "text_en": "Family history of breast cancer",
                "text_ar": "سرطان الثدي في العائلة",
                "text_es": "Cáncer de mama familiar",
            },
            {
                "categorie": "Antécédents familiaux",
                "libelle": "Cancer de lovaire",
                "text": "Cancer de lovaire dans la famille",
                "text_en": "Family history of ovarian cancer",
                "text_ar": "سرطان المبيض في العائلة",
                "text_es": "Cáncer de ovario familiar",
            },
            {
                "categorie": "Antécédents familiaux",
                "libelle": "Maladie thromboembolique",
                "text": "Antécédent de maladie thromboembolique familiale",
                "text_en": "Family history of thromboembolic disease",
                "text_ar": "تاريخ عائلي للجلطات الوريدية",
                "text_es": "Enfermedad tromboembólica familiar",
            },
            {
                "categorie": "Antécédents médico-chirurgicaux",
                "libelle": "Appendicectomie",
                "text": "Appendicectomie à lâge de ...",
                "text_en": "Appendectomy at age...",
                "text_ar": "استئصال الزائدة في سن...",
                "text_es": "Apendicectomía a la edad de...",
            },
            {
                "categorie": "Antécédents médico-chirurgicaux",
                "libelle": "Chirurgie ovarienne",
                "text": "Chirurgie ovarienne (préciser)",
                "text_en": "Ovarian surgery (specify)",
                "text_ar": "جراحة المبيض (تحديد)",
                "text_es": "Cirugía ovárica (especificar)",
            },
            {
                "categorie": "Antécédents médico-chirurgicaux",
                "libelle": "Myomectomie",
                "text": "Myomectomie",
                "text_en": "Myomectomy",
                "text_ar": "استئصال الورم الليفي",
                "text_es": "Miomectomía",
            },
            {
                "categorie": "Antécédents médico-chirurgicaux",
                "libelle": "Conisation",
                "text": "Conisation",
                "text_en": "Conization",
                "text_ar": "استئصال مخروطي",
                "text_es": "Conización",
            },
            {
                "categorie": "Antécédents médico-chirurgicaux",
                "libelle": "Hystéroscopie",
                "text": "Hystéroscopie diagnostique/opératoire",
                "text_en": "Diagnostic/operative hysteroscopy",
                "text_ar": "تنظير الرحم التشخيصي/الجراحي",
                "text_es": "Histeroscopia diagnóstica/operatoria",
            },
            {
                "categorie": "Antécédents gynécologiques",
                "libelle": "Grossesse extra-utérine",
                "text": "Antécédent de GEU",
                "text_en": "History of ectopic pregnancy",
                "text_ar": "تاريخ حمل خارج الرحم",
                "text_es": "Antecedente de embarazo ectópico",
            },
            {
                "categorie": "Antécédents gynécologiques",
                "libelle": "Kyste ovarien",
                "text": "Kyste ovarien droit/gauche",
                "text_en": "Right/left ovarian cyst",
                "text_ar": "كيس مبيضي أيمن/أيسر",
                "text_es": "Quiste ovárico derecho/izquierdo",
            },
            {
                "categorie": "Antécédents gynécologiques",
                "libelle": "Syndrome des ovaires polykystiques",
                "text": "SOPK",
                "text_en": "Polycystic ovary syndrome (PCOS)",
                "text_ar": "تعدد كيسات المبيض",
                "text_es": "Síndrome de ovario poliquístico",
            },
            {
                "categorie": "Antécédents gynécologiques",
                "libelle": "Endométriose",
                "text": "Endométriose (préciser le stade)",
                "text_en": "Endometriosis (specify stage)",
                "text_ar": "بطانة رحميه مهاجره (تحديد المرحلة)",
                "text_es": "Endometriosis (especificar estadio)",
            },
            {
                "categorie": "Antécédents gynécologiques",
                "libelle": "Ménopause précoce",
                "text": "Ménopause précoce familiale",
                "text_en": "Family history of premature menopause",
                "text_ar": "انقطاع الطمث المبكر العائلي",
                "text_es": "Menopausia precoce familiar",
            },
            {
                "categorie": "Allergies",
                "libelle": "Allergie aux antibiotiques",
                "text": "Allergie à la pénicilline / autres antibiotiques",
                "text_en": "Allergy to penicillin / other antibiotics",
                "text_ar": "حساسية من البنسلين / مضادات حيوية أخرى",
                "text_es": "Alergia a la penicilina / otros antibióticos",
            },
            {
                "categorie": "Allergies",
                "libelle": "Allergie à lodothérapie",
                "text": "Allergie à liode",
                "text_en": "Allergy to iodine",
                "text_ar": "حساسية من اليود",
                "text_es": "Alergia al yodo",
            },
            {
                "categorie": "Allergies",
                "libelle": "Allergie aux antiseptiques",
                "text": "Allergie aux antiseptiques",
                "text_en": "Allergy to antiseptics",
                "text_ar": "حساسية من المطهرات",
                "text_es": "Alergia a los antisépticos",
            },
            {
                "categorie": "Allergies",
                "libelle": "Allergie au latex",
                "text": "Allergie au latex",
                "text_en": "Latex allergy",
                "text_ar": "حساسية من اللاتكس",
                "text_es": "Alergia al látex",
            },
        ]

        for phrase_data in phrases_data:
            phrase, created = PhrasierAntecedent.objects.get_or_create(
                libelle=phrase_data["libelle"],
                defaults={
                    "text": phrase_data["text"],
                    "text_en": phrase_data.get("text_en", phrase_data["text"]),
                    "text_ar": phrase_data.get("text_ar", phrase_data["text"]),
                    "text_es": phrase_data.get("text_es", phrase_data["text"]),
                    "categorie": categories_by_libelle[phrase_data["categorie"]],
                },
            )
            if created:
                self.stdout.write(f"  Created phrase: {phrase_data['libelle']}")
            else:
                phrase.text_en = phrase_data.get("text_en", phrase_data["text"])
                phrase.text_ar = phrase_data.get("text_ar", phrase_data["text"])
                phrase.text_es = phrase_data.get("text_es", phrase_data["text"])
                phrase.save()
                self.stdout.write(
                    f"  Updated translations for: {phrase_data['libelle']}"
                )

        liste_choix_data = [
            {
                "formulaire": "antecedents",
                "champ": "FCV",
                "libelle": "Normal",
                "libelle_en": "Normal",
                "libelle_ar": "طبيعي",
                "libelle_es": "Normal",
                "normale": True,
            },
            {
                "formulaire": "antecedents",
                "champ": "FCV",
                "libelle": "Anormal",
                "libelle_en": "Abnormal",
                "libelle_ar": "غير طبيعي",
                "libelle_es": "Anormal",
            },
            {
                "formulaire": "antecedents",
                "champ": "FCV",
                "libelle": "ASC-H",
                "libelle_en": "ASC-H",
                "libelle_ar": "ASC-H",
                "libelle_es": "ASC-H",
            },
            {
                "formulaire": "antecedents",
                "champ": "FCV",
                "libelle": "ASC-US",
                "libelle_en": "ASC-US",
                "libelle_ar": "ASC-US",
                "libelle_es": "ASC-US",
            },
            {
                "formulaire": "antecedents",
                "champ": "FCV",
                "libelle": "LSIL",
                "libelle_en": "LSIL",
                "libelle_ar": "LSIL",
                "libelle_es": "LSIL",
            },
            {
                "formulaire": "antecedents",
                "champ": "FCV",
                "libelle": "HSIL",
                "libelle_en": "HSIL",
                "libelle_ar": "HSIL",
                "libelle_es": "HSIL",
            },
            {
                "formulaire": "antecedents",
                "champ": "FCV",
                "libelle": "AGC",
                "libelle_en": "AGC",
                "libelle_ar": "AGC",
                "libelle_es": "AGC",
            },
            {
                "formulaire": "antecedents",
                "champ": "FCV",
                "libelle": "Échantillon insatisfaisant",
                "libelle_en": "Unsatisfactory sample",
                "libelle_ar": "عينة غير مرضية",
                "libelle_es": "Muestra insatisfactoria",
            },
            {
                "formulaire": "antecedents",
                "champ": "FCV",
                "libelle": "Néonatalogie positive",
                "libelle_en": "Positive neonatology",
                "libelle_ar": "نيوناتولوجيا إيجابية",
                "libelle_es": "Neonatología positiva",
            },
            {
                "formulaire": "antecedents",
                "champ": "Mammographie",
                "libelle": "Normal",
                "libelle_en": "Normal",
                "libelle_ar": "طبيعي",
                "libelle_es": "Normal",
                "normale": True,
            },
            {
                "formulaire": "antecedents",
                "champ": "Mammographie",
                "libelle": "Anormal",
                "libelle_en": "Abnormal",
                "libelle_ar": "غير طبيعي",
                "libelle_es": "Anormal",
            },
            {
                "formulaire": "antecedents",
                "champ": "Mammographie",
                "libelle": "Calcifications",
                "libelle_en": "Calcifications",
                "libelle_ar": "تكلسات",
                "libelle_es": "Calcificaciones",
            },
            {
                "formulaire": "antecedents",
                "champ": "Mammographie",
                "libelle": "Masse",
                "libelle_en": "Mass",
                "libelle_ar": "كتلة",
                "libelle_es": "Masa",
            },
            {
                "formulaire": "antecedents",
                "champ": "Mammographie",
                "libelle": "Distorsion architecturale",
                "libelle_en": "Architectural distortion",
                "libelle_ar": "تشوه معماري",
                "libelle_es": "Distorsión arquitectónica",
            },
            {
                "formulaire": "antecedents",
                "champ": "Mammographie",
                "libelle": "Asymétrie",
                "libelle_en": "Asymmetry",
                "libelle_ar": "عدم تماثل",
                "libelle_es": "Asimetría",
            },
            {
                "formulaire": "antecedents",
                "champ": "Mammographie",
                "libelle": "BI-RADS 0",
                "libelle_en": "BI-RADS 0",
                "libelle_ar": "BI-RADS 0",
                "libelle_es": "BI-RADS 0",
            },
            {
                "formulaire": "antecedents",
                "champ": "Mammographie",
                "libelle": "BI-RADS 3",
                "libelle_en": "BI-RADS 3 - Probably Benign",
                "libelle_ar": "BI-RADS 3 - حميد على الأرجح",
                "libelle_es": "BI-RADS 3 - Probablemente benigno",
            },
            {
                "formulaire": "antecedents",
                "champ": "Mammographie",
                "libelle": "BI-RADS 4",
                "libelle_en": "BI-RADS 4 - Suspicious",
                "libelle_ar": "BI-RADS 4 - مشبوه",
                "libelle_es": "BI-RADS 4 - Sospechoso",
            },
            {
                "formulaire": "antecedents",
                "champ": "Mammographie",
                "libelle": "BI-RADS 5",
                "libelle_en": "BI-RADS 5 - Highly Suspicious",
                "libelle_ar": "BI-RADS 5 - مشبوه جداً",
                "libelle_es": "BI-RADS 5 - Altamente sospechoso",
            },
            {
                "formulaire": "antecedents",
                "champ": "Echo Mammaire",
                "libelle": "Normal",
                "libelle_en": "Normal",
                "libelle_ar": "طبيعي",
                "libelle_es": "Normal",
                "normale": True,
            },
            {
                "formulaire": "antecedents",
                "champ": "Echo Mammaire",
                "libelle": "Anormal",
                "libelle_en": "Abnormal",
                "libelle_ar": "غير طبيعي",
                "libelle_es": "Anormal",
            },
            {
                "formulaire": "antecedents",
                "champ": "Echo Mammaire",
                "libelle": "Kyste simple",
                "libelle_en": "Simple cyst",
                "libelle_ar": "كيس بسيط",
                "libelle_es": "Quiste simple",
            },
            {
                "formulaire": "antecedents",
                "champ": "Echo Mammaire",
                "libelle": "Kyste complexe",
                "libelle_en": "Complex cyst",
                "libelle_ar": "كيس معقد",
                "libelle_es": "Quiste complejo",
            },
            {
                "formulaire": "antecedents",
                "champ": "Echo Mammaire",
                "libelle": "Fibroadénome",
                "libelle_en": "Fibroadenoma",
                "libelle_ar": "ورم ليفية",
                "libelle_es": "Fibroadenoma",
            },
            {
                "formulaire": "antecedents",
                "champ": "Echo Mammaire",
                "libelle": "Nodule solide",
                "libelle_en": "Solid nodule",
                "libelle_ar": "عقدة صلبة",
                "libelle_es": "Nódulo sólido",
            },
            {
                "formulaire": "antecedents",
                "champ": "Echo Mammaire",
                "libelle": "Dilatation canalaire",
                "libelle_en": "Ductal dilatation",
                "libelle_ar": "توسع قناة",
                "libelle_es": "Dilatación ductal",
            },
            {
                "formulaire": "antecedents",
                "champ": "Echo Mammaire",
                "libelle": "Lipome",
                "libelle_en": "Lipoma",
                "libelle_ar": "ورم شحمي",
                "libelle_es": "Lipoma",
            },
        ]

        for choix_data in liste_choix_data:
            choix, created = ListeChoix.objects.get_or_create(
                formulaire=choix_data["formulaire"],
                champ=choix_data["champ"],
                libelle=choix_data["libelle"],
                defaults={
                    "libelle_en": choix_data.get("libelle_en", ""),
                    "libelle_ar": choix_data.get("libelle_ar", ""),
                    "libelle_es": choix_data.get("libelle_es", ""),
                    "normale": choix_data.get("normale", False),
                },
            )
            if created:
                self.stdout.write(
                    f"  Created ListeChoix: {choix_data['libelle']} ({choix_data['champ']})"
                )
            else:
                choix.libelle_en = choix_data.get("libelle_en", "")
                choix.libelle_ar = choix_data.get("libelle_ar", "")
                choix.libelle_es = choix_data.get("libelle_es", "")
                choix.normale = choix_data.get("normale", False)
                choix.save()
                self.stdout.write(
                    f"  Updated translations for: {choix_data['libelle']} ({choix_data['champ']})"
                )

        self.stdout.write(
            self.style.SUCCESS("Successfully loaded antecedent data with translations")
        )
