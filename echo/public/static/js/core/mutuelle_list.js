moment.locale('fr');

let minDate = moment().subtract(365, 'days');
let maxDate = moment().add(1, 'days');


/* Custom filtering function which will search data in column four between two values */
$.fn.dataTable.ext.search.push(
    function (settings, data, dataIndex, row) {
        let dt = moment(data[2], "DD/MM/YYYY");
        if (dt.isValid()) {
            dt = dt.set('minute', 1);
            console.log('Check date', dt.format('DD/MM/YY HH:mm'));
            //console.log('maxdate', maxDate, 'mindate', minDate);
            let date_ret = dt.isBefore(maxDate) && dt.isAfter(minDate);
            return date_ret;
        }
        return true;
    }
);
$(document).ready(function () {

    const initTable1 = function () {
        var table = $('#kt_datatable').DataTable({
            language: {
                "url": "/static/plugins/custom/datatables/French.json"
            },
            responsive: true,
            // read more: https://datatables.net/examples/basic_init/dom.html
            lengthMenu: [5, 10, 25, 50, 75, 100],
            pageLength: 10,
            searchDelay: 500,
            processing: true,
            serverSide: false,
            data: data,

            columns: [
                {
                    data: null, 'targets': 0,
                    'searchable': false,
                    'orderable': false,
                    'width': '50px',
                    'className': 'dt-body-center',
                    'render': function (data, type, full, meta) {
                        return '<input type="checkbox" class="reglement_mutuelle" name="reglements_ids[]" value="'
                            + $('<div/>').text(data.id).html() + '">';
                    }
                },
                {data: 'id'},
                {
                    data: 'date_creation',
                    render: function (data) {
                        return moment(data).format('DD/MM/YYYY');
                    }
                },
                {data: 'patient.num_carnet_soin'},
                {
                    data: 'patient.nom',
                    render: function (data, type, full, meta) {
                        return (full.patient.nom_naissance + ' ' + full.patient.prenom).toUpperCase();
                    },
                },
                {data: 'patient.lien_parente'},
                {data: 'patient.code_apci'},
                {
                    data: 'lignes_reglement',
                    render: function (data) {
                        return data[0].code;
                    },
                },
                {
                    data: 'lignes_reglement',
                    render: function (data) {
                        return data.length;
                    },
                },
                {
                    data: 'lignes_reglement',
                    render: function (data) {
                        total = data[0].prix_initial;
                        return total;
                    },
                },
                {
                    data: 'lignes_reglement',
                    render: function (data) {
                        prix_pec = data[0].prix_ttc;
                        return prix_pec;
                    },
                },
                {
                    data: 'lignes_reglement',
                    render: function (data) {
                        prix_cnam = data[0].prix_initial - data[0].prix_ttc;
                        return prix_cnam;
                    },
                },


                {data: 'patient.code_medecin_famille'},

            ],
            initComplete: function () {
                resetDates();
            },

            drawCallback: function (settings) {
                if (settings.fnRecordsDisplay() === 0) {
                    const data = _.map($('[data-search-key]').get(), el => $(el).attr('data-search-key') + '=' + $(el).val());
                }
            },

        });
    };

    initTable1();
    $('#reglements_ids').click(function (e) {
        var table = $(e.target).closest('table');
        $('td input:checkbox', table).prop('checked', this.checked);
    });
    const initTableBordereau = function () {

        const _t = _.template($('#actions-bordereau-template').html());

        const table = $('#datatable_bordereau').DataTable({
            language: {
                "url": "/static/plugins/custom/datatables/French.json"
            },
            responsive: true,
            // read more: https://datatables.net/examples/basic_init/dom.html
            lengthMenu: [5, 10, 25, 50],
            pageLength: 10,
            searchDelay: 500,
            processing: true,
            serverSide: false,

            data: bordereaux,

            columns: [
                {data: 'num_bordereau'},
                {data: 'nom_medecin'},
                {data: 'code_conventionnel'},
                {data: 'periode'},
                {data: null},
            ],

            order: [[0, "asc"]],
            columnDefs: [
                {
                    targets: 4,
                    title: 'Actions',
                    orderable: false,
                    width: '50px',
                    render: (data, type, full, meta) => _t({id: full.id}),
                }
            ],

            createdRow: (row, data, index) => {
                //console.log("Created row");
            }

        });

    };

    initTableBordereau();

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
        const tableMutulle = $('#kt_datatable').DataTable();
        tableMutulle.table().draw();
    });

    $("#kt_datatable").on('click', ':checkbox', e => {
        if ($('.reglement_mutuelle:checked').length > 0) {
            $('#btn_enregistrer').prop('disabled', false);
        } else {
            $('#btn_enregistrer').prop('disabled', true);
        }
    });

});

function resetSearch() {
    $('input').val('');
    resetDates();
}

function resetDates() {
    minDate = moment().subtract(365, 'days');
    maxDate = moment().add(1, 'days');
    var tabMutuelle = $('#kt_datatable').DataTable();
    tabMutuelle.table().draw();

}