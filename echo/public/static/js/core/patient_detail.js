const antecedents_list_choix_map = {
    'FCV': {liste: '#fcv'},
    'Mammographie': {liste: '#mammographie'},
    'Echo Mammaire': {liste: '#echo-mammaire'},
};
let antecedent_selectionne = '';

const template_antecedent_timeline = _.template(unescapeTemplate($('#antecedent-timeline-item-template').html()));

// ListeChoix Item dont les valeurs sont entrain d'être modifiés
let targetListeChoix = null;

let minDate;
let maxDate;
let tagify;

function resetDates() {
    minDate = moment().subtract(180, 'days');
    maxDate = moment().add(180, 'days');
}

resetDates();

/* Custom filtering function which will search data in column four between two values */
$.fn.dataTable.ext.search.push(
    function (settings, data, dataIndex) {
        /*console.log(maxDate, minDate); */
        if (settings.nTable.id == "table-tentatives-pma")
            return true;
        const dt = moment(data[3], "DD/MM/YYYY").set('minute', 1);
        //console.log('Date', dt.format('DD/MM/YY'));
        let ret = dt.isBefore(maxDate) && dt.isAfter(minDate);
        //if (ret) console.log('Condition true');
        return ret;
    }
);

function resetSearch() {
    $('input').val('');
    $('select').val('');
    resetDates();
}

function getConsultationsModifsUrl(consultation) {
    switch (consultation.motif.code) {
        case 'gynecologique-defaut':
            return `/consultation_gynecologique/${consultation.id}/modifier/`;
        case 'colposcopie':
            return `/consultation_colposcopie/${consultation.id}/modifier/`;
        case 'echo-pelvienne':
            return `/consultation_echo_pelvienne/${consultation.id}/modifier/`;
        case 'obs_echo_11SA':
            return `/consultation_obs_echo_11SA/${consultation.id}/modifier/`;
        case 'obs_echo_trimestre_1':
            return `/consultation_obs_echo_premier_trimestre/${consultation.id}/modifier/`;
        case 'obs_echo_trimestre_2':
            return `/consultation_obs_echo_deuxieme_trimestre/${consultation.id}/modifier/`;
        case 'obs_echo_trimestre_3':
            return `/consultation_obs_echo_troisieme_trimestre/${consultation.id}/modifier/`;
        case 'obs_echo_croissance':
            return `/consultation_obs_echo_croissance/${consultation.id}/modifier/`;

        default:
            return `/patients/${consultation.patient.id}/consultation/${consultation.id}/modifier/`;
    }
}

function getConsultationDeleteUrl(id) {
    return `/consultation/${id}/supprimer/`;
}

function supprimerConsultation(id) {
    swal.fire({
        title: "Attention",
        text: "Voulez vous supprimer cette consultation ?",
        type: "warning",
        showCancelButton: true,
        confirmButtonClass: "btn-danger",
        confirmButtonText: "Oui, supprimer!",
        cancelButtonText: "Non, annuler",
        closeOnConfirm: false
    }).then(function (result) {
        if (result.value) {
            window.location.replace(getConsultationDeleteUrl(id));
        }
    });
}

function supprimerPMA(id) {
    swal.fire({
        title: "Attention",
        text: "Voulez vous supprimer cette tentative PMA ?",
        type: "warning",
        showCancelButton: true,
        confirmButtonClass: "btn-danger",
        confirmButtonText: "Oui, supprimer!",
        cancelButtonText: "Non, annuler",
        closeOnConfirm: false
    }).then(function (result) {
        if (result.value) {
            window.location.replace(`/tentative-pma/${id}/supprimer/`);
        }
    });
}

function initTentativesPMADatatable() {
    let _t = _.template(unescapeTemplate($('#actions-pma-template').html()));

    $('#table-tentatives-pma').DataTable({
        language: {"url": "/static/plugins/custom/datatables/French.json"},
        dom: `<'row'<'col-sm-12'tr>><'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7 dataTables_pager'lp>>`,
        responsive: true, lengthMenu: [5, 10, 25, 50], pageLength: 5, searchDelay: 500, processing: true, serverSide: false,
        data: tentativesPMA,
        columns: [
            {data: 'updated_at'},
            {data: null},
            {data: 'reussie'},
            {data: 'praticien.nom'},
            {data: null, responsivePriority: -1},
        ],
        order: [[0, "desc"]],
        columnDefs: [
            {
                targets: -1, title: 'Actions', orderable: false, width: '150px',
                render: (data, type, full, meta) => _t({modifUrl: `/tentative-pma/${full.id}/modifier`, id: full.id}),
            },
            {
                targets: 0, width: '100px',
                render: function (data, type, full, meta) {
                    // https://datatables.net/forums/discussion/45692/how-to-date-sort-as-date-instead-of-string
                    return type === 'sort' ? data : moment(data).format('DD/MM/YYYY');
                }
            },
            { targets: 1, width: '360px', render: (data, type, full, meta) => 'Tentative PMA' },
            { targets: 2, width: '360px', render: (data, type, full, meta) => data ? 'Résussite' : 'Echec' },
            { targets: 3, width: '320px', }
        ],
    });
}

function initConsultationDatatable(el) {
    let _t = _.template(unescapeTemplate($('#actions-template').html()));

    let data = [];
    const cat = $(el).attr('data-categorie');
    if (cat == 1) {
        if (grossesse != null) {
            // Catégorie Obstetrique
            // Filtrer sur la grossesse en cours
            data = consultations_obs[grossesse.id];

            $(el).DataTable({
                language: {"url": "/static/plugins/custom/datatables/French.json"},
                responsive: true,
                // Pagination settings
                dom: `<'row'<'col-sm-12'tr>><'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7 dataTables_pager'lp>>`,
                // read more: https://datatables.net/examples/basic_init/dom.html
                lengthMenu: [5, 10, 25, 50],
                pageLength: 5,
                searchDelay: 500,
                processing: true,
                serverSide: false,
                data: data,
                columns: [
                    {data: 'date'},
                    {data: 'terme'},
                    {data: 'motif.libelle'},
                    {data: 'praticien'},
                    {data: null, responsivePriority: -1},
                ],
                order: [[0, "desc"]],
                columnDefs: [
                    {
                        targets: -1, title: 'Actions', orderable: false, width: '150px',
                        render: (data, type, full, meta) => _t({modifUrl: getConsultationsModifsUrl(full), id: full.id}),
                    },
                    {
                        targets: 0, width: '150px',
                        render: function (data, type, full, meta) {
                            // https://datatables.net/forums/discussion/45692/how-to-date-sort-as-date-instead-of-string
                            return type === 'sort' ? data : moment(data).format('DD/MM/YYYY');
                        }
                    },
                    {
                        targets: 1, width: '160px',
                    },
                    {
                        targets: 2, width: '360px',
                    },
                    {
                        targets: 3, width: '320px',
                        render: function (data, type, full, meta) {
                            return data ? data.nom : '-';
                        }
                    }
                ],
            });
        }
    } else {
        data = _.filter(consultations, c => c.motif.categorie.id == $(el).attr('data-categorie'));

        $(el).DataTable({
            language: {"url": "/static/plugins/custom/datatables/French.json"},
            responsive: true,
            // Pagination settings
            dom: `<'row'<'col-sm-12'tr>><'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7 dataTables_pager'lp>>`,
            // read more: https://datatables.net/examples/basic_init/dom.html
            lengthMenu: [5, 10, 25, 50],
            pageLength: 5,
            searchDelay: 500,
            processing: true,
            serverSide: false,
            data: data,
            columns: [
                {data: 'date'},
                {data: 'motif.libelle'},
                {data: 'praticien'},
                {data: null, responsivePriority: -1},
            ],
            order: [[0, "desc"]],
            columnDefs: [
                {
                    targets: -1, title: 'Actions', orderable: false, width: '150px',
                    render: (data, type, full, meta) => _t({modifUrl: getConsultationsModifsUrl(full), id: full.id}),
                },
                {
                    targets: 0, width: '150px',
                    render: function (data, type, full, meta) {
                        // https://datatables.net/forums/discussion/45692/how-to-date-sort-as-date-instead-of-string
                        return type === 'sort' ? data : moment(data).format('DD/MM/YYYY');
                    }
                },
                {
                    targets: 1, width: '360px',
                },
                {
                    targets: 2, width: '320px',
                    render: function (data, type, full, meta) {
                        return data ? data.nom : '-';
                    }
                }
            ],
        });
    }
    console.log('initConsultationDatatable', data);
}

function showConsultationsObstetriques(el) {

    const antecedent_id = el.id.split('collapse')[1];
    console.log('Show accordion antecedent', antecedent_id);

    const tableId = '#table' + antecedent_id;
    // Si le table existe déjà, ne pas la créer
    if ($.fn.DataTable.isDataTable(tableId)) {
        console.log('La table existe déjà');
        return;
    }

    let _t = _.template(unescapeTemplate($('#actions-template').html()));

    let data;
    const ant = _.filter(antecedents_obstetriques_patient, a => a.id == antecedent_id);
    if (ant && ant.length > 0) {
        if (ant[0].grossesse_patient) {
            console.log('Grossess patient', ant[0].grossesse_patient.id);
            data = consultations_obs[ant[0].grossesse_patient.id];
            console.log('data', consultations_obs);
            console.log('data', data);
        }
    }

    $(tableId).DataTable({
        language: {"url": "/static/plugins/custom/datatables/French.json"},
        dom: `<'row'<'col-sm-12'tr>>`, responsive: true,
        lengthMenu: [5, 10, 25, 50], pageLength: -1, searchDelay: 500,
        processing: true, serverSide: false,
        data: data,
        columns: [
            {data: 'date'},
            {data: 'terme'},
            {data: 'motif.libelle'},
            {data: 'praticien.nom'},
            {data: null, responsivePriority: -1},
        ],
        order: [[0, "desc"]],
        columnDefs: [
            {
                targets: -1, title: 'Actions', orderable: false, width: '150px',
                render: (data, type, full, meta) => _t({id: full.id, modifUrl: getConsultationsModifsUrl(full)}),
            },
            {
                targets: 0, width: '150px',
                render: function (data, type, full, meta) {
                    return moment(data).format('DD/MM/YYYY');
                }
            },
            {targets: 1, width: '160px'},
            {targets: 2, width: '360px'},
            {targets: 3, width: '320px'}
        ],
    });
}

function initOrdonnancesDatatable() {
    let _t = _.template(unescapeTemplate($('#actions-ordonnances-template').html()));

    $('#ordonnances-table').DataTable({
        language: {"url": "/static/plugins/custom/datatables/French.json"},
        responsive: true,
        // Pagination settings
        dom: `<'row'<'col-sm-12'tr>><'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7 dataTables_pager'lp>>`,
        // read more: https://datatables.net/examples/basic_init/dom.html
        lengthMenu: [5, 10, 25, 50],
        pageLength: 5,
        searchDelay: 500,
        processing: true,
        serverSide: false,
        data: ordonnances,
        columns: [
            {data: 'date'},
            {data: 'type'},
            {data: 'praticien'},
            {data: null, responsivePriority: -1},
        ],
        order: [[0, "desc"]],
        columnDefs: [
            {
                targets: -1, title: 'Actions', orderable: false, width: '150px',
                render: (data, type, full, meta) => _t({id: full.pk}),
            },
            {
                targets: 0, width: '150px',
                render: function (data, type, full, meta) {
                    return moment(data).format('DD/MM/YYYY');
                }
            },
            {
                targets: 1, width: '360px',
            },
        ],
    });
}


function afficherOrdonnance(id) {
    showFrameLoading();
    $('#ordonnances-modal iframe').attr('src', `/ordonnances/${id}`);
    bootstrap.Modal.getOrCreateInstance('#ordonnances-modal').show();
}

function ajouterAntecedent(editor) {
    console.log('Editor', editor);
    const id = parseInt($(event.target).attr('data-id'));
    const phrasier = _.find(phrasiers, {id: id});
    quill = Quill.find(document.getElementById(`antecedents-${editor}`));
    quill.insertText(0, phrasier.text + "\n");
    enregistrerAntecedents(quill, editor);
}

function afficherDateAntecedent(champ) {
    $('.antecedent-date-container').css('display', 'none');
    $(champ + '-date-container').css('display', 'flex');
    const id = parseInt($(event.target).attr('data-id'));
    antecedent_selectionne = _.find(formulaire_antecedents_liste_choix, i => i.id == id);
}

function ajouterAntecedentParChamp(champ) {
    const selector = antecedents_list_choix_map[champ].liste;
    let date = $(selector + '-date').val();
    const sous_categorie = _.find(sous_categories_antecedents, sc => sc.libelle == champ);
    $.post(`/patients/${patient}/antecedents/ajouter`, {
        'sous_categorie': sous_categorie.id,
        'date': moment(date, 'DD/MM/YYYY').format('YYYY-MM-DD'),
        'text': antecedent_selectionne.valeur
    })
        .done(() => {
            toastr.success("Modifications enregistrées");
            $('.antecedent-date-container').css('display', 'none');
            $(selector + '-timeline-empty').css('display', 'none');
            const html = template_antecedent_timeline({
                date: moment(date, 'DD/MM/YYYY').format('DD/MM/YYYY'),
                valeur: antecedent_selectionne.valeur
            });
            $(selector + '-timeline').append(html);
        })
        .fail(() => {
            toastr.warning("Impossible d'enregistrer les modifications");
        });

}

function enregistrerAntecedents(editor, idx) {
    let type = idx;
    return $.post(`/patients/${patient}/antecedents`, {
        'type_antecedent': type,
        'text': $(`#antecedents-${idx} .ql-editor`).html().replace('<p', '<p style="margin:0"')
    })
        .done(() => {
            toastr.success("Modifications enregistrées");
        })
        .fail(() => {
            toastr.warning("Impossible d'enregistrer les modifications");
        });
}

function enregistrerNotes(editor) {
    console.log('Contents', editor.root.innerHTML);
    return $.post(`/patients/${patient}/notes`, {
        'text': $(`#edt-notes .ql-editor`).html().replace('<p', '<p style="margin:0"')
    })
        .done(() => {
            toastr.success("Modifications enregistrées");
        })
        .fail(() => {
            toastr.warning("Impossible d'enregistrer les modifications");
        });
}

window.fermerAntecedentObstetrique = function () {
    bootstrap.Modal.getOrCreateInstance('#antecedent-obstetrique-modal').hide();
};

function nouvelAntecedentObstetrique() {
    showFrameLoading();
    $('#antecedent-obstetrique-modal iframe').attr('src', `/patients/${patient}/antecedent_obstetrique/ajouter`);
    bootstrap.Modal.getOrCreateInstance('#antecedent-obstetrique-modal').show();

}

function modifierAntecedentObstetrique(id) {
    showFrameLoading();
    $('#antecedent-obstetrique-modal iframe').attr('src', `/antecedent_obstetrique/${id}/modifier`);
    bootstrap.Modal.getOrCreateInstance('#antecedent-obstetrique-modal').show();
}

function supprimerAntecedentObstetrique(id) {
    swal.fire({
        title: "Attention",
        text: "Voulez vous supprimer cet antécédent ?",
        type: "warning",
        showCancelButton: true,
        confirmButtonClass: "btn-danger",
        confirmButtonText: "Oui, supprimer!",
        cancelButtonText: "Non, annuler",
        closeOnConfirm: false
    }).then(function (result) {
        if (result.value) {
            window.location.replace(`/antecedent_obstetrique/${id}/supprimer/`);
        }
    });
}

function supprimerAntecedent(event, id) {
    $.get(`/antecedent/${id}/supprimer/`)
        .done(function (result) {
            $(event.target).parents('.timeline-item').remove();
            toastr.success('Antécédent supprimé');
        })
        .fail(function () {
            toastr.error("Une erreur s'est produite");
        });
}

function priseRdv() {
    showFrameLoading();
    const debut = $('#id_rdv_suivant_apres').val() || moment().add(1, 'days').format('YYYY-MM-DD');
    const fin = $('#id_rdv_suivant_avant').val() || moment().add(9, 'days').format('YYYY-MM-DD');
    $('#dispo-rdv-modal iframe').attr('src', `/rdvs/dispo/ajouter/?patient=${patient}&debut=${debut}&fin=${fin}`);
    bootstrap.Modal.getOrCreateInstance('#dispo-rdv-modal').show();
}

function rechargerInfosGrossesse() {
    window.location.reload();
}

function ajouterOptionAntecedent(liste, item) {
    const str = item.valeur.length > 50 ? item.valeur.substring(0, 50) + '...' : item.valeur;
    console.log(liste)
    $(liste).append(`<div class="menu-item px-3"><a onclick="afficherDateAntecedent('${liste}')" class="menu-link" data-id="${item.id}" href="javascript:void(0)">${str}</a></div>`);
    //$(val.liste).append(`<div class="menu-item px-3"><a onclick="ajouterAntecedent(${val.editor})" class="menu-link" data-id="${p.id}" href="javascript:void(0)">${str}</a></div>`);
}

function ajouterAlerte(text) {
    $.post(`/patients/${patientId}/alerte/`, {
        'text': text
    })
        .done(function (result) {
            console.log('Succes');
            const _t = _.template($('#alerte-template').html());
            const date = moment(result.date, 'YYYY-MM-DD').format('DD/MM/YYYY');
            $('#alertes-container').append(_t({id: result.id, text, date}));
        })
        .fail(function () {
            console.error("Impossible d'ajouter une alerte patient");
        });
}

function dismissAlerte(id) {
    $.post(`/alertes/${id}/supprimer/`, {})
        .done(function (result) {
            console.log('Succes');
           $(`#alerte-${id}`).remove();
        })
        .fail(function () {
            console.error("Impossible de supprimer une alerte patient");
        });
}

function gotoAlerte(lien) {
    const tokens = lien.split(':');
    if (tokens[0] == 'dialog') {
        if (tokens[1] == 'analyses')
            modifierPrescription(tokens[2]);
    }
}


function initEditors() {

    // init editor
    let options = {
        modules: {
            toolbar: {
                container: "#kt_forms_widget_1_editor_toolbar"
            }
        },
        placeholder: 'Saisir des notes',
        theme: 'snow'
    };

    let quill = new Quill('#edt-notes', options);
    quill.on('text-change', function (delta, oldDelta, source) {
        if (source == 'api') {
            console.log("An API call triggered this change.");
        } else if (source == 'user') {
            enregistrerNotes(quill);
        }
    });



    $('.antecedent-editor').each( (idx, el) => {
        options = {
            modules: {
                toolbar: {
                    container: "#antecedent-editor-toolbar-" + (idx+1)
                }
            },
            placeholder: 'Saisir des antécédents',
            theme: 'snow'
        };
        quill = new Quill('#'+el.id, options);
        quill.on('text-change', function (delta, oldDelta, source) {
            if (source == 'api') {
                console.log("An API call triggered this change.");
            } else if (source == 'user') {
                enregistrerAntecedents(quill, idx+1);
            }
        });
    });
}

function initTableConsultations() {
    // begin first table
    const _t = _.template(unescapeTemplate($('#actions-rapport-template').html()));

    var table = $('#rapport_consultation_datatable').DataTable({
        language: {
            "url": "/static/plugins/custom/datatables/French.json"
        },
        responsive: true,
        // read more: https://datatables.net/examples/basic_init/dom.html
        lengthMenu: [5, 10, 25, 50],
        pageLength: 25,
        searchDelay: 1000,
        processing: true,
        serverSide: true,

        ajax: {url: `/patient/${patientId}/consultation/rechercher/`, type: 'POST'},

        columns: [
            {
                data: 'date',
                render: function (data) {
                    return moment(data).format('DD/MM/YYYY');
                }
            },
            {data: 'motif.categorie.libelle'},
            {data: 'motif.libelle'},
            {data: 'praticien.nom'},
            {data: 'patient.mot_cle', "visible": false},
            {data: 'date', "visible": false},
            {data: 'date', "visible": false},
            {
                data: null, title: 'Actions', orderable: false, width: '80px',
                render: (data, type, full, meta) => _t({
                    id: full.id,
                    patientId: full.patient.id,
                    motif: full.motif.code,
                    modifUrl: getConsultationsModifsUrl(full)
                }),
            },
        ],

        order: [[0, "desc"]],

        initComplete: function () {
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


    // Filtrer la table à la saisie sans click sur le bouton chercher
    $('input,select').on('keyup', chercher);
    $('input,select').on('change', chercher);

    $('#praticiens-correspondants,#praticien').select2()
        .on('select2:select', function (e) {
            chercher();
        });


    function innerSearch() {
        let debut = $('#debut').val();
        let fin = $('#fin').val();
        if (debut != "") {
            minDate = moment(debut, 'DD/MM/YYYY');
        }
        if (fin != "") {
            maxDate = moment(fin, 'DD/MM/YYYY');
        }

        let params = {};
        $('[data-col-index]').each(function () {
            var i = $(this).data('col-index');
            let val = $(this).val();
            if (val != '' && (i == 11 || i == 12)) {
                val = moment(val, "DD/MM/YYYY").format("YYYY-MM-DD");
            }
            if (params[i]) {
                params[i] += '|' + val;
            } else {
                params[i] = val;
            }
        });

        //console.log(params);

        $.each(params, function (i, val) {
            // apply search params to datatable
            table.column(i).search(val ? val : '', false, false);
        });
        table.table().draw();
    }

    let toCtrl = null;

    function chercher() {
        if (toCtrl)
            clearTimeout(toCtrl);
        toCtrl = setTimeout(innerSearch, 500);
    }

}

function afficherConsultation(id, motif) {
    if (motif == 'pma') {
        $.get(`/tentative-pma/chercher/${id}/`)
            .done(function (result) {
                console.log('Tentative', result);
                const tentative = JSON.parse(result.tentative);
                if (tentative != -1)
                    window.location.href = `/tentative-pma/${tentative}/modifier/`;
            })
            .fail(function () {
                console.error("Impossible de chercher la tentative PMA");
            });
        return;
    }
    showFrameLoading();
    $('#consultation-modal iframe').attr('src', `/consultation/${id}`);
    bootstrap.Modal.getOrCreateInstance('#consultation-modal').show();
}

$(document).ready(() => {

    initEditors();


    tinymce.init({
        selector: '.editor_antecedent',
        language: 'fr_FR',
        plugins: ['link', 'lists', 'autolink', 'paste'],
        paste_as_text: true,
        contextmenu: 'image table',

        toolbar: [
            'undo redo | bold italic underline | fontsizeselect | forecolor backcolor | alignleft aligncenter alignright alignfull | numlist bullist outdent indent'
        ],
        menubar: false,
        inline: true,
        forced_root_block: '',
        //content_style: ".editor_antecedent { font-family: arial, sans-serif; }",
        init_instance_callback: function (editor) {
            const idx = -1 + parseInt(editor.id.substring(editor.id.indexOf('-') + 1));
            if (editor.getContent() === '' && idx < antecedents_defaut.length) {
                editor.setContent(antecedents_defaut[idx]);
            }
            editor.on('Change', e => {
                enregistrerAntecedents(editor);
            });
        }
    });

    tinymce.init({
        selector: '#editor-notes',
        language: 'fr_FR',
        plugins: ['link', 'lists', 'autolink', 'paste'],
        paste_as_text: true,
        contextmenu: 'image table',

        toolbar: [
            'undo redo | bold italic underline | fontsizeselect | forecolor backcolor | alignleft aligncenter alignright alignfull | numlist bullist outdent indent'
        ],
        menubar: false,
        inline: true,
        forced_root_block: false,
        init_instance_callback: function (editor) {
            editor.on('Change', e => {
                enregistrerNotes(editor);
            });
        }
    });

    $('.table-examen').each((i, el) => {
        initConsultationDatatable(el);
    });

    initOrdonnancesDatatable();

    initTentativesPMADatatable();

    //$('[data-toggle="popover"]').popover();
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // Phrasiers
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    const phrasiers_antecedents_map = {
        'Antécédents familiaux': {liste: '#phrases-antecedents-familiaux', editor: 1},
        'Antécédents médico-chirurgicaux': {liste: '#phrases-antecedents-chirurgicaux', editor: 2},
        'Antécédents gynécologiques': {liste: '#phrases-antecedents-gynecologiques', editor: 3},
        'Allergies': {liste: '#phrases-allergies', editor: 4}
    };
    _.each(phrasiers_antecedents_map, (val, key) => {
        _.each(phrasiers_par_categorie[key], p => {
            const str = p.libelle.length > 50 ? p.libelle.substring(0, 50) + '...' : p.libelle;
            $(val.liste).append(`<div class="menu-item px-3"><a onclick="ajouterAntecedent(${val.editor})" class="menu-link" data-id="${p.id}" href="javascript:void(0)">${str}</a></div>`);
        });
    });
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // Antécédents
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    _.each(antecedents_list_choix_map, (val, key) => {
        _.each(formulaire_antecedents_liste_choix_par_champ[key], p => {
            ajouterOptionAntecedent(val.liste, p);
        });
    });
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    const url = window.location.href;
    const activeTab = url.substring(url.indexOf("#") + 1);
    if (activeTab) {
        setTimeout(() => $(`a[href="#${activeTab}"]`).tab('show'), 1500);
    }

    const nowDate = new Date();
    const DD = ((nowDate.getDate()) < 10 ? '0' : '') + (nowDate.getDate());
    const MM = ((nowDate.getMonth() + 1) < 10 ? '0' : '') + (nowDate.getMonth() + 1);

    Inputmask("datetime", {
        inputFormat: 'dd/mm/yyyy',
        placeholder: "jj/mm/aaaa",
        min: '01/01/1900',
        max: DD + '/' + MM + '/' + nowDate.getFullYear(),
    }).mask(document.querySelectorAll('.date-picker'));

    $('.date-picker').on('keyup', (e) => {
        let m = Inputmask().mask(e.target);
        if (m.isComplete())
            $(e.target).siblings().children('button').prop('disabled', false);
    }).on('change', (e) => {
    });

    $('#cloturer-tentative-pma').modalForm({
        formURL: `/tentative-pma/${tentativePMAId}/cloturer/?next=/patients/${patientId}/#tab-pma`
    });

    $('#new-alerte').keydown(e => {
        if(e.which == 13) {
            ajouterAlerte($('#new-alerte').val());
            $('#new-alerte').val('');
        }
    })

    $('[data-form]').contextmenu(e => {
        e.preventDefault();
        const $el = $(e.target);
        targetListeChoix = null;
        let formulaire = $el.attr('data-form');
        let champ = $el.attr('data-champ');
        if (formulaire && champ) {
            showFrameLoading();
            $('#liste-choix-modal iframe').attr('src', `/listes/?formulaire=${formulaire}&champ=${champ}`);
            bootstrap.Modal.getOrCreateInstance('#liste-choix-modal').show();
            targetListeChoix = $el;
        }
    });

    $('#consult-cat-tabs .tab-pane').first().addClass(['active', 'show']);

    $('.collapse').on('show.bs.collapse', e => {
        showConsultationsObstetriques(e.target)
    });

    if (grossesse) {
        $('#terme').text(calcTerme(moment(grossesse.ddr, 'YYYY-MM-DD'), grossesse.cycle));
        $('#ddg').text(calcDDG(moment(grossesse.ddr, 'YYYY-MM-DD'), grossesse.cycle));
        $('#ddr').text(moment(grossesse.ddr, 'YYYY-MM-DD').format('DD/MM/YYYY'));
        $('#accouchement').text(calcDateAccouchement(moment(grossesse.ddr, 'YYYY-MM-DD'), grossesse.cycle));
    }

    $('#categorie').on("change", function (e) {
        $("#motif").empty();
        let motifs_categorie = _.filter(motifs_json, c => c.categorie.id == $('#categorie').val());
        $("#motif").append('<option value="" disabled selected> -------- </option>');
        motifs_categorie.map((item) => {
            if (item.code != '-')
                $('#motif').append(`<option value="${item.id}">${item.libelle}</option>`);
                console.log('code', item.libelle)
        });
    });

    $('#debut').datepicker({
        todayHighlight: true,
        autoclose: true,
        language: 'fr',
        weekStart: 1,
        format: 'dd/mm/yyyy',
        orientation: 'bottom',
    });

    $('#fin').datepicker({
        todayHighlight: true,
        autoclose: true,
        language: 'fr',
        weekStart: 1,
        format: 'dd/mm/yyyy',
        orientation: 'bottom'
    });


    initTableConsultations();

    EventManager.subscribe("patient:updated", function (event) {
        console.info('Event patient:updated', event);
        window.location.reload();
    });

    EventManager.subscribe("grossesse:updated", function (event) {
        console.info('Event grossesse:updated', event);
        rechargerInfosGrossesse();
    });

    EventManager.subscribe("liste:updated", function (event, payload) {
        console.info('Event liste:updated', event, payload);
        let sel = $(`[data-form="${payload.formulaire}"][data-champ="${payload.champ}"]`).siblings('.dropdown-menu');
        sel.empty();
        formulaire_antecedents_liste_choix = payload.liste;
        payload.liste.forEach(item => {
            ajouterOptionAntecedent('#'+sel.attr('id'), item);
        });
    });

    EventManager.subscribe("liste:selected", function (event, listechoix) {
        console.info('Event liste:selected', event, listechoix);
        const el = antecedents_list_choix_map[listechoix.champ].liste;
        $('.antecedent-date-container').css('display', 'none');
        $(el + '-date-container').css('display', 'flex');
        antecedent_selectionne = listechoix;
    });
});

