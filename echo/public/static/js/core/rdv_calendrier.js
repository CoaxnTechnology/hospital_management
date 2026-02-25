let g_cal;

moment.locale('fr');

let minDate = moment().startOf('day');
let maxDate = moment().add(180, 'days');
let date_selectionnee = moment();

/* Custom filtering function which will search data in column four between two values */
$.fn.dataTable.ext.search.push(
    function( settings, data, dataIndex ) {
        //console.log(`Filtre entre ${minDate.format('DD/MM/YY HH:mm')} et ${maxDate.format('DD/MM/YY HH:mm')}`);
        const dt = moment(data[0], "DD/MM/YYYY").set('minute', 1);
        //console.log('Check date', dt.format('DD/MM/YY HH:mm'));
        return dt.isBefore(maxDate) && dt.isAfter(minDate);
    }
);

function classParStatutRdv(statut, motif) {
    let cls = "fc-event-type-" + statut;
    if (motif == 'Consultation') cls += ' fc-event-thick-border';
    return cls;
}

function supprimer(pk) {
    swal.fire({
        title: "Etes vous sûr ?",
        type: "warning",
        showCancelButton: true,
        confirmButtonClass: "btn-danger",
        confirmButtonText: "Oui, annuler le rendez-vous!",
        cancelButtonText: "Non, conserver le rendez-vous",
        closeOnConfirm: false
    }).then(function (result) {
        if (result.value) {
            window.location.replace("/rdvs/" + pk + "/supprimer/?next=/rdvs/#liste");
        }
    });
}

function filtrerDate(el, event, dateIndex) {
    event.preventDefault();
    switch (dateIndex) {
        case 0:
            minDate = moment().startOf('day');
            maxDate = moment().add(180, 'days');
            break;
        case 1:
            minDate = moment().startOf('day');
            maxDate = moment().endOf('day');
            break;
        case 2:
            minDate = moment().add(1, 'days').startOf('day');
            maxDate = moment().add(1, 'days').endOf('day');
            break;
        case 3:
            minDate = moment().add(2, 'days').startOf('day');
            maxDate = moment().add(2, 'days').endOf('day');
            break;
        case 4:
            minDate = moment();
            maxDate = moment().endOf('week');
            break;
        case 5:
            let nextWeek = moment().endOf('week').add(1, 'seconds');
            minDate = nextWeek;
            maxDate = nextWeek.clone().endOf('week');
            break;
    }

    $('#dates-filtre .nav-link').removeClass('active');
    $(el).addClass('active');
    const tableRdvs = $('#datatable_rdv').DataTable();
    tableRdvs.table().draw();
}

jQuery(document).ready(function () {

    //_.templateSettings.interpolate = /%%([\s\S]+?)%%/g;
    const tpl = _.template(unescapeTemplate($('#popover-template').html()));

    const eves1 = _.map(rdvs, rdv => {
        let title = rdv.nom_naissance ? rdv.nom_naissance : rdv.nom;
        title += ` ${rdv.prenom}`;
        return {
            id: rdv.pk,
            title: title,
            start: rdv.debut,
            end: rdv.fin,
            className: classParStatutRdv(rdv.statut, rdv.motif),
            description: tpl(rdv),
            url: '/rdvs/' + rdv.pk + '/modifier'
        }
    });

    const eves2 = _.map(absences, absence => {
        const motif  = absence.motif ? absence.motif : '-';
        const praticien_remplacant  = absence.praticien_remplacant ? absence.praticien_remplacant : '-';
        const titre = `${absence.praticien} \n Motif: ${motif}\n Remplaçant: ${praticien_remplacant}`;
        return {
            id: absence.pk,
            title: titre,
            start: absence.date_debut,
            end: absence.date_fin,
            className: "fc-event-type-absence",
            description: '',
            url: `/absences/${absence.pk}/modifier`
        };
    });

    const eves3 = _.map(programmes_operatoire, po => {
        //console.log('Pro', po);
        let title = po.praticien ? `${po.praticien.nom}\n` : '';
        title += po.patient ? `${po.patient.nom_complet}\n` : '';
        title += po.type_acte ? `${po.type_acte}\n` : '';
        title += po.lieu_accouchement ? `${po.lieu_accouchement.nom}\n` : '';
        return {
            id: po.id,
            title: title,
            start: po.debut,
            end: po.fin,
            className: "fc-event-type-programme-operatoire",
            description: '',
            url: `/programme_operatoire/${po.id}/modifier`
        };
    });

    var todayDate = moment().startOf('day');
    var YM = todayDate.format('YYYY-MM');
    var YESTERDAY = todayDate.clone().subtract(1, 'day').format('YYYY-MM-DD');
    var TODAY = todayDate.format('YYYY-MM-DD');
    var TOMORROW = todayDate.clone().add(1, 'day').format('YYYY-MM-DD');

    let isDragging = false;
    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        //plugins: ['bootstrap', 'interaction', 'dayGrid', 'timeGrid', 'list', 'momentTimezonePlugin '],
        //themeSystem: 'bootstrap',
        locale: 'fr',
        isRTL: KTUtil.isRTL(),

        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },

        height: window.innerHeight - 140,
        /*contentHeight: '200px',*/
        /*aspectRatio: 2,*/

        nowIndicator: true,
        now: moment().format(),

        slotDuration: duree_defaut, // https://fullcalendar.io/docs/duration-object
        scrollTime: moment().subtract(120, 'minutes').format('hh:mm:ss'),

        businessHours: {
            daysOfWeek: [1, 2, 3, 4, 5, 6],
            startTime: '08:00', // 7h -> 22h
            endTime: '21:00',
        },

        minTime: '8:00',
        maxTime: '21:00',

        initialView: KTUtil.isMobileDevice() ? 'timeGridDay' : 'timeGridWeek',
        defaultDate: TODAY,

        editable: true, //https://fullcalendar.io/docs/event-dragging-resizing
        eventOverlap: false,
        eventDurationEditable: false,
        selectable: true, // https://fullcalendar.io/docs/selectable
        eventLimit: true, // allow "more" link when too many events
        navLinks: true,
        selectLongPressDelay: 100,

        slotLabelFormat: {
            hour: 'numeric',
            minute: '2-digit',
            omitZeroMinute: false,
            meridiem: 'short'
        },

        select: function (info) {
            //alert('selected ' + info.startStr + ' to ' + info.endStr);
            //info.dayEl.style.backgroundColor = 'red';
            console.log('Selected cell');
            if (moment(info.startStr).isBefore(moment())) return;
            //$('#dialog').modal();
            $('#date').text(moment(info.startStr).format('dddd DD MMMM'));
            $('#from').text(moment(info.startStr).format('HH:mm'));
            $('#to').text(moment(info.endStr).format('HH:mm'));
            debut = info.startStr.replace('+', '%2b');
            fin = info.endStr.replace('+', '%2b');
            //$('#lien_creer').attr('href', `rdvs/ajouter?debut=${debut}&fin=${fin}`);
            $('#rdv-modal iframe').attr('src', `/rdvs/ajouter?debut=${debut}&fin=${fin}`);
            bootstrap.Modal.getOrCreateInstance('#rdv-modal').show();
        },

        events: eves1.concat(eves2,eves3),

        eventClick: function (info) {
            console.log('Event: ' + info.event.title);
            console.log('Coordinates: ' + info.jsEvent.pageX + ',' + info.jsEvent.pageY);
            console.log('View: ' + info.view.type);
            console.log('link', info.event.url);
            $('#rdv-modal iframe').attr('src', info.event.url);
            bootstrap.Modal.getOrCreateInstance('#rdv-modal').show();
            info.jsEvent.preventDefault();
        },

        eventDragStart: function () {
            isDragging = true;
        },

        eventDragEnd: function () {
            isDragging = false;
        },

        eventRender: function (info) {
            //if (isDragging) return;
            //console.log('Event render ', info);
            var element = $(info.el);
            element.css('margin:', '0px');
            element.data('title', info.event.title);
            element.data('content', info.event.extendedProps.description);
            element.data('placement', 'top');
            //KTApp.initPopover(element);
        },

        viewRender: function () {
            console.log('viewRender');
        },

        eventDrop: function (info) {
            swal.fire({
                title: `Déplacer le rendez-vous au ${moment(info.event.start).format('DD MMM à HH:mm')} ?`,
                type: "warning",
                showCancelButton: true,
                confirmButtonClass: "btn-danger",
                confirmButtonText: "Oui, déplacer le rendez-vous",
                cancelButtonText: "Non",
                closeOnConfirm: false
            }).then(function (result) {
                if (result.value) {
                    const debut = moment(info.event.start).format('YYYY-MM-DD HH:mm');
                    const fin = moment(info.event.end).format('YYYY-MM-DD HH:mm');
                    $.post(`/rdvs/${info.event.id}/modifier_horaire/`, {
                        'debut': debut,
                        'fin': fin,
                    })
                        .done(function (result) {
                            console.log("Rdv modifié avec succès");
                            //html = `<li class="list-group-item"><span class="font-weight-bolder">Dr ${praticien.nom} ${praticien.prenom}</span><br><span class="text-muted">${praticien.specialite}</span></li>`;
                            //$('.praticiens-list').append(html);
                        })
                        .fail(function () {
                            console.error("Impossible de modifier le rdv");
                        })
                        .always(function () {
                        });
                } else {
                    info.revert();
                }
            });
        },
    });

    calendar.render();

    $('#mobile-datepicker').val(moment().format('DD/MM/yyyy'));

    $('.fc-timegrid-slot-label-cushion:contains("00")').css('font-weight', 'bold').css('font-size', '1rem');

    $('a[href="#calendrier"]').on('shown.bs.tab', function (e) {
        calendar.render();
    });

    $('a[href="#liste"]').on('shown.bs.tab', function (e) {
        const tableRdvs = $('#datatable_rdv').DataTable();
        tableRdvs.table().draw();
        //console.log('Tab shown');
    });

    const url = window.location.href;
    const activeTab = url.substring(url.indexOf("#") + 1);
    if (activeTab) {
        //ole.log('Active tab', activeTab);
        // Activer le calendrier ou la liste en fonction de l'url
        $('a[href="#' + activeTab + '"]').tab('show');

        if (activeTab === 'liste') {

        } else {
            calendar.render();
        }
    } else {
        calendar.render();
    }

    g_cal = calendar;

    var arrows;
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

    $('.datepicker').datepicker({
        rtl: KTUtil.isRTL(),
        todayHighlight: true,
        templates: arrows,
        language: 'fr',
        weekStart: 1
    }).on('changeDate', (e) => {
        calendar.gotoDate(e.format('yyyy-mm-dd'));
    });

    $('#mobile-datepicker').datepicker({
        rtl: KTUtil.isRTL(),
        todayHighlight: true,
        templates: arrows,
        language: 'fr',
        format: 'dd/mm/yyyy',
        weekStart: 1,
        autoclose: true,
    }).on('changeDate', (e) => {
        calendar.gotoDate(e.format('yyyy-mm-dd'));
    });

    Inputmask("datetime", {
        inputFormat: 'dd/mm/yyyy',
        placeholder: "jj/mm/aaaa",
        min: '01/01/1900',
        max: '31/12/2900',
    }).mask(document.querySelectorAll('.date'));

    $('#btn_aujourdhui').click(() => {
        date_selectionnee = moment();
        $('#mobile-datepicker').datepicker('update', new Date());
        calendar.gotoDate(date_selectionnee.format('YYYY-MM-DD'));
    });

    $('#btn_jour_precedent').click(() => {
        date_selectionnee = date_selectionnee.subtract(1, 'days');
        const jour = date_selectionnee.format('DD/MM/yyyy');
        //ole.log('Date ', jour);
        $('#mobile-datepicker').datepicker('update', jour);
        calendar.gotoDate(date_selectionnee.format('YYYY-MM-DD'));
    });

    $('#btn_jour_suivant').click(() => {
        date_selectionnee = date_selectionnee.add(1, 'days');
        const jour = date_selectionnee.format('DD/MM/yyyy');
        $('#mobile-datepicker').datepicker('update', jour);
        calendar.gotoDate(date_selectionnee.format('YYYY-MM-DD'));
    });

    $('#lien_creer').click((e) => {
        e.preventDefault();
        $('#rdv-modal iframe').attr('src', $(e.target).attr('href'));
        bootstrap.Modal.getOrCreateInstance('#rdv-modal').show();
        bootstrap.Modal.getOrCreateInstance('#dialog').hide();
    });

    const rdvs_ouverts = _.filter(rdvs_futurs, rdv => rdv.statut == 1 || rdv.statut == 2);
    console.log("RDV ouverts", rdvs_ouverts)

    const initTableRdvs = function () {

        const _t = _.template($('#actions-rdv-template').html());

        const tableRdvs = $('#datatable_rdv').DataTable({
            language: {
                "url": "/static/plugins/custom/datatables/French.json"
            },
            responsive: true,
            // Pagination settings
            //dom: `<'row'<'col-sm-12'tr>><'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7 dataTables_pager'lp>>`,
            // read more: https://datatables.net/examples/basic_init/dom.html

            lengthMenu: [25, 50, 75, 100],
            pageLength: 50,

            searchDelay: 500,
            processing: true,
            serverSide: false,

            data: rdvs_ouverts,

            columns: [
                {data: 'debut'},
                {data: 'debut'},
                {data: 'nom_naissance'},
                {data: 'prenom'},
                {data: 'ville'},
                {data: 'telephone'},
                {data: null},
            ],

            order: [[0, "asc"]],

            columnDefs: [
                {
                    targets: 6, title: 'Actions', orderable: false, width: '150px',
                    render: function (data, type, full, meta) {
                        return _t({id: full.pk});
                    }
                },
                {
                    targets: 0, width: '80px',
                    render: (data, type, full, meta) => {
                        // https://datatables.net/forums/discussion/45692/how-to-date-sort-as-date-instead-of-string
                        return type === 'sort' ? data : moment(data).format('DD/MM/YYYY');
                    },
                },
                {
                    targets: 1, width: '80px',
                    render: (data, type, full, meta) => moment(data).format('HH:mm'),
                },
                {targets: 2, width: '360px'},
                {targets: 3, width: '320px'},
                {targets: 4, width: '100px'},
                {targets: 5, width: '100px'}
            ],
        });

        $('#kt_search').on('click', function (e) {
            e.preventDefault();
            var params = {};
            $('.datatable-input').each(function () {
                var i = $(this).data('col-index');
                if (params[i]) {
                    params[i] += '|' + $(this).val();
                } else {
                    params[i] = $(this).val();
                }
            });
            $.each(params, function (i, val) {
                // apply search params to datatable
                tableRdvs.column(i).search(val ? val : '', false, false);
            });
            tableRdvs.table().draw();
        });

        $('.datatable-input').on('keyup', e => {
            var params = {};
            $('.datatable-input').each(function () {
                var i = $(this).data('col-index');
                if (params[i]) {
                    params[i] += '|' + $(this).val();
                } else {
                    params[i] = $(this).val();
                }
            });
            $.each(params, function (i, val) {
                // apply search params to datatable
                tableRdvs.column(i).search(val ? val : '', false, false);
            });
            tableRdvs.table().draw();
        });

        $('#kt_reset').on('click', function (e) {
            e.preventDefault();
            $('.datatable-input').each(function () {
                $(this).val('');
                tableRdvs.column($(this).data('col-index')).search('', false, false);
            });
            tableRdvs.table().draw();
        });

    };

    initTableRdvs();

});
