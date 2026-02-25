let datasource = listes;
let showDesactives = false;


function setNewDataSource(source) {
    let table = $('table').DataTable();
    table.clear();
    table.rows.add(source);
    table.draw();
}

function toggleAfficherDesactives(show) {
    showDesactives = show;
    setNewDataSource(getDataSource());
}

function getDataSource() {
    return showDesactives ? datasource : _.filter(datasource, {actif: true})
}

function toggleActif(id, actif) {
    let postData = {actif: actif};
    $.ajax(`/listes/${id}/desactiver/`, { method: 'POST', data: JSON.stringify(postData)})
        .done(function (result) {
            toastr.success(actif ? "Entrée activée" : "Entrée désactivée");
            const idx = _.findIndex(datasource, {id: id});
            if (idx > -1) {
                datasource[idx].actif = actif;
                setNewDataSource(getDataSource());
                EventManager.publish("liste:updated",
                    {formulaire: formulaire, champ: champ, liste: _.filter(datasource, {actif: true})});
            } else {
                console.error(`ListeChoix avec ID ${id} non trouvée dans la source`);
            }
        })
        .fail(function () {
            toastr.error("Une erreur s'est produite");
        });
}

function selectionner(id) {
    let liste = _.find(listes, e => e.id == id);
    EventManager.publish("liste:selected", liste);
    window.parent.fermerModals();
}

$(document).ready(() => {

    if (startEvent) {
        EventManager.publish("liste:updated",
                    {formulaire: formulaire, champ: champ, liste: _.filter(datasource, {actif: true})});
    }

    $('#cb-show-desactive').on('change', e => {
        toggleAfficherDesactives($(e.target).is(':checked'));
    });

    const initTable = function () {
        const _t = _.template($('#actions-template').html());

        const table = $('table').DataTable({
            language: {
                "url": "/static/plugins/custom/datatables/French.json"
            },
            responsive: true,
            // Pagination settings
            dom: `<'row'<'col-sm-12'tr>>
			<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7 dataTables_pager'lp>>`,
            // read more: https://datatables.net/examples/basic_init/dom.html
            lengthMenu: [5, 10, 25, 50],
            pageLength: 25,
            searchDelay: 500,
            processing: true,
            serverSide: false,

            data: getDataSource(),

            columns: [
                {data: 'libelle'},
                {data: 'valeur'},
                {data: 'actif'},
                {data: null},
            ],

            order: [[0, "asc"]],

            columnDefs: [
                {
                    targets: 3, title: 'Actions', orderable: false, width: '150px',
                    render: function (data, type, full, meta) {
                        return _t({id: full.id, actif: full.actif});
                    }
                },
                {targets: 0, width: '150px'},
                {targets: 1, width: '300px'},
                {
                    targets: 2, width: '50px',
                    render: function (data, type, full, meta) {
                        return data ? 'Oui' : 'Non';
                    }
                }
            ],
        });

        function chercher() {
            let params = {};
            $('.datatable-input').each(function () {
                var i = $(this).data('col-index');
                if (params[i]) {
                    params[i] += '|' + $(this).val();
                } else {
                    params[i] = $(this).val();
                }
            });

            $.each(params, function (i, val) {
                // apply search params to datatable
                table.column(i).search(val ? val : '', false, false);
            });
            table.table().draw();
        }

        $('input').on('keyup', chercher);

    };

    initTable();
});