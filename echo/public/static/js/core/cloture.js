function imprimerClick() {
    window.print();
}

$(document).ready(() => {
    const initTableCloture = function () {

        const table = $('#datatable_detail_cloture').DataTable({
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

            data: cloture_reglements,

            columns: [
                {
                    data: 'date_creation',
                    render: function (data, type, full, meta) {
                        return moment(data).format('DD/MM/YY');
                    },
                },
                {data: 'patient.nom'},
                {data: 'patient.nom_naissance'},
                {data: 'patient.prenom'},
                {
                    data: 'espece_payment', name: 'espece_payment',
                    render: function (data, type, full, meta) {
                        if (full.cb_payment > 0) {
                            full.espece_payment = full.espece_payment + full.cb_payment;
                        }
                        if (full.cheque_payment > 0) {
                            full.espece_payment = full.espece_payment + full.cheque_payment;
                        }
                        return `${full.espece_payment.toFixed(3)}`.replace('.', ',');
                    }
                },
                {
                    data: 'mutuelle',
                    render: function (data, type, full, meta) {
                        return data ? 'Oui' : 'Non';
                    }
                }
            ],

            order: [[0, "asc"]],

        });

    };

    initTableCloture();
});
