let pdfDoc;
const templateHeader = _.template(unescapeTemplate($('#template-header').html()));
const templateSignature = _.template(unescapeTemplate($('#template-signature').html()));

function download_facture(pk) {

    const admission = _.find(admissions, {'id': pk});
    const reglement = admission.reglements[0];

    let numero = derniere_facture_id + 1;

    if (reglement.factures.length == 0) {
        console.log('Enregistrement de la facture');
        $.ajax({
            method: 'post',
            dataType: 'json',
            url: "reglement/" + reglement.id + "/facture",
            success: function (data) {
                if (!data.error) {
                    console.log('Facture enregistrée');
                }
            }
        });
    } else {
        numero = reglement.factures[0].id;
        console.log('ICIIIII', numero)
    }

    const total = _.sumBy(reglement.lignes_reglement, 'prix_ttc').toFixed(3).replace('.', ',');

    reglement.lignes_reglement = _.map(reglement.lignes_reglement,
        ligne => {
            const p = parseFloat(ligne.prix_ttc);
            ligne.prix_ttc = p.toFixed(3).replace('.', ',');
            return ligne;
        });

    const headerData = {
        date: moment().format('DD/MM/YYYY'),
        admission: admission,
        reglement: reglement,
        total: total,
        facture: numero,
    };

    console.info('Règlement', reglement);

    const docDefinition = {
        pageMargins: defaultMargins(),
        pageSize: 'A5',
        header: defaultHeader,
        footer: defaultFooter,
        content: [
            htmlToPdfmake(templateHeader(headerData), {tableAutoSize: true})
        ],
        styles: {
            'table': {}
        }
    };
    pdfDoc = pdfMake.createPdf(docDefinition);
    pdfDoc.open();

}

$(document).ready(() => {

    const initTable = function () {

        const _t = _.template(unescapeTemplate($('#actions-template').html()));

        const table = $('#datatable_admission').DataTable({
            language: {
                "url": "/static/plugins/custom/datatables/French.json"
            },
            responsive: true,
            // Pagination settings
            dom: `<'row'<'col-sm-12'tr>>
			<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7 dataTables_pager'lp>>`,
            // read more: https://datatables.net/examples/basic_init/dom.html
            lengthMenu: [10, 25, 50, 75, 100],
            pageLength: 100,
            searchDelay: 500,
            processing: true,
            serverSide: false,

            data: admissions,

            columns: [
                {data: 'id', width: '100px'},
                {data: 'patient.nom'},
                {data: 'patient.nom_naissance'},
                {data: 'patient.prenom'},
                {
                    data: 'statut', name: 'statut',
                    render: function (data, type, full, meta) {
                        if (full.statut == 1) {
                            return '<span class="chip lighten-5 pink pink-text">En attente</span>';
                        } else if (full.statut == 2) {
                            return '<span class="chip lighten-5 pink pink-text">En consultation</span>';
                        } else if (full.statut == 3) {
                            return '<span class="chip lighten-5 pink pink-text">Consultation terminée</span>';
                        } else if (full.statut == 4) {
                            return '<span class="chip lighten-5 pink pink-text">Annulé</span>';
                        } else {
                            return '<span class="chip lighten-5 pink pink-text">--</span>';
                        }
                    }
                },
                {data: null},
            ],

            order: [[0, "asc"]],
            columnDefs: [
                {
                    targets: 5,
                    title: 'Actions',
                    orderable: false,
                    width: '200px',
                    render: (data, type, full, meta) => _t({admission: full}),
                }
            ],
        });
    };

    initTable();

    const initTableReglement = function () {

        const _t = _.template($('#actions-reglement-template').html());

        const table = $('#datatable_reglement').DataTable({
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

            data: reglements_caisse,

            columns: [
                {
                    data: null, 'targets': 0,
                    'searchable': false,
                    'orderable': false,
                    'width': '50px',
                    'className': 'dt-body-center',
                    'render': function (data, type, full, meta) {
                        return '<input type="checkbox" class="reglement_cb" name="reglements_ids[]" value="'
                            + $('<div/>').text(data.id).html() + '">';
                    }
                },
                {data: 'id'},
                {data: 'date_creation'},
                {data: 'patient.nom'},
                {data: 'patient.nom_naissance'},
                {data: 'patient.prenom'},
                {data: 'espece_payment'},
                {data: 'cheque_payment'},
                {data: null},

            ],

            order: [[0, "asc"]],
            columnDefs: [
                {
                    targets: 1, width: '20px'
                },
                {
                    targets: 2, width: '80px',
                    render: (data, type, full, meta) => data ? moment(data).format('DD/MM/YY') : '',
                },
                {
                    targets: 6, width: '50px',
                    render: (data, type, full, meta) => data ? parseFloat(data).toFixed(3).replace('.',',') : '',
                },
                {
                    targets: 7, width: '50px',
                    render: (data, type, full, meta) => data ? parseFloat(data).toFixed(3).replace('.',',') : '',
                },
                {
                    targets: 8,
                    title: 'Actions',
                    orderable: false,
                    width: '200px',
                    render: (data, type, full, meta) => _t({id: full.id}),
                }
            ],

        });

    };

    initTableReglement();

    $('#reglements_ids').click(function (e) {
        var table = $(e.target).closest('table');
        $('td input:checkbox', table).prop('checked', this.checked);
    });

    const initTableCaisse = function () {

        const _t = _.template($('#actions-caisse-template').html());

        const table = $('#datatable_caisse').DataTable({
            language: {
                "url": "/static/plugins/custom/datatables/French.json"
            },
            responsive: true,
            // Pagination settings
            dom: `<'row'<'col-sm-12'tr>>
			<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7 dataTables_pager'lp>>`,
            // read more: https://datatables.net/examples/basic_init/dom.html
            lengthMenu: [10, 25, 50, 75, 100],
            pageLength: 100,
            searchDelay: 500,
            processing: true,
            serverSide: false,

            data: caisses,

            columns: [
                {data: 'id'},
                {
                    data: 'date_cloture',
                    render: function (data, type, full, meta) {
                        return moment(data).format('DD/MM/YY');
                    },
                },
                {data: 'total'},
                {data: 'periode'},
                {data: null},
            ],

            order: [[0, "desc"]],
            columnDefs: [
                {
                    targets: 0, width: '20px'
                },
                {
                    targets: 1, width: '50px'
                },
                {
                    targets: 2, width: '50px',
                    render: (data, type, full, meta) =>
                        data ? parseFloat(data).toFixed(3).replace('.', ',') + ' DT' : '' ,
                },
                {
                    targets: 3, width: '50px'
                },
                {
                    targets: 4,
                    title: 'Actions',
                    orderable: false,
                    width: '50px',
                    render: (data, type, full, meta) => _t({id: full.id}),
                }
            ],

            initComplete: function () {
                $('.reglement_cb').on('click', e => {
                    let cbs = $('.reglement_cb');
                    let count = 0;
                    for (let i = 0; i < cbs.length; i++) {
                        if (cbs[i].checked) count++;
                    }
                    $('#btn_cloturer_caisse').prop('disabled', count == 0);
                });
            },

        });

    };

    initTableCaisse();

    const url = window.location.href;
    let tabs = url.split('#');
    if (tabs.length > 1) {
        tabs.forEach(tab => $(`a[href="#${tab}"]`).tab('show'));
    }
});

