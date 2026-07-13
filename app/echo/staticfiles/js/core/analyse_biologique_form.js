$(document).ready(() => {
    const fv = FormValidation.formValidation(
        document.getElementById('form_1'),
        {
            fields: {
                'code': {
                    validators: {
                        notEmpty: {
                            message: 'Code est obligatoire'
                        }
                    }
                },
                'libelle': {
                    validators: {
                        notEmpty: {
                            message: 'Libellé est obligatoire'
                        }
                    }
                },
                'type': {
                    validators: {
                        notEmpty: {
                            message: 'Type est obligatoire'
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
        }
    );

    fv.on('core.form.valid', function (event) {
        $('#btn-enregistrer').prop('disabled', true);
    });
});