saveUrl = () => !isConsultationEnregistree()
    ? `/patients/${patient_pk}/consultation_echo_pelvienne/ajouter/`
    : `/consultation_echo_pelvienne/${consultation_pk}/modifier/`;

function enregistrerConsultationCustom() {
    console.log('enregistrerConsultationEchoPelvienne');
    // Fonctions définies dans consultation_form.js
    enregistrerConsultation(tinymce.activeEditor);
}

function updateEditor() {
    console.log('Update editor');
    let champsValeurs = getValeursForm();

    let data = '';
    data += '<br>';

    data += printSelectField('titre_echo_pelvienne', 'Motif de consultation', champsValeurs);

    data += _updateEditor(champsValeurs);

    data += printTextField('conclusion_echo', 'Conclusion échographie', champsValeurs);
    data += printTextField('conclusion', 'Conclusion', champsValeurs);
    data += printTextField('conduite', 'Conduite à tenir', champsValeurs);

    const edt = tinymce.activeEditor;
    edt.setContent(templateConsultation({data, date: getDateConsultation()}));

    if (isConsultationEnregistree())
        enregistrerConsultationCustom();
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

$(document).ready(function () {

    $('#btn_enregistrer_gyneco').click(e => {
        e.preventDefault();
        enregistrerConsultationCustom();
    });

    createEditor('#editor-2', () => {
        if (isConsultationEnregistree()) {
            enregistrerConsultationCustom();
        }
    });

});