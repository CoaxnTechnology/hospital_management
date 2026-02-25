function supprimer(pk) {
     swal.fire({
        title: "Etes vous sûr ?",
        text: "La suppression est définitive!",
        type: "warning",
        showCancelButton: true,
        confirmButtonClass: "btn-danger",
        confirmButtonText: "Oui, supprimer!",
        cancelButtonText: "Non, annuler",
        closeOnConfirm: false
    }).then(function (result) {
        if (result.value) {
            window.location.replace("/etablissements/" + pk + "/supprimer");
        }
    });
}

function selectionner(id) {
    let etablissement = _.find(etablissements, e => e.id == id);
    EventManager.publish("etablissement:selected", etablissement);
    window.parent.fermerModals();
}

$(document).ready(() => {
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
            pageLength: 10,
            searchDelay: 500,
            processing: true,
            serverSide: false,

            data: etablissements,

            columns: [
                {data: 'nom'},
                {data: 'telephone'},
                {data: null},
            ],

            order: [[0, "asc"]],

            columnDefs: [
                {
                    targets: 2, title: 'Actions', orderable: false, width: '150px',
                    render: function (data, type, full, meta) {
                        return _t({id: full.id});
                    }
                },
                { targets: 0, width: '300px'},
                {targets: 1, width: '160px'}
            ],
        });

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