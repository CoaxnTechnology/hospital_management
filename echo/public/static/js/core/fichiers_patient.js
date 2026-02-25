function creerFormDeplacementFichier(el) {
    const id = el.data('id');
    const patient_id = el.data('patient');
    el.modalForm({
        formURL: `/patients/${patient_id}/fichier/${id}/deplacer/`
    });
}

$(document).ready(() => {

    $('.deplacer_fichier').each((index, element) => {
        creerFormDeplacementFichier($(element));
    });

    const template_fichier = _.template(unescapeTemplate($('#template-fichier').html()));
    $('#kt_dropzone_1').dropzone({
        url: `/patients/${patient}/fichier/ajouter/`, // Set the url for your upload script location
        paramName: "file", // The name that will be used to transfer the file
        maxFiles: 1,
        maxFilesize: 10, // MB
        addRemoveLinks: true,
        params: {
            //dossier: parseInt($('.dossiers .nav-link.active').attr('data-id'))
        },
        headers: {
            'X-CSRFToken': csrftoken
        },
        accept: function (file, done) {
            done();
        },
        init: function () {
            this.on("sending", function (file, xhr, formData) {
                formData.append("dossier", parseInt($('.dossiers .nav-link.active').attr('data-id')));
            });
            this.on("success", function (file, response) {
                console.log('response ', response);
                const dossier = response.dossier;
                const nom = response.nom.length > 22 ? `${response.nom.substring(0, 22)}...` : response.nom;
                let html = template_fichier({pk: response.pk, chemin: response.chemin, nom: nom});
                $(`#tab-dossier-${response.dossierId}`).prepend(html);
                // Sélectionner le premier element qui vient d'être ajouté
                creerFormDeplacementFichier($('.deplacer_fichier').first());
                toastr.success("Fichier téléchargé avec succès");
                this.removeAllFiles(true);
            });
        }
    });
})