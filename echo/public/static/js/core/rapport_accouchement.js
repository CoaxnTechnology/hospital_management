moment.locale('fr');

let minDate = moment().subtract(100, 'days');
let maxDate = moment().add(500, 'days');
let terme = 1;


/* Custom filtering function which will search data in column four between two values */
$.fn.dataTable.ext.search.push(
    function (settings, data, dataIndex) {
        const dt = moment(data[8], "DD/MM/YYYY").set('minute', 1);
        //console.info('Terme compare', data[4], terme, data[4] >= terme);
        let date_ret = dt.isBefore(maxDate) && dt.isAfter(minDate) && parseInt(data[4]) >= terme;
        return date_ret;
    }
);

jQuery(document).ready(function () {

    const initTableAccouchement = function () {
        // begin first table
        const _t = _.template(unescapeTemplate($('#actions-rapport-accouchement-template').html()));

        var table = $('#rapport_accouchement_datatable').DataTable({
            language: {
                "url": "/static/plugins/custom/datatables/French.json"
            },
            responsive: true,

            // read more: https://datatables.net/examples/basic_init/dom.html
            buttons: [
                {
                    extend: 'excel',
                    text: 'Export Excel',
                    exportOptions: {
                        columns: [0, 3, 4, 5, 6, 7, 8, 9]
                    }
                }
            ],
            // read more: https://datatables.net/examples/basic_init/dom.html
            lengthMenu: [5, 10, 25, 50],
            pageLength: 25,
            searchDelay: 500,
            processing: true,
            serverSide: false,
            data: data,
            order: [[0, "asc"]],
            columns: [
                {data: 'patient.identifiant_unique'},
                {data: 'patient.nom', width: '200px'},
                {data: 'patient.prenom', width: '150px'},
                {
                    data: 'ddr',
                    render: (data, type, full, meta) => data ? moment(data).format('DD/MM/YYYY') : '-'
                },
                {
                    data: 'cycle', "visible": false,
                    render: function (data, type, full, meta) {
                        return full.ddr ? calcTermeSA(moment(full.ddr, 'YYYY-MM-DD'), full.cycle) : '';
                    }
                },
                {
                    data: 'cycle', width: '120px',
                    render: function (data, type, full, meta) {
                        return full.ddr ? calcTerme(moment(full.ddr, 'YYYY-MM-DD'), full.cycle) : '';
                    }
                },
                {data: 'type_grossesse', width: '200px'},
                {
                    data: 'lieu_accouchement',
                    render: (data, type, full, meta) => data ? data.nom : '-'
                },
                {
                    data: 'cycle',
                    render: function (data, type, full, meta) {
                        return calcDateAccouchement(moment(full.ddr, 'YYYY-MM-DD'), full.cycle);
                    }
                },
                {data: null},
            ],
            columnDefs: [
                {
                    targets: 9,
                    title: 'Actions',
                    orderable: false,
                    width: '50px',
                    render: (data, type, full, meta) => _t({id: full.patient.id}),

                }
            ],
            initComplete: function () {
                terme = 1;
                resetDates();
                //chercher();
            },

            drawCallback: function (settings) {
                if (settings.fnRecordsDisplay() === 0) {
                    const temp = _.template($('#creer-patient-template').html());
                    const data = _.map($('[data-search-key]').get(), el => $(el).attr('data-search-key') + '=' + $(el).val());
                    const html = temp({params: '&' + data.join('&')});
                    $('.dataTables_empty').html(html);
                }
            },

        });
        $('input,select').on('keyup', chercher);
        $('input,select').on('change', chercher);

        function chercher() {
            terme = parseInt($('#terme').val());
            table.table().draw();
        }


    };

    initTableAccouchement();
});

function resetDates() {
    minDate = moment().subtract(100, 'days');
    maxDate = moment().add(500, 'days');
    var tabAcc = $('#rapport_accouchement_datatable').DataTable();
    tabAcc.table().draw();

}

$('#daterangepicker').daterangepicker({
    buttonClasses: ' btn',
    applyClass: 'btn-primary',
    cancelClass: 'btn-light-primary',
    "locale": {
        "applyLabel": "Appliquer",
        "cancelLabel": "Fermer",
    }
}, function (start, end, label) {
    $('#daterangepicker .form-control').val(start.format('DD/MM/YYYY') + ' - ' + end.format('DD/MM/YYYY'));
    minDate = moment(start, 'YYYY-MM-DD');
    maxDate = moment(end, 'YYYY-MM-DD');
    const tableAccouchement = $('#rapport_accouchement_datatable').DataTable();
    tableAccouchement.table().draw();
});

function filtrerDate(el, event, dateIndex) {
    event.preventDefault();
    switch (dateIndex) {
        case 0:
            minDate = moment();
            maxDate = moment().add(270, 'days');
            $('#date_range_input').val('');
            break;
        case 1:
            minDate = moment();
            maxDate = moment().endOf('month');
            $('#date_range_input').val('');
            break;
        case 2:
            let nextMonth = moment().endOf('month').add(1, 'seconds');
            minDate = nextMonth;
            maxDate = nextMonth.clone().endOf('month');
            $('#date_range_input').val('');
            break;
    }
    $('#dates-filtre .nav-link').removeClass('active');
    $(el).addClass('active');
    const tableAccouchement = $('#rapport_accouchement_datatable').DataTable();
    tableAccouchement.table().draw();

}

function resetSearch() {
    $('input').val('');
    terme = 1;
    resetDates();
}

function afficherHistorique(id) {
    showFrameLoading();
    $('#historique-consultations-modal iframe').attr('src', `/patients/${id}/consultations/`);
    bootstrap.Modal.getOrCreateInstance('#historique-consultations-modal').show();
}
