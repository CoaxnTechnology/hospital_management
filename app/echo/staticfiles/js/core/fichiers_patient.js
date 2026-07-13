$(document).ready(() => {

    const template_fichier = _.template(unescapeTemplate($('#template-fichier').html()));
    $('#kt_dropzone_1').dropzone({
        url: `/patients/${patient_pk}/fichier/ajouter/`,
        paramName: "file",
        maxFiles: 1,
        maxFilesize: 10,
        addRemoveLinks: true,
        headers: {
            'X-CSRFToken': csrftoken
        },
        init: function () {
            this.on("success", function (file, response) {
                const nom = response.nom.length > 22 ? `${response.nom.substring(0, 22)}...` : response.nom;
                let html = template_fichier({pk: response.pk, chemin: response.chemin, nom: nom});
                $('#files-grid').prepend(html);
                if ($('#files-grid .text-muted').length) {
                    $('#files-grid .text-muted').remove();
                }
                toastr.success(upload_success_msg);
                this.removeAllFiles(true);
            });
        }
    });
})