$(document).ready(() => {
    FormValidation.formValidation(
        document.getElementById('form_1'),
        {
            fields: {
                'nom': {
                    validators: {
                        notEmpty: {
                            message: 'Nom est obligatoire'
                        }
                    }
                },

                'telephone': {
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
