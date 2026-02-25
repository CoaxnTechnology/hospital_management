let saveUrl = () => interrogatoireId == -1
    ? `/patients/${patientId}/interrogatoire-pma/ajouter/`
    : `/interrogatoire-pma/${interrogatoireId}/modifier/`;

function ajouterLigne(modelName) {
    let form_idx = parseInt($(`#id_${modelName}-TOTAL_FORMS`).val());
    let row = $(`#${modelName}-template`).html().replace(/__prefix__/g, form_idx).replace(/__title__/g, form_idx+1);
    $(`#${modelName}-list`).append(row);
    $(`#id_${modelName}-TOTAL_FORMS`).val(parseInt(form_idx) + 1);
    resetDatePickers();
}

function supprimerLigne(modelName, event, idx) {
    $(event.target).parents(`.${modelName}-item`).addClass('d-none');
    $('form').append(`<input type="hidden" name="${modelName}-${idx-1}-DELETE" value="on">`);
    // updateEditor();
}

function enregistrer() {
    $('#libelle_statut')
        .toggleClass('label-success', false)
        .text('Brouillon')
        .show();

    let baseData = {
        'consultation_pk': interrogatoireId,
        //'text': editor.getContent(),
        'patient': patientId,
        'praticien': $('#id_praticien').val()
    };

    let data = $.param(baseData) + '&' + $('#form_1').serialize();

    //console.info('Post data', data);
    $.post(saveUrl(), data)
        .done(function (result) {
            interrogatoireId = result.id;
            dateEdition = moment(result.date).format('DD/MM/YYYY');
            console.log('Succes', result);
            $('#libelle_statut')
                .toggleClass('label-success', true)
                .text('Enregistré')
                .show();
            $('#btn_terminer').removeClass('d-none');
            $('.enregistrer').addClass('d-none');
        })
        .fail(function () {
            console.error('Impossible de sauvegarder');
        })
        .always(function () {

        });
}

function resetDatePickers() {
    $('.date').datepicker({
        todayHighlight: true,
        autoclose: true,
        language: 'fr',
        weekStart: 1,
        format: 'dd/mm/yyyy',
        orientation: 'bottom',
    });
}

function selectionnerEtablissement() {
    showFrameLoading();
    $('#etablissements-modal iframe').attr('src', `/etablissements`);
    bootstrap.Modal.getOrCreateInstance('#etablissements-modal').show();
}

$(document).ready(() => {

    resetDatePickers();

    initTimer();

    if (interrogatoireId != -1) {
        $('#libelle_statut')
            .toggleClass('label-success', true)
            .text('Enregistré')
            .show();
    } else {
        $('#libelle_statut')
            .toggleClass('label-success', false)
            .text('Brouillon')
            .show();
    }

    $("#btn_enregistrer").click(() => enregistrer());

    $('#id_sperme_congenalation').change(e => {
        if (e.target.checked) {
            $('#lieu_congelation').removeClass('d-none');
        } else {
            $('#lieu_congelation').addClass('d-none');
        }
    });

    if ($('#id_sperme_congenalation').is(':checked'))
        $('#lieu_congelation').removeClass('d-none');

    window.parent.EventManager.subscribe("etablissement:selected", function (event, payload) {
        console.info('Event etablissement:selected', event, payload);
        $('#id_sperme_congenalation_clinique').val(payload.id);
        $('#lieu_disp').removeClass('d-none').val(payload.nom);
        $('#btn-selection-etablissement').text('Modifier');
    });


});