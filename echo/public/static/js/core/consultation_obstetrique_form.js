const dopplerUterinTemp = _.template($('#doppler-uterin-template').html());
const dopplerDvTemp = _.template($('#doppler-dv-template').html());
const dopplerAcmTemp = _.template($('#doppler-acm-template').html());
const dopplerOmbiTemp = _.template($('#doppler-ombi-template').html());

function getFoetusChamp(foetus, vals, champ) {
    const pre = `donneesfoetus_set-${foetus}-`;
    //console.log('getFoetusChamp', pre+champ, vals[pre + champ]);
    //console.log(vals);
    return vals[pre + champ];
}

function printFoetusData(foetus, vals) {
    const pre = `donneesfoetus_set-${foetus}-`;
    console.log("printFoetusData", vals);
    output = '';
    output += printSelectField(pre + 'presentation', 'Présentation', vals);
    output += printGroup('Vitalité', groupFields('group-vitalite', pre), vals, false, pre);
    output += printGroup('Biométries', groupFields('group-biometrie', pre), vals, false, pre);
    output += printGroup('Morpohologie', groupFields('group-morpho', pre), vals, false, pre);
    output += printGroup('Annexes', groupFields('group-annexes', pre), vals, false, pre);
    output += printTextField(pre + 'commentaires', 'Commentaires', vals);

    if (isNotEmptyGroup('doppler-ombi', pre, vals)) {
        output += dopplerOmbiTemp(groupFieldsValues('doppler-ombi', pre, vals));
    }

    if (isNotEmptyGroup('doppler-acm', pre, vals)) {
        output += dopplerAcmTemp(groupFieldsValues('doppler-acm', pre, vals));
    }

    if (isNotEmptyGroup('doppler-dv', pre, vals)) {
        output += dopplerDvTemp(groupFieldsValues('doppler-dv', pre, vals));
    }

    return output;
}

function fusionnerChamp(nom) {
    let out = '';
    $("[data-champ=nom]").each( (idx, el) => {

    });
}

function nbFoetus(nb) {
    switch(nb) {
        case 'Unique': return 1;
        case 'Gemellaire': return 2;
        case 'Triple': return 3;
    }
    return 0;
}

function updateEditor() {
    console.log('Update editor obstétrique');

    const edt = tinymce.activeEditor;
    let champsValeurs = getValeursForm();

    // Vérifier si un template est sélectionné
    const tempId = $('#id_template_edition_obs').val();
    const temp = _.find(templates_edition, t => t.id == tempId);
    if (temp) {
        let imc = '';
        if (patient.poids && patient.taille) {
            imc = Number.parseFloat(100 * 100 * patient.poids / (patient.taille * patient.taille)).toFixed(1);
            console.log('IMC', imc);
        }

        let deviceId = parseInt($('#materiel').val());
        let device = {
            marque: '', modele: '', mise_circulation: ''
        };
        if (deviceId && deviceId != -1) {
            device = _.find(devices, d => d.id == deviceId);
        }

        let data = {
            nom_naissance_patient: patient.nom_naissance,
            prenom_patient: patient.prenom,
            age: patient.age,
            imc: imc,
            device_marque: device.marque,
            device_modele: device.modele,
            device_mise_circulation: moment(device.mise_circulation, 'YYYY-MM-DD').format('DD/MM/YYYY'),
            date: getDateConsultation(),
            ddr: moment(grossesse.ddr, 'YYYY-MM-DD').format('DD/MM/YYYY'),
            ddg: moment(grossesse.ddg, 'YYYY-MM-DD').format('DD/MM/YYYY'),
            terme: grossesse.terme,
            nb_foetus: nbFoetus(grossesse.nb_foetus),
            activite_cardiaque: '',
            mobilite: '',
        };

        let fields = [];
        $('[data-champ]').each((idx, el) => fields.push($(el).attr('data-champ')));
        //console.log('Fields', fields);

        //getFoetusChamp(1, champsValeurs, 'activite_cardiaque')
        if (isFormNotEmpty('#f_1')) {
            _.each(fields, f => data[f] = getFoetusChamp(0, champsValeurs, f));
        }

        if (isFormNotEmpty('#f_2')) {
            _.each(fields, f => data[f] = getFoetusChamp(1, champsValeurs, f));
        }

        if (isFormNotEmpty('#f_3')) {
            _.each(fields, f => data[f] = getFoetusChamp(2, champsValeurs, f));
        }

        fields = [];
        $('[data-cr]').each((idx, el) => fields.push($(el).attr('data-cr')));
        _.each(fields, f => data[f] = champsValeurs[f]);

        console.info('Data passed to template', data);
        //console.info('Template', temp.contenu);
        let tpl = _.template(unescapeTemplate(temp.contenu));
        edt.setContent(tpl(data));
        //console.log('Template', temp);
        if (isConsultationEnregistree())
            enregistrerConsultation();
        return;
    }

    let ddr = moment(grossesse.ddr, 'YYYY-MM-DD');
    let data = '';
    data += `DDR: ${ddr.format('DD/MM/YYYY')} - DDG: ${calcDDG(ddr.clone(), grossesse.cycle)}, soit un terme théorique de ${calcTerme(ddr.clone(), grossesse.cycle)}`;
    data += '<br><br>';

    if (grossesse.nb_foetus) {
        data += 'Grossesse ' + grossesse.nb_foetus;
        data += '<br>';
    }

    if (isFormNotEmpty('#f_1')) {
        data += '<h3 style="font-size: 13pt">Foetus A</h3>';
        data += printFoetusData(0, champsValeurs);
        data += '<br>';
    }

    if (isFormNotEmpty('#f_2')) {
        data += '<h3 style="font-size: 13pt">Foetus B</h3>';
        data += printFoetusData(1, champsValeurs);
        data += '<br>';
    }

    if (isFormNotEmpty('#f_3')) {
        data += '<h3 style="font-size: 13pt">Foetus C</h3>';
        data += printFoetusData(2, champsValeurs);
        data += '<br>';
    }

    if (isFormNotEmpty('.doppler-uterin')) {
        data += '<strong>Dopplers utérins</strong><br>';
        data += dopplerUterinTemp(champsValeurs);
    }

    if (isFormNotEmpty('.group-col')) {
        data += printGroup('Col', ['col_long', 'col_orifice_interne', 'col_entonnoir'], champsValeurs);
    }

    if (isFormNotEmpty('.group-pelvis')) {
        data += printGroup('Pelvis', ['pelvis_maternel'], champsValeurs);
    }

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

    data += printTextField('echo_morpho', 'Echographie morphologique', champsValeurs);
    data += printTextField('conclusion', 'Conclusion', champsValeurs);
    data += printTextField('conduite', 'Conduite à tenir', champsValeurs);

    edt.setContent(templateConsultation({data, date: getDateConsultation()}));

    if (isConsultationEnregistree())
        enregistrerConsultation();
}

function setQuickT2T3() {
    let foetus = parseInt($('.tab-pane.foetus.active').attr('id').split('_')[1])-1;
    console.log(`#id_donneesfoetus_set-${foetus}-activite_cardiaque`);

    $(`#id_donneesfoetus_set-${foetus}-activite_cardiaque`).val(413);
    $(`#id_donneesfoetus_set-${foetus}-mobilite`).val(416);

    $(`#id_donneesfoetus_set-${foetus}-morpho_crane`).val(2005);
    $(`#id_donneesfoetus_set-${foetus}-morpho_struct`).val(2006);
    $(`#id_donneesfoetus_set-${foetus}-morpho_face`).val(2007);
    $(`#id_donneesfoetus_set-${foetus}-morpho_thorax`).val(2008);
    $(`#id_donneesfoetus_set-${foetus}-morpho_coeur`).val(2009);
    $(`#id_donneesfoetus_set-${foetus}-morpho_abdo`).val(2001);

    $(`#id_donneesfoetus_set-${foetus}-morpho_digest`).val(2010);
    $(`#id_donneesfoetus_set-${foetus}-morpho_urine`).val(2011);
    $(`#id_donneesfoetus_set-${foetus}-morpho_rachis`).val(2012);
    $(`#id_donneesfoetus_set-${foetus}-morpho_membres`).val(2013);
    $(`#id_donneesfoetus_set-${foetus}-morpho_liquide_amnio`).val(2003);
    $(`#id_donneesfoetus_set-${foetus}-morpho_cordon`).val(554);

    _.chain(listes_choix)
        .filter(l => l.formulaire == "consultation_obs_foetus" && l.normale == true)
        .each(l => {
            let id = `#id_donneesfoetus_set-${foetus}-${l.champ}`;
            $(id).val(l.id);
        }).value();

    updateEditor();
}

$(document).ready(() => {
    createEditor('#editor-2', () => {
        if (isConsultationEnregistree()) {
            enregistrerConsultation();
        }
    });
});