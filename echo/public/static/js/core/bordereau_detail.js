function range(start, end) {
    return Array(end - start + 1). fill(). map((_, idx) => start + idx);
}

function telechargerRapport() {
    let url = `/bordereau/${bordereauId}/rapport`;
    $.post(url)
        .done(function (result) {
            //window.open(result)
            console.log(result);
            window.open(url, '_blank');
        })
        .fail(function (resp) {
            console.log(resp);
            toastr.warning(resp.responseText, {timeOut: 100000});
        });
}


function Unite( nombre ){
	var unite;
	switch( nombre ){
		case 0: unite = "zéro";		break;
		case 1: unite = "un";		break;
		case 2: unite = "deux";		break;
		case 3: unite = "trois"; 	break;
		case 4: unite = "quatre"; 	break;
		case 5: unite = "cinq"; 	break;
		case 6: unite = "six"; 		break;
		case 7: unite = "sept"; 	break;
		case 8: unite = "huit"; 	break;
		case 9: unite = "neuf"; 	break;
	}//fin switch
	return unite;
}//-----------------------------------------------------------------------

function Dizaine( nombre ){
	switch( nombre ){
		case 10: dizaine = "dix"; break;
		case 11: dizaine = "onze"; break;
		case 12: dizaine = "douze"; break;
		case 13: dizaine = "treize"; break;
		case 14: dizaine = "quatorze"; break;
		case 15: dizaine = "quinze"; break;
		case 16: dizaine = "seize"; break;
		case 17: dizaine = "dix-sept"; break;
		case 18: dizaine = "dix-huit"; break;
		case 19: dizaine = "dix-neuf"; break;
		case 20: dizaine = "vingt"; break;
		case 30: dizaine = "trente"; break;
		case 40: dizaine = "quarante"; break;
		case 50: dizaine = "cinquante"; break;
		case 60: dizaine = "soixante"; break;
		case 70: dizaine = "soixante-dix"; break;
		case 80: dizaine = "quatre-vingt"; break;
		case 90: dizaine = "quatre-vingt-dix"; break;
	}//fin switch
	return dizaine;
}//-----------------------------------------------------------------------

function NumberToLetter( nombre ) {
    var i, j, n, quotient, reste, nb;
    var ch
    var numberToLetter = '';
    //__________________________________

    if (nombre.toString().replace(/ /gi, "").length > 15) return "dépassement de capacité";
    if (isNaN(nombre.toString().replace(/ /gi, ""))) return "Nombre non valide";

    nb = parseFloat(nombre.toString().replace(/ /gi, ""));
    if (Math.ceil(nb) != nb) return "Nombre avec virgule non géré.";

    n = nb.toString().length;
    switch (n) {
        case 1:
            numberToLetter = Unite(nb);
            break;
        case 2:
            if (nb > 19) {
                quotient = Math.floor(nb / 10);
                reste = nb % 10;
                if (nb < 71 || (nb > 79 && nb < 91)) {
                    if (reste == 0) numberToLetter = Dizaine(quotient * 10);
                    if (reste == 1) numberToLetter = Dizaine(quotient * 10) + "-et-" + Unite(reste);
                    if (reste > 1) numberToLetter = Dizaine(quotient * 10) + "-" + Unite(reste);
                } else numberToLetter = Dizaine((quotient - 1) * 10) + "-" + Dizaine(10 + reste);
            } else numberToLetter = Dizaine(nb);
            break;
        case 3:
            quotient = Math.floor(nb / 100);
            reste = nb % 100;
            if (quotient == 1 && reste == 0) numberToLetter = "cent";
            if (quotient == 1 && reste != 0) numberToLetter = "cent" + " " + NumberToLetter(reste);
            if (quotient > 1 && reste == 0) numberToLetter = Unite(quotient) + " cents";
            if (quotient > 1 && reste != 0) numberToLetter = Unite(quotient) + " cent " + NumberToLetter(reste);
            break;
        case 4 :
            quotient = Math.floor(nb / 1000);
            reste = nb - quotient * 1000;
            if (quotient == 1 && reste == 0) numberToLetter = "mille";
            if (quotient == 1 && reste != 0) numberToLetter = "mille" + " " + NumberToLetter(reste);
            if (quotient > 1 && reste == 0) numberToLetter = NumberToLetter(quotient) + " mille";
            if (quotient > 1 && reste != 0) numberToLetter = NumberToLetter(quotient) + " mille " + NumberToLetter(reste);
            break;
        case 5 :
            quotient = Math.floor(nb / 1000);
            reste = nb - quotient * 1000;
            if (quotient == 1 && reste == 0) numberToLetter = "mille";
            if (quotient == 1 && reste != 0) numberToLetter = "mille" + " " + NumberToLetter(reste);
            if (quotient > 1 && reste == 0) numberToLetter = NumberToLetter(quotient) + " mille";
            if (quotient > 1 && reste != 0) numberToLetter = NumberToLetter(quotient) + " mille " + NumberToLetter(reste);
            break;
        case 6 :
            quotient = Math.floor(nb / 1000);
            reste = nb - quotient * 1000;
            if (quotient == 1 && reste == 0) numberToLetter = "mille";
            if (quotient == 1 && reste != 0) numberToLetter = "mille" + " " + NumberToLetter(reste);
            if (quotient > 1 && reste == 0) numberToLetter = NumberToLetter(quotient) + " mille";
            if (quotient > 1 && reste != 0) numberToLetter = NumberToLetter(quotient) + " mille " + NumberToLetter(reste);
            break;
        case 7:
            quotient = Math.floor(nb / 1000000);
            reste = nb % 1000000;
            if (quotient == 1 && reste == 0) numberToLetter = "un million";
            if (quotient == 1 && reste != 0) numberToLetter = "un million" + " " + NumberToLetter(reste);
            if (quotient > 1 && reste == 0) numberToLetter = NumberToLetter(quotient) + " millions";
            if (quotient > 1 && reste != 0) numberToLetter = NumberToLetter(quotient) + " millions " + NumberToLetter(reste);
            break;
        case 8:
            quotient = Math.floor(nb / 1000000);
            reste = nb % 1000000;
            if (quotient == 1 && reste == 0) numberToLetter = "un million";
            if (quotient == 1 && reste != 0) numberToLetter = "un million" + " " + NumberToLetter(reste);
            if (quotient > 1 && reste == 0) numberToLetter = NumberToLetter(quotient) + " millions";
            if (quotient > 1 && reste != 0) numberToLetter = NumberToLetter(quotient) + " millions " + NumberToLetter(reste);
            break;
        case 9:
            quotient = Math.floor(nb / 1000000);
            reste = nb % 1000000;
            if (quotient == 1 && reste == 0) numberToLetter = "un million";
            if (quotient == 1 && reste != 0) numberToLetter = "un million" + " " + NumberToLetter(reste);
            if (quotient > 1 && reste == 0) numberToLetter = NumberToLetter(quotient) + " millions";
            if (quotient > 1 && reste != 0) numberToLetter = NumberToLetter(quotient) + " millions " + NumberToLetter(reste);
            break;
        case 10:
            quotient = Math.floor(nb / 1000000000);
            reste = nb - quotient * 1000000000;
            if (quotient == 1 && reste == 0) numberToLetter = "un milliard";
            if (quotient == 1 && reste != 0) numberToLetter = "un milliard" + " " + NumberToLetter(reste);
            if (quotient > 1 && reste == 0) numberToLetter = NumberToLetter(quotient) + " milliards";
            if (quotient > 1 && reste != 0) numberToLetter = NumberToLetter(quotient) + " milliards " + NumberToLetter(reste);
            break;
        case 11:
            quotient = Math.floor(nb / 1000000000);
            reste = nb - quotient * 1000000000;
            if (quotient == 1 && reste == 0) numberToLetter = "un milliard";
            if (quotient == 1 && reste != 0) numberToLetter = "un milliard" + " " + NumberToLetter(reste);
            if (quotient > 1 && reste == 0) numberToLetter = NumberToLetter(quotient) + " milliards";
            if (quotient > 1 && reste != 0) numberToLetter = NumberToLetter(quotient) + " milliards " + NumberToLetter(reste);
            break;
        case 12:
            quotient = Math.floor(nb / 1000000000);
            reste = nb - quotient * 1000000000;
            if (quotient == 1 && reste == 0) numberToLetter = "un milliard";
            if (quotient == 1 && reste != 0) numberToLetter = "un milliard" + " " + NumberToLetter(reste);
            if (quotient > 1 && reste == 0) numberToLetter = NumberToLetter(quotient) + " milliards";
            if (quotient > 1 && reste != 0) numberToLetter = NumberToLetter(quotient) + " milliards " + NumberToLetter(reste);
            break;
        case 13:
            quotient = Math.floor(nb / 1000000000000);
            reste = nb - quotient * 1000000000000;
            if (quotient == 1 && reste == 0) numberToLetter = "un billion";
            if (quotient == 1 && reste != 0) numberToLetter = "un billion" + " " + NumberToLetter(reste);
            if (quotient > 1 && reste == 0) numberToLetter = NumberToLetter(quotient) + " billions";
            if (quotient > 1 && reste != 0) numberToLetter = NumberToLetter(quotient) + " billions " + NumberToLetter(reste);
            break;
        case 14:
            quotient = Math.floor(nb / 1000000000000);
            reste = nb - quotient * 1000000000000;
            if (quotient == 1 && reste == 0) numberToLetter = "un billion";
            if (quotient == 1 && reste != 0) numberToLetter = "un billion" + " " + NumberToLetter(reste);
            if (quotient > 1 && reste == 0) numberToLetter = NumberToLetter(quotient) + " billions";
            if (quotient > 1 && reste != 0) numberToLetter = NumberToLetter(quotient) + " billions " + NumberToLetter(reste);
            break;
        case 15:
            quotient = Math.floor(nb / 1000000000000);
            reste = nb - quotient * 1000000000000;
            if (quotient == 1 && reste == 0) numberToLetter = "un billion";
            if (quotient == 1 && reste != 0) numberToLetter = "un billion" + " " + NumberToLetter(reste);
            if (quotient > 1 && reste == 0) numberToLetter = NumberToLetter(quotient) + " billions";
            if (quotient > 1 && reste != 0) numberToLetter = NumberToLetter(quotient) + " billions " + NumberToLetter(reste);
            break;
    }//fin switch
    /*respect de l'accord de quatre-vingt*/
    if (numberToLetter.substr(numberToLetter.length - "quatre-vingt".length, "quatre-vingt".length) == "quatre-vingt") numberToLetter = numberToLetter + "s";

    return numberToLetter;
}

function montantLettres(montant) {
    let parts = montant.split('.');
    let res = '';
    if (parts.length > 1 && parseFloat(parts[1]) !== 0.0 ) {
        res = `${NumberToLetter(parts[0])} dinars et ${NumberToLetter(parts[1])} millimes`
    } else {
        res = `${NumberToLetter(parts[0])} dinars`
    }
    return res.toUpperCase();
}

$(document).ready(function () {

    const totalPEC = _.sumBy(data, 'prise_en_charge');
    $('#totalPEC').html(`${totalPEC.toFixed(3)} DT`);
    //$('#totalPEC-lettres').html(montantLettres(totalPEC.toFixed(3)));

    const initTable1 = function () {
        for (let i = 0; i < data.length; i++) {
            data[i].num = i+1;
        }

        const code = bordereau[0].code_conventionnel ? bordereau[0].code_conventionnel : '';
        let message = `Médecin : ${bordereau[0].nom_medecin}    Code conventionnel : ${code}      Période : ${bordereau[0].periode_format}`;
        let messageBottom = `\nTotal à payer ${totalPEC.toFixed(3)} DT \n ${montantLettres(totalPEC.toFixed(3))}`;

        let table = $('#kt_datatable').DataTable({
            language: {
                "url": "/static/plugins/custom/datatables/French.json"
            },
            responsive: true,
            // Pagination settings
            dom: `<'row'<'col-sm-6 text-left'f><'col-sm-6 text-right'B>>
			<'row'<'col-sm-12'tr>>
			<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7 dataTables_pager'lp>>`,
            // read more: https://datatables.net/examples/basic_init/dom.html
            buttons: [
                //'copy', 'csv', 'excel', 'print',
                {
                    extend: 'pdfHtml5',
                    text: 'Imprimer',
                    orientation: 'landscape',
                    pageSize: 'A4',
                    title: "NOTE D'HONORAIRES DES CONSULTATIONS ET DE ACTES AMBULATOIRES EFFECTUES PAR MEDECIN CONVENTIONNE DANS LE CADRE DU TIERS PAYANT",
                    messageTop: message,
                    messageBottom: messageBottom,
                    customize: function (doc) {
                        // Set the font size fot the entire document
						doc.defaultStyle.fontSize = 8;
						// Set the fontsize for the table header
						doc.styles.tableHeader.fontSize = 8;
                    }
                }
            ],
            lengthMenu: [5, 10, 25, 50],
            pageLength: 10,
            searchDelay: 500,
            processing: true,
            serverSide: false,
            data: data,
            columns: [
                {data: 'num'},
                {
                    data: 'date_creation',
                    render: function (data) {
                        return moment(data).format('DD/MM/YYYY');
                    }
                },
                {data: 'patient.num_carnet_soin'},
                {
                    data: 'patient.nom',
                    render: function (data, type, full, meta) {
                        return (full.patient.nom_naissance + ' ' + full.patient.prenom).toUpperCase();
                    },
                },
                {data: 'patient.lien_parente'},
                {data: 'patient.code_apci'},
                {
                    data: 'lignes_reglement',
                    render: function (data) {
                        list = data[0].code;
                        return list;
                    },
                },
                {
                    data: 'lignes_reglement',
                    render: function (data) {
                        return data.length;
                    },
                },
                {
                    data: 'total',
                    render: function (data) {
                        return data.toFixed(3);
                    },
                },
                {
                    data: 'prise_en_charge',
                    render: function (data) {
                        return data.toFixed(3);
                    },
                },
                {
                    data: 'ticket_moderateur',
                    render: function (data) {
                        return data.toFixed(3);
                    },
                },
                {data: 'patient.code_medecin_famille'},

            ],


            drawCallback: function (settings) {
                if (settings.fnRecordsDisplay() === 0) {
                    const data = _.map($('[data-search-key]').get(), el => $(el).attr('data-search-key') + '=' + $(el).val());
                }
            },

        });

    };

    initTable1();

});
