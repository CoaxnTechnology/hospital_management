$(document).ready(() => {
    FormValidation.formValidation(
        document.getElementById('form_1'),
        {
            fields: {
                'libelle': {
                    validators: {
                        notEmpty: {
                            message: 'Libellé est obligatoire'
                        }
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
        });
});
