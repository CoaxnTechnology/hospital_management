$(document).ready(() => {


$('.date').datepicker({
    todayHighlight: true,
    autoclose: true,
    language: 'fr',
    weekStart: 1,
    format: 'dd/mm/yyyy',
    onSelect: function (dateText, inst) {
        // insert into editor
        //tinymce.activeEditor.execCommand('mceInsertContent', false, dateText);
    }
});
$('body').style('background-color', '#ff0');

});