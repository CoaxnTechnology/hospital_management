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
            window.location.replace("/utilisateurs/" + pk + "/supprimer");
        }
    });
};

jQuery(document).ready(function () {


})