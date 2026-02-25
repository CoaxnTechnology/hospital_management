const saveUrl = '/analyses/enregistrer/';
let collectionAnalyses = [];
let ajouterDatePrescription = true;

function enregistrerPrescription() {
    console.log('Enregistrer prescription');
    let date_presc = $('#date_prescription').val();
    let date_res = $('#date_resultat').val();
    let data = {
        id: prescriptionId,
        patient: patient.id,
        date_prescription: dtPickToDb(date_presc)
    };
    if(date_res != '') data['date_resultat'] = dtPickToDb(date_res);

    console.info('enregistrerPrescription post data', data);

    return new Promise((resolve, reject) => {
        $.post(saveUrl, data)
            .done(function (result) {
                prescriptionId = result.id;
                console.log('Succes', result);
                window.parent.EventManager.publish("prescription-analyse-biologique:created");
                resolve();
            })
            .fail(function () {
                console.error('Impossible de sauvegarder');
                reject();
            });
    });
}

function ajouterResultats(analyses) {
    let data = {
        prescription: prescriptionId,
        analyses: JSON.stringify(analyses)
    };
    console.log('Data post', data);
    $.post('/resultats-analyses', data)
        .done(function (result) {
            prescriptionId = result.id;
            res = result.resultats;
            resultats = resultats.concat(res);
            _.each(res, r => {
                let html = _t({resultat: r});
                $('#presc-analyses-container').append(html);
            });
            window.parent.EventManager.publish("prescription-analyse-biologique:created");
            console.log('Succes', result);
        })
        .fail(function () {
            console.error('Impossible de sauvegarder');
        });
}

function modifierResultat(id) {
    const val = $(`.valeur-resultat[data-id=${id}]`).val();
    let data = {
        valeur: val,
    };
    console.log('Data post', data);
    $.ajax(`/resultats-analyses/${id}`, { method: 'PUT', data: JSON.stringify(data)})
        .done(function (result) {
            let r = _.find(resultats, {id: result.id});
            if (r) r.valeur = val;
            window.parent.EventManager.publish("prescription-analyse-biologique:created");
            console.log('Succes', result);
        })
        .fail(function () {
            console.error('Impossible de sauvegarder');
        });
}

function modifierObs(id) {
    const val = $(`.obs-resultat[data-id=${id}]`).val();
    let data = {
        observation: val,
    };
    console.log('Data post', data);
    $.ajax(`/resultats-analyses/${id}`, { method: 'PUT', data: JSON.stringify(data)})
        .done(function (result) {
            let r = _.find(resultats, {id: result.id});
            if (r) r.observation = val;
            window.parent.EventManager.publish("prescription-analyse-biologique:created");
            console.log('Succes', result);
        })
        .fail(function () {
            console.error('Impossible de sauvegarder');
        });
}

function modifierAnormale(id) {
    const val = $(`.anormale-resultat[data-id=${id}]`).is(":checked");
    let data = {
        valeur_anormale: val,
    };
    console.log('Data post', data);
    $.ajax(`/resultats-analyses/${id}`, { method: 'PUT', data: JSON.stringify(data)})
        .done(function (result) {
            let r = _.find(resultats, {id: result.id});
            if (r) r.valeur_anormale = val;
            window.parent.EventManager.publish("prescription-analyse-biologique:created");
            console.log('Succes', result);
        })
        .fail(function () {
            console.error('Impossible de sauvegarder');
        });
}

function supprimerResultat(id) {
    $.ajax(`/resultats-analyses/${id}`, { method: 'DELETE'})
        .done(function (result) {
            _.remove(resultats, {id: result.id});
            $(`#resultat-${id}`).remove();
            window.parent.EventManager.publish("prescription-analyse-biologique:created");
            console.log('Succes', result);
        })
        .fail(function () {
            console.error('Impossible de supprimer');
        });
}

const _t = _.template($('#presc-analyse-item-template').html());

function onAjouterAnalyseClick(analyseId) {
    //const target = el.hasClass('ajouter_analyse') ? el : el.parents('.ajouter_analyse');
    //const analyseId = parseInt(target.attr('data-id'));
    if (_.find(resultats, r => r.analyse.id == analyseId)) return; // Ne pas ajouter une analyse en double
    let analyse = _.find(analyses, {id: analyseId});
    $('#msg-vide').css('display', 'none');
    if (prescriptionId == -1)
        enregistrerPrescription().then(() => ajouterResultats([analyse]));
    else
        ajouterResultats([analyse]);
}

function onAjouterCollectionClick(collectionId) {
    let collection = _.find(collections, {id: collectionId});
    let resultatsToSave = [];
    for (let i = 0; i < collection.analyses_list.length; i++) {
        const analyse = collection.analyses_list[i];
        if (_.find(resultats, r => r.analyse.id == analyse.id)) continue; // Ne pas ajouter une analyse en double
        resultatsToSave.push(analyse);
    }
    $('#msg-vide').css('display', 'none');

    if (resultatsToSave.length > 0) {
        if (prescriptionId == -1)
            enregistrerPrescription().then(() => ajouterResultats(resultatsToSave));
        else
            ajouterResultats(resultatsToSave);
    }
}

function onResultatChange(id) {
    if ($('#date_resultat').val() == '') {
        $('#date_resultat').datepicker('update', moment().format('DD/MM/yyyy'));
        enregistrerPrescription().then(() => {});
    }
    modifierResultat(id);
}

function onObsChange(id) {
    modifierObs(id);
}

function onAnormaleChange(id) {
    modifierAnormale(id);
}

function onSelectionnerCollectionClick(eve, collectionId) {
    let collection = _.find(collections, {id: collectionId});
    collectionAnalyses = collection.analyses_list;
    let table = $('#table-collection-analyse').DataTable();
    table.clear();
    table.rows.add(collectionAnalyses);
    table.draw();

    $('#collections-group .list-group-item').removeClass('bg-light-blue-100');
    $(`#collection-${collectionId}`).addClass('bg-light-blue-100');

}

function imprimerPrescription() {
    const tpl = _.template(unescapeTemplate(modele));
    const templateSignature = _.template(unescapeTemplate($('#template-signature').html()));
    const signatureData = {signature_titre: praticien, signature_img: signatureB64};

    let data = '<p><ul>';
    _.each(resultats, res => {
        data += '<li style="margin-bottom: 10px">';
        data += `<strong>${res.analyse.libelle}</strong>`;
        if (res.observation)
            data += '<br>' + res.observation;
        data += '</li>';
    });
    data += '</ul></p>';
    let content = tpl({
        ville: ajouterDatePrescription ? ville : '',
        date: ajouterDatePrescription ? (datePrescription ? datePrescription.format('DD/MM/YYYY') : moment().format('DD/MM/YYYY')) : null,
        motif: 'Analyses biologiques',
        patient: patient,
        data: data
    });
    console.log('Content', content);
    //impressionGenerique(content);

    let makeDoc = [];
    cleanPDF(htmlToPdfmake(content, defaultHtml2PDFOptions), makeDoc);
    console.log(makeDoc[0]);

    const dd = {
        pageSize: 'A5',
        pageMargins: defaultMargins(),
        header: defaultHeader,
        footer: defaultFooter,
        content: [
            makeDoc[0],
            htmlToPdfmake(templateSignature(signatureData))
        ],
        defaultStyle: {
            fontSize: 10
        }
    };

    pdfDoc = pdfMake.createPdf(dd, defaultHtml2PDFOptions);
    pdfDoc.print();
}

$(document).ready(e => {
    if (prescriptionId == -1) {
        $('#date_prescription').val(moment().format('DD/MM/yyyy'));
    }

    if (_.isEmpty(modele) || _.isNil(modele) || modele === 'None') {
        modele = $('#edition-prescription-template').html();
    }

    $('.date').datepicker({
        todayHighlight: true,
        autoclose: true,
        language: 'fr',
        weekStart: 1,
        format: 'dd/mm/yyyy',
    }).on('changeDate', function (e) {
        enregistrerPrescription().then(() => {});
    });

    $('#date_prescription').change(e => {
        $el = $(e.target);
        if ($el.val() == '') {
            // Forcer une valeur
            $el.val(datePrescription.format('DD/MM/yyyy'));
        } else {
            datePrescription = dtPickToMoment($el.val());
        }
    });


    $('#btn-imprimer').click(() => {
        imprimerPrescription();
    });

    $('#cb-inserer-date-prescription').on('change', e => {
        ajouterDatePrescription = $(e.target).is(':checked');
    });

    const analyseTpl = _.template($('#analyse-template').html());

    $('#table-analyses').DataTable({
        language: {"url": "/static/plugins/custom/datatables/French.json"},
        responsive: true,
        // Pagination settings
        dom: "<'row'<'col-sm-12 col-md-6'f>>" +
            "<'row'<'col-sm-12'tr>>" +
            "<'row'<'col-sm-12 col-md-5'><'col-sm-12 col-md-7'p>>",
        // read more: https://datatables.net/examples/basic_init/dom.html
        lengthMenu: [5, 10, 25, 50],
        pageLength: 15,
        searchDelay: 500,
        processing: true,
        serverSide: false,
        data: analyses,
        ordering: false,
        columns: [
            {data: 'code'},
            {data: 'libelle'},
            {data: null},
        ],
        columnDefs: [
            {
                targets: -1, title: '&nbsp;', orderable: false, width: '50px',
                render: (data, type, full, meta) => {
                    return analyseTpl({analyse: full})
                },
            },
            {
                targets: 0, width: '100px'
            },
            {
                targets: 1, width: '360px',
            }
        ],

        initComplete() {
            console.log('initComplete');
            //$('.ajouter_analyse').click(e => onAjouterAnalyseClick($(e.target)));
        }
    });

    collectionAnalyses = collections.length > 0 ? collections[0].analyses_list : [];
    $('#table-collection-analyse').DataTable({
        language: {"url": "/static/plugins/custom/datatables/French.json"},
        responsive: true,
        // Pagination settings
        dom: "<'row'<'col-sm-12 col-md-6'f>>" +
            "<'row'<'col-sm-12'tr>>" +
            "<'row'<'col-sm-12 col-md-5'><'col-sm-12 col-md-7'p>>",
        // read more: https://datatables.net/examples/basic_init/dom.html
        lengthMenu: [5, 10, 25, 50],
        pageLength: 15,
        searchDelay: 500,
        processing: true,
        serverSide: false,
        scrollY: '40vh',
        scrollX: false,
        scrollCollapse: true,
        data: collectionAnalyses,
        columns: [
            {data: 'code'},
            {data: 'libelle'},
            {data: null, responsivePriority: -1},
        ],
        ordering: false,
        columnDefs: [
            {
                targets: -1, title: '&nbsp;', orderable: false, width: '50px',
                render: (data, type, full, meta) => {
                    return analyseTpl({analyse: full})
                },
            },
            {
                targets: 0, width: '100px'
            },
            {
                targets: 1, width: '360px',
            }
        ],
    });

    $('#btn_enregistrer').click(e => {
        enregistrerPrescription().then(() => {
            window.parent.fermerModals();
            //setTimeout(() => window.parent.location.reload(), 500);
        });
    });

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        $('#table-collection-analyse').DataTable().draw();
    });
});