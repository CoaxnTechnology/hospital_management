let statutTemplate;

function findRdvForPatient(patientId) {
    return _.find(rdvs_jour, r => {
        if (!r.patient) return false;
        const rdvPatientId = typeof r.patient === 'object' ? r.patient.id : r.patient;
        return rdvPatientId === patientId;
    });
}

function enrichAdmissions(admissionsList) {
    return _.map(admissionsList, p => {
        const rdv = findRdvForPatient(p.patient.id);
        if (rdv) {
            return _.extend({}, p, _.pick(rdv, ['debut', 'nouveau']));
        }
        p = _.extend({}, p);
        p.debut = p.debut_consultation || '-';
        p.nouveau = p.patient.nouveau;
        return p;
    });
}

function initAdmissionsData(admissionsJson) {
    admissions = enrichAdmissions(admissionsJson);
    patients_en_attente = _.filter(admissions, p => p.statut == 1);
    consultations_en_cours = _.filter(admissions, p => p.statut == 2);
    syncAccueilKpiCounts();
}

function syncAccueilKpiCounts() {
    if (typeof patients_en_attente === 'undefined' || typeof consultations_en_cours === 'undefined') {
        return;
    }
    $('#nb_attente').text(patients_en_attente.length);
    $('#nb_consultations_en_cours').text(consultations_en_cours.length);
    $('#kpi_nb_attente').text(patients_en_attente.length);
    $('#kpi_nb_en_cours').text(consultations_en_cours.length);
}

function refreshAdmissionsFromApi(apiAdmissions) {
    initAdmissionsData(apiAdmissions);
    if (typeof window.filtrerPraticien === 'function') {
        window.filtrerPraticien(window.filterPraticienId != null ? window.filterPraticienId : -1);
    }
}

const ACCUEIL_TAB_IDS = [
    'liste_complete',
    'liste_salle_attente',
    'liste_en_consultation',
    'liste_consultations',
    'liste_modifies_annules',
];

const ACCUEIL_TAB_LINKS = {
    liste_complete: 'link_rdv_jour',
    liste_salle_attente: 'link_salle',
    liste_en_consultation: 'link_en_consultation',
    liste_consultations: 'link_consultations',
    liste_modifies_annules: 'link_modifications',
};

function activateAccueilTab(tabPaneId) {
    const linkId = ACCUEIL_TAB_LINKS[tabPaneId];
    const trigger = linkId ? document.getElementById(linkId) : document.querySelector(`[data-bs-toggle="tab"][href="#${tabPaneId}"]`);
    if (!trigger) {
        return;
    }
    if (window.bootstrap && bootstrap.Tab) {
        bootstrap.Tab.getOrCreateInstance(trigger).show();
    } else {
        trigger.click();
    }
}

function saveAccueilTab(tabPaneId) {
    if (!ACCUEIL_TAB_IDS.includes(tabPaneId)) {
        return;
    }
    try {
        localStorage.setItem('accueil_active_tab', tabPaneId);
    } catch (e) {}
    if (window.history && window.history.replaceState) {
        const baseUrl = window.location.pathname + window.location.search;
        window.history.replaceState(null, '', `${baseUrl}#${tabPaneId}`);
    }
}

function restoreAccueilTab() {
    let tabId = window.location.hash ? window.location.hash.slice(1) : '';
    if (!ACCUEIL_TAB_IDS.includes(tabId)) {
        try {
            tabId = localStorage.getItem('accueil_active_tab') || '';
        } catch (e) {
            tabId = '';
        }
    }
    if (ACCUEIL_TAB_IDS.includes(tabId)) {
        activateAccueilTab(tabId);
        setTimeout(adjustDashboardTables, 150);
    }
}

function annulerRdv(pk) {
    const _swal = (typeof SWAL_RDV !== 'undefined') ? SWAL_RDV : {};
    swal.fire({
        title: _swal.titre || "Etes vous sûr ?",
        type: "warning",
        showCancelButton: true,
        confirmButtonClass: "btn-danger",
        confirmButtonText: _swal.confirmer_annuler || "Oui, annuler le rendez-vous!",
        cancelButtonText: _swal.conserver || "Non, conserver le rendez-vous",
        closeOnConfirm: false
    }).then(function (result) {
        if (result.value) {
            window.location.replace("/rdvs/" + pk + "/supprimer/?next=accueil");
        }
    });
}

function annulerAdmission(pk) {
    const _sm = (typeof SWAL_MESSAGES !== 'undefined') ? SWAL_MESSAGES : {};
    swal.fire({
        title: _sm.titre || "Etes vous sûr ?",
        type: "warning",
        showCancelButton: true,
        confirmButtonClass: "btn-danger",
        confirmButtonText: _sm.confirmer_annuler_admission || "Oui, annuler l'admission!",
        cancelButtonText: _sm.conserver_admission || "Non, conserver l'admission",
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
    adjustDashboardTables();
}

function formatHeureAdmission(data) {
    if (!data || data === '-') return '';
    const m = moment(data);
    return m.isValid() ? m.format('HH:mm') : '';
}

function adjustDashboardTables() {
    [
        '#kt_datatable_rdvs',
        '#kt_datatable_salle',
        '#kt_datatable_en_consultation',
        '#kt_datatable_consultations',
        '#kt_datatable_modifies_annules',
    ].forEach(sel => {
        if ($.fn.DataTable.isDataTable(sel)) {
            const dt = $(sel).DataTable();
            dt.columns.adjust();
            if (dt.responsive && dt.responsive.recalc) {
                dt.responsive.recalc();
            }
        }
    });
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
        case '4':
            msg = 'Examen terminé';
            cssClass = 'bg-secondary';
            smiley = 'la-check-circle';
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

function mettreEnSalle(pk) {
    $.post(`/rdvs/${pk}/mettre_en_salle/`)
        .done(function () {
            toastr.success("Patient mis en salle");
            location.reload();
        })
        .fail(function (xhr) {
            var msg = "Erreur lors du changement de statut";
            if (xhr.responseJSON && xhr.responseJSON.message) msg = xhr.responseJSON.message;
            toastr.error(msg);
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

function bootstrapAccueilDashboard() {
    if (window.accueilDashboardBootstrapped) {
        return;
    }

    try {
    statutTemplate = _.template(unescapeTemplate($('#statut-template').html()));

    let tableRdvs;

    // -----------------------------------------------------------------------------------------------

    let initTableRdvs = function () {

        const _t = _.template($('#actions-rdv-template').html());

        tableRdvs = $('#kt_datatable_rdvs').DataTable({
            language: window.DT_LANGUAGE || {},
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
                                annulation: full.statut == 10 ? 'invisible' : 'visible',
                                statut: full.statut
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
            language: window.DT_LANGUAGE || {},
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
                {data: 'ordre', width: '40px'},
                {data: 'nouveau', width: '60px'},
                {data: 'patient.nom_naissance', width: '120px'},
                {data: 'patient.nom', width: '120px'},
                {data: 'patient.prenom', width: '100px'},
                {data: 'patient.age', width: '60px'},
                {data: 'patient.adresse', render: (data, type, full, meta) => data ? data.ville : '', width: '100px'},
                {data: 'patient.telephone', width: '100px', className: 'phone-cell'},
                {data: 'date', width: '80px'},
                {data: null, width: '80px', className: 'admission-cell'},
                {
                    data: 'motif',
                    render: (data, type, full, meta) => {
                        return _motifRdvTemp({id: full.id, motif: data.libelle});
                    }, width: '150px'
                },
                {
                    data: 'praticien',
                    render: (data, type, full, meta) => {
                        let nom = data ? data.nom : '';
                        return _pratTemp({id: full.id, nom: nom});
                    }, width: '150px', className: 'praticien-cell'
                },
                {data: null, width: '100px', className: 'waiting-cell'},
            ],

            order: [[0, "asc"]],

            columnDefs: [
                {
                    targets: 12, title: 'Actions', orderable: false, width: '100px', className: 'w-100px',
                    render: (data, type, full, meta) => {
                        const mesures = full.patient.mesures_jour;
                        return _t({id: full.patient.id, admission_id: full.id, mesuresId: mesures ? mesures.id : -1, en_exam_occupied: en_exam_count > 0});
                    }
                },
                {
                    targets: 0, width: '40px', orderable: true, className: 'reorder',
                    render: (data, type, full, meta) => '<i class="fas fa-arrows-alt-v mr-3"></i>' + data,
                },
                {
                    targets: 1, width: '60px', className: 'new-cell',
                    render: (data, type, full, meta) =>
                        data ? `<span class="label label-pill label-inline label-info">Nouveau</span>` : '',
                },
                {targets: 2, width: '120px', className: 'nom-naissance-cell'},
                {targets: 3, width: '120px', className: 'nom-cell'},
                {targets: 4, width: '100px', className: 'prenom-cell'},
                {targets: 5, width: '60px', className: 'age-cell'},
                {targets: 6, width: '100px', className: 'ville-cell'},
                {targets: 7, width: '100px', className: 'phone-cell'},
                {
                    targets: 8, width: '80px', className: 'date-cell',
                    render: (data, type, full, meta) => {
                        if (!data) return '';
                        const date = moment(data);
                        return date.isValid() ? date.format('HH:mm') : '-';
                    },
                },
                {
                    targets: 9, width: '80px', className: 'admission-cell',
                    render: (data, type, full, meta) => '',
                    createdCell: function (td, cellData, rowData, row, col) {
                        $(td).attr('data-heure', rowData['date']);
                    }
                },
                {targets: 10, width: '150px', className: 'motif-cell'},
                {targets: 11, width: '150px', className: 'praticien-cell'},
                {targets: 12, width: '100px', className: 'waiting-cell'}
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
    $('#kpi_nb_attente').text(patients_en_attente.length);

    // -----------------------------------------------------------------------------------------------

    let initTableConsultationEnCours = function () {

        const _t = _.template($('#actions-consultation-template').html());

        const tab = $('#kt_datatable_en_consultation').DataTable({
            language: window.DT_LANGUAGE || {},
            responsive: true,
            rowId: 'id',

            lengthMenu: [10, 25, 50, 75, 100],
            pageLength: 100,

            searchDelay: 500,
            processing: true,
            serverSide: false,

            data: consultations_en_cours,

            columns: [
                {data: 'id'},
                {data: 'nouveau'},
                {data: 'patient.nom_naissance', defaultContent: ''},
                {data: 'patient.nom'},
                {data: 'patient.prenom'},
                {data: 'patient.age'},
                {data: 'patient.adresse', render: (data, type, full, meta) => data ? data.ville : ''},
                {data: 'patient.telephone', defaultContent: ''},
                {data: 'debut'},
                {data: 'motif.libelle', defaultContent: ''},
                {data: 'praticien', render: (data, type, full, meta) => data ? data.nom : '', width: '300px'},
                {data: null},
            ],

            order: [[0, "asc"]],

            columnDefs: [
                {
                    targets: 11, title: 'Actions', orderable: false, width: '450px',
                    render: (data, type, full, meta) => {
                        const cons = typeof consultations !== 'undefined'
                            ? _.find(consultations, c => c.patient && c.patient.id === full.patient.id)
                            : null;
                        return _t({
                            id: full.patient.id,
                            consultationId: cons ? cons.id : null,
                        });
                    }
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
                    render: (data, type, full, meta) => formatHeureAdmission(data),
                },
                {targets: 9, width: '320px'},


            ],
        });

        return tab;
    };

    let tableConsultationsEnCours = initTableConsultationEnCours();
    $('#nb_consultations_en_cours').text(consultations_en_cours.length);
    $('#kpi_nb_en_cours').text(consultations_en_cours.length);

    // -----------------------------------------------------------------------------------------------

    let initTableConsultationsRealisees = function () {

        const _t = _.template($('#actions-consultation-template').html());

        const tab = $('#kt_datatable_consultations').DataTable({
            language: window.DT_LANGUAGE || {},
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
                {data: 'date', visible: false},
            ],

            order: [[8, "desc"]],

            columnDefs: [
                {
                    targets: 7, title: 'Actions', orderable: false, width: '450px',
                    render: (data, type, full, meta) => _t({id: full.patient.id, consultationId: full.id})
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
    $('#kpi_nb_realises').text(consultations.length);

    // -----------------------------------------------------------------------------------------------

    let initTableRdvsModifiesAnnules = function () {

        const _tRdv = _.template($('#actions-rdv-modif-template').html());
        const _tCons = _.template($('#actions-cons-modif-template').html());

        const tab = $('#kt_datatable_modifies_annules').DataTable({
            language: window.DT_LANGUAGE || {},
            responsive: true,

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
                        if (full.isTerminated) {
                            return _tCons({id: full.id});
                        }
                        return _tRdv(
                            {
                                id: full.id,
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
    $('#kpi_nb_modifies_card').text(rdvs_modifies_annules.length);

    // -----------------------------------------------------------------------------------------------

    function filtrerDate(dt) {
        console.info('Filtrage sur la date', dt.format('YYYY-MM-DD'));
        filtreDate = dt;
        if (!dt.isSame(moment(), 'day')) {
            activateAccueilTab('liste_complete');
            $('#link_salle,#link_consultations,#link_modifications').addClass('disabled');
        } else {
            $('#link_salle,#link_consultations,#link_modifications').removeClass('disabled');
        }
        let data = _.filter(rdvs_jour, rdv => {
            return moment(rdv.debut).isSame(dt, 'day') || moment(rdv.ancien_debut).isSame(dt, 'day');
        });

        if (window.filterPraticienId > 0)
            data = _.filter(data, rdv => rdv.praticien ? rdv.praticien.id == window.filterPraticienId : false);
        changeDonneesTable(tableRdvs, data);
        $('#nb_rdvs').text(data.length);
        $('#kpi_nb_rdvs').text(data.length);
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
        language: currentLang,
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

        window.filterPraticienId = praticienId;
        console.log('Filtre sur praticien', praticienId);

        let rdvs, salle, encours, realises, modifies;

        if (praticienId == -1) {
            rdvs = rdvs_jour;
            salle = patients_en_attente;
            encours = consultations_en_cours;
            realises = consultations;
            modifies = rdvs_modifies_annules;
        } else {
            rdvs = _.filter(rdvs_jour, rdv => rdv.praticien ? rdv.praticien.id == praticienId : false)
            salle = _.filter(patients_en_attente, c => !c.praticien || c.praticien.id == praticienId);
            encours = _.filter(consultations_en_cours, c => !c.praticien || c.praticien.id == praticienId);
            realises = _.filter(consultations, c => c.praticien ? c.praticien.id == praticienId : false);
            modifies = _.filter(rdvs_modifies_annules, rdv => rdv.praticien ? rdv.praticien.id == praticienId : false)
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
        // Sync KPI cards
        $('#kpi_nb_rdvs').text(rdvs.length);
        $('#kpi_nb_attente').text(salle.length);
        $('#kpi_nb_en_cours').text(encours.length);
        $('#kpi_nb_realises').text(realises.length);
        $('#kpi_nb_modifies_card').text(modifies.length);
    }
    window.filtrerPraticien = filtrerPraticien;
    filtrerPraticien(window.filterPraticienId != null ? window.filterPraticienId : -1);
    filtreDate = moment();
    filtrerDate(filtreDate);

    document.querySelectorAll('a[data-bs-toggle="tab"], .kpi-card[data-bs-toggle="tab"]').forEach(el => {
        el.addEventListener('shown.bs.tab', (event) => {
            const href = event.target.getAttribute('href');
            if (href && href.charAt(0) === '#') {
                saveAccueilTab(href.slice(1));
            }
            setTimeout(adjustDashboardTables, 50);
        });
    });
    $('.kpi-card[data-bs-toggle="tab"]').on('click', () => setTimeout(adjustDashboardTables, 150));
    restoreAccueilTab();

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

    window.accueilDashboardBootstrapped = true;
    } catch (error) {
        console.error('Accueil dashboard init failed:', error);
        syncAccueilKpiCounts();
    }
}

function initAccueilPage() {
    if (typeof admissions_json_initial !== 'undefined') {
        initAdmissionsData(admissions_json_initial);
    } else if (typeof patients_en_attente !== 'undefined' && typeof consultations_en_cours !== 'undefined') {
        syncAccueilKpiCounts();
    }
    bootstrapAccueilDashboard();
}

jQuery(function() {
    initAccueilPage();
});

function terminerConsultation(patientId) {
    if (!confirm("Terminer la consultation en cours ?")) return;
    fetch(`/patients/${patientId}/terminer-consultation/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            toastr.success("Consultation terminée");
            setTimeout(() => { window.location.href = '/accueil/#liste_modifies_annules'; }, 1000);
        } else {
            toastr.error(data.message || "Erreur");
        }
    })
    .catch(err => {
        console.error(err);
        toastr.error("Erreur de connexion");
    });
}

function demarrerExamen(patientId) {
    fetch(`/patients/${patientId}/demarrer-examen/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.href = data.redirect;
        } else {
            toastr.error(data.message || "Erreur");
        }
    })
    .catch(err => {
        console.error(err);
        toastr.error("Erreur de connexion");
    });
}

function remettreEnSalle(patientId) {
    fetch(`/patients/${patientId}/remettre-en-salle/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            toastr.success("Patient renvoyé en salle d'attente");
            setTimeout(() => { location.reload(); }, 1000);
        } else {
            toastr.error(data.message || "Erreur");
        }
    })
    .catch(err => {
        console.error(err);
        toastr.error("Erreur de connexion");
    });
}

function ouvrirAjoutPatientSalle() {
    document.getElementById('recherche_patient_salle').value = '';
    bootstrap.Modal.getOrCreateInstance('#modal_ajout_patient_salle').show();
    setTimeout(function() {
        document.getElementById('recherche_patient_salle').focus();
        rechercherPatientAjax();
    }, 300);
}

var rechercheTimer = null;
function rechercherPatientAjax() {
    var msg = window.MESSAGES_SALLE || {};
    var query = document.getElementById('recherche_patient_salle').value.trim();
    var container = document.getElementById('resultats_recherche_salle');
    if (rechercheTimer) clearTimeout(rechercheTimer);
    rechercheTimer = setTimeout(function() {
    rechercheTimer = null;
    container.innerHTML = '<div class="text-center py-4"><i class="la la-spinner la-spin la-2x"></i></div>';
    fetch('/patients/recherche_async/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json; charset=UTF-8', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({nom: query})
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('HTTP ' + response.status);
        }
        return response.text();
    })
    .then(function(text) {
        var items = JSON.parse(text);
        if (!items || items.length === 0) {
            container.innerHTML = '<div class="text-center text-muted py-4">' + (msg.aucun_patient || 'Aucun patient trouv\u00e9') + '</div>';
            return;
        }
        var html = '';
        items.forEach(function(p) {
            var ville = p.adresse ? (p.adresse.ville || '') : '';
            html += '<div class="list-group-item list-group-item-action d-flex align-items-center justify-content-between">' +
                '<div>' +
                '<strong>' + escapeHtml(p.nom_naissance || '') + '</strong>' +
                (p.nom ? ' ep. ' + escapeHtml(p.nom) : '') +
                ' <span class="text-muted">' + escapeHtml(p.prenom || '') + '</span>' +
                (ville ? ' <small class="text-muted"> - ' + escapeHtml(ville) + '</small>' : '') +
                (p.telephone ? ' <small class="text-muted"> - ' + escapeHtml(p.telephone) + '</small>' : '') +
                '</div>' +
                '<button class="btn btn-sm btn-success" onclick="ajouterPatientSalle(' + p.id + ')">' +
                '<i class="la la-plus"></i> ' + (msg.ajouter || 'Ajouter') + '</button>' +
                '</div>';
        });
        container.innerHTML = html;
    })
    .catch(function(err) {
        console.error('Search error:', err);
        container.innerHTML = '<div class="text-center text-danger py-4">' + (msg.erreur_recherche || 'Erreur lors de la recherche') + '</div>';
    });
    }, 300);
}

function ajouterPatientSalle(patientId) {
    var msg = window.MESSAGES_SALLE || {};
    var btn = event.target;
    if (btn.disabled) return;
    btn.disabled = true;
    btn.innerHTML = '<i class="la la-spinner la-spin"></i>';
    fetch('/patients/' + patientId + '/admission-rapide/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.status === 'success') {
            toastr.success(msg.ajoute || "Patient ajout\u00e9 en salle d'attente");
            bootstrap.Modal.getOrCreateInstance('#modal_ajout_patient_salle').hide();
            setTimeout(function() { location.reload(); }, 500);
        } else {
            btn.disabled = false;
            btn.innerHTML = '<i class="la la-plus"></i> ' + (msg.ajouter || 'Ajouter');
            toastr.error(data.message || "Erreur");
        }
    })
    .catch(function() {
        btn.disabled = false;
        btn.innerHTML = '<i class="la la-plus"></i> ' + (msg.ajouter || 'Ajouter');
        toastr.error(msg.erreur_connexion || "Erreur de connexion");
    });
}

function escapeHtml(str) {
    if (!str) return '';
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}