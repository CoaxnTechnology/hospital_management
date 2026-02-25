let targetSelect = null;

function afficherLieuAccouchement() {
    if (['H', 'C'].includes($('#id_lieu_accouchement_principal').val())) {
        $('#lieu_accouch_precis').removeClass('d-none');
    } else {
        $('#lieu_accouch_precis').addClass('d-none');
    }

    if (['A'].includes($('#id_lieu_accouchement_principal').val())) {
        $('#lieu_accouch_libre').removeClass('d-none');
    } else {
        $('#lieu_accouch_libre').addClass('d-none');
    }
}

function selectionnerEtablissement() {
    showFrameLoading();
    $('#etablissements-modal iframe').attr('src', `/etablissements`);
    $('#etablissements-modal').modal();
}

$(document).ready(() => {
    $('#id_nb_foetus').change(e => {
        $('#foetus_2, #foetus_3').css('display', 'none');
        const nb = $(e.target).val();
        if (nb > 1)
            $('#foetus_2').css('display', 'block');
        if (nb > 2)
            $('#foetus_3').css('display', 'block');
    });

    /*$('#id_date_accouchement').inputmask("datetime", {
        inputFormat: 'dd/mm/yyyy',
        placeholder: "jj/mm/aaaa",
        min: '01/01/1900',
        max: '31/12/2900',
    });*/

    $('#id_date_accouchement').datepicker({
        todayHighlight: true,
        autoclose: true,
        language: 'fr',
        weekStart: 1,
        format: 'dd/mm/yyyy'
    }).on('changeDate', function (e) {
        let acc = moment(e.format('yyyy-mm-dd'));
        if (ddr) {
            if (acc.isValid()) {
                console.log('Accc', acc);
                const terme = acc.diff(ddr, 'days');
                $('.terme').val(Math.floor(terme/7));
            }
        }
    });


    $('#btn_annuler').click(e => {
        window.parent.fermerAntecedentObstetrique();
    });

    if (nb_foetus > 1)
        $('#foetus_2').css('display', 'block');

    if (nb_foetus > 2)
        $('#foetus_3').css('display', 'block');

    afficherLieuAccouchement();
    $('#id_lieu_accouchement_principal').change(e => afficherLieuAccouchement());

    $('#id_grossesse').djangoSelect2({containerCssClass : 'select2-sm'});


    $('.select2, select').contextmenu(e => {
        e.preventDefault();
        targetSelect = null;
        let target = $(e.target);
        if (target.parents().hasClass('select2')) {
            // Traiter cas spécial de select2 qui crée un autre node dans le dom et masque le select original
            target = target.parents('.select2').siblings('select');
        }
        let formulaire = target.attr('data-form');
        let champ = target.attr('data-champ');
        if (formulaire && champ) {
            showFrameLoading();
            $('#liste-choix-modal iframe').attr('src', `/listes/?formulaire=${formulaire}&champ=${champ}`);
            $('#liste-choix-modal').modal();
            targetSelect = target;
        }
    });


    window.parent.EventManager.subscribe("etablissement:selected", function (event, payload) {
        console.info('Event etablissement:selected', event, payload);
        $('#id_lieu_accouchement').val(payload.id);
        $('#lieu_disp').removeClass('d-none').val(payload.nom);
        $('#btn-selection-etablissement').text('Modifier');
    });

    EventManager.subscribe("liste:updated", function (event, payload) {
        console.info('Event liste:updated', event, payload);
        let sel = $(`select[data-form="${payload.formulaire}"][data-champ="${payload.champ}"]`);
        let selectedVal = sel.val();
        sel.empty();
        sel.append('<option value="" selected="">---------</option>');
        payload.liste.forEach(item => {
            let opt = `<option value="${item.id}">${item.libelle}</option>`;
            sel.append(opt);
        });
        console.log('Selected value', selectedVal);
        if (_.find(payload.liste, l => l.id == selectedVal)) {
            console.log('Setting selected value', selectedVal);
            sel.val(selectedVal);
        }
    });

    EventManager.subscribe("liste:selected", function (event, listechoix) {
        console.info('Event liste:selected', event, listechoix);
        if (targetSelect) {
            targetSelect.val(`${listechoix.id}`);
        }
    });
});