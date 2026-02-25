"use strict";

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

    $('#praticiens-correspondants,#praticien').val(null).trigger('change');
    tagify.removeAllTags();
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


jQuery(document).ready(function () {

    $('#categorie').on("change", function (e) {
        $("#motif").empty();
        const catId = $('#categorie').val();
        let motifs_categorie = _.filter(motifs, c => c.categorie.id == catId && c.actif == true);
        console.log("Motifs",motifs_categorie);
        $("#motif").append('<option value="" disabled selected> -------- </option>');
        motifs_categorie.map((item) => {
            if (item.code != '-') {
                $('#motif').append(`<option value="${item.id}">${item.libelle}</option>`);
                console.log('code', item.libelle);
            }
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

    const inputElm = document.querySelector('input[name=tags]');

    tagify = new Tagify(inputElm, {
        keepInvalidTags: true,
        placeholder: "Saisir un mot clé",
        delimiters: " ",
        editTags: false,
        // make an array from the initial input value
        whitelist: list_mots
    });

    const initTable1 = function () {
        // begin first table
        const _t = _.template(unescapeTemplate($('#actions-rapport-template').html()));

        var table = $('#rapport_consultation_datatable').DataTable({
            language: {
                "url": "/static/plugins/custom/datatables/French.json"
            },
            responsive: true,
            // Pagination settings
            /*dom: `<'row'<'col-sm-6 text-left'f><'col-sm-6 text-right'B>>
			<'row'<'col-sm-12'tr>>
			<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7 dataTables_pager'lp>>`,*/

            // read more: https://datatables.net/examples/basic_init/dom.html
            dom: 'Bfrtip',
            buttons: [
                {
                    extend: 'excel',
                    text: 'Export Excel',
                    exportOptions: {
                        columns: [ 0, 3, 4, 5, 6, 7, 8, 9 ]
                    }
                }
            ],
            lengthMenu: [10, 25, 50, 75, 100],

            pageLength: 50,

            searchDelay: 1000,
            processing: true,
            serverSide: true,

            ajax: { url: "/rapports/consultation/rechercher/", type: 'POST' },

            columns: [
                {data: 'patient.id', "visible": false},
                {data: 'patient.adresse', "visible": false, render: (data, type, full, meta) => data ? data.gouvernorat : '' },
                {data: 'patient.praticiens_correspondants' ,"visible": false,
                    render: function (data) {
                    var list = '';
                        for(var i=0;i<data.length; i++){
                            list +=data[i].nom+' '+data[i].prenom+',';
                        }
                        return list;
                    }
                },
                {
                    data: 'date',
                    render: function (data) {
                        return moment(data).format('DD/MM/YYYY');
                    }
                },
                {data: 'patient.nom'},
                {data: 'patient.nom_naissance'},
                {data: 'patient.prenom'},
                {data: 'motif.categorie.libelle'},
                {data: 'motif.libelle'},
                {data: 'praticien.nom'},
                {data: 'patient.mot_cle',"visible": false},
                {data: 'date', "visible": false},
                {data: 'date', "visible": false},
                {   data: null,
                    title: 'Actions',
                    orderable: false,
                    width: '80px',
                    render: (data, type, full, meta) => _t({id: full.id, patientId: full.patient.id, motif: full.motif.code}),},
            ],

            order: [[0, "asc"]],

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

    };
     initTable1();

});

