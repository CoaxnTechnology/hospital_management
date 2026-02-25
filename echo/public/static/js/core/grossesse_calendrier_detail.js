$(document).ready(() => {
    _t = _.template($('#template-header').html());
    $('#btn-imprimer').click(() => {
        let content = _t({date: moment().format('DD/MM/YYYY')});
        console.log(content);
        content += $('#calendrier').html();
        impressionGenerique(content);
    });
})