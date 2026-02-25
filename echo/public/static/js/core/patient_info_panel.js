let patientId = _.isObject(patient) ? patient.id : patient;
let selectionEtablissement = false;

function supprimer_praticen(pk) {
    swal.fire({
        title: "Etes vous sûr ?",
        type: "warning",
        showCancelButton: true,
        confirmButtonClass: "btn-danger",
        confirmButtonText: "Oui, supprimer le praticien!",
        cancelButtonText: "Non, conserver le praticien",
        closeOnConfirm: false
    }).then(function (result) {
            if (result.value) {
                $.ajax({
                    method: 'post',
                    dataType: 'json',
                    url: "/praticiens/" + pk + "/supprimer",
                    success: function (data) {
                        if (!data.error) {
                            window.location.reload();
                        }
                    }
                });
            }
        }
    );
}

function dissocierEtablissement(eve, pk) {
    $.ajax({
        method: 'post',
        dataType: 'json',
        url: `/patients/${pk}/etablissement/dissocier/`,
        success: function (data) {
            if (!data.error) {
                window.location.reload();
            } else {
                console.error(data.error);
                toastr.warning("Une erreur s'est produite");
            }
        }
    });
}

function ajouterPraticien(praticien) {

    $.post(`/patients/${patientId}/praticien/ajouter/`, {
        'praticien': praticien.id,
    })
        .done(function (result) {
            console.log("Praticien ajouté avec succès");
            const html = _.template($('#praticien-template').html())({praticien});
            $('.praticiens-list').append(html);
            $('#praticiens-msg-vide').css('display', 'none');
            creerFormModifierPraticien($('.modifier_praticien').last());
            toastr.success('Praticien ajouté');
        })
        .fail(function () {
            console.error("Impossible d'ajouter le praticien");
            toastr.error("Une erreur s'est produite");
        })
        .always(function () {
        });
}

function creerFormModifierPraticien(el) {
    const praticien_id = el.data('id');
    /*el.modalForm({
        formURL: `/praticiens/${praticien_id}/modifier/?patient=${patientId}&next=/patients/${patientId}`
    });*/
}

function modifierPrescription(id) {
    showFrameLoading();
    const url = `/analyses/${id}/modifier`;
    $('#prescription-analyses-modal iframe').attr('src', url);
    bootstrap.Modal.getOrCreateInstance('#prescription-analyses-modal').show();
}

function supprimerPrescription(id) {
    swal.fire({
        title: "Etes vous sûr ?",
        type: "warning",
        showCancelButton: true,
        confirmButtonClass: "btn-danger",
        confirmButtonText: "Oui, supprimer la prescription!",
        cancelButtonText: "Non, conserver la prescription",
        closeOnConfirm: false
    }).then(function (result) {
            if (result.value) {
                $.ajax({
                    method: 'post',
                    dataType: 'json',
                    url: `/analyses/${id}/supprimer/`,
                })
                    .done(data => {
                        $(`#prescription-${id}`).remove();
                        toastr.success('Prescription supprimée');
                    })
                    .fail(function () {
                        toastr.error("Une erreur s'est produite");
                    });
            }
        }
    );
}

function modifierEtablissement(id) {
    showFrameLoading();
    $('#etablissements-modal iframe').attr('src', `/etablissements/${id}/modifier`);
    bootstrap.Modal.getOrCreateInstance('#etablissements-modal').show();
}


function modifierPatient(id) {
    showFrameLoading();
    $('#patient-form-modal iframe').attr('src', `/patients/${id}/modifier`);
    bootstrap.Modal.getOrCreateInstance('#patient-form-modal').show();
}

function rechargerInfosPatient() {
    $.get(`/patients/${patientId}/infos/`)
        .done(function (data) {
            const _t = _.template($('#patient-info-template').html());
            const patient = JSON.parse(data);
            console.log('Patient infos', patient);
            $('#patient-info-container').html(_t({patient}));
            initTags();
            if (patient.grossesse_encours) {
                const g = patient.grossesse_encours;
                const ddr = moment(g.ddr, 'YYYY-MM-DD');
                $('.terme').text(calcTerme(ddr.clone(), g.cycle));
                let ddg = ddr.clone().add(g.cycle - 14, 'days');
                $('.ddg').text(ddg.format('DD/MM/YYYY'));
                $('.ddr').text(ddr.format('DD/MM/YYYY'));
                $('.accouchement').text(calcDateAccouchement(ddr.clone(), g.cycle));
            }
            toastr.success('Modifications enregistrées');
        }).fail(function () {
            console.error("Impossible de charger les infos patient");
    });
}

function onAddTag(e) {
    let val = $('#tags').val();
    let mot_cles = [];
    if (val != '')
        mot_cles = JSON.parse(val);
    mot_cles.push({value: e.detail.data.value});
    $.ajax({
        type: "POST",
        url: `/patients/${patientId}/mot_cle/ajouter/`,
        data: { mot_cle: JSON.stringify(mot_cles) },
        success: function (data) {
            toastr.success('Modifications enregistrées');
        }
    });
}

function onRemoveTag(e) {
    mot_cle = $('#tags').val();
    $.ajax({
        type: "POST",
        url: `/patients/${patientId}/mot_cle/supprimer/`,
        data: {mot_cle: mot_cle},
        success: function (data) {
            toastr.success('Modifications enregistrées');
        }
    });
}

function initTags() {
    const inputElm = document.querySelector('input[name=tags]');
    const tagify = new Tagify(inputElm, {
        keepInvalidTags: true,
        placeholder: "Saisir un mot clé",
        delimiters: " ",
        editTags: false,
        // make an array from the initial input value
        whitelist: list_mots
    });

    tagify.on('add', onAddTag)
        .on('remove', onRemoveTag);
}

function modifierGrossesse() {
    showFrameLoading();
    $('#grossesse-modal iframe').attr('src', `/grossesse/${grossesse.id}/modifier`);
    bootstrap.Modal.getOrCreateInstance('#grossesse-modal').show();
}

function ajouterPrescriptionAnalyses() {
    showFrameLoading();
    $('#prescription-analyses-modal iframe').attr('src', `/patients/${patientId}/analyses/ajouter/`);
    bootstrap.Modal.getOrCreateInstance('#prescription-analyses-modal').show();
}

function nouvelleGrossesse() {
    showFrameLoading();
    $('#grossesse-modal iframe').attr('src', `/patients/${patientId}/grossesse/ajouter`);
    bootstrap.Modal.getOrCreateInstance('#grossesse-modal').show();
}

function afficherCalendrierGrossesse() {
    showFrameLoading();
    $('#calendrier-grossesse-modal iframe').attr('src', `/grossesses/${grossesse.id}/calendrier`);
    bootstrap.Modal.getOrCreateInstance('#calendrier-grossesse-modal').show();
}

function cloturerGrossesse() {
    showFrameLoading();
    $('#antecedent-obstetrique-modal iframe').attr('src', `/patients/${patientId}/antecedent_obstetrique/ajouter/?action=cloturer_grossesse`);
    bootstrap.Modal.getOrCreateInstance('#antecedent-obstetrique-modal').show();
}


$(document).ready(() => {

    let gross_data_disp = {
        'NFS': 'nfs',
        'GP75': 'gp75',
        'Gly': 'gly',
        'PV': 'pv',
        'Rubéole': 'rub'
    };
    const itemTemp = _.template($('#grossesse-data-item').html());
    _.each(gross_data_disp, (val, key) => {
        if (grossesse_data[val]) {
            $('#grossesse-panel').append(
                itemTemp({label: key, titre: grossesse_data[val], valeur: grossesse_data[val].replace(/(\r\n|\r|\n)/g, '<br>')})
            );
        }
    });
    $('[data-toggle="tooltip"]').tooltip();
    //$('[data-toggle="popover"]').popover();
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));

    const autocomplete = function (key) {
        return new Bloodhound({
            local: praticiens,
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace(key),
            queryTokenizer: Bloodhound.tokenizers.whitespace
        });
    };

    $('#praticien_recherche').typeahead(null, {
        name: 'praticiens',
        display: 'nom',
        source: autocomplete('nom'),
        minLength: 2,
        templates: {
            suggestion: _.template('<div>Dr. <%=nom%> <%=prenom%> - <%=specialite%></div>'),
        }
    }).on('typeahead:select', (e, suggestion) => {
        ajouterPraticien(suggestion);
    });

    /*$('#nouveau_praticien').modalForm({
        formURL: `/praticiens/ajouter/?patient=${patientId}&next=/patients/${patientId}`
    });*/

    $('.modifier_praticien').each((index, element) => {
        creerFormModifierPraticien($(element));
    });

    initTags();

    function afficherRecherche() {
        $('#chercher_praticien').fadeOut(100);
        $('#praticiens_label').fadeOut(100);
        $('#nouveau_praticien').fadeOut(100);
        $('#praticien_recherche_container').css({opacity: 0.0, visibility: "visible"}).animate({opacity: 1.0}, 200);
        $('#praticien_recherche').focus();
    }

    function masquerRecherche() {
        $('#praticien_recherche_container').css({opacity: 1.0, visibility: "visible"}).animate({opacity: 0.0}, 200);
        $('#chercher_praticien').fadeIn(100);
        $('#praticiens_label').fadeIn(100);
        $('#nouveau_praticien').fadeIn(100);
        $('#praticien_recherche').typeahead('val', '');
    }

    $('#chercher_praticien').click(afficherRecherche);
    $('#btn-retour').click(masquerRecherche);

    $('#praticien_recherche').keyup(() => {
        const text = $('#praticien_recherche').val();
        $('.quick-search-close').css('display', text === '' ? 'none' : 'block');
    });

    $('.quick-search-close').click(() => {
        $('#praticien_recherche').typeahead('val', '');
        $('#praticien_recherche').focus();
    });

    const template_etablissement = _.template(unescapeTemplate($('#etablissement-template').html()));

    //Chercher un etablissement
    function afficherRechercheEtablissement() {
        $('#chercher_etablissement').fadeOut(100);
        $('#etablissement_label').fadeOut(100);
        $('#nouveau_lieu').fadeOut(100);
        $('#etablissement_recherche_container').css({opacity: 0.0, visibility: "visible"}).animate({opacity: 1.0}, 200);
        $('#etablissement_recherche').focus();
    }

    function masquerRechercheEtablissement() {
        $('#etablissement_recherche_container').css({opacity: 1.0, visibility: "visible"}).animate({opacity: 0.0}, 200);
        $('#chercher_etablissement').fadeIn(100);
        $('#etablissement_label').fadeIn(100);
        $('#nouveau_lieu').fadeIn(100);
        $('#etablissement_recherche').typeahead('val', '');
    }

    $('#chercher_etablissement').click(e => {
        selectionEtablissement = true;
        showFrameLoading();
        $('#etablissements-modal iframe').attr('src', `/etablissements`);
        bootstrap.Modal.getOrCreateInstance('#etablissements-modal').show();
    });
    $('#btn-retour-etablissement').click(masquerRechercheEtablissement);

    $('#etablissement_recherche').keyup(() => {
        const text = $('#etablissement_recherche').val();
        $('.quick-search-etablishment-close').css('display', text === '' ? 'none' : 'block');
    });

    $('.quick-search-etablishment-close').click(() => {
        $('#etablissement_recherche').typeahead('val', '');
        $('#etablissement_recherche').focus();
    });

    const autocomplete_etablissement = function (key) {
        return new Bloodhound({
            local: etablissements,
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace(key),
            queryTokenizer: Bloodhound.tokenizers.whitespace
        });
    };

    $('#etablissement_recherche').typeahead(null, {
        name: 'etablissements',
        display: 'nom',
        source: autocomplete_etablissement('nom'),
        minLength: 2,
        templates: {
            suggestion: _.template('<div><%=nom%></div>'),
        }
    }).on('typeahead:select', (e, suggestion) => {
        associerEtablissement(suggestion);
    });

    function associerEtablissement(etablissement) {
        console.log('Asssociation etablissement', etablissement);

        $.post(`/patients/${patientId}/etablissement/associer/`, {
            'etablissement': etablissement.id,
        })
            .done(function (result) {
                let html = template_etablissement({
                    nom: etablissement.nom,
                    patient_id: patient,
                    etablissement_id: etablissement.id
                });
                $('.etablissement-list').html(html);
                $('#etablissements-vide').remove();
                $('#lieu-toolbar').css('visibility', 'hidden');
                toastr.success('Modifications enregistrées');
            })
            .fail(function () {
                console.error("Impossible d'associer un établissement");
                toastr.error("Une erreur s'est produite");
            })
            .always(function () {
            });
    }

    $('#ouvrir_liste_ordonnances').click(() => {
        showFrameLoading();
        $('#ordonnances-modal iframe').attr('src', `/patients/${patientId}/ordonnances/ajouter`);
        bootstrap.Modal.getOrCreateInstance('#ordonnances-modal').show();
    });

    $('#ouvrir_historique_consultations').click(() => {
        showFrameLoading();
        $('#historique-consultations-modal iframe').attr('src', `/patients/${patientId}/consultations/`);
        bootstrap.Modal.getOrCreateInstance('#historique-consultations-modal').show();
    });

    $('#ouvrir_antecedents').click(() => {
        bootstrap.Modal.getOrCreateInstance('#antecedents-modal').show();
    });

    $('#ouvrir_liste_certificats').click(() => {
        showFrameLoading();
        $('#certificats-modal iframe').attr('src', `/patients/${patientId}/certificats/ajouter`);
        bootstrap.Modal.getOrCreateInstance('#certificats-modal').show();
    });

    $('.modifier_rdv').click(e => {
        showFrameLoading();
        const target = $(e.target).hasClass('modifier_rdv') ? $(e.target) : $(e.target).parents('.modifier_rdv');
        const url = `/rdvs/${target.attr('data-id')}/modifier`;
        $('#rdv-modal iframe').attr('src', url);
        bootstrap.Modal.getOrCreateInstance('#rdv-modal').show();
    });

    EventManager.subscribe("prescription-analyse-biologique:created", function () {
        $.get(`/patients/${patientId}/analyses/`)
            .done(function (result) {
                $('#prescriptions-container').html(result);
                //KTApp.initPopovers();
            })
            .fail(function () {
                console.error("Impossible de charger les prescriptions");
            });
    });

    EventManager.subscribe("etablissement:selected", function (event, payload) {
        console.info('Event etablissement:selected', event, payload);
        if (selectionEtablissement)
            associerEtablissement(payload);
        selectionEtablissement = false;
    });

    EventManager.subscribe("patient:updated", function (event) {
        console.info('Event patient:updated', event);
        rechargerInfosPatient();
    });

    EventManager.subscribe("grossesse:updated", function (event) {
        console.info('Event grossesse:updated', event);
        rechargerInfosPatient();
    });
});