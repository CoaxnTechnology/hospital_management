saveUrl = () => !isConsultationEnregistree()
    ? `/patients/${patient_pk}/consultation_colposcopie/ajouter/`
    : `/consultation_colposcopie/${consultation_pk}/modifier/`;


function enregistrerConsultationColposcopie() {
    console.log('enregistrerConsultationColposcopie');
    // Fonctions définies dans consultation_form.js
    enregistrerConsultation(tinymce.activeEditor);
}

function updateEditor() {
    console.log('Update editor');
    let champsValeurs = getValeursForm();

    let data = '';
    data += '<br>';
    data += printSelectField('indications', 'Indications', champsValeurs);
    data += printSelectField('test_hpv', 'Test HPV', champsValeurs, false);
    data += printSelectField('typage', 'Typage', champsValeurs, false);
    data += champsValeurs['commentaires_1'] + '<br>';

    data += printSelectField('examen_sans_preparation', 'Examen sans préparation', champsValeurs, false);
    data += champsValeurs['commentaires_2'] + '<br>';

    data += printSelectField('acide_acetique', 'Acide acétique', champsValeurs);
    data += printSelectField('tag', 'Tag', champsValeurs, false);
    data += printSelectField('localisation', 'Localisation', champsValeurs, false);
    data += printSelectField('lugol', 'Lugol', champsValeurs, false);
    data += champsValeurs['commentaires_3'] + '<br>';

    data += printSelectField('biopsie', 'Biopsie', champsValeurs);
    data += champsValeurs['commentaires_4'] + '<br>';

    data += printTextField('conclusion', 'Conclusion', champsValeurs);
    data += printTextField('conduite', 'Conduite à tenir', champsValeurs);

    const edt = tinymce.activeEditor;
    edt.setContent(templateConsultation({data, date: getDateConsultation()}));

    if (isConsultationEnregistree())
        enregistrerConsultationColposcopie();
}

$(document).ready(function () {
    // Charger le handler après le chargement de la page
    setTimeout(() => {
        $('.form-control').change(e => {
            updateEditor();
        });
    }, 2000);

    $('#btn_enregistrer_gyneco').click(e => {
        e.preventDefault();
        enregistrerConsultationColposcopie();
    });

    createEditor('#editor-2', () => {
        if (isConsultationEnregistree()) {
            enregistrerConsultationColposcopie();
        }
    });

});