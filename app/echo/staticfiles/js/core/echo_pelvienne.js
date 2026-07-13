const colors = ['bg-blue-600', 'bg-green-600', 'bg-grey-700', 'bg-deep-purple-700', 'bg-deep-orange-700', 'bg-light-green-600'];

function dragMoveListener(event) {
    var target = event.target;
    // keep the dragged position in the data-x/data-y attributes
    var x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
    var y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

    // translate the element
    target.style.webkitTransform =
        target.style.transform =
            'translate(' + x + 'px, ' + y + 'px)';

    // update the posiion attributes
    target.setAttribute('data-x', x);
    target.setAttribute('data-y', y);
}

window.dragMoveListener = dragMoveListener;

function _updateEditor(champsValeurs) {
    let data = "";
    if (isFormNotEmpty('#uterus-container') || isFormNotEmpty('#adenomyose-modal')) {
        data += '<strong>Utérus</strong><br>';
    }
    data += printGroup('',
        ['position_uterus', 'lateralisation'],
        champsValeurs);

    if (isFormNotEmpty($('#uterus-dim'))) {
        data += `Dimensions :`;
        data += ` ${getTextField('longueur', champsValeurs, '', 'mm x ')}`;
        data += `${getTextField('largeur', champsValeurs, '', 'mm x ')}`;
        data += `${getTextField('hauteur', champsValeurs, '', 'mm')}`;
        data += `${getTextField('longueur_totale', champsValeurs, ', longueur totale : ', 'mm')}`;
        data += '<br>';
    }
    data += printGroup('',
        ['volume_uterin', 'volume_uterin_commentaire', 'asymetrie', 'paroi_anterieure',
            'paroi_posterieure', 'mobilite', 'structures', 'commentaires_myometre', 'cavite', 'malformation',
            'ligne_cavitaire', 'largeur_interostiale', 'hysterometrie'],
        champsValeurs);
    data += printSelectField('adenomyose', 'Adénomyose', champsValeurs, false);
    data += printSelectField('adenomyose_conclusion', 'Conclusion', champsValeurs, false);

    $('#myome-list .myome-item:not(.d-none)').each((idx, el) => {
        const $el = $(el);
        const prepend = `myome_set-${idx}-`;
        data += printGroup(`Myome ${idx+1}`,
            ['situation', 'type_figo', 'situation_coupe_longitudinale', 'situation_coupe_transversale',
                'contours', 'structure', 'calcifications', 'vascularisation'],
            champsValeurs, false, prepend);
        if (isFormNotEmpty($el.find('.dimensions'))) {
            data += `Dimensions :`;
            data += ` ${getTextField(prepend+'longueur', champsValeurs, '', 'mm x ')}`;
            data += `${getTextField(prepend+'largeur', champsValeurs, '', 'mm x ')}`;
            data += `${getTextField(prepend+'hauteur', champsValeurs, '', 'mm')}`;
            data += `${getTextField(prepend+'diametre_moyen', champsValeurs, ', Diamètre moyen : ', 'mm')}`;
            data += `${getTextField(prepend+'volume', champsValeurs, ', Volume : ', 'cm3')}`;
            data += '<br>';
        }
    });

    data += printGroup('Endomètre',
        ['endometre_visualisation', 'endometre_echogenicite', 'endometre_epaisseur'],
        champsValeurs);

    data += printGroup('Col',
        ['col_longueur', 'col_aspect', 'col_vascularisation', 'commentaire_col_endometre'],
        champsValeurs);

    data += printGroup('Dispositif intra-utérin',
        ['type_dispositif_intra_uterin', 'localisation_dispositif_intra_uterin', 'anomalies_dispositif_intra_uterin'],
        champsValeurs);
    data += printGroup('Dispositif intra-tubaire',
        ['dispositif_intra_tubaire'],
        champsValeurs);

    data += printGroup('Ovaire gauche',
        ['ovaire_gauche_visibilite', 'ovaire_gauche_aspect'],
        champsValeurs);
    if (isFormNotEmpty($('#ovaire-gauche-dim'))) {
        data += `Dimensions :`;
        data += ` ${getTextField('ovaire_gauche_longueur', champsValeurs, '', ' x ')}`;
        data += `${getTextField('ovaire_gauche_largeur', champsValeurs, '', ' x ')}`;
        data += `${getTextField('ovaire_gauche_hauteur', champsValeurs, '', '')}`;
        data += '<br>';
    }
    data += printGroup('',
        ['ovaire_gauche_volume', 'ovaire_gauche_accessibilite', 'ovaire_gauche_follicules', 'ovaire_gauche_commentaire'],
        champsValeurs);

    data += printGroup('Ovaire droit',
        ['ovaire_droit_visibilite', 'ovaire_droit_aspect'],
        champsValeurs);
    if (isFormNotEmpty($('#ovaire-droit-dim'))) {
        data += `Dimensions :`;
        data += ` ${getTextField('ovaire_droit_longueur', champsValeurs, '', ' x ')}`;
        data += `${getTextField('ovaire_droit_largeur', champsValeurs, '', ' x ')}`;
        data += `${getTextField('ovaire_droit_hauteur', champsValeurs, '', '')}`;
        data += '<br>';
    }
    data += printGroup('',
        ['ovaire_droit_volume', 'ovaire_droit_accessibilite', 'ovaire_droit_follicules', 'ovaire_droit_commentaire'],
        champsValeurs);

    data += printGroup('Cul de sac latéro',
        ['cul_de_sac_latero'],
        champsValeurs);
    return data;
}

function ajouterMyome() {
    let form_idx = parseInt($('#id_myome_set-TOTAL_FORMS').val());
    $('#myome-list').append($('#myome-template').html()
        .replace(/__prefix__/g, form_idx).replace(/__title__/g, form_idx + 1));
    $('#id_myome_set-TOTAL_FORMS').val(parseInt(form_idx) + 1);
}

function supprimerMyome(event, idx) {
    $(event.target).parents('.myome-item').addClass('d-none');
    $('form').append(`<input type="hidden" name="myome_set-${idx - 1}-DELETE" value="on">`);
    updateEditor();
}

function afficherSchemaMyomes() {
    window.scrollTo(0,0);
    $("#myomes-schema-modal").modal();
}

$(document).ready(() => {
    $('#dispositif-intra-uterin').click((e) => {
        $('#dispositif-intra-uterin-champs').toggleClass('d-none');
    });

    $('.type-figo').each((i, el) => {
        _.each(types_figo, type => {
            $(el).append(new Option(type.valeur, type.valeur));
        });
    });

    $('.myome-input').change(e => {
        const id = $(e.target).attr('data-id');
        let cercles = $(`.cercle[data-id="${id}"]`);
        if ($(e.target).val() == '' && cercles.length > 0) {
            // Supprimer les cercles
            cercles.remove();
        }
        if (cercles.length > 0) return;
        const html = `<div class="cercle draggable ${colors[id]}" data-id="${id}">${id}</div>`;
        $('#schema-myome-container').append(html);
        $('#schema-myome-container').append(html);
        $('#schema-myome-container').append(html);
        creerCercle();
    });

    $('.img-cb').click(onImageCbClick);


    const follicTpl = _.template($('#follicule-template').html());
    for (let i = 1; i <= 6; i++) {
        let html = follicTpl({num: i, lat: 'g'});
        $('#ovaire-gauche-follicules-mesures').append(html);
        html = follicTpl({num: i, lat: 'd'});
        $('#ovaire-droit-follicules-mesures').append(html);
    }

    let lst = $('#id_ovaire_gauche_follicules_list').val();
    if (lst != "") {
        let items = JSON.parse(lst);
        for (let i = 0; i < items.length; i++) {
            let root = $(`#fol-g-${i+1}`);
            root.find('.diam').val(items[i].diametre);
            root.find('.long').val(items[i].longueur);
            root.find('.larg').val(items[i].largeur);
            root.find('.haut').val(items[i].hauteur);
        }
    }
    lst = $('#id_ovaire_droit_follicules_list').val();
    if (lst != "") {
        let items = JSON.parse(lst);
        for (let i = 0; i < items.length; i++) {
            let root = $(`#fol-d-${i+1}`);
            root.find('.diam').val(items[i].diametre);
            root.find('.long').val(items[i].longueur);
            root.find('.larg').val(items[i].largeur);
            root.find('.haut').val(items[i].hauteur);
        }
    }
});