function supprimer(pk) {
    const _sm = (typeof SWAL_MESSAGES !== 'undefined') ? SWAL_MESSAGES : {};
    swal.fire({
        title: _sm.titre || "Etes vous sûr ?",
        text: _sm.suppression_definitive || "La suppression est définitive!",
        type: "warning",
        showCancelButton: true,
        confirmButtonClass: "btn-danger",
        confirmButtonText: _sm.confirmer_supprimer || "Oui, supprimer!",
        cancelButtonText: _sm.annuler || "Non, annuler",
        closeOnConfirm: false
    }).then(function (result) {
        if (result.value) {
            window.location.replace("/collection-analyses/" + pk + "/supprimer");
        }
    });
}

$(document).ready(() => {
    const initTable = function () {

        const _t = _.template($('#actions-template').html());

        const table = $('#datatable').DataTable({
            language: window.DT_LANGUAGE || {},
            responsive: true,
            // Pagination settings
            dom: `<'row'<'col-sm-12'tr>>
			<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7 dataTables_pager'lp>>`,
            // read more: https://datatables.net/examples/basic_init/dom.html
            lengthMenu: [5, 10, 25, 50],
            pageLength: 10,
            searchDelay: 500,
            processing: true,
            serverSide: true,
            ajax: { url: "/collection-analyses/recherche/", type: 'POST' },

            columns: [
                {data: 'nom'},
                {data: null},
            ],

            order: [[0, "asc"]],

            columnDefs: [
                {
                    targets: 1, title: 'Actions', orderable: false, width: '100px',
                    render: function (data, type, full, meta) {
                        return _t({id: full.id});
                    }
                },

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