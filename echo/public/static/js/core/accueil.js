let statutTemplate;

function annulerRdv(pk) {
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
            window.location.replace("/rdvs/" + pk + "/supprimer/?next=accueil");
        }
    });
}

function annulerAdmission(pk) {
    swal.fire({
        title: "Etes vous sûr ?",
        type: "warning",
        showCancelButton: true,
        confirmButtonClass: "btn-danger",
        confirmButtonText: "Oui, annuler l'admission!",
        cancelButtonText: "Non, conserver l'admission",
        closeOnConfirm: false
    }).then(function (result) {
        if (result.value) {
            window.location.replace("/admissions/" + pk + "/supprimer/?next=accueil");
        }
    });
}

function changeDonneesTable(datatable, data) {
    datatable.clear();
    datatable.rows.add(data);
    datatable.draw();
}

function afficherStatut(ligne) {
    let libelle = '';
    let msg = '';
    let cssClass = '';
    let smiley = '';
    switch (ligne.statut) {
        case '1':
            if (moment(ligne.debut).isBefore(moment().subtract(10, "minutes"))) {
                // Rdv en retard (10 minutes dépassées)
                msg = 'En retard';
                cssClass = 'bg-danger';
                smiley = 'la-frown-o';
            } else if (ligne.ancien_debut && !moment(ligne.debut).isSame(moment(), 'day')) {
                // Rdv prévue initialement dans ce jour mais modifié
                msg = 'Modifié';
                cssClass = 'bg-info';
                smiley = 'la-meh-o';
            } else {
                msg = 'Confirmé';
                cssClass = `fc-event-type-${ligne.statut}`;
                smiley = 'la-smile-o';
            }
            break;
        case '2':
            msg = 'En salle';
            cssClass = `fc-event-type-${ligne.statut}`;
            smiley = 'la-smile-o';
            break;
        case '3':
            msg = 'Terminée';
            cssClass = `fc-event-type-${ligne.statut}`;
            smiley = 'la-smile-o';
            break;
        case '10':
            msg = 'Annulé';
            cssClass = `fc-event-type-${ligne.statut}`;
            smiley = 'la-meh-o';
    }

    libelle = `<div class="symbol symbol-circle symbol-25px mr-2"><span class="symbol-label ${cssClass}"><i class="la ${smiley} icon-lg-2x text-white"></i></span></div><span class="align-middle">${msg}</span>`;
    libelle = statutTemplate({cssClass, smiley, msg});
    return libelle;
}

function rappel(el, id, r) {
    $.post(`/rdvs/${id}/rappel/`, {
        'rappel': r
    })
        .done(function (result) {
            console.log('Succes', id);
            const _tpl = _.template($('#action-rappel-rdv').html());
            console.log('el', el);
            $(el).parents('.rappel-container').html(_tpl({id, action:1-r}));
        })
        .fail(function () {
            console.error("Impossible de modifier le rdv (rappel)");
        });
}

function modifierPraticien(el, admissionId, praticienId) {
    $('.praticien-dropdown').dropdown('toggle');
    $.post(`/admissions/${admissionId}/modifier/`, {
        'praticien': praticienId
    })
        .done(function (result) {
            let table = $('#kt_datatable_salle').DataTable();
            let row = table.row('#' + admissionId);
            let dt = row.data();
            dt.praticien = _.find(praticiens, p => p.id == praticienId);
            row.data(dt).draw();
        })
        .fail(function () {
            console.error("Impossible de modifier le rdv (rappel)");
        });
}

function modifierMotifRdv(el, admissionId, motifRdvId) {
    $('.motif-rdv-dropdown').dropdown('toggle');
    $.post(`/admissions/${admissionId}/modifier/`, {
        'motif': motifRdvId
    })
        .done(function (result) {
            let table = $('#kt_datatable_salle').DataTable();
            let row = table.row('#' + admissionId);
            let dt = row.data();
            dt.motif = _.find(motifs_rdvs, p => p.id == motifRdvId);
            row.data(dt).draw();
        })
        .fail(function () {
            console.error("Impossible de modifier le rdv (rappel)");
        });
}

jQuery(document).ready(function () {

    statutTemplate = _.template(unescapeTemplate($('#statut-template').html()));

    let tableRdvs;

    // -----------------------------------------------------------------------------------------------

    let initTableRdvs = function () {

        const _t = _.template($('#actions-rdv-template').html());

        tableRdvs = $('#kt_datatable_rdvs').DataTable({
            language: {
                "url": "/static/plugins/custom/datatables/French.json"
            },
            responsive: true,
            fixedColumns: true,
            // Pagination settings

            lengthMenu: [10, 25, 50, 75, 100],
            pageLength: 100,
            searchDelay: 500,
            processing: true,
            serverSide: false,

            data: rdvs_jour,
            columns: [
                {data: 'nouveau'},
                {data: 'statut'},
                {data: 'nom_naissance'},
                {data: 'nom'},
                {data: 'prenom'},
                {data: 'ville'},
                {data: 'telephone'},
                {data: 'debut'},
                {data: 'motif.libelle'},
                {data: 'praticien', width: '300px', render: (data, type, full, meta) => data ? data.nom : '-'},
                {data: null},
            ],

            order: [[7, "asc"]],

            columnDefs: [
                {
                    targets: 10, title: 'Actions', orderable: false, width: 650,
                    render: function (data, type, full, meta) {
                        return _t(
                            {
                                id: full.id,
                                rappele: full.patient_rappele,
                                admission: moment(full.debut).isSame(moment(), 'day') && full.statut == 1 ? 'visible' : 'invisible',
                                annulation: full.statut == 10 ? 'invisible' : 'visible'
                            });
                    }
                },
                {
                    targets: 0, width: '10px',
                    render: (data, type, full, meta) =>
                        data ? `<span class="label label-pill label-inline label-info">Nouveau</span>` : '',
                },
                {
                    targets: 1, width: 200,
                    render: (data, type, full, meta) => afficherStatut(full),
                },
                {targets: 2, width: '360px'},
                {targets: 3, width: '360px', /*render: () => '-' */},
                {targets: 4, width: '360px'},
                {targets: 5, width: '320px'},
                {targets: 6, width: '100px'},
                {
                    targets: 7, width: '80px',
                    render: (data, type, full, meta) => data != '-' ? moment(data).format('HH:mm') : '',
                },
                {targets: 8, width: '80px'},
            ],
        });
    };

    initTableRdvs();

    // -----------------------------------------------------------------------------------------------

    let initTableSalleAttente = function () {

        const _t = _.template($('#actions-attente-template').html());
        const _pratTemp = _.template($('#praticien-template').html());
        const _motifRdvTemp = _.template($('#motif-rdv-template').html());

        const tab = $('#kt_datatable_salle').DataTable({
            language: {
                "url": "/static/plugins/custom/datatables/French.json"
            },
            responsive: true,
            // Pagination settings

            // read more: https://datatables.net/examples/basic_init/dom.html

            lengthMenu: [10, 25, 50, 75, 100],
            pageLength: 100,

            searchDelay: 500,
            processing: true,
            serverSide: false,

            rowReorder: {
                dataSrc: 'ordre'
            },

            data: patients_en_attente,
            rowId: 'id',

            columns: [
                {data: 'ordre'},
                {data: 'nouveau'},
                {data: 'patient.nom_naissance'},
                {data: 'patient.nom'},
                {data: 'patient.prenom', width: '100px'},
                {data: 'patient.age'},
                {data: 'patient.adresse', render: (data, type, full, meta) => data ? data.ville : '', width: '200px'},
                {data: 'patient.telephone', width: '100px'},
                {data: 'date'},
                {data: null},
                {
                    data: 'motif',
                    render: (data, type, full, meta) => {
                        return _motifRdvTemp({id: full.id, motif: data.libelle});
                    }, width: '200px'
                },
                {
                    data: 'praticien',
                    render: (data, type, full, meta) => {
                        let nom = data ? data.nom : '';
                        return _pratTemp({id: full.id, nom: nom});
                    }, width: '200px'
                },
                {data: null},
            ],

            order: [[0, "asc"]],

            columnDefs: [
                {
                    targets: 12, title: 'Actions', orderable: false, width: '450px', className: 'w-100px',
                    render: (data, type, full, meta) => {
                        const mesures = full.patient.mesures_jour;
                        return _t({id: full.patient.id, admission_id: full.id, mesuresId: mesures ? mesures.id : -1});
                    }
                },
                {
                    targets: 0, width: '40px', orderable: true, className: 'reorder',
                    render: (data, type, full, meta) => '<i class="fas fa-arrows-alt-v mr-3"></i>' + data,
                },
                {
                    targets: 1, width: '10px',
                    render: (data, type, full, meta) =>
                        data ? `<span class="label label-pill label-inline label-info">Nouveau</span>` : '',
                },
                {targets: 2, width: '320px'},
                {targets: 3, width: '320px'},
                {targets: 4, width: '320px'},
                {targets: 5, width: '100px'},
                {targets: 6, width: '320px'},
                {targets: 7, width: '320px'},
                {
                    targets: 8, width: '100px',
                    render: (data, type, full, meta) => {
                        if (!data) return '';
                        const date = moment(data);
                        return date.isValid() ? date.format('HH:mm') : '-';
                    },
                },
                {
                    targets: 9, width: '80px', className: 'attente-cell',
                    render: (data, type, full, meta) => '',
                    createdCell: function (td, cellData, rowData, row, col) {
                        $(td).attr('data-heure', rowData['date']);
                    }
                },
                {targets: 10, width: '320px'}
            ],
        });

        tab.on('row-reorder', function (e, diff, edit) {
            id = edit.triggerRow.data()['id'];
            ordre = edit.triggerRow.data()['ordre'];
            for (let i = 0, ien = diff.length; i < ien; i++) {
                let rowData = tab.row(diff[i].node).data();
                if (rowData['id'] == id) ordre = diff[i].newData;
            }
            console.log('Ordre de %d modifié', id, ordre);
            $.post(`/admissions/${id}/ordre/`, {
                'ordre': ordre
            })
                .done(function (result) {
                    console.log('Succes');
                })
                .fail(function () {
                    console.error("Impossible de modifier l'ordre");
                });
        });

        return tab;
    }

    let tableSalleAttente = initTableSalleAttente();
    $('#nb_attente').text(patients_en_attente.length);

    // -----------------------------------------------------------------------------------------------

    let initTableConsultationEnCours = function () {

        const _t = _.template($('#actions-consultation-template').html());

        const tab = $('#kt_datatable_en_consultation').DataTable({
            language: {
                "url": "/static/plugins/custom/datatables/French.json"
            },
            responsive: true,
            // Pagination settings

            // read more: https://datatables.net/examples/basic_init/dom.html

            lengthMenu: [10, 25, 50, 75, 100],
            pageLength: 100,

            searchDelay: 500,
            processing: true,
            serverSide: false,

            data: consultations_en_cours,

            columns: [
                {data: 'id'},
                {data: 'nouveau'},
                {data: 'patient.nom_naissance'},
                {data: 'patient.nom'},
                {data: 'patient.prenom'},
                {data: 'patient.age'},
                {data: 'patient.adresse', render: (data, type, full, meta) => data ? data.ville : ''},
                {data: 'patient.telephone'},
                {data: 'debut'},
                {data: 'motif.libelle'},
                {data: 'praticien', render: (data, type, full, meta) => data ? data.nom : '', width: '300px'},
                {data: null},
            ],

            order: [[0, "asc"]],

            columnDefs: [
                {
                    targets: 11, title: 'Actions', orderable: false, width: '450px',
                    render: (data, type, full, meta) => _t({id: full.patient.id})
                },
                {targets: 0, width: '100px'},
                {
                    targets: 1, width: '10px',
                    render: (data, type, full, meta) =>
                        data ? `<span class="label label-pill label-inline label-info">Nouveau</span>` : '',
                },
                {targets: 2, width: '360px'},
                {targets: 3, width: '360px'},
                {targets: 4, width: '320px'},
                {targets: 5, width: '100px'},
                {targets: 6, width: '320px'},
                {targets: 7, width: '320px'},
                {
                    targets: 8, width: '80px',
                    render: (data, type, full, meta) => data != '-' ? moment(data).format('HH:mm') : '',
                },
                {targets: 9, width: '320px'},


            ],
        });

        return tab;
    };

    let tableConsultationsEnCours = initTableConsultationEnCours();
    $('#nb_consultations_en_cours').text(consultations_en_cours.length);

    // -----------------------------------------------------------------------------------------------

    let initTableConsultationsRealisees = function () {

        const _t = _.template($('#actions-consultation-template').html());

        const tab = $('#kt_datatable_consultations').DataTable({
            language: {
                "url": "/static/plugins/custom/datatables/French.json"
            },
            responsive: true,
            // Pagination settings

            // read more: https://datatables.net/examples/basic_init/dom.html

            lengthMenu: [10, 25, 50, 75, 100],
            pageLength: 100,

            searchDelay: 500,
            processing: true,
            serverSide: false,

            data: consultations,

            columns: [
                {data: 'patient.nom_naissance'},
                {data: 'patient.nom'},
                {data: 'patient.prenom'},
                {data: 'patient.age'},
                {data: 'patient.adresse', render: (data, type, full, meta) => data ? data.ville : ''},
                {data: 'motif.libelle'},
                {data: 'praticien', width: '300px', render: (data, type, full, meta) => data ? data.nom : '-'},
                {data: null},
            ],

            order: [[0, "asc"]],

            columnDefs: [
                {
                    targets: 7, title: 'Actions', orderable: false, width: '450px',
                    render: (data, type, full, meta) => _t({id: full.patient.id})
                },
                {targets: 0, width: '360px'},
                {targets: 1, width: '360px'},
                {targets: 2, width: '320px'},
                {targets: 3, width: '100px'},
                {targets: 5, width: '300px'},

            ],
        });

        return tab;
    };

    let tableConsultationsRealisees = initTableConsultationsRealisees();
    $('#nb_realises').text(consultations.length);

    // -----------------------------------------------------------------------------------------------

    let initTableRdvsModifiesAnnules = function () {

        const _t = _.template($('#actions-rdv-modif-template').html());

        const tab = $('#kt_datatable_modifies_annules').DataTable({
            language: {
                "url": "/static/plugins/custom/datatables/French.json"
            },
            responsive: true,
            // Pagination settings

            // read more: https://datatables.net/examples/basic_init/dom.html

            lengthMenu: [10, 25, 50, 75, 100],
            pageLength: 100,

            searchDelay: 500,
            processing: true,
            serverSide: false,

            data: rdvs_modifies_annules,

            columns: [
                {data: 'statut'},
                {data: 'nom_naissance'},
                {data: 'nom'},
                {data: 'prenom'},
                {data: 'ville'},
                {data: 'telephone'},
                {data: 'debut'},
                {data: 'motif.libelle'},
                {data: 'praticien', width: '300px', render: (data, type, full, meta) => data ? data.nom : '-'},
                {data: null},

            ],

            order: [[1, "asc"]],

            columnDefs: [
                {
                    targets: 9, title: 'Actions', orderable: false, width: '300px',
                    render: function (data, type, full, meta) {
                        return _t(
                            {
                                id: full.id,
                                admission: moment(full.debut).isSame(moment(), 'day') && full.statut == 1 ? 'visible' : 'invisible',
                                annulation: full.statut == 10 ? 'invisible' : 'visible'
                            });
                    }
                },
                {
                    targets: 0, width: '100px',
                    render: (data, type, full, meta) => afficherStatut(full),
                },
                {targets: 1, width: '360px'},
                {targets: 2, width: '300px', render: () => ''},
                {targets: 3, width: '360px'},
                {targets: 4, width: '320px'},
                {targets: 5, width: '100px'},
                {
                    targets: 6, width: '50px',
                    render: (data, type, full, meta) => data != '-' ? moment(data).format('HH:mm') : '',
                },
                {targets: 7, width: '80px'},
            ],
        });

        return tab;
    };

    let tableRdvsModifiesAnnules = initTableRdvsModifiesAnnules();
    $('#nb_modifies').text(rdvs_modifies_annules.length);

    // -----------------------------------------------------------------------------------------------

    function filtrerDate(dt) {
        console.info('Filtrage sur la date', dt.format('YYYY-MM-DD'));
        filtreDate = dt;
        if (!dt.isSame(moment(), 'day')) {
            $('#link_rdv_jour').tab('show');
            $('#link_salle,#link_consultations,#link_modifications').addClass('disabled');
        } else {
            $('#link_salle,#link_consultations,#link_modifications').removeClass('disabled');
        }
        let data = _.filter(rdvs_jour, rdv => {
            return moment(rdv.debut).isSame(dt, 'day') || moment(rdv.ancien_debut).isSame(dt, 'day');
        });

        if (filterPraticienId > 0)
            data = _.filter(data, rdv => rdv.praticien ? rdv.praticien.id == filterPraticienId : false);
        changeDonneesTable(tableRdvs, data);
        $('#nb_rdvs').text(data.length);
    }

    let date_selectionnee = moment();
    const max_date = 10;

    $('#btn_aujourdhui').click(() => {
        date_selectionnee = moment();
        $('#date_courante_picker').datepicker('update', new Date());
        filtrerDate(date_selectionnee);
    });

    $('#btn_jour_precedent').click(() => {
        // S'arrêter à aujourd'hui-10
        if (date_selectionnee.isSame(moment().subtract(max_date, 'days'), 'day'))
            return;
        date_selectionnee = date_selectionnee.subtract(1, 'days');
        const jour = date_selectionnee.format('DD/MM/yyyy');
        $('#date_courante_picker').datepicker('update', jour);
        filtrerDate(date_selectionnee);
    });

    $('#btn_jour_suivant').click(() => {
        // S'arrêter à aujourd'hui-10
        if (date_selectionnee.isSame(moment().add(max_date, 'days'), 'day'))
            return;
        date_selectionnee = date_selectionnee.add(1, 'days');
        const jour = date_selectionnee.format('DD/MM/yyyy');
        $('#date_courante_picker').datepicker('update', jour);
        filtrerDate(date_selectionnee);
    });

    $('#date_courante_picker').datepicker({
        todayHighlight: true,
        autoclose: true,
        language: 'fr',
        weekStart: 1,
        format: 'dd/mm/yyyy',
        startDate: '-10d',
        endDate: '+10d',
    }).on('changeDate', function (e) {
        date_selectionnee = moment(e.format('yyyy-mm-dd'));
        filtrerDate(date_selectionnee);
    });

    $('#date_courante_picker').val(moment().format('DD/MM/yyyy'));


    function filtrerPraticien(praticienId) {

        filterPraticienId = praticienId;
        console.log('Filtre sur praticien', praticienId);

        let rdvs, salle, encours, realises, modifies;

        if (praticienId == -1) {
            rdvs = rdvs_jour;
            salle = patients_en_attente;
            encours = consultations_en_cours;
            realises = consultations;
            modifies = rdvs_modifies_annules;
        } else {
            rdvs = _.filter(rdvs_jour, rdv => rdv.praticien ? rdv.praticien.id == filterPraticienId : false)
            salle = _.filter(patients_en_attente, c => c.praticien ? c.praticien.id == filterPraticienId : false);
            encours = _.filter(consultations_en_cours, c => c.praticien ? c.praticien.id == filterPraticienId : false);
            realises = _.filter(consultations, c => c.praticien ? c.praticien.id == filterPraticienId : false);
            modifies = _.filter(rdvs_modifies_annules, rdv => rdv.praticien ? rdv.praticien.id == filterPraticienId : false)
        }

        changeDonneesTable(tableRdvs, rdvs);
        changeDonneesTable(tableSalleAttente, salle);
        changeDonneesTable(tableConsultationsEnCours, encours);
        changeDonneesTable(tableConsultationsRealisees, realises);
        changeDonneesTable(tableRdvsModifiesAnnules, modifies);

        $('#nb_rdvs').text(rdvs.length);
        $('#nb_attente').text(salle.length);
        $('#nb_consultations_en_cours').text(encours.length);
        console.log('Nb en cours', encours.length);
        $('#nb_realises').text(realises.length);
        $('#nb_modifies').text(modifies.length);
    }
    filtrerPraticien(filterPraticienId);
    filtreDate = moment();
    filtrerDate(filtreDate);

    let initStats = function () {
        let element = document.getElementById("stats");
        let height = parseInt(KTUtil.css(element, 'height'));

        if (!element) {
            return;
        }
        let consultations = 0;
        if (rdvs_jour.length)
            consultations = Math.floor(100 * _.filter(rdvs_jour, {'statut': '3'}).length / rdvs_jour.length);

        let options = {
            series: [consultations],
            chart: {
                height: height,
                type: 'radialBar',
                offsetY: 0
            },
            plotOptions: {
                radialBar: {
                    startAngle: -90,
                    endAngle: 90,

                    hollow: {
                        margin: 0,
                        size: "70%"
                    },
                    dataLabels: {
                        showOn: "always",
                        name: {
                            show: true,
                            fontSize: "13px",
                            fontWeight: "700",
                            offsetY: -5,
                            color: KTApp.getSettings()['colors']['gray']['gray-500']
                        },
                        value: {
                            color: KTApp.getSettings()['colors']['gray']['gray-700'],
                            fontSize: "30px",
                            fontWeight: "700",
                            offsetY: -40,
                            show: true
                        }
                    },
                    track: {
                        background: KTApp.getSettings()['colors']['theme']['light']['primary'],
                        strokeWidth: '100%'
                    }
                }
            },
            colors: [KTApp.getSettings()['colors']['theme']['base']['primary']],
            stroke: {
                lineCap: "round",
            },
            labels: ["réalisés"]
        };

        let chart = new ApexCharts(element, options);
        chart.render();
    };

    $('.attente-cell').each((idx, el) => {

    });

    $('select#praticien').change(e => {
        filtrerPraticien($("select#praticien option:checked").val());
        filtrerDate(filtreDate);
    });

    //initStats();
    let handler = function () {
        let now = moment();
        $('.attente-cell').each((idx, el) => {
            let heureDebut = $(el).attr('data-heure');
            if (!_.isUndefined(heureDebut)) {
                let d = moment.duration(now.clone().diff(moment(heureDebut)));
                //console.log('Heure début', heureDebut);
                //$(el).html(moment.utc(d.asMilliseconds()).format("HH:mm"));
                const min = Math.floor(d.asMinutes());
                if (min <= 20) {
                    $(el).html(`<span class="label label-pill label-inline label-success">${min} min</span>`);
                }
                if (min > 20 && min <= 40) {
                    // <span class="label label-pill label-inline label-success"></span>
                    $(el).html(`<span class="label label-pill label-inline label-warning">${min} min</span>`);
                }
                if (min > 40) {
                    // <span class="label label-pill label-inline label-success"></span>
                    $(el).html(`<span class="label label-pill label-inline label-danger">${min} min</span>`);
                }
            }
        });
    };
    setInterval(handler, 1000);
    handler();

    const url = window.location.href;
    const activeTab = url.substring(url.indexOf("#") + 1);
    if (activeTab) $(`a[href="#${activeTab}"]`).tab('show');

});