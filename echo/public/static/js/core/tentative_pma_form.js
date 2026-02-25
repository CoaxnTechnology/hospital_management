let saveUrl = () => tentativeId == -1
    ? `/patients/${patientId}/tentative-pma/ajouter/`
    : `/tentative-pma/${tentativeId}/modifier/`;

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
        'consultation_pk': tentativeId,
        //'text': editor.getContent(),
        'patient': patientId,
        'praticien': $('#id_praticien').val()
    };

    let data = $.param(baseData) + '&' + $('#form_1').serialize();

    //console.info('Post data', data);
    $.post(saveUrl(), data)
        .done(function (result) {
            tentativeId = result.id;
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
            saving = false;
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
    }).on('changeDate', function (e) {
        let dt = moment(e.format('yyyy-mm-dd'));
        $('.date').each((idx, el) => {
            let d = dt.clone().add(idx, 'days').format('DD/MM/yyyy');
            console.log('here', idx, d);
            $(el).val(d);
        });
    });
}

let saving = false;
let saveTimeout;

$(document).ready(() => {

    if (archive) {
        $('input, select, textarea').prop( "disabled", true );
        $('#libelle_statut')
            .toggleClass('label-success', true)
            .text('Clôturé')
            .show();
        return;
    }

    resetDatePickers();

    initTimer();

    if (tentativeId != -1) {
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

    $('.traitement-select').change(e => {
        $el = $(e.target);
        let row = $el.attr('data-id');
        $(`.traitement-val[data-id="${row}"]`).each( (idx, el) => {
            let container = $(el);
            $traitement = container.children().first();
            $traitement.val($el.val());
        });
    });

    $('.traitement-select').each((idx, el) => {
        let rang = $(el).attr('data-id');
        let traitementId = $(`.traitement-val[data-id="${rang}"]`).children().first().val();
        $(el).val(traitementId);
    });

    $('.form-control,input').on('change keyup', e => {
        $('#libelle_statut')
            .toggleClass('label-success', false)
            .text('Brouillon')
            .show();

        if (saving) {
            if (saveTimeout) {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(() => {
                    enregistrer();
                }, 2000);
            }
            return;
        }
        saving = true;
        saveTimeout = setTimeout(() => {
            enregistrer();
        }, 2000);
    });

});