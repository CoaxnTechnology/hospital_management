jQuery(document).ready(function () {

    $('#id_first_name, #id_last_name').on('keyup', e => {
        if (!mode_edition) {
            const first = $('#id_first_name').val();
            const last = $('#id_last_name').val();
            if (first && last) {
                const username = `${first.toLowerCase()}.${last.toLowerCase()}`;
                $('#id_username').val(username);
            }
        }
    });

    Inputmask("datetime", {
        inputFormat: 'dd/mm/yyyy',
        placeholder: "jj/mm/aaaa",
        min: '01/01/1900',
        max: '31/12/2900',
    }).mask(document.querySelectorAll('.datepicker'));

    Inputmask({
        mask: "*{1,20}[.*{1,20}][.*{1,20}][.*{1,20}]@*{1,20}[.*{2,6}][.*{1,2}]",
        greedy: false,
        onBeforePaste: function (pastedValue, opts) {
            pastedValue = pastedValue.toLowerCase();
            return pastedValue.replace("mailto:", "");
        },
        definitions: {
            '*': {
                validator: "[0-9A-Za-z!#$%&'*+/=?^_`{|}~\-]",
                cardinality: 1,
                casing: "lower"
            }
        }
    }).mask(document.querySelectorAll('#id_email'));

    Inputmask({
        regex: "[a-zA-Z0-9._]*"
    }).mask(document.querySelectorAll('[name="username"]'));

    if (mode_edition) {
        $('[name="password"]').css('display', 'none');
    }


    /*
    var signature = new KTImageInput('signature');

    signature.on('change', function (imageInput) {
        swal.fire({
            title: 'Signature ajoutée',
            type: 'success',
            buttonsStyling: false,
            confirmButtonText: 'Ok',
            confirmButtonClass: 'btn btn-primary font-weight-bold'
        });
    });

    signature.on('remove', function (imageInput) {
        swal.fire({
            title: 'Signature supprimée',
            type: 'error',
            buttonsStyling: false,
            confirmButtonText: 'Ok',
            confirmButtonClass: 'btn btn-primary font-weight-bold'
        });
    });*/

    $('#btn-modifier-mdp').modalForm({
        formURL: `/utilisateurs/${utilisateur}/mdp/?next=${window.location.href}?msg=mdp_succes`,
    });

    Inputmask({
        mask: "99/99999999/99"
    }).mask(document.querySelectorAll('#id_profil-0-code_conventionnel'));

    FormValidation.formValidation(
        document.getElementById('form_1'),
        {
            fields: {
                'first_name': {
                    validators: {
                        notEmpty: {
                            message: 'Prénom est obligatoire'
                        }
                    }
                },

                'last_name': {
                    validators: {
                        notEmpty: {
                            message: 'Nom est obligatoire'
                        }
                    }
                },

                'email': {
                    validators: {
                        emailAddress: {
                            message: 'Email non valide'
                        }
                    }
                },

                'username': {
                    validators: {
                        notEmpty: {
                            message: 'Nom d\'utilisateur est obligatoire'
                        }
                    }
                },

                'password': {
                    validators: {
                        notEmpty: {
                            message: 'Mot de passe est obligatoire'
                        },
                        stringLength: {
                            min: 6,
                            message: 'Le mot de passe doit avoir 6 caractères au minimum',
                        },
                    }
                },

                'group': {
                    validators: {
                        notEmpty: {
                            message: 'Groupe est obligatoire'
                        }
                    }
                },

                'profil-0-telephone_principal': {
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
                bootstrap: new FormValidation.plugins.Bootstrap5({
                        rowSelector: '.fv-row'
                }),
                submitButton: new FormValidation.plugins.SubmitButton(),
                // Submit the form when all fields are valid
                defaultSubmit: new FormValidation.plugins.DefaultSubmit(),
            }
        }
    );
});
