let logoB64 = '', footerB64 = '', signatureB64 = '';

if (logo_url && logo_url != '') {
    console.log('Logo url', logo_url);
    chargerImageB64(logo_url, (b64) => {
        logoB64 = b64;
    });
}

if (footer_url && footer_url != '') {
    chargerImageB64(footer_url, (b64) => {
        footerB64 = b64;
    });
}

if (signature_url && signature_url != '') {
    chargerImageB64(signature_url, (b64) => {
        signatureB64 = b64;
    });
}

function defaultHeader(currentPage, pageCount, pageSize) {
    return [
        addEntetes ?
            {image: logoB64, width: pageSize.width, margin: [0, 0, 0, 0], alignment: 'center'} :
            {text: ' ', fit: [420, 55], margin: [0, 0, 0, 0], alignment: 'center'}
    ];
}

function defaultFooter(currentPage, pageCount, pageSize) {
    return [
        addEntetes ?
            {image: footerB64, width: pageSize.width, margin: [0, 0, 0, 0], alignment: 'center'} :
            {text: ' ', fit: [420, 85], margin: [0, 0, 0, 0], alignment: 'center'},
            {
                text: `Edité sur ${productBrand} - ` + currentPage.toString() + '/' + pageCount,
                margin: [5, addEntetes ? 0 : 60, 5, 0],
                fontSize: 8,
                color: '#777',
                alignment: 'left'
            }
    ];
}

function defaultMargins() {
    return [parametresCompte.marge_gauche, parametresCompte.marge_entete, parametresCompte.marge_droite, parametresCompte.marge_footer];
}

function impressionGenerique(content, pageSize = 'A5') {
    const headerImg = (addEntetes && logoB64)   ? `<div style="text-align:center;margin-bottom:6px;"><img src="${logoB64}" style="max-width:100%;max-height:80px;"/></div>` : '';
    const footerImg = (addEntetes && footerB64) ? `<div style="text-align:center;margin-top:10px;"><img src="${footerB64}" style="max-width:100%;max-height:60px;"/></div>` : '';
    const margins   = defaultMargins();
    const marginCss = `${margins[1]}pt ${margins[2]}pt ${margins[3]}pt ${margins[0]}pt`;
    const pageW     = pageSize === 'A4' ? 'A4' : 'A5';

    const win = window.open('', '_blank');
    win.document.write(`<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
  @page { size: ${pageW}; margin: ${marginCss}; }
  * { box-sizing: border-box; }
  body { font-family: Arial, sans-serif; font-size: 11pt; margin: 0; padding: 10mm; }
  p { margin: 0 0 4px; }
  strong { font-weight: bold; }
</style>
</head><body>
${headerImg}
${content}
${footerImg}
</body></html>`);
    win.document.close();
    setTimeout(() => { win.print(); }, 300);
}

function cleanPDF(el, parent) {
    /*if (el["text"] && el["text"] == " ") {
        console.info("empty");
      return;
    }
    */

    if (_.has(el, "id")) {
        //console.log("Element id", el["id"]);
    }

    if (_.isArray(el)) {
        const st = el;
        let child = [];
        parent.push(child);
        //p = _.cloneDeep(el)
        for (let i = 0; i < st.length; i++) {
            console.log('Item', i);
            console.log('Item', st[i]);
            cleanPDF(st[i], child);
        }
    } else {
        if (_.has(el, "text")) {
            if (el["text"] != " " && el["text"] != " ") {//} || el["style"].length > 0) {
                console.info("Text", el["text"]);
                parent.push(el);
            }
        }

        if (_.has(el, "stack") && el["stack"]) {
            const st = _.cloneDeep(el["stack"]);
            el['stack'] = [];
            parent.push(el);
            for (let j = 0; j < st.length; j++) {
                cleanPDF(st[j], el['stack']);
            }
        } else if (!_.has(el, "text")) {
            //console.info(el["text"]);
            parent.push(el);
        }
    }
}

const defaultHtml2PDFOptions = {
    defaultStyles: {
        "p": {"margin": 0},
        "div": {"margin": 0},
        "strong": {"margin": 0},
        "li": {"margin": 0},
        "br": {"lineHeight": 0, "margin": 0}
    },
    tableAutoSize: true
};