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
    let makeDoc = [];
    cleanPDF(htmlToPdfmake(content, defaultHtml2PDFOptions), makeDoc);
    console.log(makeDoc[0]);

    const dd = {
        pageMargins: defaultMargins(),
        pageSize: pageSize,
        header: defaultHeader,
        footer: defaultFooter,
        content: [
            makeDoc[0]
            //htmlToPdfmake(templateSignature(signatureData))
        ],
        defaultStyle: {
            fontSize: 10
        }
    };

    pdfDoc = pdfMake.createPdf(dd);
    pdfDoc.print();
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