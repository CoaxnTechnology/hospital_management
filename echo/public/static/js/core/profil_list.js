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
            window.location.replace("/utilisateurs/" + pk + "/supprimer");
        }
    });
};

jQuery(document).ready(function () {


})