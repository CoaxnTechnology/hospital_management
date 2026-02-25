$(document).ready(() => {

    tinymce.init({
        selector: '#id_contenu',
        plugins: ['link', 'lists', 'autolink', 'paste', 'table', 'code'],
        language: 'fr_FR',
        contextmenu: 'image table code',
        paste_as_text: true,
        menubar: 'file edit view insert format tools table tc help',
        toolbar: [
            'undo redo | bold italic underline | fontsizeselect | forecolor backcolor | alignleft aligncenter alignright alignfull | numlist bullist outdent indent | table'
        ],
        statusbar: false,
        inline: false,
        forced_root_block: false,
        //content_style: "body { font-family: Arial; }",
        init_instance_callback: function (editor) {
            $('.tox-tinymce').height(window.innerHeight - 130);
            editor.on('Change', function (e) {
            });
        }
    });

    $(window).resize(e => {
        $('.tox-tinymce').height(window.innerHeight - 130);
    });

});