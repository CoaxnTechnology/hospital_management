let minDate = moment().set('hour', 0);

$.fn.dataTable.ext.search.push(
    function (settings, data, dataIndex) {
        /*console.log(maxDate, minDate); */
        const dt = moment(data[4], "DD/MM/YYYY").set('Hour', 1);
        //console.log('Date', dt.format('DD/MM/YY'));
        let ret = dt.isAfter(minDate);
        return ret;
    }
);
jQuery(document).ready(function () {

    $('#debut').datepicker({
        todayHighlight: true,
        autoclose: true,
        language: 'fr',
        weekStart: 1,
        format: 'dd/mm/yyyy'
    });

    $('#debut').val(moment().format('DD/MM/YYYY'));


    const initTableProgrammeOperatoire = function () {

        var table = $('#datatable_programme_operatoire').DataTable({
            language: {
                "url": "/static/plugins/custom/datatables/French.json"
            },
            responsive: true,
            // Pagination settings
            dom: `<'row'<'col-sm-6 text-left'f><'col-sm-6 text-right'B>>
			<'row'<'col-sm-12'tr>>
			<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7 dataTables_pager'lp>>`,

            // read more: https://datatables.net/examples/basic_init/dom.html
            buttons: [
                {
                    extend: 'excelHtml5',
                    text: 'Export Excel',
                    exportOptions: {
                        columns: [0, 1, 2, 3, 4, 5, 6, 7, 8]
                    }
                }
            ],
            // read more: https://datatables.net/examples/basic_init/dom.html
            lengthMenu: [5, 10, 25, 50],
            pageLength: 10,
            searchDelay: 500,
            processing: true,
            serverSide: false,
            data: data,
            order: [[4, "asc"]],
            columns: [
                {
                    data: 'patient',
                    render: (data, type, full, meta) => data ? data.nom : '-',
                },
                {
                    data: 'patient',
                    render: (data, type, full, meta) => data ? data.prenom : '-',
                },
                {
                    data: 'patient',
                    render: (data, type, full, meta) => data ? data.nom_naissance : '-',
                },
                {data: 'type_acte'},
                {
                    data: 'debut',
                    render: (data, type, full, meta) => data ? moment(data).format('DD/MM/YYYY') : '-'
                },
                {
                    data: 'debut',
                    render: (data, type, full, meta) => data ? moment(data).format('hh:mm') : '-'
                },
                {
                    data: 'fin',
                    render: (data, type, full, meta) => data ? moment(data).format('hh:mm') : '-'
                },


                {
                    data: 'lieu_accouchement',
                    render: (data, type, full, meta) => data ? data.nom : '-',
                    width: '200px'
                },
                {data: 'observation'},
                {data: 'praticien.nom'}
            ],


            drawCallback: function (settings) {
                if (settings.fnRecordsDisplay() === 0) {
                    const temp = _.template($('#creer-patient-template').html());
                    const data = _.map($('[data-search-key]').get(), el => $(el).attr('data-search-key') + '=' + $(el).val());
                    const html = temp({params: '&' + data.join('&')});
                    $('.dataTables_empty').html(html);
                }
            },

        });

        $('input,select').on('change', chercher);

        function chercher() {
            let debut = $('#debut').val();
            if (debut != "") {
                minDate = moment(debut, 'DD/MM/YYYY');
            }

            let params = {};
            $('[data-col-index]').each(function () {
                var i = $(this).data('col-index');
                if (params[i]) {
                    params[i] += '|' + $(this).val();
                } else {
                    params[i] = $(this).val();
                }
            });
            $.each(params, function (i, val) {
                // apply search params to datatable
                table.column(i).search(val ? val : '', false, false);
            });
            table.table().draw();
        }
    };

    initTableProgrammeOperatoire();
});
