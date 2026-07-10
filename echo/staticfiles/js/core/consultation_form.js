let pdfDoc;

let saveUrl = () => `/patients/${patient_pk}/consultation/enregistrer/`;

let templateConsultation = _.template(unescapeTemplate($('#consultation-template').html()));
if (!ajouterDateLieuEdition) {
    templateConsultation = _.template(unescapeTemplate($('#consultation-template-no-date').html()));
}
const templateAntecedents = _.template(unescapeTemplate($('#antecedents-template').html()));
const templateNotes = _.template(unescapeTemplate($('#notes-template').html()));
const templateGrossesse = _.template(unescapeTemplate($('#grossesse-info-template').html()));
const templatePmaInterro = _.template(unescapeTemplate($('#pma-interro-template').html()));

let targetSelect = null;

let touched = false;

let imgItemTpl = '';

let addNotes = false;

let addGrossesseInfo = false;

function getDateConsultation() {
    return isConsultationEnregistree() ? consultation_date : moment().format('DD/MM/YYYY');
}


function enregistrerConsultation(editor = tinymce.activeEditor, champsSupplementaires = {}) {
    console.log('enregistrerConsultation');

    $('#libelle_statut')
        .toggleClass('label-success', false)
        .text('Brouillon')
        .show();

    let baseData = {
        'consultation_pk': consultation_pk,
        'text': editor.getContent(),
        'motif': motif_pk,
        'patient': patient_pk,
        'praticien': $('#id_praticien').val()
    };

    let data = $.param(baseData) + '&' + $('#form_1').serialize();

    if (!_.isEmpty(champsSupplementaires)) {
        data += '&' + $.param(champsSupplementaires);
    }

    //console.info('Post data', data);
    $.post(saveUrl(), data)
        .done(function (result) {
            consultation_pk = result.consultation_pk;
            consultation_date = moment(result.date).format('DD/MM/YYYY');
            if (result.foetus_pk) {
                let ids = result.foetus_pk.split(',');
                $('#id_donneesfoetus_set-INITIAL_FORMS').val(ids.length);
                for (let i = 0; i < 3 && i < ids.length; i++) {
                    const sel = `id_donneesfoetus_set-${i}-id`;
                    //console.log(`#id_donneesfoetus_set-${i}-id`, ids[i]);
                    if ($(`#${sel}`).length == 0)
                        $('.foetus').get(i).after(`<input type="hidden" name="${sel}" value="${ids[i]}" id="${sel}">`);
                    else
                        $(`#${sel}`).val(ids[i]);
                }
            }
            console.log('Succes', result);
            $('#libelle_statut')
                .toggleClass('label-success', true)
                .text('Enregistré')
                .show();
            $('#btn_terminer').removeClass('d-none');
            $('#btn_terminer').attr('href', `/consultation/${consultation_pk}/cloturer/`);
            $('.enregistrer').addClass('d-none');

            EventManager.publish("consultation:updated", {consultation: result});
        })
        .fail(function () {
            console.error('Impossible de sauvegarder');
        })
        .always(function () {

        });
}

function isConsultationEnregistree() {
    return consultation_pk != -1;
}

function getSelectField(champ, champsValeurs) {
    let ret = champsValeurs[champ];
    if (ret != 'unknown' && ret != '---------')
        return ret;
    else
        return '';
}

function getTextField(champ, champsValeurs, prepend = '', append = '') {
    let ret = champsValeurs[champ];
    console.info('getTextField', champ, ret);
    if (ret != '')
        return prepend + ret + append;
    else
        return '';
}

function printTextField(champ, label, champsValeurs, strong = true) {
    if (_.isUndefined(champsValeurs[champ]))
        return '';
    let val = champsValeurs[champ];
    if (val != '') {
        return strong ? `<strong>${label} : </strong>${val}<br>` : `${label} : ${val}<br>`;
    }
    return '';
}

function printSelectField(champ, label, champsValeurs, strong = true) {
    if (_.isUndefined(champsValeurs[champ]))
        return '';
    let val = getSelectField(champ, champsValeurs);
    if (val != '') {
        return strong ? `<strong>${label} : </strong>${val}<br>` : `${label} : ${val}<br>`;
    }
    return '';
}

function printGroup(groupe, champs, champsValeurs, inline = false, prependFields = '') {
    let out = _.map(champs, champ => {
        if (_.isUndefined(champsValeurs[prependFields + champ]))
            return '';
        const v = champsValeurs[prependFields + champ];
        let firstChild = $('#id_' + prependFields + champ).parent().children().first();
        let label = '';
        if (firstChild.hasClass('input-group-text'))
            label = firstChild.text();
        if (label === '')
            label = $('#id_' + prependFields + champ).siblings('.form-label').text();
        if (label === '')
            label = $('#id_' + prependFields + champ).parent().siblings('.form-label').text();
        return (v != '' && v != '---------' && v != 'unknown' ? `${label} : ${v}.` : '');
    });
    const separator = inline ? ' ' : '<br>';
    if (out.join('') != '') {
        let ret = '';
        if (groupe) ret += `<strong>${groupe}</strong><br>`;
        ret += _.reduce(out, function (sum, n) {
            return sum + (n != '' ? n + separator : '');
        }, '');
        if (inline) ret += '<br>';
        return ret;
    } else {
        return '';
    }
}

function getValeursForm() {
    let formData = $('#form_1').serializeArray();
    let mapped = _.mapValues(formData, c => {
        let $el = $('#id_' + c.name);
        let val = c.value;
        if ($el.prop("tagName") == 'SELECT' && c.value != '' && c.value != 'unknown') {
            let $opt = $el.find(":selected");
            val = $opt.text();
            if (listes_choix) {
                let choix = _.find(listes_choix, {id: parseInt($opt.val())});
                if (choix) {
                    val = choix.valeur;
                } else {

                }
            }
        }
        if ($(`[name="${c.name}"]`).attr("type") == 'checkbox' && c.value != '' && c.value != 'unknown') {
            val = $(`[name="${c.name}"][value="${c.value}"]`).next('label').text().trim();
        }
        if (c.value == 'unknown')
            val = ''
        const unit = $el.attr('data-unit');
        if (val != '' && typeof unit !== typeof undefined && unit !== false) {
            val += ' ' + unit;
        }
        return {name: c.name, value: val};
    });

    let champsValeurs = _.chain(mapped)
        .groupBy('name')
        .mapValues(o => {
            if (o.length == 1) return o[0].value;
            else return _.map(o, 'value').join(', ');
        })
        .value();

    console.log('Champs valeurs', champsValeurs);

    return champsValeurs;
}

function groupFields(group, pre) {
    return _.map(_.filter(_.map($(`.${group} .form-control, .${group} .form-select`).serializeArray(), 'name'), v => v.includes(pre)), v => v.split(pre)[1]);
}

function groupFieldsValues(group, pre, vals) {
    let raw = _.filter(_.map($(`.${group} .form-control`).serializeArray(), 'name'), v => v.includes(pre));
    let res = {};
    for (let i = 0; i < raw.length; i++) {
        res[raw[i].split(pre)[1]] = vals[raw[i]];
    }
    return res;
}

function isNotEmptyGroup(group, pre, vals) {
    let fields = groupFieldsValues(group, pre, vals);
    return _.some(_.values(fields), i => i != '');
}

function afficherEdition() {
    bootstrap.Modal.getOrCreateInstance('#edition-modal').show();
}

function imprimerClick() {
    //getConsultationImagesB64();
    enregistrerConsultation(tinymce.activeEditor);
    createPdf().then(pdfDoc => {
        pdfDoc.open();
        //let f = document.getElementById('pdf-frame');
        //pdfDoc.getDataUrl(url => f.setAttribute('src', url));
        //$('#pdf-modal').modal();
    });
}

function modifierGrossesse() {
    $('#grossesse-modal iframe').attr('src', `/grossesse/${grossesse.id}/modifier`);
    bootstrap.Modal.getOrCreateInstance('#grossesse-modal').show();
}

function priseRdv() {
    enregistrerConsultation();
    showFrameLoading();
    const debut = $('#id_rdv_suivant_apres').val() || moment().add(1, 'days').format('YYYY-MM-DD');
    const fin = $('#id_rdv_suivant_avant').val() || moment().add(9, 'days').format('YYYY-MM-DD');
    $('#dispo-rdv-modal iframe').attr('src', `/rdvs/dispo/ajouter/?patient=${patient_pk}&debut=${debut}&fin=${fin}`);
    bootstrap.Modal.getOrCreateInstance('#dispo-rdv-modal').show();
}

let consultationImagesB64 = {};

function getConsultationImagesB64() {
    console.info('Consultation images', consultationImages);
    const imagesToPrint = _.filter(consultationImages, i => i.impression == true);
    console.log('Images à imprimer = ', imagesToPrint.length);
    const promises = _.map(imagesToPrint, img =>
        new Promise((resolve, reject) => {
                if (!_.has(consultationImagesB64, img.id)) {
                    console.info('Loading image', img.image);
                    chargerImageB64(img.image, (b64) => {
                        consultationImagesB64[img.id] = b64;
                        resolve();
                    });
                } else {
                    resolve();
                }
            }
        ));
    return Promise.all(promises);
}

function getEditorSelector() {
    return $(".tox-edit-area__iframe").contents().find("body");
}

function replaceEditorFormFields() {
    let editorContent = tinymce.activeEditor.getContent();

    let $contentBody = getEditorSelector();
    $contentBody.find('select').each((idx, el) => {
        let id = $(el).attr('id');
        const rx = new RegExp(`<select id="${id}"(.+?)select>`, 'gis');
        editorContent = editorContent.replace(rx, $(el).val())
    });
    $contentBody.find('input').each((idx, el) => {
        let id = $(el).attr('id');
        const rx = new RegExp(`<input id="${id}"(.+?)>`, 'gis');
        //let select =  editorContent.match(rx);
        editorContent = editorContent.replace(rx, $(el).val())
    });

    return editorContent;
}

function traverseTree(node, parent) {
    if (node) {
        if (node['stack']) {
            for (let i = 0; i < node['stack'].length; i++) {
                traverseTree(node['stack'][i]);
            }
            return;
        } else {
            console.log('Node text', node['text']);
            if (node['text'] == " " && parent)
                parent.pop(node);
        }
    }
}

function createPdf() {

    return new Promise((resolve, reject) => {
        getConsultationImagesB64().then(() => {
            const templateSignature = _.template(unescapeTemplate($('#template-signature').html()));
            const templateAntecedents = _.template(unescapeTemplate($('#antecedents-template').html()));
            const templateImages = _.template($('#image-grid-4-template').html());

            const praticien = _.find(medecins, p => p.id == $('#id_praticien').val());
            const signatureData = {signature_titre: praticien.nom, signature_img: signatureB64};

            let content = [];
            let editorContent = replaceEditorFormFields();
            //editorContent = editorContent.replaceAll('<p', '<p style="margin:0"');
            console.log('---------------------------------');
            console.log(editorContent);

            $('#consultation-print').html(editorContent);
            $('#consultation-print #antecedents-container br').attr("data-pdfmake", `{"lineHeight":"0"}`);
            $('#consultation-print #antecedents-container').replaceWith(function(){
                return $("<p />", {html: $(this).html()});
            });
            $('#consultation-print #allergies-container br').attr("data-pdfmake", `{"lineHeight":"0"}`);
            $('#consultation-print #allergies-container').replaceWith(function(){
                return $("<p />", {html: $(this).html()});
            });

            editorContent = $('#consultation-print').html();
            //editorContent = editorContent.replaceAll('<div', '<p').replaceAll('</div>', '</p>');
                /*<div id="antecedents-container">
                .replaceAll('<p style="margin: 0;">', '')
                //.replaceAll('<span style="color: #3f4254;">', '')
                //.replaceAll('</span>', '')
                .replaceAll('</p>', '<br>');
                */

            console.log('---------------------------------');
            console.log(editorContent);

            let makeDoc = [];
            cleanPDF(htmlToPdfmake(editorContent, defaultHtml2PDFOptions), makeDoc);
            console.log(makeDoc[0]);
            content.push(makeDoc[0]);

            if (addAntecedents) {
                //content.push(htmlToPdfmake(templateAntecedents()));
            }
            content.push(htmlToPdfmake(templateSignature(signatureData)));
            const images = _.values(consultationImagesB64);
            const rows = images.length % 3 > 0 ? Math.floor(images.length / 3) + 1 : Math.floor(images.length / 3);
            if (rows) content.push({ text: '_', pageBreak: 'after'});
            for (let row = 0; row < rows; row++) {
                let cols = [];
                for (let col = 0; col < 3 && row * 3 + col < images.length; col++) {
                    cols.push({width: 170, image:images[row*3+col]});
                }
                content.push({columns: cols});
            }

            const docDefinition = {
                pageMargins: defaultMargins(),
                header: defaultHeader,
                footer: defaultFooter,
                content: content,
                defaultStyles: { // change the default styles
                    "br": {
                        "line-height": 0,
                    }
                },
                pageBreakBefore: function (currentNode) {
                    return currentNode.style && currentNode.style.indexOf('pdf-pagebreak-before') > -1;
                }
            };

            pdfDoc = pdfMake.createPdf(docDefinition);
            resolve(pdfDoc);
        });
    });
}

function updateEditor() {
    // Fonction à redéfinir pour chaque consultation
    // Elle est appelée pour mettre à jour l'éditeur avec les valeurs des
    // champs du formulaire
}

function insererTemplateEdition($select) {
    const edt = tinymce.activeEditor;
    let content = templateConsultation({data: "", date: getDateConsultation()});
    const tempId = $select.val();
    const temp = _.find(templates_edition, t => t.id == tempId);
    if (temp) content += temp.contenu;
    edt.setContent(content);
    $select.val('-1');
}

function updateSR(data) {
    if (!data || typeof data !== 'object') return;
    // Uterus
    $(`#id_longueur`).val(data['uterus_longueur']);
    $(`#id_largeur`).val(data['uterus_largeur']);
    $(`#id_hauteur`).val(data['uterus_hauteur']);
    $(`#id_volume_uterin`).val(data['uterus_volume']);
    $(`#id_endometre_epaisseur`).val(data['endometre_epaisseur']);
    $(`#id_col_longueur`).val(data['col_longueur']);
    $(`#id_col_long`).val(data['col_longueur']);

    $(`#id_ovaire_gauche_longueur`).val(data['ovaire_gauche_longueur']);
    $(`#id_ovaire_gauche_largeur`).val(data['ovaire_gauche_largeur']);
    $(`#id_ovaire_gauche_hauteur`).val(data['ovaire_gauche_hauteur']);
    $(`#id_ovaire_gauche_volume`).val(data['ovaire_gauche_volume']);

    $(`#id_ovaire_droit_longueur`).val(data['ovaire_droit_longueur']);
    $(`#id_ovaire_droit_largeur`).val(data['ovaire_droit_largeur']);
    $(`#id_ovaire_droit_hauteur`).val(data['ovaire_droit_hauteur']);
    $(`#id_ovaire_droit_volume`).val(data['ovaire_droit_volume']);

    if (data['ovaire_gauche_fol']) {
        _.each(data['ovaire_gauche_fol'], (fol, key) => {
            let i = parseInt(key);
            $(`#fol-g-${i+1}`).find('.long').val(fol['diam'][0]);
            $(`#fol-g-${i+1}`).find('.larg').val(fol['diam'][1]);
            $(`#fol-g-${i+1}`).find('.haut').val(fol['diam'][2]);
            const moyenne = (fol['diam'][0] + fol['diam'][1] + fol['diam'][2]) / 3
            $(`#fol-g-${i+1}`).find('.diam').val(moyenne);
        });
    }
    if (data['ovaire_droit_fol']) {
        _.each(data['ovaire_droit_fol'], (fol, key) => {
            let i = parseInt(key);
            $(`#fol-d-${i+1}`).find('.long').val(fol['diam'][0]);
            $(`#fol-d-${i+1}`).find('.larg').val(fol['diam'][1]);
            $(`#fol-d-${i+1}`).find('.haut').val(fol['diam'][2]);
            const moyenne = (fol['diam'][0] + fol['diam'][1] + fol['diam'][2]) / 3
            $(`#fol-d-${i+1}`).find('.diam').val(moyenne);
        });
    }

    // Foetus
    /*$(`#id_bip`).val(data['bip']);
    $(`#id_lcc`).val(data['lcc']);
    $(`#id_sac_gestationnel_diametre`).val(data['sac_gestationnel_diametre']);
    $(`#id_donneesfoetus_set-0-bip`).val(data['bip']);
    $(`#id_donneesfoetus_set-0-pc`).val(data['pc']);
    $(`#id_donneesfoetus_set-0-pa`).val(data['pa']);*/
    console.log(data);

    if (data['doppler_uterin']) {
        let dop_ut = data['doppler_uterin'];
        console.log('Doppler uterin', dop_ut);
        _.each(dop_ut, (v, k) => $(`#id_${k}`).val(v));
    }

    foetus = data['foetus']
    if (!_.isNil(foetus)) {
        for (let i = 0; i < foetus.length; i++) {
            f = foetus[i];
            console.log(f);
            const id = parseInt(f.id) - 1;
            let selector = '#id_donneesfoetus_set-' + id + '-';
            console.log(selector);

            if (f.poids) {
                $(selector + 'poids').val(f.poids);
            }
            let bio = f.biometrie;
            console.log('Biométrie', bio);
            _.each(bio, (v, k) => $(selector + k).val(v));

            let os = f.os;
            console.log('Os', os);
            _.each(os, (v, k) => $(selector + k).val(v));

            let crane = f.crane;
            console.log('Crane', crane);
            _.each(crane, (v, k) => $(selector + k).val(v));

            let dop = f.doppler_ombilical;
            if (dop) {
                console.log('Doppler ombilical', dop);
                _.each(dop, (v, k) => $(selector + k).val(v));
            }

            let dop_acm = f.doppler_acm;
            if (dop_acm) {
                console.log('Doppler acm', dop_acm);
                _.each(dop_acm, (v, k) => $(selector + k).val(v));
            }

            let dop_dv = f.doppler_dv;
            if (dop_dv) {
                console.log('Doppler dv', dop_dv);
                _.each(dop_dv, (v, k) => $(selector + k).val(v));
            }

            // < 11SA
            $(`#id_bip`).val(bio['bip']);
            $(`#id_lcc`).val(bio['lcc']);
            $(`#id_sac_gestationnel_diametre`).val(bio['sac_gestationnel_diametre']);
        }
    }

    updateEditor();
}

var MESURES_MESSAGES = {
    fr: "Nouvelles mesures reçue de l'échographe",
    en: "New measurements received from the ultrasound machine",
    ar: "تم استلام قياسات جديدة من جهاز الإيكوغراف",
    es: "Nuevas mediciones recibidas del ecógrafo"
};

function getMesuresMessage() {
    var lang = document.documentElement.lang || 'fr';
    return MESURES_MESSAGES[lang] || MESURES_MESSAGES.fr;
}

function checkReceptionDonnees() {
    if(!isConsultationEnregistree()) return;
    console.log('Check reception mise à jour donnees');
    // Récupérer les nouvelles images et les mesures

    $.get(`/consultations/${consultation_pk}/images/`)
        .done(function (result) {
            try {
                let images = JSON.parse(result.images);
                console.info('Received images', images);
                _.each(images, img => {
                    if (_.findIndex(consultationImages, {id: img.id}) == -1) {
                        $('#images-container').append(imgItemTpl({img}));
                        $(`[name=img-cb-${img.id}]`).click(onImageCbClick);
                        consultationImages.push(img);
                    }
                });
                filterImagesByDevice();
            } catch (e) {
                console.error('Error processing images', e);
            }
        })
        .fail(function () {
            console.error("Impossible de charger les images");
        });

    $.get(`/consultations/${consultation_pk}/sr/`)
        .done(function (result) {
            try {
                let data = result.data;
                // data may be a JSON string or already an object depending on backend
                if (typeof data === 'string') {
                    data = JSON.parse(data);
                }
                // Treat null and {} as equivalent empty states
                let prev = (consultationSR && typeof consultationSR === 'object' && !_.isEmpty(consultationSR)) ? consultationSR : null;
                let cur = (data && typeof data === 'object' && !_.isEmpty(data)) ? data : null;
                if (prev === null && cur === null) {
                    console.log('No new data received');
                } else if (typeof consultationSR === 'undefined') {
                    consultationSR = data;
                    updateSR(data);
                } else if (!_.isEqual(consultationSR, data)) {
                    toastr.success(getMesuresMessage());
                    consultationSR = data;
                    updateSR(data);
                }
            } catch (e) {
                console.error('Error processing SR data', e);
            }
        })
        .fail(function () {
            console.error("Impossible de charger les sr");
        });
}

function onImageCbClick(e) {
    const id = $(e.target).attr('data-id');
    const data = {
        impression: e.target.checked
    };
    $.post(`/images/${id}/modifier/`, data)
        .done(function (result) {
            console.info("Image modifiée");
        })
        .fail(function () {
            console.error("Impossible de modifier l'image");
        });

    const idx = _.findIndex(consultationImages, i => i.id == id);
    if (idx > -1) {
        console.log('Images is checked', e.target.checked);
        consultationImages[idx].impression = e.target.checked;
    }

    if (!_.has(consultationImagesB64, id)) {
        if (e.target.checked)
            getConsultationImagesB64().then(() => console.log('Images B64 mis à jour', consultationImagesB64));
    } else {
        if (!e.target.checked) {
            delete consultationImagesB64[id];
        }
    }
}

function supprimerImage(eve, id) {
    eve.preventDefault();
    $.post(`/images/${id}/supprimer/`, {})
        .done(function (result) {
            $(`[data-image-id=${id}]`).remove();
            if (_.has(consultationImagesB64, id)) {
                delete consultationImagesB64[id];
            }
            _.remove(consultationImages, i => i.id == result.pk);
        })
        .fail(function () {
            console.error("Impossible de supprimer l'image");
            toastr.error("Une erreur s'est produite");
        });
}

function filterImagesByDevice() {
    const deviceId = $('#materiel').val();
    $('#images-container > div[data-image-id]').each(function () {
        const imgDevice = $(this).attr('data-device') || '';
        if (deviceId === '-1' || imgDevice === deviceId || imgDevice === '') {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
}

function toggleGrossesseInfo(afficher) {
    const edt = tinymce.activeEditor;
    let grossesse = templateGrossesse();
    edt.dom.remove('grossesse-container');
    let $edt = $(edt.getBody());
    $edt.find('#grossesse').empty();
    if (afficher) {
        edt.dom.add('grossesse', 'div', '', grossesse);
        fixEditorHtml('#grossesse-container', $edt);
    }
    addGrossesseInfo = afficher;
}

function toggleAntecedents(afficher) {
    const edt = tinymce.activeEditor;
    let antecedents = templateAntecedents();
    edt.dom.remove('antecedents-container');
    console.log('Antecedents', antecedents);
    if (afficher) {
        edt.dom.add('antecedents', 'div', '', antecedents);
        let $edt = $(edt.getBody());
        fixEditorHtml('#antecedents-container', $edt);
        //$edt.find('#antecedents-container').empty();
    }
    addAntecedents = afficher;
}

function toggleNotes(afficher) {
    const edt = tinymce.activeEditor;
    let notes = templateNotes();
    edt.dom.remove('notes-container');
    if (afficher) {
        edt.dom.add('notes', 'p', '', notes);
        let $edt = $(edt.getBody());
        fixEditorHtml('#notes-container', $edt);
    }
    addNotes = afficher;
}

function createEditor(selector, changeCb) {
    return tinymce.init({
        selector: selector,
        language: 'fr_FR',
        plugins: ['link', 'lists', 'autolink', 'paste', 'table'],
        paste_as_text: true,
        contextmenu: 'image table',
        toolbar: [
            'undo redo | bold italic underline | fontsizeselect | forecolor backcolor | alignleft aligncenter alignright alignfull | numlist bullist outdent indent | table'
        ],
        statusbar: false,
        menubar: false,
        inline: false,
        forced_root_block: false,
        //content_style: "body { font-size: 10pt }",
        init_instance_callback: function (editor) {
            $('.tox-tinymce').height(window.innerHeight - 240);

            editor.on('Change', function (e) {
                changeCb();
            });

            editor.on('keyup', function (e) {
                $('#libelle_statut')
                    .toggleClass('label-success', false)
                    .text('Brouillon')
                    .show();
            });

            editor.on('SetContent', function (e) {
                toggleGrossesseInfo(addGrossesseInfo);
                toggleAntecedents(addAntecedents);
                toggleNotes(addNotes);
            });

            if (modeEdition) {
                createPdf().then(pdfDoc => {
                    pdfDoc.print();
                    parent.fermerModals();
                });
            }
        }
    });
}

function editionClick() {
    afficherEdition();
}

function demarrerImpression() {
    createPdf().then(pdfDoc => {
        pdfDoc.print();
    });
}

function afficherImpressionImages() {
    const container = $('#print-images-container');
    const empty = $('#print-images-empty');
    container.empty();

    const activeImages = consultationImages || [];

    if (activeImages.length === 0) {
        empty.show();
        container.hide();
    } else {
        empty.hide();
        container.show();
        _.each(activeImages, img => {
            const imgUrl = img.url || img.image;
            container.append(
                `<div class="col-4 mb-3">
                    <div class="card card-custom gutter-b bg-white border h-100">
                        <div class="card-body p-2 text-center d-flex flex-column align-items-center justify-content-center">
                            <label class="d-block cursor-pointer w-100">
                                <input type="checkbox" class="img-cb-print mb-2" data-id="${img.id}" ${img.impression ? 'checked' : ''}>
                                <br>
                                <img src="${imgUrl}" class="img-fluid" style="max-height:120px;object-fit:contain">
                            </label>
                        </div>
                    </div>
                </div>`
            );
        });
    }

    bootstrap.Modal.getOrCreateInstance('#modal-impression-images').show();
}

function selectionnerToutesImages(select) {
    $('#modal-impression-images .img-cb-print').prop('checked', select);
}

function imprimerImagesSelectionnees() {
    const selectedIds = [];
    $('#modal-impression-images .img-cb-print:checked').each(function () {
        selectedIds.push($(this).attr('data-id'));
    });

    if (selectedIds.length === 0) {
        toastr.warning(typeof S_PRINT !== 'undefined' ? S_PRINT.select_one : "Veuillez sélectionner au moins une image");
        return;
    }

    bootstrap.Modal.getOrCreateInstance('#modal-impression-images').hide();

    const allImages = consultationImages || [];
    const imagesToPrint = _.filter(allImages, i => selectedIds.indexOf(String(i.id)) > -1);

    const promises = _.map(imagesToPrint, img =>
        new Promise((resolve) => {
            chargerImageB64(img.url || img.image, (b64) => resolve(b64));
        })
    );

    Promise.all(promises).then(imagesB64 => {
        const IMAGES_PER_PAGE = 6;
        let content = [];
        if (imagesB64.length) content.push({ text: 'Images', style: 'header', margin: [0, 0, 0, 10] });
        for (let i = 0; i < imagesB64.length; i += IMAGES_PER_PAGE) {
            const pageImages = imagesB64.slice(i, i + IMAGES_PER_PAGE);
            const rows = Math.ceil(pageImages.length / 3);
            for (let row = 0; row < rows; row++) {
                let cols = [];
                for (let col = 0; col < 3 && row * 3 + col < pageImages.length; col++) {
                    cols.push({ width: 170, image: pageImages[row * 3 + col] });
                }
                if (cols.length) content.push({ columns: cols, margin: [0, 0, 0, 10] });
            }
            if (i + IMAGES_PER_PAGE < imagesB64.length) {
                content.push({ text: '', pageBreak: 'after' });
            }
        }

        const docDefinition = {
            pageMargins: [20, 20, 20, 20],
            content: content,
            styles: { header: { fontSize: 16, bold: true } }
        };

        pdfMake.createPdf(docDefinition).print();
    });
}

function imprimerGraphique() {
    const gl = (typeof S_PRINT !== 'undefined' && S_PRINT.graph_labels) || {};
    const graphConfig = [
        { id: 'graph-poids', label: gl['graph-poids'] || 'Poids foetal' },
        { id: 'graph-bip', label: gl['graph-bip'] || 'Diamètre bipariétal' },
        { id: 'graph-pc', label: gl['graph-pc'] || 'Périmètre céphalique' },
        { id: 'graph-pa', label: gl['graph-pa'] || 'Périmètre abdominal' },
        { id: 'graph-femur', label: gl['graph-femur'] || 'Longueur du fémur' },
    ];

    const $tabGraphs = $('#tab-graphs');
    const wasHidden = $tabGraphs.is(':hidden');
    if (wasHidden) {
        $tabGraphs.css({ display: 'block', visibility: 'hidden', position: 'absolute' });
    }

    const populateAndShow = () => {
        const $container = $('#print-graphs-container').empty();
        const $empty = $('#print-graphs-empty');
        let hasGraph = false;

        _.each(graphConfig, cfg => {
            const canvas = $(`#${cfg.id} canvas`)[0];
            if (canvas && canvas.width > 0 && canvas.height > 0) {
                hasGraph = true;
                const b64 = canvas.toDataURL('image/png');
                $container.append(`
                    <div class="col-6 mb-4">
                        <div class="card card-custom gutter-b bg-white border h-100">
                            <div class="card-body p-3 text-center">
                                <h6 class="fw-bold mb-3">${cfg.label}</h6>
                                <img src="${b64}" class="img-fluid" style="max-height:350px;object-fit:contain">
                            </div>
                        </div>
                    </div>
                `);
            }
        });

        if (wasHidden) {
            $tabGraphs.css({ display: '', visibility: '', position: '' });
        }

        if (hasGraph) {
            $empty.hide();
            $container.show();
        } else {
            $empty.show();
            $container.hide();
        }
        bootstrap.Modal.getOrCreateInstance('#modal-impression-graphs').show();
    };

    const waitForFlotResize = (callback, retries = 30) => {
        const firstCanvas = $(`#${graphConfig[0].id} canvas`)[0];
        if (firstCanvas && firstCanvas.width > 100) {
            callback();
        } else if (retries > 0) {
            requestAnimationFrame(() => waitForFlotResize(callback, retries - 1));
        } else {
            callback();
        }
    };

    if (wasHidden) {
        requestAnimationFrame(() => waitForFlotResize(populateAndShow));
    } else {
        waitForFlotResize(populateAndShow);
    }
}

function imprimerGraphiquesSelectionnes() {
    const $container = $('#print-graphs-container');
    const gl = (typeof S_PRINT !== 'undefined' && S_PRINT.graph_labels) || {};
    const labels = {
        'graph-poids': gl['graph-poids'] || 'Poids foetal',
        'graph-bip': gl['graph-bip'] || 'Diamètre bipariétal',
        'graph-pc': gl['graph-pc'] || 'Périmètre céphalique',
        'graph-pa': gl['graph-pa'] || 'Périmètre abdominal',
        'graph-femur': gl['graph-femur'] || 'Longueur du fémur',
    };
    let content = [];
    $container.find('img').each(function () {
        const $parent = $(this).closest('.col-6');
        const label = $parent.find('h6').text();
        const b64 = $(this).attr('src');
        if (b64 && b64.length > 100) {
            content.push({ text: label, style: 'header', margin: [0, 10, 0, 5] });
            content.push({ image: b64, width: 500, alignment: 'center', margin: [0, 0, 0, 10] });
        }
    });

    if (content.length === 0) {
        toastr.warning(typeof S_PRINT !== 'undefined' ? S_PRINT.no_graph : "Aucun graphique disponible pour cette consultation");
        return;
    }

    bootstrap.Modal.getOrCreateInstance('#modal-impression-graphs').hide();

    const docDefinition = {
        pageMargins: [40, 40, 40, 40],
        content: content,
        styles: {
            header: { fontSize: 14, bold: true, margin: [0, 10, 0, 5] }
        }
    };

    pdfMake.createPdf(docDefinition).print();
}

$(document).ready(function () {

    if (!isConsultationEnregistree()) {
        setTimeout(() => enregistrerConsultation(), 2000);
    }

    imgItemTpl = _.template($('#image-item-template').html())

    setTimeout(() => {
        $('.form-control,.form-select,input').change(e => {
            console.log('Form control changed');
            updateEditor();
        });
    }, 2000);

    if (isConsultationEnregistree()) {
        $('#libelle_statut')
            .toggleClass('label-success', true)
            .text('Enregistré')
            .show();
        $('#btn_terminer').removeClass('d-none');
        $('#btn_terminer').attr('href', `/consultation/${consultation_pk}/cloturer/`);
        $('.enregistrer').addClass('d-none');
    } else {
        $('#libelle_statut')
            .toggleClass('label-success', false)
            .text('Brouillon')
            .show();
    }


    tinymce.init({
        selector: '#editor-1',
        language: 'fr_FR',
        plugins: ['link', 'lists', 'autolink', 'paste', 'table'],
        contextmenu: 'image table',
        paste_as_text: true,
        toolbar: [
            'undo redo | bold italic underline | fontsizeselect | forecolor backcolor | alignleft aligncenter alignright alignfull | numlist bullist outdent indent | table'
        ],
        statusbar: false, menubar: false, inline: false, forced_root_block: false,
        //content_style: "body { font-size: 10pt }",
        init_instance_callback: function (editor) {
            $('.tox-tinymce').height(window.innerHeight - 240);

            getEditorSelector().find('select, input').on('change', e => {
                console.log('Select changed', $(e.target).val());
                $(e.target).attr('value', $(e.target).val());
            });

            editor.on('Change', function (e) {
                if (isConsultationEnregistree()) {
                    enregistrerConsultation(editor);
                }
            });

            editor.on('keyup', function (e) {
                $('#libelle_statut')
                    .toggleClass('label-success', false)
                    .text('Brouillon')
                    .show();
                touched = true;
            });

            editor.on('SetContent', function (e) {
                toggleGrossesseInfo(addGrossesseInfo);
                toggleAntecedents(addAntecedents);
                toggleNotes(addNotes);
            });

            if (!isConsultationEnregistree()) {
                editor.setContent(templateConsultation({data: "", date: getDateConsultation()}));
            }

            if (modeEdition) {
                createPdf().then(pdfDoc => {
                    pdfDoc.print();
                    parent.fermerModals();
                });
            }
        }
    });

    const date = getDateConsultation();
    $('#date-consultation').html(date);

    $('#btn_enregistrer').click(e => {
        if (typeof enrgistrerConsultationCustom !== "undefined")
            enrgistrerConsultationCustom(tinymce.activeEditor)
        else
            enregistrerConsultation(tinymce.activeEditor);
    });

    $('#btn-demarrer-impression').click(e => {
        demarrerImpression();
    });

    $('#id_praticien').change(eve => {
        signatureB64 = '';
        const id = $("#id_praticien option:selected").val();
        const medecin = _.find(medecins, p => p.id == id);
        console.info('Changement Medecin', medecin)
        if (medecin.ajouter_signature_edition && medecin.signature && medecin.signature != '') {
            chargerImageB64(medecin.signature, (b64) => {
                signatureB64 = b64;
            });
        }
    });

    $('select').contextmenu(e => {
        e.preventDefault();
        targetSelect = null;
        let formulaire = $(e.target).attr('data-form');
        let champ = $(e.target).attr('data-champ');
        if (formulaire && champ) {
            showFrameLoading();
            $('#liste-choix-modal iframe').attr('src', `/listes/?formulaire=${formulaire}&champ=${champ}`);
            bootstrap.Modal.getOrCreateInstance('#liste-choix-modal').show();
            targetSelect = $(e.target);
        }
    });

    $('#id_template_edition').change(e => {
        if (!isConsultationEnregistree() && touched) {
            swal.fire({
                text: _sm.remplacer_saisie || "Remplacer la saisie ?",
                type: "warning",
                showCancelButton: true,
                confirmButtonClass: "btn-danger",
                confirmButtonText: _sm.oui || "Oui",
                cancelButtonText: _sm.non || "Non",
                closeOnConfirm: false
            }).then(function (result) {
                if (result.value) {
                    insererTemplateEdition($(e.target));
                }
            });
        } else {
            insererTemplateEdition($(e.target));
        }
    });


    $('#cb-inserer-antecedents').prop("checked", addAntecedents);
    $('#cb-inserer-antecedents').on('change', e => {
        toggleAntecedents($(e.target).is(':checked'));
    });

    $('#cb-inserer-notes').on('change', e => {
        toggleNotes($(e.target).is(':checked'));
    });

    $('#cb-inserer-grossesse-info').on('change', e => {
        toggleGrossesseInfo($(e.target).is(':checked'));
    });

    $('#materiel').change(e => {
        if (consultation_pk == -1)
            return;
        const id = $('#materiel').val();
        console.log('Materiel', $('#materiel').val());
        data = {
            device: id
        }
        $.post(`/worklists/${consultation_pk}/modifier/`, data)
            .done(function (result) {
                console.log('Matériel changé')
                filterImagesByDevice();
            })
            .fail(function () {
                console.error('Impossible de sauvegarder');
            })
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
            updateEditor();
        }
    });


    $('#btn_imprimer').click(e => {
        imprimerClick();
    });

    $(window).resize(e => {
        $('.tox-tinymce').height(window.innerHeight - 240);
    });

    initTimer();

    filterImagesByDevice();
});

