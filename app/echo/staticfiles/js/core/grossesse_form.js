let targetSelect = null;

function afficherLieuAccouchement() {
    if (['H', 'C'].includes($('#id_lieu_accouchement_principal').val())) {
        $('#lieu_accouch_precis').removeClass('d-none');
    } else {
        $('#lieu_accouch_precis').addClass('d-none');
    }

    if (['A'].includes($('#id_lieu_accouchement_principal').val())) {
        $('#lieu_accouch_libre').removeClass('d-none');
    } else {
        $('#lieu_accouch_libre').addClass('d-none');
    }
}

function updateFoetus() {
    $('#id_type_grossesse_v2').prop('disabled', 'disabled');
    const val = $('#id_nb_foetus').find(":selected").val();
    if (val == 'unique' || val == '') {
        $('.foetus_2, .foetus_3').addClass('d-none');
        $('#id_type_grossesse_v2').prop('disabled', 'disabled');
        $('#id_type_grossesse_v2').val('');
    }
    if (val == 'gemellaire') {
        $('.foetus_3').addClass('d-none');
        $('.foetus_2').removeClass('d-none');
        $('#id_type_grossesse_v2').prop('disabled', false);
    }
    if (val == 'triple') {
        $('.foetus_2, .foetus_3').removeClass('d-none');
        $('#id_type_grossesse_v2').prop('disabled', false);
    }
}

function calcImc() {
    const poids = $('#id_poids_avant_grossesse').val();
    const taille = $('#id_taille').val();
    if (poids && taille) {
        $('#imc').val(Number.parseFloat(100 * 100 * poids / (taille * taille)).toFixed(1));
    }
}

function updateTermeTheorique() {
    const cycle = $('#id_cycle').val();

    if ($('#id_ddr').val()) {
        const ddr = moment($('#id_ddr').val(), 'DD/MM/YYYY');
        const ddg = calcDDG(ddr.clone(), cycle);
        $('#ddg_theorique').val(ddg);
        const terme = calcTerme(ddr.clone(), cycle);
        $('#terme-theorique').text(terme);
    }

    if ($('#id_ddr_corrige').val()) {
        const ddr_cor = moment($('#id_ddr_corrige').val(), 'DD/MM/YYYY');
        const ddg_cor = calcDDG(ddr_cor.clone(), cycle);
        $('#id_ddg_corrige').val(ddg_cor);
        const terme_cor = calcTerme(ddr_cor.clone(), cycle);
        $('#terme-corrige').text(terme_cor);
    } else {
        $('#id_ddg_corrige').val('');
    }
}

function updateTermeTheoriqueDDG() {
    const cycle = $('#id_cycle').val();
    if ($('#ddg_theorique').val()) {
        const ddg = moment($('#ddg_theorique').val(), 'DD/MM/YYYY');
        const ddr = calcDDR(ddg.clone(), cycle);
        $('#id_ddr').val(ddr);
        const terme = calcTermeDDG(ddg.clone(), cycle);
        $('#terme-theorique').text(terme);
    }

    if ($('#id_ddg_corrige').val()) {
        const ddg_cor = moment($('#id_ddg_corrige').val(), 'DD/MM/YYYY');
        const ddr_cor = calcDDR(ddg_cor.clone(), cycle);
        $('#id_ddr_corrige').val(ddr_cor);
        const terme_cor = calcTermeDDG(ddg_cor.clone(), cycle);
        $('#terme-corrige').text(terme_cor);
    }
}

function selectionnerEtablissement() {
    showFrameLoading();
    $('#etablissements-modal iframe').attr('src', `/etablissements`);
    $('#etablissements-modal').modal();
}

$(document).ready(() => {
    $('.date').inputmask("datetime", {
        inputFormat: 'dd/mm/yyyy',
        placeholder: "jj/mm/aaaa",
        min: '01/01/1900',
        max: '31/12/2900',
    });

    $('#t21-container').css('display', $('#id_test_t21_fait').is(":checked") ? 'flex' : 'none');
    $('#id_test_t21_fait').on('change', e => {
        $('#t21-container').css('display', $('#id_test_t21_fait').is(":checked") ? 'flex' : 'none');
    });

    var nowDate = new Date();
    var DD = ((nowDate.getDate()) < 10 ? '0' : '') + (nowDate.getDate());
    var MM = ((nowDate.getMonth() + 1) < 10 ? '0' : '') + (nowDate.getMonth() + 1);
    $('#id_date_naissance_conjoint').inputmask("datetime", {
        inputFormat: 'dd/mm/yyyy',
        placeholder: "jj/mm/aaaa",
        min: '01/01/1900',
        max: DD + '/' + MM + '/' + nowDate.getFullYear(),
    });

    $('#id_ddr, #id_ddr_corrige').inputmask("datetime", {
        inputFormat: 'dd/mm/yyyy',
        placeholder: "jj/mm/aaaa",
        min: '01/01/1900',
        max: DD + '/' + MM + '/' + nowDate.getFullYear(),
    });

    $('#btn_annuler').click(e => {
        window.parent.fermerAntecedentObstetrique();
    });

    $('#id_poids_avant_grossesse, #id_taille').change(() => {
        calcImc();
    });

    calcImc();

    $('#id_ddr, #id_ddr_corrige').change(() => {
        updateTermeTheorique();
    });

    $('#ddg_theorique, #id_ddg_corrige').change(() => {
        updateTermeTheoriqueDDG();
    });

    $('#id_cycle').change(() => {
        updateTermeTheorique();
    });

    if (grossesse != -1) {
        updateTermeTheorique();
    }

    $('#id_nb_foetus').change(() => {
        updateFoetus();
    });
    updateFoetus();

    afficherLieuAccouchement();
    $('#id_lieu_accouchement_principal').change(e => afficherLieuAccouchement());

    $('select').contextmenu(e => {
        e.preventDefault();
        targetSelect = null;
        let formulaire = $(e.target).attr('data-form');
        let champ = $(e.target).attr('data-champ');
        if (formulaire && champ) {
            showFrameLoading();
            $('#liste-choix-modal iframe').attr('src', `/listes/?formulaire=${formulaire}&champ=${champ}`);
            $('#liste-choix-modal').modal();
            targetSelect = $(e.target);
        }
    });

    const fv = FormValidation.formValidation(
        document.getElementById('form_1'),
        {
            fields: {
                /*'type_grossesse': {
                    validators: {
                        notEmpty: {
                            message: 'Type de grossesse est obligatoire'
                        }
                    }
                },*/
                /*'poids_avant_grossesse': {
                    validators: {
                        notEmpty: {
                            message: 'Poids avant grossesse est obligatoire'
                        }
                    }
                },*/
                'telephone_conjoint': {
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
                }
            },

            plugins: {
                trigger: new FormValidation.plugins.Trigger(),
                bootstrap: new FormValidation.plugins.Bootstrap(),
                submitButton: new FormValidation.plugins.SubmitButton(),
                defaultSubmit: new FormValidation.plugins.DefaultSubmit()
            }
        }
    );

    fv.on('core.form.valid', function (event) {
        $('#btn_enregistrer').prop('disabled', true);
        //$('#form_1').submit();
    });

    EventManager.subscribe("etablissement:selected", function (event, payload) {
        console.info('Event etablissement:selected', event, payload);
        $('#id_lieu_accouchement').val(payload.id);
        $('#lieu_disp').removeClass('d-none').val(payload.nom);
        $('#btn-selection-etablissement').text('Modifier');
    });

    EventManager.subscribe("liste:updated", function (event, payload) {
        console.info('Event liste:updated', event, payload);
        let sel = $(`select[data-form="${payload.formulaire}"][data-champ="${payload.champ}"]`);
        let selectedVal = sel.val();
        sel.empty();
        sel.append('<option value="" selected="">---------</option>');
        payload.liste.forEach(item => {
            let opt = `<option value="${item.id}">${item.libelle}</option>`;
            sel.append(opt);
        });
        console.log('Selected value', selectedVal);
        if (_.find(payload.liste, l => l.id == selectedVal)) {
            console.log('Setting selected value', selectedVal);
            sel.val(selectedVal);
        }
    });

    EventManager.subscribe("liste:selected", function (event, listechoix) {
        console.info('Event liste:selected', event, listechoix);
        if (targetSelect) {
            targetSelect.val(`${listechoix.id}`);
        }
    });

});