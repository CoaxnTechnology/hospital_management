let pdfDoc;
let  templateHeader;

function updateEditor() {
    const type = $('#id_type').val();
    const praticien = _.find(praticiens, p => p.id == $('#id_praticien').val());
    const modele = _.template(unescapeTemplate(modeles[type]));
    let content = '';
    let data = {
        civilite: _.capitalize(patient.civilite),
        nom_patient: patient.nom_complet,
        date_naissance: moment(patient.date_naissance).format('DD/MM/YYYY'),
        age: `${patient.age} ans`,
        poids: patient.poids ? `${patient.poids} Kg` : '',
        patient: patient,
        nom_praticien: praticien.nom,
    };
    data = _.assign(data, grossesse_data);
    switch (type) {
        case 'certificat_medical':
            data['nb_jours'] = $('#id_duree').val() + ' jour' + (parseInt($('#id_duree').val()) > 1 ? 's' : '');
            break;
        case 'lettre_accouchement':
            //data = _.assign(data, grossesse_data);
            break;
    }

    content = modele(data);

    let output = templateHeader({
        date: $('#id_date').val(),
        patient: patient,
        praticien: praticien,
        content: content,
        titre: titres[type]
    });

    console.log('Type', type, titres[type]);
    //console.log(output);

    output = output.replaceAll('<br><br>', '<br>')
                .replaceAll('<br/><br/>', '<br/>');

    tinymce.activeEditor.setContent(output);
}

function initModeles() {
    if (_.isEmpty(modeles['certificat_medical']) || _.isNil(modeles['certificat_medical']) || modeles['certificat_medical'] === 'None') {
        modeles['certificat_medical'] = $('#modele-certificat-medical-defaut').html();
    }
    if (_.isEmpty(modeles['certificat_presence']) || _.isNil(modeles['certificat_presence']) || modeles['certificat_presence'] === 'None') {
        modeles['certificat_presence'] = $('#modele-certificat-presence-defaut').html();
    }
    if (_.isEmpty(modeles['lettre_accouchement']) || _.isNil(modeles['lettre_accouchement']) || modeles['lettre_accouchement'] === 'None') {
        modeles['lettre_accouchement'] = $('#modele-lettre-accouchement-defaut').html();
    }
    if (_.isEmpty(modeles['lettre_confidentielle']) || _.isNil(modeles['lettre_confidentielle']) || modeles['lettre_confidentielle'] === 'None') {
        modeles['lettre_confidentielle'] = $('#modele-lettre-confidentielle-defaut').html();
    }
    if (_.isEmpty(modeles['attestation_grossesse']) || _.isNil(modeles['attestation_grossesse']) || modeles['attestation_grossesse'] === 'None') {
        modeles['attestation_grossesse'] = $('#modele-attestation-grossesse-defaut').html();
    }
    if (_.isEmpty(modeles['lettre_fittofly']) || _.isNil(modeles['lettre_fittofly']) || modeles['lettre_fittofly'] === 'None') {
        modeles['lettre_fittofly'] = $('#modele-lettre-fittofly-defaut').html();
    }
}

$(document).ready(() => {

    initModeles();

    if ($('#id_date').val() == '')
        $('#id_date').val(moment().format('DD/MM/yyyy'));
    else
        $('#id_date').val(moment($('#id_date').val('DD/MM/yyyy HH:mm:ss')).format('DD/MM/yyyy'));

    $('#id_date').datepicker({
        todayHighlight: true,
        autoclose: true,
        language: 'fr',
        weekStart: 1,
        format: 'dd/mm/yyyy'
    }).on('changeDate', () => {
        updateEditor();
    });

    if (ajouterDateLieuEdition)
        templateHeader = _.template(unescapeTemplate($('#template-header').html()));
    else
        templateHeader = _.template(unescapeTemplate($('#template-header-no-date').html()));

    tinymce.init({
        selector: '#id_text',
        plugins: ['link', 'lists', 'autolink', 'paste'],
        language: 'fr_FR',
        paste_as_text: true,
        contextmenu: 'image table',
        toolbar: [
            'undo redo | bold italic underline | fontsizeselect | forecolor backcolor | alignleft aligncenter alignright alignfull | numlist bullist outdent indent'
        ],
        statusbar: false,
        menubar: false,
        inline: false,
        forced_root_block: false,
        content_style: "body { font-size: 12pt; }",
        init_instance_callback: function (editor) {
            if (certificat_id == -1) {
                updateEditor();
            }
            $('.tox-tinymce').height(window.innerHeight-80);
        }
    });

    let logoB64 = '', signatureB64 = '';
    const templateSignature = _.template(unescapeTemplate($('#template-signature').html()));

    if (logo_url) {
        chargerImageB64(logo_url, (b64) => {
            logoB64 = b64;
        });
    }

    if (signature_url && signature_url != '') {
        chargerImageB64(signature_url, (b64) => {
            signatureB64 = b64;
        });
    }

    $('#id_duree').on('change keyup', eve => {
        updateEditor();
    });

    $('#id_praticien').change(eve => {
        signatureB64 = '';
        const id = $("#id_praticien option:selected").val();
        const praticien = _.find(praticiens, p => p.id == id);
        if (praticien.ajouter_signature_edition && praticien.signature && praticien.signature != '') {
            chargerImageB64(praticien.signature, (b64) => {
                signatureB64 = b64;
            });
            updateEditor();
        }
    });

    $('#btn-enregistrer').click(eve => {
        $('#form_1').submit();
    });

    $('#btn-imprimer').click(eve => {
        const praticien = _.find(praticiens, p => p.id == $('#id_praticien').val());
        const signatureData = {signature_titre: praticien.nom, signature_img: signatureB64};
        // Prendre en compte les parametres d'ajout de l'entete et pied de page pour le type de certificat
        addEntetes = impressionEntetes[$('#id_type').val()];
        const type = $('#id_type').val();
        let format = 'A5';
        if (type == 'lettre_accouchement')
            format = 'A4';

        let editor = tinymce.activeEditor;
        let editorContent = editor.getContent();
        let makeDoc = [];
        cleanPDF(htmlToPdfmake(editorContent, defaultHtml2PDFOptions), makeDoc);
        console.log(makeDoc[0]);
        const docDefinition = {
            pageMargins: defaultMargins(),
            pageSize: format,
            header: defaultHeader,
            footer: defaultFooter,
            content: [
                makeDoc[0],
                htmlToPdfmake(templateSignature(signatureData))
            ],
        };

        pdfDoc = pdfMake.createPdf(docDefinition);
        pdfDoc.open();

        setTimeout(() => {
            $('#form_1').submit();
        }, 2000);
    });

    $('id_text').css('display', 'none');

    $('#id_type').change(e => {
        const type = $(e.target).val();
        if (type === 'certificat_medical') {
            $('#id_duree_container').css('display', 'block');
        } else {
            $('#id_duree_container').css('display', 'none');
        }
        /*if (type === 'lettre_accouchement') {
            tinymce.activeEditor.dom.setStyle(tinymce.activeEditor.getBody(), 'font-size', '14pt')
        } else {
            tinymce.activeEditor.dom.setStyle(tinymce.activeEditor.getBody(), 'font-size', '14pt')
        }*/
        updateEditor();
    });

    $(window).resize(e => {
        $('.tox-tinymce').height(window.innerHeight-80);
    });

    if (grossesse_data) {
        $el = $("#atcd-print");
        $el.html(grossesse_data['atcd']);
        $el.children('p').after('<br/>');
        $el.children('p').contents().unwrap();
        grossesse_data['atcd'] = $el.html();
    }

});