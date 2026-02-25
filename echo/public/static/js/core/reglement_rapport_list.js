let pdfDoc;

let minDate = moment().startOf('month');
let maxDate = moment().endOf('month');


$.fn.dataTable.ext.search.push(
    function (settings, data, dataIndex, row) {
        let dt = moment(data[0], "DD/MM/YYYY");
        if (dt.isValid() && (typeof row.lignes_reglement !== 'undefined')) {
            dt = dt.set('minute', 1);
            //console.log('Check date', dt.format('DD/MM/YY HH:mm'));
            //console.log('maxdate', maxDate, 'mindate', minDate);
            let date_ret = dt.isBefore(maxDate) && dt.isAfter(minDate);
            return date_ret;
        }
        return true;
    }
);


$(document).ready(() => {
    const inputElm = document.querySelector('input[name=tags]');

    tagify = new Tagify(inputElm, {
        keepInvalidTags: true,
        placeholder: "Saisir un mot clé",
        delimiters: " ",
        editTags: false,
        // make an array from the initial input value
        whitelist: list_mots
    });


    const initTableRapport = function () {
        const _t = _.template($('#actions-rapport-template').html());

        const table = $('#datatable_rapport').DataTable({
            language: {
                "url": "/static/plugins/custom/datatables/French.json"
            },
            responsive: true,
            // Pagination settings
            dom: `<'row'<'col-sm-12'tr>>
			<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7 dataTables_pager'lp>>`,
            // read more: https://datatables.net/examples/basic_init/dom.html
            lengthMenu: [5, 10, 25, 50],
            pageLength: 10,
            searchDelay: 500,
            processing: true,
            serverSide: false,

            data: reglements,

            columns: [
                {
                    data: 'date_creation',
                    render: function (data, type, full, meta) {
                        return moment(data).format('DD/MM/YY');
                    },
                },
                {
                    data: 'somme_payee'
                },
                {
                    data: 'lignes_reglement',
                    render: function (data) {
                        let list = '';
                        for (let i = 0; i < data.length; i++) {
                            if (i > 0) {
                                list += ', ' + data[i].prestation;
                            } else {
                                list += data[i].prestation;
                            }
                        }
                        return list;
                    },
                },
                {
                    data: 'patient.nom_complet',

                },
                {data: 'patient.mot_cle', "visible": false},
                {data: 'mutuelle', "visible": false},
                {data: null},
            ],

            order: [[0, "asc"]],
            columnDefs: [
                {
                    targets: 6,
                    title: 'Actions',
                    orderable: false,
                    width: '200px',
                    render: (data, type, full, meta) => _t({id: full.id}),
                }
            ],
            initComplete: function () {
                resetDates();
                chercher();
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

            let params = {};
            $('[data-col-index]').each(function () {
                var i = $(this).data('col-index');
                if (params[i]) {
                    params[i] += '|' + $(this).val();
                } else {
                    params[i] = $(this).val();
                }
            });

            //console.log(params);
            $.each(params, function (i, val) {
                // apply search params to datatable
                table.column(i).search(val ? val : '', false, false);
            });
            table.table().draw();

        }
    };

    initTableRapport();

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
        const tableRapport = $('#datatable_rapport').DataTable();
        tableRapport.table().draw();
    });

    const url = window.location.href;
    let tabs = url.split('#');
    if (tabs.length > 1) {
        tabs.forEach(tab => $(`a[href="#${tab}"]`).tab('show'));
    }

});

function resetDates() {
    minDate = moment().startOf('month');
    maxDate = moment().endOf('month');
    var tabRapp = $('#datatable_rapport').DataTable();
    tabRapp.table().draw();
    $('#daterangepicker .form-control').val(minDate.format('DD/MM/YYYY') + ' - ' + maxDate.format('DD/MM/YYYY'));

}

function resetSearch() {
    $('input').val('');
    $('select').val('');
    resetDates();
}

