const digits = 3;
const reducer = (acc, curr) => acc + parseFloat($(curr).val() || 0);

function calcTotal() {
    const total = $('.prix_ttc').toArray().reduce(reducer, 0.0);
    console.info('Total', total);
    $('#id_total').val(total.toFixed(digits));
    return total;
}

function onPrixChange(eve) {
    updatePrixFormat();
    $('.espece_payment').val(parseFloat(calcTotal()).toFixed(digits));
}

function onTotalChange(event) {
    const total_mutuelle = parseFloat($('.prix_ttc_mutuelle').val().replace(',','.'));
    console.log('teeeeettt', total_mutuelle);
    $('#id_total').val(parseFloat(total_mutuelle).toFixed(digits));
    $('.espece_payment').val(parseFloat(total_mutuelle).toFixed(digits));
}

function onPrestationListChange(eve) {
    const el = $(eve.target);
    let prestation_code = el.val();
    const prest = _.find(prestations, {code: prestation_code});
    if (prestation_code == null) return;
    let selected = el.find('option:selected');
    let prix = selected.data('prix');
    console.info('on change');
    console.log('onPrestationListChange code', prestation_code);
    console.log('onPrestationListChange prix', prix);
    let prixFormat = parseFloat(prix.replace(",", ".")).toFixed(digits);
    el.parent().children('.prix_initial').val(prixFormat);
    let prestation_nom = prest.prestation;
    if (prest_defaut != null && prest_defaut.code == prestation_code && $(".mutuelle_checked").val() == "oui") {
        prixFormat = prest_defaut.prix_pec;
        prestation_nom = prest_defaut.prestation;
    }
    el.parent().parent().find('.prix_ttc').val(prixFormat);
    el.parent().children('.code_prestation').val(prestation_code);
    el.parent().children('.prestation').val(prestation_nom);
    onPrixChange();
}

function updatePrixFormat() {
    $(".prix_ttc").each((idx, el) => {
        console.log('Val', $(el).val());
        $(el).val(parseFloat($(el).val()).toFixed(digits));
    });
}

jQuery(document).ready(function () {

    $(".mutuelle").change(function (event) {
        var checkbox = event.target;
        if (checkbox.checked) {
            $(".lines-formset").attr("style", "display:none");
            $(".mutuelle_bloc").attr("style", "");
            $(".mutuelle_checked").val("oui");

            onTotalChange();
        } else {
            $(".lines-formset").attr("style", "");
            $(".mutuelle_bloc").attr("style", "display:none");
            $(".mutuelle_checked").val("non");
            onPrixChange();

        }
    });
    // https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver
    const targetNode = $('.lines-formset')[0];//document.getElementById('id_formset');
    const config = {attributes: true, childList: true, subtree: true};
    const observer = new MutationObserver(function () {
        console.log('Dom changed');

        $('.prestation_list').off('change');
        $('.prestation_list').on("change", onPrestationListChange);
        $('.prix_ttc').off('change');
        $('.prix_ttc').on("change", onPrixChange);
        if ($(".mutuelle_checked").val() == "non") {
            onPrixChange();
        }


        if ($('.prix_ttc').length == 1) {
            $('.delete-row').css('visibility', 'hidden');
        } else {
            $('.delete-row').css('visibility', 'visible');
        }
    });
    setTimeout(() => observer.observe(targetNode, config), 3000);

    $('.prestation_list').on("change", onPrestationListChange);
    $('.prix_ttc').on("change", onPrixChange);

    if ($('.prix_ttc').length == 1) {
        $('.delete-row').css('visibility', 'hidden');
    } else {
        $('.delete-row').css('visibility', 'visible');
    }
    $(".delete-row").on("click", function (e) {
        console.log('oooffffffffffffff');
        const reducer = (acc, curr) => acc + parseFloat($(curr).val());
        res = $('.prix_ttc').toArray().reduce(reducer, 0);
        onPrixChange();
        $('#id_total').val(res);
    });


    $("#moyen_cheque").keyup(function () {
        if ($("#moyen_cheque").val() == "") {
            $("#div_cheque_number").attr("style", "display:none");
            $("#div_titulaire").attr("style", "display:none");
            $("#div_date_cheque").attr("style", "display:none");
        } else {
            $("#div_cheque_number").attr("style", "");
            $("#div_titulaire").attr("style", "");
            $("#div_date_cheque").attr("style", "");
        }
    });

    $('#btn_enregistrer').on('click', e => {
        if ($('.paiement').toArray().reduce(reducer, 0) != $('#id_total').val()) {
            $('#somme-erreur').addClass('d-block');
            e.preventDefault();
        }
        if ($('#moyen_cheque').val() != "" && ($('#num_cheque').val() == "" || $('#titulaire').val() == "" || $('#date_cheque').val() == "")) {
            $('#required_cheque').addClass('d-block');
            e.preventDefault();
        }
    });

    $('.lines-formset .row').formset({
        formTemplate: $('#ligne_reglement_template').html(),
        deleteText: '',
        addText: '<i class="la la-plus icon-sm"></i>Ajouter',
        addCssClass: 'add-row',
        deleteButtonClassname: 'delete-row',
        prefix: formset_prefix
    });

    $('.delete-row').click(e => {

    });

    function supprimerMyome(event, idx) {
        $(event.target).parents('.myome-item').addClass('d-none');
        $('form').append(`<input type="hidden" name="myome_set-${idx - 1}-DELETE" value="on">`);
        updateEditor();
    }

    $('#ligne_reglement_template input').each((i, el) => {
        let name = $(el).attr('name');
        let id = $(el).attr('id');
        console.log('name', name);
        console.log('new name', name.replace('form-__prefix__', ''));
        $(el).attr('name', name.replace('form-__prefix__', ''));
        $(el).attr('id', id.replace('form-__prefix__', ''));
    });

    /*if (prest_defaut != null && $(".mutuelle_checked").val() == "non") {
        console.log('Prestation par defaut', prest_defaut);
        $('.prestation_list').trigger('change');
    }*/
    $('.prestation_list').trigger('change');

});



