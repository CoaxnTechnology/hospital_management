jQuery(document).ready(function () {


    $('#debut').datepicker({
        todayHighlight: true,
        autoclose: true,
        language: 'fr',
        weekStart: 1,
        format: 'dd/mm/yyyy'
    });

    $('#heure_debut').timepicker({
        timeFormat: 'HH:mm',
        minTime: '7',
        maxTime: '22',
        startTime: '07:00',
        dynamic: false,
        dropdown: true,
        scrollbar: true,
    });

    $('#heure_fin').timepicker({
        timeFormat: 'HH:mm',
        minTime: '7',
        maxTime: '22',
        startTime: '07:00',
        dynamic: false,
        dropdown: true,
        scrollbar: true
    });

    FormValidation.formValidation(
        document.getElementById('form_1'),
        {
            fields: {
                'praticien': {
                    validators: {
                        notEmpty: {
                            message: 'Praticien est obligatoire'
                        }
                    }
                },
                'debut': {
                    validators: {
                        notEmpty: {
                            message: 'Champ obligatoire'
                        }
                    }
                },
                'heure_debut': {
                    validators: {
                        notEmpty: {
                            message: 'Champ obligatoire'
                        }
                    }
                },
                'heure_fin': {
                    validators: {
                        notEmpty: {
                            message: 'Champ obligatoire'
                        }
                    }
                },
            },

            plugins: {
                trigger: new FormValidation.plugins.Trigger(),
                bootstrap: new FormValidation.plugins.Bootstrap(),
                submitButton: new FormValidation.plugins.SubmitButton(),
                // Submit the form when all fields are valid
                defaultSubmit: new FormValidation.plugins.DefaultSubmit(),
            }
        });

});

