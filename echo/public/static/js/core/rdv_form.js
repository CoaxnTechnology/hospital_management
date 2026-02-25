function supprimer(eve, pk) {
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
            window.location.replace("/rdvs/" + pk + "/supprimer");
        }
    });

    eve.preventDefault();
}

let duree_rdv = duree_rdv_defaut;
let now = moment();

$(document).ready(function () {

    $('#libelle_statut').text(statut);

    $('#date_debut').datepicker({
        todayHighlight: true,
        autoclose: true,
        language: 'fr',
        weekStart: 1,
        format: 'dd/mm/yyyy'
    }).on('changeDate', () => {

        debut = moment($('#date_debut').val() + ' ' + $('#heure_debut').val(), "DD/MM/YYYY HH:mm");
        if (debut.isBefore(now)) {
            $('#invalide_date').addClass('d-block');
        } else {
            $('#invalide_date').addClass('invalid-feedback');
        }
        console.log($('#heure_debut').val());
        if ($('#heure_debut').val()) {
            debut = moment($('#date_debut').val() + ' ' + $('#heure_debut').val(), "DD/MM/YYYY HH:mm");
            console.log(debut.format());
            $('#id_debut').val($('#date_debut').val() + 'T' + $('#heure_debut').val());
        }
    });

    $('#date_fin').datepicker({
        todayHighlight: true,
        autoclose: true,
        language: 'fr',
        weekStart: 1,
        format: 'dd/mm/yyyy'
    }).on('changeDate', () => {
        if ($('#heure_fin').val()) {
            $('#id_fin').val($('#date_fin').val() + 'T' + $('#heure_fin').val());
        }
    });

    const time_step = 5;

    $('#heure_debut').timepicker({
        timeFormat: 'HH:mm',
        interval: time_step,
        minTime: '7',
        maxTime: '22',
        startTime: '07:00',
        dynamic: false,
        dropdown: true,
        scrollbar: true,
        change: function (time) {
            const timepicker = $(this).timepicker();
            let fin = moment(timepicker.format(time), 'HH:mm').add(duree_rdv, 'minutes');
            console.log('fin', fin);
            console.log('duree', duree_rdv);
            $('#heure_fin').val(fin.format('HH:mm'));
        }
    });

    $('#heure_fin').timepicker({
        timeFormat: 'HH:mm',
        interval: time_step,
        minTime: '7',
        maxTime: '22',
        startTime: '07:00',
        dynamic: false,
        dropdown: true,
        scrollbar: true
    });


    if (rdv_id != -1 && $('#heure_debut').val() && $('#heure_fin').val()) {
        duree_rdv = moment($('#heure_fin').val(), "HH:mm").diff(moment($('#heure_debut').val(), "HH:mm"), 'minutes');
        console.log('Durée rdv initiale', duree_rdv);
    }

    function completerChampsPatient(patient) {
        $('[name="prenom"]').typeahead('val', patient.prenom);
        $('[name="nom"]').typeahead('val', patient.nom);
        $('[name="nom_naissance"]').typeahead('val', patient.nom_naissance);
        patient.telephone && $('[name="telephone"]').val(patient.telephone);
        if (patient.adresse) {
            patient.adresse.ville && $('[name="ville"]').typeahead('val', patient.adresse.ville);
            patient.adresse.cp && $('[name="cp"]').typeahead('val', patient.adresse.cp);
            patient.adresse.gouvernorat && $('[name="gouvernorat"]').typeahead('val', patient.adresse.gouvernorat);
        }
        /*if (patient.adresse.ville)
            $('[name="telephone"]').get(0).focus();
        else
            $('[name="ville"]').get(0).focus();*/
        console.log('Patient id', patient.id);
        $('#id_patient').val(patient.id);
        $('[name="nouveau"]').prop("checked", false);
        console.log('Patient field', $('#id_patient').val());
    }

    const autocompletePatients = function (key) {
        return new Bloodhound({
            remote: {
                url: '/patients/recherche_async/',

                prepare: function (query, settings) {
                    settings.type = "POST";
                    settings.contentType = "application/json; charset=UTF-8";
                    data = {};
                    data[key] = query;
                    settings.data = JSON.stringify(data);
                    return settings;
                },
                transform: function (data) {
                    let newData = [];
                    let items = JSON.parse(data);
                    console.log('Autocomplete count', items.length);
                    items.forEach(function (item) {
                        newData.push(item);
                    });
                    return newData;
                }
            },
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace(key),
            queryTokenizer: Bloodhound.tokenizers.whitespace
        });

    };

    $('[name="nom"]').typeahead(null, {
        name: 'patients',
        display: 'nom',
        source: autocompletePatients('nom'),
        minLength: 2,
        templates: {
            suggestion: _.template('<div><%=nom_naissance%> ep. <strong><%=nom%></strong> <%=prenom%> (<%=date_naissance%>)</div>')
        }
    }).on('typeahead:select', (e, suggestion) => {
        console.log('Suggestion', suggestion)
        completerChampsPatient(suggestion);
    }).on('typeahead:autocomplete', (e, suggestion) => {
        completerChampsPatient(suggestion);
    });

    $('[name="nom_naissance"]').typeahead(null, {
        name: 'patients',
        display: 'nom_naissance',
        source: autocompletePatients('nom_naissance'),
        minLength: 2,
        templates: {
            suggestion: _.template('<div><strong><%=nom_naissance%></strong> ep. <%=nom%> <%=prenom%> (<%=date_naissance%>)</div>')
        }
    }).on('typeahead:select', (e, suggestion) => {
        completerChampsPatient(suggestion);
    }).on('typeahead:autocomplete', (e, suggestion) => {
        completerChampsPatient(suggestion);
    });

    $('[name="prenom"]').typeahead(null, {
        name: 'patients',
        display: 'prenom',
        source: autocompletePatients('prenom'),
        minLength: 2,
        templates: {
            suggestion: _.template('<div><%=nom_naissance%> ep. <%=nom%> <strong><%=prenom%></strong> (<%=date_naissance%>)</div>')
        }
    }).on('typeahead:select', (e, suggestion) => {
        completerChampsPatient(suggestion);
    }).on('typeahead:autocomplete', (e, suggestion) => {
        completerChampsPatient(suggestion);
    });

    FormValidation.formValidation(
        document.getElementById('form_1'),
        {
            fields: {
                'prenom': {
                    validators: {
                        notEmpty: {
                            message: 'Prénom est obligatoire'
                        }
                    }
                },

                'nom_naissance': {
                    validators: {
                        notEmpty: {
                            message: 'Nom naissance est obligatoire'
                        }
                    }
                },

                'telephone': {
                    validators: {
                        notEmpty: {
                            message: 'Téléphone est obligatoire'
                        },
                        numeric: {
                            message: 'Téléphone doit contenir des chiffres uniquement'
                        },
                        /*stringLength: {
                            min: 8,
                            max: 8,
                            message: 'Téléphone doit contenir 8 chiffres'
                        }*/
                    }
                },

            },

            plugins: {
                trigger: new FormValidation.plugins.Trigger(),
                bootstrap: new FormValidation.plugins.Bootstrap(),
                submitButton: new FormValidation.plugins.SubmitButton(),
                // Submit the form when all fields are valid
                defaultSubmit: new FormValidation.plugins.DefaultSubmit(),
            }
        }
    );


});
