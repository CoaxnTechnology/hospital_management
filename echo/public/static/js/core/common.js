toastr.options = {
    "closeButton": false,
    "debug": false,
    "newestOnTop": false,
    "progressBar": true,
    "positionClass": "toastr-bottom-right",
    "preventDuplicates": true,
    "onclick": null,
    "showDuration": "300",
    "hideDuration": "1000",
    "timeOut": "5000",
    "extendedTimeOut": "1000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
};

function unescapeTemplate(str) {
    return str.replace(/&lt;%/gi, '<%').replace(/%&gt;/gi, '%>');
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

let csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

moment.locale('fr');

function chargerImageB64(logo_url, callback) {
    // To bypass errors (“Tainted canvases may not be exported” or “SecurityError: The operation is insecure”)
    // The browser must load the image via non-authenticated request and following CORS headers
    let logoB64 = '';
    let img = new Image();
    img.crossOrigin = 'Anonymous';
    // The magic begins after the image is successfully loaded
    img.onload = function () {
        let canvas = document.createElement('canvas'),
            ctx = canvas.getContext('2d');

        canvas.height = img.naturalHeight;
        canvas.width = img.naturalWidth;
        ctx.drawImage(img, 0, 0);

        // Unfortunately, we cannot keep the original image type, so all images will be converted to PNG
        // For this reason, we cannot get the original Base64 string
        let uri = canvas.toDataURL('image/png');
        logoB64 = uri.replace(/^data:image.+;base64,/, '');
        logoB64 = 'data:image/jpeg;base64,' + logoB64;
        callback(logoB64);
    };

    // If you are loading images from a remote server, be sure to configure “Access-Control-Allow-Origin”
    // For example, the following image can be loaded from anywhere.
    img.src = logo_url;
}

// Calcul terme de grossesse à partir des dernière règles
function calcTerme(ddr, cycle) {
    //console.log('Calc terme', ddr.format('DD/MM/YY'), cycle)
    const newddr = ddr.add(cycle - 28, 'days');
    const terme = moment().diff(newddr, 'days');
    const sa = Math.floor(terme / 7);
    let termeDisp = `${sa} SA`;
    const jours = terme % 7;
    if (jours > 0) {
        termeDisp += ` + ${jours} J`;
    }
    //console.log('Terme', termeDisp);
    return termeDisp;
}

function calcTermeDDG(ddg, cycle) {
    const ddr = ddg.subtract(cycle - 14, 'days');
    return calcTerme(ddr.clone(), cycle);
}

function calcTermeSA(ddr, cycle) {
    const newddr = ddr.add(cycle - 28, 'days');
    const terme = moment().diff(newddr, 'days');
    const sa = Math.floor(terme / 7);

    //console.log('Terme SA', sa);
    return sa;
}

function calcDDG(ddr, cycle) {
    return ddr.add(cycle - 14, 'days').format('DD/MM/YYYY');
}

function calcDDR(ddg, cycle) {
    return ddg.subtract(cycle - 14, 'days').format('DD/MM/YYYY');
}

function calcDateAccouchement(ddr, cycle) {
    return ddr.add(cycle - 28, 'days').add(dureeGrossesse, 'days').format('DD/MM/YYYY');
}

function isFormNotEmpty(el) {
    let fields = $(el).find('.form-control,.form-select');
    for (let i = 0; i < fields.length; i++) {
        if ($(fields[i]).val() != '')
            return true;
    }

    fields = $(el).find('.form-check-input');
    for (let i = 0; i < fields.length; i++) {
        if ($(fields[i]).is(':checked'))
            return true;
    }
    return false;
}

function afficherRdvModal(url) {
    showFrameLoading();
    $('#rdv-modal iframe').attr('src', url);
    bootstrap.Modal.getOrCreateInstance('#rdv-modal').show();
}
function afficherAbsenceModal(url) {
    showFrameLoading();
    $('#absence-modal iframe').attr('src', url);
    bootstrap.Modal.getOrCreateInstance('#absence-modal').show();
}

function afficherTelechargerFichierModal(patientId) {
    showFrameLoading();
    let url = `/patients/${patientId}/telecharger/`;
    $('#fichiers-patient-modal iframe').attr('src', url);
    bootstrap.Modal.getOrCreateInstance('#fichiers-patient-modal').show();
}

function afficherMesuresModal(patientId, mesuresId) {
    showFrameLoading();
    if (mesuresId != -1)
        url = `/mesures/${mesuresId}/modifier`;
    else
        url = `/patients/${patientId}/mesures/ajouter`;
    $('#mesures-modal iframe').attr('src', url);
    bootstrap.Modal.getOrCreateInstance('#mesures-modal').show();
}

function afficherSupportModal() {
    bootstrap.Modal.getOrCreateInstance('#support-modal').show();
}

function envoyerMessageSupport() {
    let msg = '';
    msg += `<b>Compte client</b>: ${nom_client}<br>`;
    msg += `<b>Nom utilisateur</b>: ${nom_utilisateur}<br><br>`;
    msg += 'Message:<br>'
    msg += $('#support-msg-desc').val().replace(/\r\n|\r|\n/g, "<br />");
    $.post(`/utils/email/`, {
        'subject': 'Demande de support',
        'body': msg,
    })
        .done(function (result) {
            console.info('Message envoyé');
        });
    bootstrap.Modal.getOrCreateInstance('#support-modal').hide();
}


function showFrameLoading() {
    $('iframe').css('visibility', 'hidden');
    $('.loading').removeClass('d-none');
    $('.loading').addClass('d-flex');
}

function hideFrameLoading() {
    $('.loading').addClass('d-none');
    $('.loading').removeClass('d-flex');
    $('iframe').css('visibility', 'visible');
}

// Conversion d'une date sélectionnée avec un Date Picker au format date de la base
function dtPickToDb(dt) {
    return moment(dt, 'DD/MM/YYYY').format('YYYY-MM-DD');
}

function dtPickToMoment(dt) {
    return moment(dt, 'DD/MM/YYYY');
}


function formatNomPatient(nom_naissance, nom, prenom) {
    if (nom_naissance == '') nom_naissance = nom;
    if (nom == '') nom = nom_naissance;

    if (nom_naissance != nom) {
        return `${prenom} ${nom_naissance} ep ${nom}`;
    } else {
        return `${prenom} ${nom_naissance}`;
    }
}

function disp(variable, defaultIfEmpty = '') {
    return (_.isNil(variable) || variable === '') ? defaultIfEmpty : variable;
}

function scrollToEl(elId) {
    $('html, body').animate({
        scrollTop: $(elId).offset().top
    }, 1000);
}

window.EventManager = {
    subscribe: function (event, fn) {
        $(this).bind(event, fn);
    },
    publish: function (event, payload = {}) {
        $(this).trigger(event, [payload]);
    }
};


function initTimer() {
    // Nombre de secondes depuis l'ouverture de la consultation
    let totalSeconds = 0;

    function pad(val) {
        var valString = val + "";
        if (valString.length < 2) {
            return "0" + valString;
        } else {
            return valString;
        }
    }

    function setTime() {
        ++totalSeconds;
        $('#timer-seconds').html(pad(totalSeconds % 60));
        $('#timer-minutes').html(pad(parseInt(totalSeconds / 60)));
    }

    setInterval(setTime, 1000);
}

function creerCercle() {
    interact('.draggable')
        .draggable({
            // enable inertial throwing
            inertia: true,
            // keep the element within the area of it's parent
            modifiers: [
                interact.modifiers.restrictRect({
                    restriction: 'parent',
                    endOnly: true
                })
            ],
            listeners: {
                // call this function on every dragmove event
                move: dragMoveListener,

                // call this function on every dragend event
                end(event) {
                    var textEl = event.target.querySelector('p')

                    textEl && (textEl.textContent =
                        'moved a distance of ' +
                        (Math.sqrt(Math.pow(event.pageX - event.x0, 2) +
                            Math.pow(event.pageY - event.y0, 2) | 0))
                            .toFixed(2) + 'px')
                }
            }
        });
}

function ellipsis(str, chars) {
    return str.substr(0, chars - 1) + (str.length > chars ? '&hellip;' : '')
}

/*
String.prototype.ellipsis =
    function (n) {
        return this.substr(0, n - 1) + (this.length > n ? '&hellip;' : '');
    };*/

function fixEditorHtml(selector, editor) {
    editor.find(selector).children('p').after('<br/>');
    editor.find(selector).children('p').contents().unwrap();
}