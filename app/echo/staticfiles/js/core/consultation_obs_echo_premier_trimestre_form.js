saveUrl = () => !isConsultationEnregistree()
    ? `/patients/${patient_pk}/consultation_obs_echo_premier_trimestre/ajouter/`
    : `/consultation_obs_echo_premier_trimestre/${consultation_pk}/modifier/`;


function setQuick() {
    let foetus = parseInt($('.tab-pane.foetus.active').attr('id').split('_')[1])-1;
    $(`#id_donneesfoetus_set-${foetus}-activite_cardiaque`).val(413);
    $(`#id_donneesfoetus_set-${foetus}-mobilite`).val(416);
    $(`#id_donneesfoetus_set-${foetus}-morpho_coeur`).val(2000);
    $(`#id_donneesfoetus_set-${foetus}-morpho_pole_cepha`).val(580);
    $(`#id_donneesfoetus_set-${foetus}-morpho_abdo`).val(2001);
    $(`#id_donneesfoetus_set-${foetus}-morpho_membres`).val(2002);
    $(`#id_donneesfoetus_set-${foetus}-morpho_liquide_amnio`).val(2003);
    $(`#id_donneesfoetus_set-${foetus}-morpho_trophoblaste_aspect`).val(589);
    $(`#id_donneesfoetus_set-${foetus}-morpho_trophoblaste_localisation`).val(2004);
    $(`#id_donneesfoetus_set-${foetus}-morpho_decol`).val(593);

    _.chain(listes_choix)
        .filter(l => l.formulaire == "consultation_obs_foetus" && l.normale == true)
        .each(l => {
            let id = `#id_donneesfoetus_set-${foetus}-${l.champ}`;
            $(id).val(l.id);
        }).value();
    updateEditor();
}