let pdfDoc;
let traitementSelectionne;

if (ajouterDateLieuEdition)
    templateHeader = _.template(unescapeTemplate($('#template-header').html()));
else
    templateHeader = _.template(unescapeTemplate($('#template-header-no-date').html()));


function getFormeDisplay(forme, many=false) {
    //console.log('getFormeDisplay', forme);
    switch(forme) {
        case 'Pommade': case 'Gel': case 'Gouttes': case 'Autre': return 'application' + (many ? 's' : '');
        case 'Poudre': case 'Sirop': return 'prise' + (many ? 's' : '');
        default: return forme.toLowerCase() + (many ? 's' : '');
    }
}

function insererTraitement() {
    const edt = tinymce.activeEditor;
    const prises_par_jour = $("#prises_par_jour").val();
    const nb_jours = $("#nb_jours").val();
    const qte_par_prise = $("#qte_par_prise").val();
    const forme = getFormeDisplay(traitementSelectionne.forme, parseInt(qte_par_prise) > 1);
    let posologie = `${qte_par_prise} ${forme} ${prises_par_jour} fois par jour`;
    if (nb_jours != '') posologie += ` pendant ${nb_jours} jours`;
    //edt.setContent(`${edt.getContent()} <br><p><strong>${traitementSelectionne.text}</strong> : ${posologie}</p>`);
    edt.dom.add('content-container', 'p', {}, `<strong>${traitementSelectionne.text}</strong> : ${posologie}`);
    //console.log('Posologie', posologie);
    $('[name="traitement"]').typeahead('val', '');
    $('#prises_par_jour, #nb_jours').val('');
    $('#qte_par_prise').val('1');
}

function insererPrescription(prescription) {
    const edt = tinymce.activeEditor;
    edt.dom.add('content-container', 'p', {}, `${prescription.text}`);
}

function ajouterTraitement() {
    showFrameLoading();
    $('#traitements-modal iframe').attr('src', `/traitements`);
    $('#traitements-modal').modal();
}

function ajouterPrescription() {
    showFrameLoading();
    $('#prescriptions-modal iframe').attr('src', `/prescriptions`);
    $('#prescriptions-modal').modal();
}

function updateType(type) {
    $('#traitements-container').css('display', 'none');
    $('#examens-container').css('display', 'none');
    console.log('Update type', type);
    if (type.includes('Traitement'))
        $('#traitements-container').css('display', 'block');

    if (type.includes('Examen'))
        $('#examens-container').css('display', 'block');
}

function updateEditor() {
    const type = $('#id_type').val();
    const praticien = _.find(praticiens, p => p.id == $('#id_praticien').val());
    if (!modeles[type]) {
        console.info("No template for type", type);
        return;
    }
    const modele = _.template(unescapeTemplate(modeles[type]));
    let content = '';
    let data = {
        civilite: _.capitalize(patient.civilite),
        nom_patient: patient.nom_complet,
        date_naissance: moment(patient.date_naissance).format('DD/MM/YYYY'),
        age: `${patient.age} ans`,
        poids: patient.poids ? `${patient.poids} Kg` : '',
        fumeur: patient.fumeur ? 'Oui' : 'Non',
        patient: patient,
        nom_praticien: praticien.nom,
    };
    data = _.assign(data, grossesse_data);
    console.info('Data', grossesse_data);

    switch (type) {
        case 'certificat_medical':
            data['nb_jours'] = $('#id_duree').val() + ' jour' + (parseInt($('#id_duree').val()) > 1 ? 's' : '');
            break;
    }

    content = modele(data);

    const rensCliniques = $('#rens-cli').val();
    if (rensCliniques != '') {
        //content += '<br><strong>Renseignements cliniques</strong><br>';
        //content += rensCliniques;
    }

    let output = templateHeader({
        date: $('#id_date').val(),
        patient: patient,
        praticien: praticien,
        content: content
    });

    output = output.replaceAll('<br><br>', '<br>')
                .replaceAll('<br/><br/>', '<br/>');

    //console.log('output', output);

    tinymce.activeEditor.setContent(output);
}

$(document).ready(() => {

    $('#id_date').datepicker({
        todayHighlight: true,
        autoclose: true,
        language: 'fr',
        weekStart: 1,
        format: 'dd/mm/yyyy'
    }).on('changeDate', () => {
        updateEditor();
    });

    tinymce.init({
        selector: '#id_text',
        plugins: ['link', 'lists', 'autolink', 'paste'],
        language: 'fr_FR',
        contextmenu: 'image table',
        paste_as_text: true,
        toolbar: [
            'undo redo | bold italic underline | fontsizeselect | forecolor backcolor | alignleft aligncenter alignright alignfull | numlist bullist outdent indent'
        ],
        statusbar: false,
        menubar: false,
        inline: false,
        forced_root_block: false,
        content_style: "body { font-size: 12pt; }",
        init_instance_callback: function (editor) {
            updateType($('#id_type option:selected').text());
            if (ordonnance_id == -1) {
                updateEditor();
            }
            $('.tox-tinymce').height(window.innerHeight-80);
        }
    });

    const autocompleteTraitements = function () {
        return new Bloodhound({
            remote: {
                url: '/traitements/recherche/',

                prepare: function (query, settings) {
                    settings.type = "POST";
                    settings.contentType = "application/json; charset=UTF-8";
                    settings.data = JSON.stringify({libelle: query});
                    return settings;
                },
                transform: function (data) {
                    let newData = [];
                    let items = JSON.parse(data);
                    console.log('Autocomplete count', items.length);
                    items.forEach(function (item) {
                        newData.push(item);
                    });
                    return newData;
                }
            },
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('libelle'),
            queryTokenizer: Bloodhound.tokenizers.whitespace
        });
    };

    const autocompletePrescriptions = function (categorie) {
        return new Bloodhound({
            remote: {
                url: '/prescriptions/recherche/',

                prepare: function (query, settings) {
                    settings.type = "POST";
                    settings.contentType = "application/json; charset=UTF-8";
                    settings.data = JSON.stringify({libelle: query, categorie: categorie});
                    return settings;
                },
                transform: function (data) {
                    let newData = [];
                    let items = JSON.parse(data);
                    console.log('Autocomplete count', items.length);
                    items.forEach(function (item) {
                        newData.push(item);
                    });
                    return newData;
                }
            },
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('libelle'),
            queryTokenizer: Bloodhound.tokenizers.whitespace
        });
    };


    $('[name="traitement"]').typeahead(null, {
        name: 'traitement',
        display: 'libelle',
        source: autocompleteTraitements(),
        minLength: 2
    }).on('typeahead:select', (e, suggestion) => {
        traitementSelectionne = suggestion;
        $('.traitement-champs').addClass('d-block');
        //console.log(suggestion);
    }).on('typeahead:autocomplete', (e, suggestion) => {
        traitementSelectionne = suggestion;
        $('.traitement-champs').addClass('d-block');
    });

    ['biologie', 'examen_complementaire'].forEach(categorie => {
        $('.' + categorie).typeahead(null, {
            name: 'biologie',
            display: 'libelle',
            source: autocompletePrescriptions(categorie),
            minLength: 2
        }).on('typeahead:select', (e, suggestion) => {
            insererPrescription(suggestion);
            $('.' + categorie).typeahead('val', '');
        }).on('typeahead:autocomplete', (e, suggestion) => {
            insererPrescription(suggestion);
            $('.' + categorie).typeahead('val', '');
        });
    });

    const template = _.template(unescapeTemplate($('#template-examen').html()));
    const templateSignature = _.template(unescapeTemplate($('#template-signature').html()));

    $('#id_praticien').change(eve => {
        signatureB64 = '';
        const id = $("#id_praticien option:selected").val();
        const praticien = _.find(praticiens, p => p.id == id);
        if (praticien.ajouter_signature_edition && praticien.signature && praticien.signature != '') {
            chargerImageB64(praticien.signature, (b64) => {
                signatureB64 = b64;
                console.info('Signature changée');
            });
        }
    });

    $('#btn-enregistrer').click(eve => {
        $('#form_1').submit();
    });

    $('#btn-imprimer').click(eve => {
        const praticien = _.find(praticiens, p => p.id == $('#id_praticien').val());
        const signatureData = {signature_titre: praticien.nom, signature_img: signatureB64};
        console.log(tinymce.activeEditor.getContent());
        let makeDoc = [];
        let html = htmlToPdfmake(tinymce.activeEditor.getContent(), defaultHtml2PDFOptions);
        console.log('PDF', html);
        cleanPDF(html, makeDoc);
        console.log('Cleaned', makeDoc);
        const docDefinition = {
            pageSize: 'A5',
            pageMargins: defaultMargins(),
            header: defaultHeader,
            footer: defaultFooter,
            content: [
                makeDoc[0],
                htmlToPdfmake(templateSignature(signatureData))
            ]
        };

        pdfDoc = pdfMake.createPdf(docDefinition, defaultHtml2PDFOptions);
        console.log(pdfDoc);
        pdfDoc.open();

        setTimeout(() => {
            $('#form_1').submit();
        }, 2000);
    });

    $('id_text').css('display', 'none');

    $(window).resize(e => {
        $('.tox-tinymce').height(window.innerHeight-80);
    });

    $("#prises_par_jour, #nb_jours, #qte_par_prise").on('change keyup', e => {
        if ($('#prises_par_jour').val() != '' && $('#qte_par_prise').val() != '')
            $('#btn-ajouter-traitement').prop('disabled', false);
        else
            $('#btn-ajouter-traitement').prop('disabled', true);
    });

    $('#rens-cli').on('keyup change', e => {
        let rens = $('#rens-cli').val().replace(/\n/g, "<br/>");
        if (rens != '')
            rens = '<strong>Renseignements cliniques</strong><br>' + rens;
        const edt = tinymce.activeEditor;
        edt.dom.setHTML('renseignements-container', rens);
    });

    $('#id_type').change(e => {
        const type = $('#id_type option:selected').text();
        updateType(type);
        updateEditor();
    });


    if (grossesse_data) {
        $el = $("#atcd-print");
        $el.html(grossesse_data['atcd']);
        $el.children('p').after('<br/>');
        $el.children('p').contents().unwrap();
        grossesse_data['atcd'] = $el.html();
    }

});