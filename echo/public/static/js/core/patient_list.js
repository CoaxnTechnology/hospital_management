function archiverPatient(pk) {
    swal.fire({
        title: "Attention",
        text: "Voulez vous archiver ce patient ?",
        type: "warning",
        showCancelButton: true,
        confirmButtonClass: "btn-danger",
        confirmButtonText: "Oui, archiver!",
        cancelButtonText: "Non, annuler",
        closeOnConfirm: false
    }).then(function (result) {
        if (result.value) {
            window.location.replace(`/patients/${pk}/supprimer`);
        }
    });
}

function modifierPatient(url) {
    showFrameLoading();
    $('#patient-form-modal iframe').attr('src', url);
    bootstrap.Modal.getOrCreateInstance('#patient-form-modal').show();
}

function creerPatient(url) {
    showFrameLoading();
    $('#patient-form-modal iframe').attr('src', url);
    bootstrap.Modal.getOrCreateInstance('#patient-form-modal').show();
}

function admissionPatient(event, patientId) {
    event.preventDefault();
    let admissionUrl = `/patients/${patientId}/admission/`;
    if(rdvId > 0) admissionUrl += `?rdv=${rdvId}`;
    $.get(`/patients/${patientId}/admissions/`)
        .done(function (result) {
            let adm = JSON.parse(result.admissions);
            console.info('Admissions', adm);
            if (adm.length > 0) {
                swal.fire({
                    title: "Message important",
                    text: "Une autre admission est en cours pour ce patient, souhaitez vous faire une nouvelle admission?",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonClass: "btn-primary",
                    confirmButtonText: "Oui, faire une nouvelle admission",
                    cancelButtonText: "Non, garder l'admission en cours",
                    closeOnConfirm: false
                }).then(function (result) {
                    if (result.value) {
                        window.location.replace(admissionUrl);
                    }
                });
            } else {
                window.location.replace(admissionUrl);
            }
        })
        .fail(function () {
            console.error("Impossible de charger les images");
        });
}

$(document).ready(function () {

    let _t = _.template($('#actions-template').html());
    let _p = _.template($('#lien-patient-template').html());
    const _tempHistReg = _.template($('#historique-reglements-template').html());

    Inputmask("datetime", {
        inputFormat: 'dd/mm/yyyy',
        placeholder: "jj/mm/aaaa",
        min: '01/01/1900',
        max: '31/12/2900',
    }).mask(document.querySelectorAll('.date_naissance'));

    $.fn.dataTable.Api.register('column().title()', function () {
        return $(this.header()).text().trim();
    });

    var initTable1 = function () {

        var table = $('#kt_datatable').DataTable({
            language: { "url": "/static/plugins/custom/datatables/French.json"},
            responsive: true,
            // dom: `<'row'<'col-sm-12'tr>><'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7 dataTables_pager'lp>>`,
            // read more: https://datatables.net/examples/basic_init/dom.html
            lengthMenu: [10, 25, 50, 75, 100],
            pageLength: 50,
            searchDelay: 500,
            processing: false,
            serverSide: true,
            ajax: { url: "/patients/recherche_async/", type: 'POST' },
            //data: data,
            columns: [
                {data: 'identifiant_unique'},
                {data: 'nom_naissance'},
                {data: 'nom'},
                {data: 'prenom'},
                {data: 'date_naissance'},
                {data: 'adresse', render: (data) => data ? data.ville : '' },
                {data: 'telephone'},
                {data: null},
                {data: 'ancien_numero', "visible": true},
                {data: null},
            ],

            initComplete: function () {
                setTimeout(() => chercher(), 0);
                this.api().columns().every(() => {
                });
            },

            drawCallback: function (settings) {
                if (settings.fnRecordsDisplay() === 0) {
                    const temp = _.template($('#creer-patient-template').html());
                    const data = _.map($('[data-search-key]').get(), el => $(el).attr('data-search-key') + '=' + $(el).val() );
                    const html = temp({params: '&' + data.join('&')});
                    $('.dataTables_empty').html(html);
                }
                //$('[data-bs-toggle="popover"]').popover();
                const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
                const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
            },

            columnDefs: [
                {
                    targets: 9,
                    title: 'Actions',
                    orderable: false,
                    width: '180px',
                    render: (data, type, full, meta) => {
                        return _t({id: full.id, reglements: _tempHistReg({reglements: full.reglement_set}) });
                    },
                },
                {
                    targets: 0,
                    render: (data, type, full, meta) => _p({id: full.id, val: full.identifiant_unique})
                },
                {
                    targets: 1,
                    width: '150px',
                    render: (data, type, full, meta) => {
                        return full.nom_naissance ? _p({id: full.id, val: full.nom_naissance}) : _p({id: full.id, val: full.nom});
                    },
                },
                {
                    targets: 2,
                    width: '150px',
                    render: (data, type, full, meta) => {
                        return full.nom ? _p({id: full.id, val: full.nom}) : _p({id: full.id, val: full.nom_naissance});
                    }
                },
                {
                    targets: 3,
                    width: '150px',
                    render: (data, type, full, meta) => _p({id: full.id, val: full.prenom}),
                },
                {
                    targets: 4,
                    width: '150px',
                    render: function (data, type, full, meta) {
                        return data ? moment(data).format('DD/MM/yyyy') : '';
                    }
                },
                {
                    targets: 7,
                    title: 'Informations',
                    orderable: false,
                    width: '250px',
                    render: function (data, type, full, meta) {
                        let gross = full.grossesse_encours;
                        let terme = gross && gross.ddr ? calcTerme(moment(gross.ddr)) : '';
                        let html = '';
                        if (terme != '')
                            html = _.template($('#terme-template').html())({terme});
                        return html;
                    }
                }
            ],
        });

        $('#kt_search').on('click', function (e) {
            e.preventDefault();
            chercher();
        });


        $('#kt_reset').on('click', function (e) {
            e.preventDefault();
            $('.datatable-input').each(function () {
                $(this).val('');
                table.column($(this).data('col-index')).search('', false, false);
            });
            table.table().draw();
        });

        // Filtrer la table à la saisie sans click sur le bouton chercher
        $('input').on('keyup', chercher);

        function chercher() {
            var params = {};
            $('.datatable-input').each(function () {
                var i = $(this).data('col-index');
                if (params[i]) {
                    params[i] += '|' + $(this).val();
                } else {
                    params[i] = $(this).val();
                }
            });

            //console.info('Chercher', params)

            $.each(params, function (i, val) {
                // apply search params to datatable
                if (i == 4 && val) {
                    // Reformat date
                    val = moment(val, 'DD/MM/YYYY').format('YYYY-MM-DD');
                }
                //console.log('Col', i, val);
                table.column(i).search(val ? val : '', false, false);
            });
            table.table().draw();
        }

    };

    initTable1();

    EventManager.subscribe("patient:updated", function (event) {
        console.info('Event patient:updated', event);
        window.location.reload();
    });
});