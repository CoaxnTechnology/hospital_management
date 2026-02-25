let arrows;
if (KTUtil.isRTL()) {
    arrows = {
        leftArrow: '<i class="la la-angle-right"></i>',
        rightArrow: '<i class="la la-angle-left"></i>'
    }
} else {
    arrows = {
        leftArrow: '<i class="la la-angle-left"></i>',
        rightArrow: '<i class="la la-angle-right"></i>'
    }
}

function filtrerDate(date) {
    window.location.replace(`/rdvs/dispo/ajouter/?patient=${patient}&debut=${date}`);
}

function afficherMatin(event) {
    $('#mat').addClass('d-flex').removeClass('d-none');
    $('#am').removeClass('d-flex').addClass('d-none');
}

function afficherApresmidi(event) {
    $('#mat').addClass('d-none').removeClass('d-flex');
    $('#am').removeClass('d-none').addClass('d-flex');
}

function minutesOfDay(dt) {
    return dt.minutes() + dt.hours() * 60;
}

$(document).ready(() => {
    let slots_per_day_mat = {};
    let slots_per_day_am = {};
    for (let i = 0; i < slots.length; i++) {
        let day = moment(slots[i]).format('ddd <br>D MMM'); //startOf('day').toISOString();
        if (minutesOfDay(moment(slots[i])) < (13*60 - 1)) {
            // heure < 13h
            if (_.isUndefined(slots_per_day_mat[day])) slots_per_day_mat[day] = [];
            slots_per_day_mat[day].push(slots[i]);
        } else {
            // heure >= 13h
            if (_.isUndefined(slots_per_day_am[day])) slots_per_day_am[day] = [];
            slots_per_day_am[day].push(slots[i]);
        }
    }
    //console.log(slots_per_day_mat);

    const tpl = _.template($('#cal-template').html());
    $('#mat').html(tpl({slots: slots_per_day_mat}));
    $('#am').html(tpl({slots: slots_per_day_am}));

    $('[data-slot]').click(e => {
        $('#id_debut').val(moment($(e.target).attr('data-slot')).format('YYYY-MM-DD HH:mm'));
        $('#form').submit();
    });

    $('#date-debut').datepicker({
        todayHighlight: true,
        autoclose: true,
        language: 'fr',
        weekStart: 1,
        format: 'dd/mm/yyyy',
        startDate: '1d',
        templates: arrows
    }).on('changeDate', function (e) {
        filtrerDate(e.format('yyyy-mm-dd'));
    });

});