$(document).ready(() => {
    $('.btn-modifier-logo').click((e) => {
        e.preventDefault();
        $el = $(e.target);
        $el.parents('.logo-preview').css('display', 'none');
        $el.parents('.logo-preview').siblings('.logo-modifier').css('display', 'block');
    });

    $('.btn-modifier-footer').click((e) => {
        e.preventDefault();
        $el = $(e.target);
        $el.parents('.footer-preview').css('display', 'none');
        $el.parents('.footer-preview').siblings('.footer-modifier').css('display', 'block');
    });

    tinymce.init({
        selector: '.editor',
        language: 'fr_FR',
        plugins: [
            'link',
            'lists',
            'autolink',
            'image',
            'table',
            'paste'
        ],
        contextmenu: 'image table',
        paste_as_text: true,

        toolbar: [
            'undo redo | bold italic underline | fontsizeselect | forecolor backcolor | alignleft aligncenter alignright alignfull | numlist bullist outdent indent'
        ],
        statusbar: false,
        menubar: false,
        inline: false
        //content_style: "body { font-family: Arial; }",
    });

    $('#btn-liste-traitements').click(() => {
        showFrameLoading();
        $('#traitements-modal iframe').attr('src', `/traitements/`);
        bootstrap.Modal.getOrCreateInstance('#traitements-modal').show();
    });
    $('#btn-liste-traitements-pma').click(() => {
        showFrameLoading();
        $('#traitements-modal iframe').attr('src', `/traitements-pma/`);
        bootstrap.Modal.getOrCreateInstance('#traitements-modal').show();
    });
    $('#btn-liste-prescriptions').click(() => {
        showFrameLoading();
        $('#prescriptions-modal iframe').attr('src', `/prescriptions/`);
        bootstrap.Modal.getOrCreateInstance('#prescriptions-modal').show();
    });
    $('#btn-liste-biologie').click(() => {
        showFrameLoading();
        $('#biologie-modal iframe').attr('src', `/analyses-biologiques/`);
        bootstrap.Modal.getOrCreateInstance('#biologie-modal').show();
    });
    $('#btn-liste-template-edition').click(() => {
        showFrameLoading();
        $('#templates-edition-modal iframe').attr('src', `/templates-edition/`);
        bootstrap.Modal.getOrCreateInstance('#templates-edition-modal').show();
    });
    $('#ouvrir_liste_prestations').click(() => {
        showFrameLoading();
        $('#prestations-modal iframe').attr('src', `/prestations/`);
        bootstrap.Modal.getOrCreateInstance('#prestations-modal').show();

    });
    $('#ouvrir_liste_motifs').click(() => {
        showFrameLoading();
        $('#motifs-modal iframe').attr('src', `/motifs_absence/`);
        bootstrap.Modal.getOrCreateInstance('#motifs-modal').show();

    });
    $('#ouvrir_liste_reglements').click(() => {
        showFrameLoading();
        $('#reglements-modal iframe').attr('src', `/reglements/`);
        bootstrap.Modal.getOrCreateInstance('#reglements-modal').show();

    });
    $('#ouvrir_liste_devices').click(() => {
        showFrameLoading();
        $('#devices-modal iframe').attr('src', `/devices/`);
        bootstrap.Modal.getOrCreateInstance('#devices-modal').show();

    });

    Inputmask({
        mask: "99:99"
    }).mask(document.querySelectorAll('.time'));

    /*
    $('.time').timepicker({
        timeFormat: 'HH:mm',
        interval: 30,
        minTime: '7',
        maxTime: '21',
        startTime: '08:00',
        dynamic: false,
        dropdown: true,
        scrollbar: true,
        change: function (time) {
            const timepicker = $(this).timepicker();
            //let fin = moment(timepicker.format(time), 'HH:mm').add(duree_rdv, 'minutes');
        }
    });*/

    FormValidation.formValidation(
        document.getElementById('form_1'),
        {
            fields: {
                'duree_rdv_defaut': {
                    validators: {
                        notEmpty: {
                            message: 'Durée de rendez-vous est obligatoire'
                        }
                    }
                },
                'duree_gross_sa': {
                    validators: {
                        notEmpty: {
                            message: 'Ce champ est obligatoire'
                        }
                    }
                },
                'duree_gross_j': {
                    validators: {
                        notEmpty: {
                            message: 'Ce champ est obligatoire'
                        }
                    }
                }
            },

            plugins: {
                trigger: new FormValidation.plugins.Trigger(),
                bootstrap: new FormValidation.plugins.Bootstrap5({

                }),
                submitButton: new FormValidation.plugins.SubmitButton(),
                // Submit the form when all fields are valid
                defaultSubmit: new FormValidation.plugins.DefaultSubmit(),
            }
        }
    );
});
