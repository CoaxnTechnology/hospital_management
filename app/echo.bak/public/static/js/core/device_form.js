$(document).ready(() => {
    $('.date').inputmask("datetime", {
        inputFormat: 'dd/mm/yyyy',
        placeholder: "jj/mm/aaaa",
        min: '01/01/1900',
        max: '31/12/2900',
    });
    $('#id_ip').inputmask({
        alias: "ip",
        greedy: false //The initial mask shown will be "" instead of "-____".
    });
});