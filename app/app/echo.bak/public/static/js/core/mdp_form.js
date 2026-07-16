$(document).ready(() => {

    FormValidation.formValidation(
        document.getElementById('form_mdp'),
        {
            fields: {
                'password': {
                    validators: {
                        notEmpty: {
                            message: 'Mot de passe est obligatoirez'
                        },
                        stringLength: {
                            min: 6,
                            message: 'Le mot de passe doit avoir 6 caractères au minimum',
                        },
                    }
                }

            },

            plugins: {
                trigger: new FormValidation.plugins.Trigger(),
                bootstrap: new FormValidation.plugins.Bootstrap(),
                submitButton: new FormValidation.plugins.SubmitButton(),
                // Submit the form when all fields are valid
                defaultSubmit: new FormValidation.plugins.DefaultSubmit(),
            }
        }
    );
});

