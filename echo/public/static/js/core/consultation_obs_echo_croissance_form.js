saveUrl = () => !isConsultationEnregistree()
    ? `/patients/${patient_pk}/consultation_obs_echo_croissance/ajouter/`
    : `/consultation_obs_echo_croissance/${consultation_pk}/modifier/`;