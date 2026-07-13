$(document).ready(() => {

    $('select').selectpicker();

    $('#kt_dropzone_1').dropzone({
        url: `/patients/${patient}/fichier/ajouter/`, // Set the url for your upload script location
        paramName: "file", // The name that will be used to transfer the file
        maxFiles: 1,
        maxFilesize: 10, // MB
        addRemoveLinks: true,
        params: {
            //dossier: $('.dossiers .nav-link.active').attr('id')
        },
        headers: {
            'X-CSRFToken': csrftoken
        },
        accept: function (file, done) {
            done();
        },
        init: function () {
            this.on("sending", function (file, xhr, formData) {
                formData.append("dossier", $('select').val());
            });
            this.on("success", function (file, response) {
                console.log('response ', response);
                window.parent.fermerModals("Fichier téléchargé avec succès");
            });
        }
    });
})