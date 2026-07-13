jQuery(document).ready(function () {

    const afficherAge = function (date) {
        const d = moment(date, 'DD/MM/YYYY');
        const age = moment().diff(d, 'years');
        $('#age').text(age + ' ans');
    };

    $('.back-btn').click(() => history.back());
    var nowDate = new Date();
    var DD =((nowDate.getDate() ) < 10 ? '0' : '') + (nowDate.getDate());
    var MM = ((nowDate.getMonth() + 1) < 10 ? '0' : '') + (nowDate.getMonth() + 1);
    $('#id_date_naissance').inputmask("datetime", {
        inputFormat: 'dd/mm/yyyy',
        placeholder: "jj/mm/aaaa",
        min: '01/01/1900',
        max: DD + '/' + MM + '/' + nowDate.getFullYear(),

    }).on('change', (e) => {
        afficherAge($(e.target).val());
    });
    $('.date_validite_mutuelle').inputmask("datetime", {
        inputFormat: 'dd/mm/yyyy',
        placeholder: "jj/mm/aaaa",
        //min: DD + '/' + MM + '/' + nowDate.getFullYear(),
    });
    $('#id_date_mariage').inputmask("datetime", {
        inputFormat: 'dd/mm/yyyy',
        placeholder: "jj/mm/aaaa",
        min: '01/01/1900',
        max: DD + '/' + MM + '/' + nowDate.getFullYear(),
    });

    $('#id_date_naissance_conjoint').inputmask("datetime", {
        inputFormat: 'dd/mm/yyyy',
        placeholder: "jj/mm/aaaa",
        min: '01/01/1900',
        max: DD + '/' + MM + '/' + nowDate.getFullYear(),

    });

    if ($('#id_date_naissance').val()) {
        afficherAge($('#id_date_naissance').val());
    }

    $('#id_code_medecin_famille').inputmask("99/99999999/99");

    $('#id_email').inputmask({
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
    });

    $('#id_fumeur')[0].checked ? $('#nombre_cigarettes_field').show() : $('#nombre_cigarettes_field').hide();
    $('#id_fumeur').change(function () {
        if (this.checked) {
            $('#nombre_cigarettes_field').show();
        } else {
            $('#nombre_cigarettes_field').hide();
        }
    });

    const fv = FormValidation.formValidation(
        document.getElementById('form_1'),
        {
            fields: {
                'prenom': {
                    validators: {
                        notEmpty: {
                            message: 'Prénom est obligatoire'
                        }
                    }
                },

                'nom_naissance': {
                    validators: {
                        notEmpty: {
                            message: 'Nom de naissance est obligatoire'
                        }
                    }
                },

                'date_naissance': {
                    validators: {
                        notEmpty: {
                            message: 'Date de naissance est obligatoire'
                        }
                    }
                },

                'telephone': {
                    validators: {
                        notEmpty: {
                            message: 'Téléphone est obligatoire'
                        },
                        numeric: {
                            message: 'Téléphone doit contenir des chiffres uniquement'
                        },
                        /*stringLength: {
                            min: 8,
                            max: 8,
                            message: 'Téléphone doit contenir 8 chiffres'
                        }*/
                    }
                },

                'telephone_secondaire': {
                    validators: {
                        numeric: {
                            message: 'Téléphone doit contenir des chiffres uniquement'
                        },
                    }
                },

                'email': {
                    validators: {
                        emailAddress: {
                            message: 'Email non valide'
                        }
                    }
                },

                'praticien_principal': {
                    validators: {
                        notEmpty: {
                            message: 'Praticien principal est obligatoire'
                        },
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
        }
    );

    fv.on('core.form.valid', function(event) {
        $('#btn-enregistrer').prop('disabled', true);
    });

});

