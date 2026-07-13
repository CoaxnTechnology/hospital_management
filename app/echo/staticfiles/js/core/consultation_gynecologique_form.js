saveUrl = () => !isConsultationEnregistree()
    ? `/patients/${patient_pk}/consultation_gynecologique/ajouter/`
    : `/consultation_gynecologique/${consultation_pk}/modifier/`;

let fv; // form validation instance

function enregistrerConsultationCustom() {
    console.log('enregistrerConsultationCustom');

    let champs = {};

    champs['traitements'] = JSON.stringify(traitements);
    champs['examens'] = JSON.stringify(examens);

    console.log(champs);

    let fol_gauche_mesures = $('#ovaire-gauche-follicules-mesures .fol-mesures-item').map((idx, el) => {
        return {
            diametre: $(el).find('.diam').val(),
            longueur: $(el).find('.long').val(),
            largeur: $(el).find('.larg').val(),
            hauteur: $(el).find('.haut').val()
        };
    }).get();
    console.log('Fol gauche mesures', fol_gauche_mesures);
    $('#id_ovaire_gauche_follicules_list').val(JSON.stringify(fol_gauche_mesures));
    let fol_droit_mesures = $('#ovaire-droit-follicules-mesures .fol-mesures-item').map((idx, el) => {
        return {
            diametre: $(el).find('.diam').val(),
            longueur: $(el).find('.long').val(),
            largeur: $(el).find('.larg').val(),
            hauteur: $(el).find('.haut').val()
        };
    }).get();
    $('#id_ovaire_droit_follicules_list').val(JSON.stringify(fol_droit_mesures));

    // Fonctions définies dans consultation_form.js
    enregistrerConsultation(tinymce.activeEditor, champs);
}

function printPrescriptions() {
    let res = '<strong>Prescriptions</strong><br>';
    if (!examens.length && !traitements.length) return '';
    if (examens.length) {
        res += 'Examens complémentaires : ';
        examens.forEach(e => {
            res += e.libelle;
        });
        res += '<br>';
    }
    if (traitements.length) {
        res += 'Traitements : ';
        traitements.forEach(e => {
            res += e.libelle;
        });
        res += '<br>';
    }
    return res;
}

// https://dev.to/ageumatheus/creating-image-from-dataurl-base64-with-pyhton-django-454g
// https://html2canvas.hertzen.com/getting-started
// https://www.geeksforgeeks.org/how-to-convert-an-html-element-or-document-into-image/
// https://interactjs.io/
function enregistrerSchemaMyome() {
    KTApp.block('#myomes-schema-modal .modal-content', {});

    if (!isConsultationEnregistree())
        enregistrerConsultationCustom();

    setTimeout(() => {
        html2canvas(document.querySelector("#schema-myome-container")).then(canvas => {
            console.log('html2canvas done');
            let data = {
                file: canvas.toDataURL("image/png"),
                type: 'G' // Graphique
            };
            $.post(`/consultations/${consultation_pk}/images/ajouter/`, data)
                .done(function (result) {
                    let image = JSON.parse(result.image);
                    let url = image.url;
                    console.info('image url', url);
                    $('#images-container').append(imgItemTpl({img: image}));
                    $(`[name=img-cb-${image.id}]`).click(onImageCbClick);
                    consultationImages.push(image);
                    console.info('Consultation images', consultationImages);
                    KTApp.unblock('#myomes-schema-modal .modal-content');
                    $('#myomes-schema-modal').modal('hide');
                })
                .fail(function () {
                    console.error("Impossible d'ajouter l'image");
                });
        });
    }, 1000);
}

function updateEditor() {
    console.log('Update editor');
    let champsValeurs = getValeursForm();

    let data = '';
    data += '<br>';
    data += printSelectField('motif_consultation', 'Motif de consultation', champsValeurs);
    data += printTextField('motif_autre', 'Motif de consultation', champsValeurs);

    if (isFormNotEmpty('#blocConjoint')) {
        data += printGroup('Conjoint',
            ['nom_conjoint', 'prenom_conjoint', 'date_naissance_conjoint', 'telephone_conjoint',
                'groupe_sanguin_conjoint', 'consanguinite_conjoint', 'etat_sante_conjoint'],
            champsValeurs);
    }

    data += printGroup('Interrogatoire', ['age_menarche', 'cycles'], champsValeurs);
    data += printGroup('Menstruation', ['duree', 'abondance', 'douleur', 'syndrome_premenstruel', 'ddr'], champsValeurs);
    data += printGroup('Rapports sexuels', ['presence_rapports_sexuels', 'partenaire', 'age_premier_rapport'], champsValeurs);
    data += printGroup('Contraception',
        ['mode_contraception', 'commentaire_contraception', 'observance', 'satisfaction'], champsValeurs);
    data += printGroup('Ménopause', ['ths', 'signe_clinique', 'bouffees_chaleur', 'incontinence', 'sensation_pesanteur', 'dyspareunies'], champsValeurs);
    data += printTextField('commentaire', 'Commentaire', champsValeurs);
    data += printSelectField('endometriose', 'Endometriose', champsValeurs);

    // Examen clinique
    if (isFormNotEmpty('#examen-clinique')) {
        data += '<br><strong>Examen clinique</strong><br>';
        data += printGroup('', ['poids', 'ta', 'temperature', 'alb', 'gly'], champsValeurs, true);
        data += printTextField('seins', 'Seins', champsValeurs, false);
        data += printSelectField('examen_sous_speculum', 'Examen sous speculum', champsValeurs, false);
        data += printSelectField('leuco', 'Leuco', champsValeurs, false);
        data += printSelectField('tv', 'TV', champsValeurs, false);
        data += printTextField('commentaires_cliniques', 'Commentaires cliniques', champsValeurs, false);
    }

    // Echo pelvienne
    data += _updateEditor(champsValeurs);

    data += printTextField('conclusion_echo', 'Conclusion échographie', champsValeurs);
    data += printTextField('conclusion', 'Conclusion', champsValeurs);
    data += printTextField('conduite', 'Conduite à tenir', champsValeurs);

    data += printPrescriptions();
    //data += printTextField('prochaine_consultation_date', 'Prochaine consultation', champsValeurs);
    data += printTextField('observations', 'Observations', champsValeurs);

    const edt = tinymce.activeEditor;
    edt.setContent(templateConsultation({data, date: getDateConsultation()}));

    fv.validate()
        .then(status => {
            if (status == 'Valid') {
                if (isConsultationEnregistree())
                    enregistrerConsultationCustom();
            }
        });
}

function insererExamen(examen) {
    examens.push(examen);
    afficherExamens();
    updateEditor();
}

function insererTraitement(traitement) {
    traitements.push(traitement);
    afficherTraitements();
    updateEditor();
}

function afficherExamens() {
    let text = '<ul>';
    for (let i = 0; i < examens.length; i++) {
        text += `<li>${examens[i].text}</li>`;
    }
    text += '</ul>';
    $('#examens_list').html(text);
}

function afficherTraitements() {
    let text = '<ul>';
    for (let i = 0; i < traitements.length; i++) {
        text += `<li>${traitements[i].text}</li>`;
    }
    text += '</ul>';
    $('#traitements_list').html(text);
}

function imprimerClick() {
    console.log('imprimerClick');
    enregistrerConsultationCustom();
    createPdf().then(pdfDoc => {
        let f = document.getElementById('pdf-frame');
        pdfDoc.getDataUrl(url => f.setAttribute('src', url));
        bootstrap.Modal.getOrCreateInstance('#pdf-modal').show();
    });
}

function setQuick() {
    $('#id_endometre_visualisation :nth-child(2)').prop('selected', true);
    $('#id_asymetrie :nth-child(4)').prop('selected', true);
    $('#id_structures :nth-child(5)').prop('selected', true);
    $('#id_cavite :nth-child(7)').prop('selected', true);
    $('#id_ligne_cavitaire :nth-child(2)').prop('selected', true);
    $('#id_cul_de_sac_latero :nth-child(2)').prop('selected', true);
    updateEditor();
}

$(document).ready(function () {

    Inputmask("datetime", {
        inputFormat: 'dd/mm/yyyy',
        placeholder: "jj/mm/aaaa",
        min: '01/01/1900',
        max: '31/12/2900',
    }).mask(document.querySelectorAll('.date'));

    var nowDate = new Date();
    var DD = ((nowDate.getDate()) < 10 ? '0' : '') + (nowDate.getDate());
    var MM = ((nowDate.getMonth() + 1) < 10 ? '0' : '') + (nowDate.getMonth() + 1);

    Inputmask("datetime", {
        inputFormat: 'dd/mm/yyyy',
        placeholder: "jj/mm/aaaa",
        min: '01/01/1900',
        max: DD + '/' + MM + '/' + nowDate.getFullYear(),
    }).mask(document.querySelectorAll('#id_date_naissance_conjoint'));

    Inputmask("datetime", {
        inputFormat: 'mm/yyyy',
        placeholder: "mm/aaaa",
        min: '01/1900',
        max: '12/2900',
    }).mask(document.querySelectorAll('#id_prochaine_consultation_approx'));


    $('#btn_enregistrer_gyneco').click(e => {
        e.preventDefault();
        enregistrerConsultationCustom();
    });

    createEditor('#editor-2', () => {
        if (isConsultationEnregistree()) {
            enregistrerConsultationCustom();
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
                    settings.data = JSON.stringify({libelle: query/*, categorie: categorie*/});
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

    $('[name="traitement_autocomplete"]').typeahead(null, {
        name: 'traitement',
        display: 'libelle',
        source: autocompleteTraitements(),
        minLength: 2
    }).on('typeahead:select', (e, suggestion) => {
        insererTraitement(suggestion);
        $('[name="traitement_autocomplete"]').typeahead('val', '');
    }).on('typeahead:autocomplete', (e, suggestion) => {
        insererTraitement(suggestion);
        $('[name="traitement_autocomplete"]').typeahead('val', '');
    });

    ['examen_autocomplete'].forEach(categorie => {
        const selector = $('[name=' + categorie + ']');
        selector.typeahead(null, {
            name: 'biologie',
            display: 'libelle',
            source: autocompletePrescriptions(categorie),
            minLength: 2
        }).on('typeahead:select', (e, suggestion) => {
            insererExamen(suggestion);
            selector.typeahead('val', '');
        }).on('typeahead:autocomplete', (e, suggestion) => {
            insererExamen(suggestion);
            selector.typeahead('val', '');
        });
    });


    fv = FormValidation.formValidation(
        document.getElementById('form_1'),
        {
            fields: {
                'telephone_conjoint': {
                    validators: {
                        numeric: {
                            message: 'Téléphone doit contenir des chiffres uniquement'
                        },
                        stringLength: {
                            min: 8,
                            max: 8,
                            message: 'Téléphone doit contenir 8 chiffres'
                        }
                    }
                }
            },

            plugins: {
                trigger: new FormValidation.plugins.Trigger(),
                bootstrap: new FormValidation.plugins.Bootstrap5({
                    rowSelector: '.fv-row'
                }),
                /*submitButton: new FormValidation.plugins.SubmitButton(),
                defaultSubmit: new FormValidation.plugins.DefaultSubmit(),*/
            }
        }
    );

    afficherExamens();
    afficherTraitements();

});