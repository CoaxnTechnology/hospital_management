saveUrl = () => !isConsultationEnregistree()
    ? `/patients/${patient_pk}/consultation_obs_echo_troisieme_trimestre/ajouter/`
    : `/consultation_obs_echo_troisieme_trimestre/${consultation_pk}/modifier/`;


function setQuick() {
    let foetus = parseInt($('.tab-pane.foetus.active').attr('id').split('_')[1])-1;

    _.chain(listes_choix)
        .filter(l => l.formulaire == "consultation_obs_foetus" && l.normale == true)
        .each(l => {
            let id = `#id_donneesfoetus_set-${foetus}-${l.champ}`;
            $(id).val(l.id);
        }).value();
    updateEditor();
}