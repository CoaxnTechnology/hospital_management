$(document).ready(() => {

    tinymce.init({
        selector: '#id_text',
        language: 'fr_FR',
        plugins: ['link', 'lists', 'autolink', 'paste'],
        paste_as_text: true,
        contextmenu: 'image table',

        toolbar: [
            'undo redo | bold italic underline | fontsizeselect | forecolor backcolor | alignleft aligncenter alignright alignfull | numlist bullist outdent indent'
        ],
        statusbar: false,
        menubar: false,
        inline: false,
        forced_root_block: false,
        //content_style: "body { font-family: Arial; }",
        init_instance_callback: function (editor) {
            editor.on('Change', function (e) {
            });
        }
    });


});