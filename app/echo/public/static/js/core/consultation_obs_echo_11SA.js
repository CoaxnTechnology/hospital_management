saveUrl = !isConsultationEnregistree()
    ? `/patients/${patient_pk}/consultation_colposcopie/ajouter/`
    : `/consultation_colposcopie/${consultation_pk}/modifier/`;

const templateConsultation = _.template(unescapeTemplate($('#consultation-template').html()));

function printGroup(groupe, champs, champsValeurs, inline = false) {
    let out = _.map(champs, champ => {
        const v = champsValeurs[champ];
        const label = $('#id_' + champ).parents('.form-group').children('label').text();
        return (v != '' && v != '---------' && v != 'unknown' ? `${label} : ${v}.` : '');
    });
    const separator = inline ? ' ' : '<br>';
    if (out.join('') != '') {
        let ret = `<strong>${groupe}</strong><br>`;
        ret += _.reduce(out, function (sum, n) {
            return sum + (n != '' ? n + separator : '');
        }, '');
        if (inline) ret += '<br>';
        return ret;
    } else {
        return '';
    }
}

function enregistrerConsultationColposcopie() {
    console.log('enregistrerConsultationColposcopie');

    let champs = _.chain($('#form_1').serializeArray())
        .keyBy('name')
        .mapValues('value')
        .value();

    console.log(champs);
    // Fonctions définies dans consultation_form.js
    enregistrerConsultation(tinymce.activeEditor, champs);
}

function getSelectField(champ, champsValeurs) {
    let ret = champsValeurs[champ];
    if (ret != 'unknown' && ret != '---------')
        return ret;
    else
        return '';
}

function printTextField(champ, label, champsValeurs, strong = true) {
    let val = champsValeurs[champ];
    if (val != '') {
        return strong ? `<strong>${label} : </strong>${val}<br>` : `${label} : ${val}<br>`;
    }
    return '';
}

function printSelectField(champ, label, champsValeurs, strong = true) {
    let val = getSelectField(champ, champsValeurs);
    if (val != '') {
        return strong ? `<strong>${label} : </strong>${val}<br>` : `${label} : ${val}<br>`;
    }
    return '';
}

function updateEditor() {
    console.log('Update editor');
    let formData = $('#form_1').serializeArray();
    mapped = _.mapValues(formData, c => {
        let $el = $('#id_' + c.name);
        let val = c.value;
        if ($el.prop("tagName") == 'SELECT' && c.value != '' && c.value != 'unknown')
            val = $el.find(":selected").text();
        if (c.value == 'unknown')
            val = ''
        return {name: c.name, value: val};
    });
    let champsValeurs = _.chain(mapped)
        .keyBy('name')
        .mapValues('value')
        .value();
    console.log(champsValeurs);

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

    const edt = tinymce.activeEditor;
    edt.setContent(templateConsultation({data}));

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

    tinymce.init({
        selector: '#editor-2',
        plugins: [
            'link',
            'lists',
            'autolink'
        ],
        toolbar: [
            'undo redo | bold italic underline | fontsizeselect',
            'forecolor backcolor | alignleft aligncenter alignright alignfull | numlist bullist outdent indent'
        ],
        statusbar: false,
        menubar: false,
        inline: false,
        forced_root_block: false,
        //content_style: "body { font-size: 10pt }",
        init_instance_callback: function (editor) {
            $('.tox-tinymce').height(window.innerHeight - 240);

            editor.on('Change', function (e) {
                if (isConsultationEnregistree()) {
                    enregistrerConsultationColposcopie(editor);
                }
            });

            editor.on('keyup', function (e) {
                $('#libelle_statut')
                    .toggleClass('label-success', false)
                    .text('Brouillon')
                    .show();
            });
        }
    });

});