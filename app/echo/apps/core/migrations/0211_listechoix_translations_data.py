from django.db import migrations

# Translations: {pk: (en, ar, es)}
TRANSLATIONS = {
    # === antecedents: FCV ===
    1:  ('ASC-US smear', 'تلطيخ ASC-US', 'Frotis ASC-US'),
    2:  ('Incomplete smear', 'تلطيخ غير مكتمل', 'Frotis incompleto'),
    3:  ('Normal smear', 'تلطيخ طبيعي', 'Frotis normal'),
    4:  ('Normal smear - results not reviewed', 'تلطيخ طبيعي - النتائج لم تُراجع', 'Frotis normal - resultados no revisados'),
    5:  ('Pathological smear', 'تلطيخ مرضي', 'Frotis patológico'),
    # === antecedents: Mammographie ===
    6:  ('Requested', 'مطلوب', 'Solicitado'),
    7:  ('Normal mammogram', 'تصوير شعاعي للثدي طبيعي', 'Mamografía normal'),
    8:  ('Pathological mammogram', 'تصوير شعاعي للثدي مرضي', 'Mamografía patológica'),
    9:  ('Right breast ACR 2 Left breast ACR 3', 'الثدي الأيمن ACR 2 الثدي الأيسر ACR 3', 'Mama derecha ACR 2 Mama izquierda ACR 3'),
    # === antecedents: Echo Mammaire ===
    10: ('ACR 2', 'ACR 2', 'ACR 2'),
    11: ('Normal', 'طبيعي', 'Normal'),
    12: ('Pathological', 'مرضي', 'Patológico'),
    13: ('Adenofibroma', 'ورم ليفي غدي', 'Adenofibroma'),
    14: ('Retroareolar ectasia', 'توسع خلف الهالة', 'Ectasia retroareolar'),
    15: ('Cyst', 'كيس', 'Quiste'),
    # === consultation_gynecologique: motif_consultation ===
    68: ('IUD removal', 'إزالة اللولب', 'Retiro de DIU'),
    69: ('Implant removal', 'إزالة الغرسة', 'Retiro de implante'),
    70: ('Advice', 'استشارة', 'Consejo'),
    71: ('Review of episiotomy scar', 'مراجعة ندبة الفصل', 'Revisión de cicatriz de episiotomía'),
    72: ('Post-miscarriage check-up', 'متابعة ما بعد الإجهاض', 'Evaluación post-aborto'),
    73: ('Postnatal consultation', 'استشارة ما بعد الولادة', 'Consulta postnatal'),
    74: ('Pre-conception consultation', 'استشارة ما قبل الحمل', 'Consulta preconcepcional'),
    75: ('Contraception', 'منع الحمل', 'Anticoncepción'),
    76: ('Emergency contraception', 'منع الحمل الطارئ', 'Anticoncepción de emergencia'),
    77: ('Check-up', 'مراجعة', 'Control'),
    78: ('Routine screening', 'فحص روتيني', 'Cribado rutinario'),
    79: ('IUD removal and insertion', 'إزالة وتركيب اللولب', 'Retirada e inserción de DIU'),
    80: ('Desire for pregnancy', 'رغبة في الحمل', 'Deseo de embarazo'),
    81: ('Pelvic pain', 'آلام الحوض', 'Dolor pélvico'),
    82: ('Voluntary termination of pregnancy', 'إنهاء الحمل الطوعي', 'Interrupción voluntaria del embarazo'),
    83: ('Vaginal discharge', 'إفرازات مهبلية', 'Leucorrea'),
    84: ('Metrorrhagia', 'نزيف الرحم', 'Metrorragia'),
    85: ('First trimester metrorrhagia', 'نزيف الرحم في الثلث الأول', 'Metrorragia del primer trimestre'),
    86: ('Initiation of hypofertility treatment', 'بدء علاج قصور الخصوبة', 'Inicio de tratamiento por hipofertilidad'),
    87: ('Candidiasis', 'داء المبيضات', 'Candidiasis'),
    88: ('Implant insertion', 'تركيب الغرسة', 'Inserción de implante'),
    89: ('IUD insertion', 'تركيب اللولب', 'Inserción de DIU'),
    90: ('Complementary exam result', 'نتيجة فحص تكميلي', 'Resultado de examen complementario'),
    91: ('IUD removal', 'إزالة اللولب', 'Retirada del DIU'),
    92: ('Routine follow-up', 'متابعة روتينية', 'Seguimiento rutinario'),
    93: ('Annual gynecological follow-up and pill renewal', 'متابعة نسائية سنوية وتجديد الحبوب', 'Seguimiento ginecológico anual y renovación de píldora'),
    94: ('Summary', 'ملخص', 'Síntesis'),
    95: ('Emergency', 'طوارئ', 'Urgencia'),
    96: ('Other', 'أخرى', 'Otros'),
    # === consultation_gynecologique: partenaire ===
    97: ('Single', 'واحد', 'Único'),
    98: ('Multiple', 'متعددون', 'Múltiples'),
    99: ('Regular', 'منتظم', 'Regular'),
    # === consultation_gynecologique: cycles ===
    100: ('Regular', 'منتظمة', 'Regulares'),
    101: ('Irregular', 'غير منتظمة', 'Irregulares'),
    # === consultation_gynecologique: syndrome_premenstruel ===
    102: ('Absent', 'غائب', 'Ausente'),
    103: ('Present', 'موجود', 'Presente'),
    # === consultation_gynecologique: abondance ===
    104: ('Amenorrhea', 'انقطاع الطمث', 'Amenorrea'),
    105: ('Heavy', 'غزيرة', 'Abundante'),
    106: ('Normal', 'طبيعية', 'Normal'),
    107: ('Light', 'قليلة', 'Escasa'),
    108: ('Very heavy', 'غزيرة جداً', 'Muy abundante'),
    # === consultation_gynecologique: douleur ===
    109: ('Absent', 'غائب', 'Ausente'),
    110: ('Severe', 'شديد', 'Intenso'),
    111: ('Tolerable', 'محتمل', 'Tolerable'),
    # === consultation_gynecologique: mode_contraception ===
    112: ('Copper IUD', 'لولب نحاسي', 'DIU de cobre'),
    113: ('Hormonal IUD', 'لولب هرموني', 'DIU hormonal'),
    114: ('Progestogen implant', 'غرسة بروجستين', 'Implante progestágeno'),
    115: ('Combined oral', 'حبوب مركبة', 'Oral combinada'),
    116: ('Progestogen only pill', 'حبوب بروجستين فقط', 'Píldora solo progestágeno'),
    117: ('No hormonal contraception', 'بدون حبوب منع الحمل', 'Sin anticonceptivos hormonales'),
    118: ('Local', 'موضعي', 'Local'),
    119: ('None', 'لا شيء', 'Ninguno'),
    120: ('Micro-progestogen', 'ميكرو بروجستين', 'Microprogestágeno'),
    121: ('Natural', 'طبيعي', 'Natural'),
    # === consultation_gynecologique: observance ===
    122: ('Good', 'جيدة', 'Buena'),
    123: ('Variable', 'متفاوتة', 'Variable'),
    124: ('Poor', 'سيئة', 'Mala'),
    # === consultation_gynecologique: satisfaction ===
    125: ('Good', 'جيدة', 'Buena'),
    126: ('Poor', 'سيئة', 'Mala'),
    127: ('Average', 'متوسطة', 'Regular'),
    128: ('Very good', 'جيدة جداً', 'Muy buena'),
    # === consultation_gynecologique: effets_indesirables ===
    129: ('Acne', 'حب الشباب', 'Acné'),
    130: ('Amenorrhea', 'انقطاع الطمث', 'Amenorrea'),
    131: ('Headaches', 'صداع', 'Cefaleas'),
    132: ('Recurrent candidiasis', 'داء المبيضات المتكرر', 'Candidiasis recurrente'),
    133: ('Weight gain', 'زيادة الوزن', 'Aumento de peso'),
    134: ('No notable side effects', 'لا آثار جانبية ملحوظة', 'Sin efectos secundarios destacables'),
    135: ('Heavier periods', 'دورة شهرية أكثر غزارة', 'Reglas más abundantes'),
    # === consultation_gynecologique: seins ===
    136: ('Normal examination', 'فحص طبيعي', 'Examen normal'),
    137: ('Normal examination + lying position', 'فحص طبيعي + وضعية الاستلقاء', 'Examen normal + posición tumbada'),
    # === consultation_gynecologique: examen_sous_speculum ===
    138: ('Normal', 'طبيعي', 'Normal'),
    139: ('IUD threads visible', 'خيوط اللولب مرئية', 'Hilos del DIU visibles'),
    140: ('Ectropion', 'تقلص عنق الرحم', 'Ectropión'),
    141: ('White discharge', 'إفرازات بيضاء', 'Leucorrea blanquecina'),
    142: ('Healthy-looking cervix', 'عنق رحم طبيعي المظهر', 'Cuello de aspecto sano'),
    143: ('Physiological discharge', 'إفرازات طبيعية', 'Flujo fisiológico'),
    144: ('Pathological-looking cervix', 'عنق رحم مرضي المظهر', 'Cuello de aspecto patológico'),
    # === consultation_gynecologique: leuco ===
    145: ('Abundant', 'وفيرة', 'Abundantes'),
    146: ('Coloured', 'ملونة', 'Coloreadas'),
    147: ('Malodorous', 'كريهة الرائحة', 'Malolientes'),
    148: ('Physiological', 'طبيعية', 'Fisiológicas'),
    149: ('Reddish', 'محمرة', 'Rojizas'),
    150: ('Greenish', 'مخضرة', 'Verdosas'),
    # === consultation_gynecologique: tv ===
    151: ('Free lateral fornices', 'قِبَب جانبية حرة', 'Fondos de saco libres'),
    152: ('Ovarian cyst', 'كيس مبيضي', 'Quiste ovárico'),
    153: ('Not performed', 'لم يُجرَ', 'No realizado'),
    154: ('Normal', 'طبيعي', 'Normal'),
    155: ('Enlarged myomatous uterus', 'رحم ليفي متضخم', 'Útero miomatoso agrandado'),
    # === consultation_colposcopie: indications_colposcopie ===
    156: ('AGUS', 'AGUS', 'AGUS'),
    157: ('ASCUS', 'ASCUS', 'ASCUS'),
    158: ('Post-conisation check-up', 'متابعة ما بعد الاستئصال المخروطي', 'Control tras conización'),
    159: ('HSIL', 'HSIL', 'HSIL'),
    160: ('LSIL', 'LSIL', 'LSIL'),
    # === consultation_colposcopie: test_hpv ===
    161: ('Positive', 'إيجابي', 'Positivo'),
    162: ('Negative', 'سلبي', 'Negativo'),
    # === consultation_colposcopie: examen_sans_preparation ===
    163: ('Unremarkable', 'لا شيء يُذكر', 'Sin particularidades'),
    # === consultation_colposcopie: acide_acetique ===
    164: ('Endocervical TZ', 'منطقة التحول داخل عنق الرحم', 'ZT endocervical'),
    165: ('Exocervical TZ', 'منطقة التحول خارج عنق الرحم', 'ZT exocervical'),
    166: ('TZ not seen', 'منطقة التحول غير مرئية', 'ZT no vista'),
    167: ('TZ OS', 'منطقة التحول OE', 'ZT OE'),
    # === consultation_colposcopie: tag ===
    168: ('1', '1', '1'),
    169: ('2', '2', '2'),
    170: ('N and S', 'ن و ص', 'N y S'),
    # === consultation_colposcopie: localisation (hours) ===
    171: ('1 o\'clock', '1 ساعة', '1 H'),
    172: ('2 o\'clock', '2 ساعة', '2 H'),
    173: ('3 o\'clock', '3 ساعة', '3 H'),
    174: ('4 o\'clock', '4 ساعة', '4 H'),
    175: ('5 o\'clock', '5 ساعة', '5 H'),
    176: ('6 o\'clock', '6 ساعة', '6 H'),
    177: ('7 o\'clock', '7 ساعة', '7 H'),
    178: ('8 o\'clock', '8 ساعة', '8 H'),
    179: ('9 o\'clock', '9 ساعة', '9 H'),
    180: ('10 o\'clock', '10 ساعة', '10 H'),
    181: ('11 o\'clock', '11 ساعة', '11 H'),
    182: ('12 o\'clock', '12 ساعة', '12 H'),
    # === consultation_colposcopie: lugol ===
    183: ('No iodo-negative zone', 'لا توجد منطقة سالبة لليود', 'Ausencia de zona yodo-negativa'),
    184: ('Iodo-negative zone', 'منطقة سالبة لليود', 'Zona yodo-negativa'),
    # === consultation_echo_pelvienne: titre_echo_pelvienne ===
    185: ('Pelvic ultrasound', 'إيكوغرافيا حوضية', 'Ecografía pélvica'),
    186: ('Ovulation monitoring', 'مراقبة الإباضة', 'Monitoreo de ovulación'),
    187: ('Ovarian reserve', 'الاحتياطي المبيضي', 'Reserva ovárica'),
    188: ('Hysterosonography', 'تصوير تجويف الرحم بالموجات فوق الصوتية', 'Histerosalpingografía'),
    189: ('Pelvic floor assessment', 'تقييم قاع الحوض', 'Evaluación del suelo pélvico'),
    190: ('Pregnancy location', 'تحديد موقع الحمل', 'Localización del embarazo'),
    191: ('Uterine cavity check', 'التحقق من فراغ تجويف الرحم', 'Verificación de vacuidad uterina'),
    # === consultation_echo_pelvienne: position_uterus ===
    192: ('Anteverted and anteflexed', 'مائل للأمام ومنثن للأمام', 'Anteverso y anteflexo'),
    193: ('Retroverted and retroflexed', 'مائل للخلف ومنثن للخلف', 'Retroverso y retroflexo'),
    194: ('Anteverted', 'مائل للأمام', 'Anteverso'),
    195: ('Retroverted', 'مائل للخلف', 'Retroverso'),
    196: ('Axial', 'محوري', 'Axial'),
    197: ('Deviated to the right', 'منحرف لليمين', 'Lateralizado a la derecha'),
    198: ('Deviated to the left', 'منحرف لليسار', 'Lateralizado a la izquierda'),
    199: ('Subtotal hysterectomy', 'استئصال الرحم الجزئي', 'Histerectomía subtotal'),
    200: ('Total hysterectomy', 'استئصال الرحم الكلي', 'Histerectomía total'),
    201: ('Uterine aplasia', 'رتق الرحم', 'Aplasia uterina'),
    202: ('Uterus not seen', 'الرحم غير مرئي', 'Útero no visto'),
    203: ('Variable', 'متغير', 'Variable'),
    # === consultation_echo_pelvienne: lateralisation ===
    204: ('Right', 'يمين', 'Derecha'),
    205: ('Left', 'يسار', 'Izquierda'),
    206: ('None', 'لا شيء', 'Ninguna'),
    # === consultation_echo_pelvienne: volume_uterin_commentaire ===
    207: ('Normal volume', 'حجم طبيعي', 'Volumen normal'),
    208: ('Increased volume', 'حجم متزايد', 'Volumen aumentado'),
    209: ('Decreased volume', 'حجم منخفض', 'Volumen disminuido'),
    210: ('Large (multiparity)', 'كبير (تعدد الولادات)', 'Grande (multiparidad)'),
    # === consultation_echo_pelvienne: asymetrie ===
    211: ('In favour of posterior wall', 'لصالح الجدار الخلفي', 'A favor de la pared posterior'),
    212: ('In favour of anterior wall', 'لصالح الجدار الأمامي', 'A favor de la pared anterior'),
    213: ('No asymmetry', 'لا توجد عدم تماثل', 'Sin asimetría'),
    # === consultation_echo_pelvienne: mobilite ===
    214: ('Reduced mobility', 'تنقل محدود', 'Movilidad reducida'),
    215: ('Fixed uterus', 'رحم ثابت', 'Útero fijo'),
    216: ('Mobile uterus', 'رحم متحرك', 'Útero móvil'),
    # === consultation_echo_pelvienne: structures ===
    217: ('Adenomyosis', 'داء بطانة الرحم العضلي', 'Adenomiosis'),
    218: ('Diffuse fibromatosis', 'ليفاوية منتشرة', 'Fibromatosis difusa'),
    219: ('Heterogeneous myometrium', 'عضل رحم غير متجانس', 'Miometrio heterogéneo'),
    220: ('Homogeneous myometrium', 'عضل رحم متجانس', 'Miometrio homogéneo'),
    221: ('Multifibromatous', 'ليفاوي متعدد', 'Multifibromatoso'),
    # === consultation_echo_pelvienne: cavite ===
    222: ('3D adenomyosis', 'داء بطانة الرحم العضلي ثلاثي الأبعاد', 'Adenomiosis 3D'),
    223: ('Normal-looking hysterotomy scar', 'ندبة بضع الرحم طبيعية المظهر', 'Cicatriz de histerotomía de aspecto normal'),
    224: ('Contains vascularised ovular remnants', 'تحتوي على بقايا بيضية مُوعاة', 'Contiene restos ovulares vascularizados'),
    225: ('Contains echogenic image = polyp', 'تحتوي على صورة صوتية = ورم ليفي', 'Contiene imagen ecogénica = pólipo'),
    226: ('Deformed by synechia', 'مشوهة بالتصاقات', 'Deformada por sinequia'),
    227: ('Normal appearance', 'مظهر طبيعي', 'Aspecto normal'),
    228: ('Normal appearance on 3D reconstruction', 'مظهر طبيعي في إعادة البناء ثلاثي الأبعاد', 'Aspecto normal en reconstrucción 3D'),
    229: ('Deformed at the base by a septal remnant (arcuate fundus)', 'مشوهة في القاعدة بقسيم بقائي (قاع مقوس)', 'Deformada en el fondo por un residuo de tabique'),
    230: ('Deformed by adenomyosis', 'مشوهة بداء بطانة الرحم العضلي', 'Deformada por adenomiosis'),
    231: ('Deformed by a fibroid', 'مشوهة بورم ليفي', 'Deformada por un mioma'),
    232: ('Tubular cavity', 'تجويف أنبوبي', 'Cavidad tubular'),
    233: ('Isthmocele', 'قيلة برزخية', 'Istmocele'),
    234: ('Bayonet-shaped cavity', 'تجويف على شكل حربة', 'Cavidad en bayoneta'),
    235: ('Cannot be evaluated', 'لا يمكن تقييمها', 'No puede evaluarse'),
    236: ('No retention', 'لا توجد احتباس', 'Sin retención'),
    # === consultation_echo_pelvienne: malformation ===
    237: ('U0 Normal', 'U0 طبيعي', 'U0 Normal'),
    238: ('U1a (T-shaped)', 'U1a (على شكل T)', 'U1a (en T)'),
    239: ('U1b (infantile)', 'U1b (طفولي)', 'U1b (infantil)'),
    240: ('U1c (arcuate fundus)', 'U1c (قاع مقوس)', 'U1c (fondo arqueado)'),
    241: ('U1c (moderate variants)', 'U1c (تنوعات معتدلة)', 'U1c (variantes moderadas)'),
    242: ('U2a (partial septum)', 'U2a (حاجز جزئي)', 'U2a (tabique parcial)'),
    243: ('U2b (complete septum)', 'U2b (حاجز كامل)', 'U2b (tabique completo)'),
    244: ('U3a (partial bicornuate)', 'U3a (مزدوج جزئي)', 'U3a (bicorne parcial)'),
    245: ('U3b (complete bicornuate)', 'U3b (مزدوج كامل)', 'U3b (bicorne completo)'),
    246: ('U3c (bicornuate with septum)', 'U3c (مزدوج مع حاجز)', 'U3c (bicorne con tabique)'),
    247: ('U4a (right hemi-uterus with rudimentary cavity)', 'U4a (نصف رحم أيمن مع تجويف بدائي)', 'U4a (hemi-útero derecho con cavidad rudimentaria)'),
    248: ('U4a (left hemi-uterus with rudimentary cavity)', 'U4a (نصف رحم أيسر مع تجويف بدائي)', 'U4a (hemi-útero izquierdo con cavidad rudimentaria)'),
    249: ('U4b (right hemi-uterus without left remnant)', 'U4b (نصف رحم أيمن بدون بقايا يسرى)', 'U4b (hemi-útero derecho sin remanente izquierdo)'),
    250: ('U4b (right hemi-uterus without rudimentary cavity)', 'U4b (نصف رحم أيمن بدون تجويف بدائي)', 'U4b (hemi-útero derecho sin cavidad rudimentaria)'),
    251: ('U4b (left hemi-uterus without rudimentary cavity)', 'U4b (نصف رحم أيسر بدون تجويف بدائي)', 'U4b (hemi-útero izquierdo sin cavidad rudimentaria)'),
    252: ('U4b (left hemi-uterus without right remnant)', 'U4b (نصف رحم أيسر بدون بقايا يمنى)', 'U4b (hemi-útero izquierdo sin remanente derecho)'),
    253: ('U5a (uterine aplasia with right rudimentary horn)', 'U5a (رتق الرحم مع قرن أيمن بدائي)', 'U5a (aplasia uterina con cuerno rudimentario derecho)'),
    254: ('U5a (uterine aplasia with left rudimentary horn)', 'U5a (رتق الرحم مع قرن أيسر بدائي)', 'U5a (aplasia uterina con cuerno rudimentario izquierdo)'),
    255: ('U5b (uterine aplasia with right remnant)', 'U5b (رتق الرحم مع بقايا يمنى)', 'U5b (aplasia uterina con remanente derecho)'),
    256: ('U5b (uterine aplasia with left remnant)', 'U5b (رتق الرحم مع بقايا يسرى)', 'U5b (aplasia uterina con remanente izquierdo)'),
    257: ('U5b (uterine aplasia without remnant)', 'U5b (رتق الرحم بدون بقايا)', 'U5b (aplasia uterina sin remanente)'),
    258: ('U5c (unclassifiable)', 'U5c (غير قابل للتصنيف)', 'U5c (no clasificable)'),
    # === consultation_echo_pelvienne: ligne_cavitaire ===
    259: ('Regular', 'منتظمة', 'Regular'),
    260: ('Irregular', 'غير منتظمة', 'Irregular'),
    # === consultation_echo_pelvienne: type_dispositif_intra_uterin ===
    261: ('Copper IUD', 'لولب نحاسي', 'DIU de cobre'),
    262: ('Mirena', 'ميرينا', 'Mirena'),
    # === consultation_echo_pelvienne: localisation_dispositif_intra_uterin ===
    263: ('Endocavitary in normal position', 'داخل التجويف في وضع طبيعي', 'Endocavitario en posición normal'),
    264: ('Endocavitary tilted', 'داخل التجويف مائل', 'Endocavitario inclinado'),
    265: ('Cervico-isthmic', 'عنقي-برزخي', 'Cervicoisítmico'),
    266: ('Intramyometrial', 'داخل عضل الرحم', 'Intramimetrial'),
    267: ('Sub-serosal', 'تحت المصلية', 'Subseroso'),
    268: ('In the omentum', 'في الثرب', 'En el epiplón'),
    # === consultation_echo_pelvienne: anomalies_dispositif_intra_uterin ===
    269: ('No notable anomaly', 'لا توجد تشوهات ملحوظة', 'Sin anomalías destacables'),
    270: ('One arm not deployed', 'ذراع واحدة غير مفتوحة', 'Un brazo no desplegado'),
    271: ('Two arms not deployed', 'ذراعان غير مفتوحتان', 'Dos brazos no desplegados'),
    272: ('One perforating arm', 'ذراع واحدة ثاقبة', 'Un brazo perforante'),
    273: ('Two perforating arms', 'ذراعان ثاقبتان', 'Dos brazos perforantes'),
    # === consultation_echo_pelvienne: endometre_visualisation ===
    274: ('Seen along its full length', 'مرئي على كامل طوله', 'Visto en toda su longitud'),
    275: ('Hydrometra', 'احتباس مائي بالرحم', 'Hidrometra'),
    276: ('Hydrosonography', 'صونوغرافيا مائية', 'Hidrosonografía'),
    277: ('Obscured by uterine position', 'محجوب بوضعية الرحم', 'Dificultado por posición uterina'),
    278: ('Obscured by fibroids', 'محجوب بالأورام الليفية', 'Dificultado por miomas'),
    279: ('Endometrium difficult to visualise', 'صعوبة في رؤية بطانة الرحم', 'Endometrio difícil de visualizar'),
    # === consultation_echo_pelvienne: endometre_echogenicite ===
    280: ('Three-line pattern', 'نمط ثلاثي الخطوط', 'Patrón trilaminar'),
    281: ('Hyperechoic', 'شديد الصدى', 'Hiperecogénico'),
    282: ('Hypoechoic', 'ضعيف الصدى', 'Hipoecogénico'),
    283: ('Isoechoic', 'متساوي الصدى', 'Isoecogénico'),
    284: ('Non-uniform with regular cystic images', 'غير متجانس مع صور كيسية منتظمة', 'No uniforme con imágenes quísticas regulares'),
    285: ('Non-uniform with irregular cystic images', 'غير متجانس مع صور كيسية غير منتظمة', 'No uniforme con imágenes quísticas irregulares'),
    286: ('Non-uniform without cystic images', 'غير متجانس بدون صور كيسية', 'No uniforme sin imágenes quísticas'),
    # === consultation_echo_pelvienne: col_aspect ===
    287: ('Normal', 'طبيعي', 'Normal'),
    288: ('Nabothian cysts', 'أكياس نابوث', 'Quistes de Naboth'),
    289: ('Normal residual cervix appearance', 'مظهر طبيعي لعنق الرحم المتبقي', 'Aspecto normal del cuello restante'),
    290: ('Enlarged', 'متضخم', 'Agrandado'),
    291: ('Dilated cervical canal', 'قناة عنق الرحم متسعة', 'Canal cervical dilatado'),
    292: ('Fluid collection (orifice stenosis)', 'تجمع سائل (تضيق الفوهة)', 'Colección líquida (estenosis orificiar)'),
    293: ('Shortened after conisation', 'مختصر بعد الاستئصال المخروطي', 'Acortado tras conización'),
    294: ('Not visualised', 'غير مرئي', 'No visualizado'),
    295: ('C0 (normal cervix)', 'C0 (عنق رحم طبيعي)', 'C0 (cuello normal)'),
    296: ('C1 (septate cervix)', 'C1 (عنق رحم حاجزي)', 'C1 (cuello tabicado)'),
    297: ('C2 (double cervix)', 'C2 (عنق رحم مزدوج)', 'C2 (cuello doble)'),
    298: ('C3 (right unilateral cervical aplasia)', 'C3 (رتق عنق الرحم الأحادي الجانب الأيمن)', 'C3 (aplasia cervical unilateral derecha)'),
    299: ('C4 (cervical aplasia)', 'C4 (رتق عنق الرحم)', 'C4 (aplasia cervical)'),
    300: ('Usual endocervix', 'عنق الرحم الداخلي المعتاد', 'Endocérvix habitual'),
    301: ('Cervical mucus', 'مخاط عنق الرحم', 'Moco cervical'),
    # === consultation_echo_pelvienne: col_vascularisation ===
    302: ('Weak', 'ضعيفة', 'Débil'),
    303: ('Single pedicle suggesting a polyp', 'قاعدة وحيدة توحي بورم', 'Pedículo único que sugiere un pólipo'),
    304: ('Diffuse and increased vascularisation', 'تروية دموية منتشرة ومتزايدة', 'Vascularización difusa y aumentada'),
    # === consultation_echo_pelvienne: ovaire_visibilite ===
    305: ('Visible', 'مرئي', 'Visible'),
    # === consultation_echo_pelvienne: ovaire_aspect ===
    306: ('Normal appearance', 'مظهر طبيعي', 'Aspecto normal'),
    307: ('Ovarian cyst', 'كيس مبيضي', 'Quiste ovárico'),
    308: ('Moderate volume', 'حجم معتدل', 'Volumen moderado'),
    309: ('Multifollicular', 'متعدد الجُريبات', 'Multifollicular'),
    310: ('Not visualised', 'غير مرئي', 'No visualizado'),
    311: ('Polycystic', 'متعدد الأكياس', 'Poliquístico'),
    312: ('Corpus luteum', 'الجسم الأصفر', 'Cuerpo lúteo'),
    313: ('Pauci-follicular', 'قليل الجُريبات', 'Paucifolicular'),
    314: ('Appearance of functional follicular cyst', 'مظهر كيس جُريبي وظيفي', 'Aspecto de quiste folicular funcional'),
    315: ('Appearance of haemorrhagic corpus luteum cyst', 'مظهر كيس الجسم الأصفر النزفي', 'Aspecto de quiste hemorrágico del cuerpo lúteo'),
    316: ('Abnormal', 'غير طبيعي', 'Anormal'),
    317: ('Macropolycystic appearance', 'مظهر متعدد الأكياس الكبيرة', 'Aspecto macropoliquístico'),
    318: ('Functional (RB)', 'وظيفي (RB)', 'Funcional (RB)'),
    319: ('Multiple functional (RB)', 'متعدد وظيفي (RB)', 'Múltiples funcionales (RB)'),
    320: ('Macropolycystic appearance', 'مظهر متعدد الأكياس الكبيرة', 'Aspecto macropoliquístico'),
    321: ('Bilateral oophorectomy', 'استئصال المبيضين الثنائي', 'Ooforectomía bilateral'),
    322: ('Right oophorectomy', 'استئصال المبيض الأيمن', 'Ooforectomía derecha'),
    323: ('Left oophorectomy', 'استئصال المبيض الأيسر', 'Ooforectomía izquierda'),
    324: ('Adnexectomy', 'استئصال الملحقات', 'Anexectomía'),
    325: ('Normally multifollicular (RB)', 'متعدد الجُريبات طبيعياً (RB)', 'Normalmente multifollicular (RB)'),
    326: ('Partially visible', 'مرئي جزئياً', 'Parcialmente visible'),
    327: ('Stimulated ovaries', 'مبايض مُحفَّزة', 'Ovarios estimulados'),
    # === consultation_echo_pelvienne: ovaire_mobilite ===
    328: ('Fixed', 'ثابت', 'Fijo'),
    # === consultation_echo_pelvienne: ovaire_accessibilite ===
    329: ('Accessible', 'يمكن الوصول إليه', 'Accesible'),
    330: ('Not accessible', 'لا يمكن الوصول إليه', 'No accesible'),
    # === consultation_echo_pelvienne: ovaire_follicules ===
    331: ('Normofollicular', 'عادي الجُريبات', 'Normofolicular'),
    332: ('No detectable follicle', 'لا جُريبات مكتشفة', 'Sin folículo detectable'),
    333: ('Number of follicles', 'عدد الجُريبات', 'Número de folículos'),
    # === consultation_echo_pelvienne: cul_de_sac_latero ===
    334: ('Free lateral fornices', 'قِبَب جانبية حرة', 'Fondos de saco laterales libres'),
    335: ('Right', 'يمين', 'Derecho'),
    336: ('Right and left', 'يمين ويسار', 'Derecho e izquierdo'),
    # === consultation_echo_pelvienne: adenomyose ===
    568: ('Wall asymmetry', 'عدم تناسق الجدران', 'Asimetría de paredes'),
    569: ('Myometrial cysts (crypts)', 'أكياس عضل الرحم (الخبايا)', 'Quistes miometriales (criptas)'),
    570: ('Hyperechoic patches', 'بقع شديدة الصدى', 'Manchas hiperecogénicas'),
    571: ('Shadowing (rain in the forest pattern)', 'ظلال صوتية (نمط المطر في الغابة)', 'Sombras acústicas (patrón lluvia en el bosque)'),
    572: ('Sub-endometrial hyperechoic streaks or buds', 'خطوط أو براعم تحت بطانة الرحم شديدة الصدى', 'Estrías o yemas subendometriales hiperecogénicas'),
    573: ('Transverse vascularisation (comb pattern)', 'تروية دموية عرضية (نمط المشط)', 'Vascularización transversa (patrón en peine)'),
    574: ('Irregular junctional zone', 'منطقة وصل غير منتظمة', 'Zona de unión irregular'),
    575: ('Interrupted junctional zone', 'منطقة وصل منقطعة', 'Zona de unión interrumpida'),
    # === consultation_echo_pelvienne: adenomyose_conclusion ===
    603: ('The combination of these signs is suggestive of diffuse adenomyosis',
         'اجتماع هذه العلامات المختلفة يوحي بداء بطانة الرحم العضلي المنتشر',
         'La asociación de estos diferentes signos es sugestiva de adenomiosis difusa'),
    604: ('The small number of ultrasound signs does not support a diagnosis of adenomyosis',
         'العدد القليل من العلامات الصوتية لا يدعم تشخيص داء بطانة الرحم العضلي',
         'El escaso número de signos ecográficos no permite retener el diagnóstico de adenomiosis'),
    # === antecedents: Mammographie (extra) ===
    605: ('Right breast ACR 1', 'الثدي الأيمن ACR 1', 'Mama derecha ACR 1'),
    606: ('Right breast ACR 2', 'الثدي الأيمن ACR 2', 'Mama derecha ACR 2'),
    607: ('Right breast ACR 3', 'الثدي الأيمن ACR 3', 'Mama derecha ACR 3'),
    608: ('Right breast ACR 4', 'الثدي الأيمن ACR 4', 'Mama derecha ACR 4'),
    609: ('Right breast ACR 5', 'الثدي الأيمن ACR 5', 'Mama derecha ACR 5'),
    610: ('Left breast ACR 1', 'الثدي الأيسر ACR 1', 'Mama izquierda ACR 1'),
    611: ('Left breast ACR 2', 'الثدي الأيسر ACR 2', 'Mama izquierda ACR 2'),
    612: ('Left breast ACR 3', 'الثدي الأيسر ACR 3', 'Mama izquierda ACR 3'),
    613: ('Left breast ACR 4', 'الثدي الأيسر ACR 4', 'Mama izquierda ACR 4'),
    614: ('Left breast ACR 5', 'الثدي الأيسر ACR 5', 'Mama izquierda ACR 5'),
    # === consultation_gynecologique: presence_rapports_sexuels ===
    615: ('Absent', 'غائبة', 'Ausentes'),
    616: ('Regular', 'منتظمة', 'Regulares'),
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
        ('core', '0210_listechoix_translations'),
    ]

    operations = [
        migrations.RunPython(apply_translations, reverse_translations),
    ]
