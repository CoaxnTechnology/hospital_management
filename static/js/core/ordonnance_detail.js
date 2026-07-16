let pdfDoc;

$(document).ready(() => {

    const templateSignature = _.template(unescapeTemplate($('#template-signature').html()));

    $('#btn-enregistrer').click(eve => {
        const signatureData = {signature_titre: praticien.nom, signature_img: signatureB64};
        const docDefinition = {
            pageMargins: defaultMargins(),
            pageSize: 'A5',
            header: defaultHeader,
            footer: defaultFooter,
            content: [
                htmlToPdfmake($('#ordonnance-text').html()),
                htmlToPdfmake(templateSignature(signatureData))
            ]
        };

        pdfDoc = pdfMake.createPdf(docDefinition);
        pdfDoc.open();

    });

});