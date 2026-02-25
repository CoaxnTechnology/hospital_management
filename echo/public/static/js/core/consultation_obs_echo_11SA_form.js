saveUrl = () => !isConsultationEnregistree()
    ? `/patients/${patient_pk}/consultation_obs_echo_11SA/ajouter/`
    : `/consultation_obs_echo_11SA/${consultation_pk}/modifier/`;

function updateEditor() {
    console.log('Update editor echo 11SA');
    let champsValeurs = getValeursForm();

    let ddr = moment(grossesse.ddr, 'YYYY-MM-DD');
    let data = '';
    data += `DDR: ${ddr.format('DD/MM/YYYY')} - DDG: ${calcDDG(ddr.clone(), grossesse.cycle)}, soit un terme théorique de ${calcTerme(ddr.clone(), grossesse.cycle)}`;
    data += '<br><br>';

    if (isFormNotEmpty('#sac_gest_form')) {
        data += `<strong>Sac gestationnel</strong><br>`;
        data += printSelectField('sac_gestationnel_localisation', 'Localisation', champsValeurs, false);
        data += printSelectField('sac_gestationnel_tonicite', 'Tonicité', champsValeurs, false);
        data += printSelectField('sac_gestationnel_trophoblaste', 'Trophoblaste', champsValeurs, false);
        if (isFormNotEmpty('#sac_gest_dim_form')) {
            data += `Dimensions :`;
            data += ` ${getTextField('sac_gestationnel_longueur', champsValeurs, '', 'mm x ')}`;
            data += `${getTextField('sac_gestationnel_largeur', champsValeurs, '', 'mm x ')}`;
            data += `${getTextField('sac_gestationnel_hauteur', champsValeurs, '', 'mm')}`;
            data += `${getTextField('sac_gestationnel_diametre', champsValeurs, ', diamètre de ', 'mm')}`;
            data += '<br>';
        }
    }
    data += printSelectField('sac_gestationnel_decollement', 'Décollement', champsValeurs, false);

    data += printGroup('Vitalité', ['activite_cardiaque'], champsValeurs);
    data += printGroup('Biométrie', ['lcc', 'bip'], champsValeurs);
    data += printGroup('Morphologie', ['morpho_extremite_cephalique', 'morpho_membres'], champsValeurs);

    data += printTextField('commentaires', 'Commentaires', champsValeurs);

    // Examen clinique
    if (isFormNotEmpty('#examen-clinique')) {
        data += '<br><strong>Examesn clinique</strong><br>';
        data += printGroup('', ['poids', 'ta', 'temperature', 'alb', 'gly'], champsValeurs, true);
        data += printTextField('seins', 'Seins', champsValeurs, false);
        data += printSelectField('examen_sous_speculum', 'Examen sous speculum', champsValeurs, false);
        data += printSelectField('leuco', 'Leuco', champsValeurs, false);
        data += printSelectField('tv', 'TV', champsValeurs, false);
        data += printTextField('commentaires_cliniques', 'Commentaires cliniques', champsValeurs, false);
    }

    data += printTextField('conclusion', 'Conclusion', champsValeurs);
    data += printTextField('conduite', 'Conduite à tenir', champsValeurs);

    const edt = tinymce.activeEditor;
    edt.setContent(templateConsultation({data, date: getDateConsultation()}));

    if (isConsultationEnregistree())
        enregistrerConsultation();
}

function setQuick() {
    $('#id_sac_gestationnel_localisation :nth-child(5)').prop('selected', true);
    $('#id_sac_gestationnel_tonicite :nth-child(3)').prop('selected', true);
    $('#id_sac_gestationnel_trophoblaste :nth-child(2)').prop('selected', true);
    $('#id_sac_gestationnel_decollement :nth-child(2)').prop('selected', true);
    $('#id_embryon_visible').prop('checked', true);
    $('#id_embryon_visible').trigger('change');
    $('#id_morpho_extremite_cephalique :nth-child(2)').prop('selected', true);
    $('#id_morpho_membres :nth-child(2)').prop('selected', true);
    $('#id_activite_cardiaque :nth-child(2)').prop('selected', true);
    updateEditor();
}

$(document).ready(function () {

    $('#id_embryon_visible').change(function () {
        if (this.checked) {
            $('#id_morpho_extremite_cephalique').prop('disabled', false);
            $('#id_morpho_membres').prop('disabled', false);
        } else {
            $('#id_morpho_extremite_cephalique').prop('disabled', true);
            $('#id_morpho_membres').prop('disabled', true);
        }
    });

});