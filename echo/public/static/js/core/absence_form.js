jQuery(document).ready(function () {
    $('#date_debut').datepicker({
        todayHighlight: true,
        autoclose: true,
        language: 'fr',
        weekStart: 1,
        format: 'dd/mm/yyyy'
    });


    $('#date_fin').datepicker({
        todayHighlight: true,
        autoclose: true,
        language: 'fr',
        weekStart: 1,
        format: 'dd/mm/yyyy'
    });

    const time_step = 5;

    $('#heure_debut').timepicker({
        timeFormat: 'HH:mm',
        interval: time_step,
        minTime: '7',
        maxTime: '22',
        startTime: '07:00',
        dynamic: false,
        dropdown: true,
        scrollbar: true,
    });

    $('#heure_fin').timepicker({
        timeFormat: 'HH:mm',
        interval: time_step,
        minTime: '7',
        maxTime: '22',
        startTime: '07:00',
        dynamic: false,
        dropdown: true,
        scrollbar: true
    });

});
