let hadlock = 2;

function getPoidsHadlock(PC, PA, LF, BIP) {
    if (hadlock == 5 && (undefined == PC || PC == '' || PC == '0.0' || PC == '0')) {
        return "";
    }
    if (hadlock == 3 && (undefined == BIP || BIP == '' || PA == '0.0' || PA == '0' || LF == '0.0' || LF == '0')) {
        return "";
    }
    if (hadlock == 2 && (undefined == PC || PC == '' || PA == '0.0' || PA == '0' || LF == '0.0' || LF == '0')) {
        return "";
    }
    if (hadlock == "intergrowth" && (undefined == PC || PC == '' || PA == '0.0' || PA == '0')) {
        return "";
    }
    var EPF = "";
    if (hadlock == 5)
        EPF = roundit(Math.pow(10, (1.3596 + 0.00064 * PC + 0.00424 * PA + 0.0174 * LF + 0.0000061 * BIP * 1 * PA - 0.0000386 * PA * 1 * LF)));
    else if (hadlock == 3)
        EPF = roundit(Math.pow(10, (1.335 + 0.00316 * BIP + 0.00457 * PA + 0.01623 * LF - 0.000034 * PA * LF)));
    else if (hadlock == 2)
        EPF = roundit(Math.pow(10, (1.326 + 0.00107 * PC + 0.00438 * PA + 0.0158 * LF - 0.0000326 * PA * LF)));
    else if (hadlock == "intergrowth")
        EPF = Math.round(Math.pow(2.71828182845905, 5.084820 - 54.06633 * Math.pow(PA / 1000, 3) - 95.80076 * Math.pow(PA / 1000, 3) * Math.log(PA / 1000) + 3.136370 * (PC / 1000)));
    //EPF = roundit(Math.pow(10,4.8));
    return EPF;
}


$(document).ready(() => {
    if (grossesse) {
        let ddg = moment(grossesse.ddr, 'YYYY-MM-DD').add(grossesse.cycle-14, 'days');
        if (grossesse.ddr) {
            $('.terme').text(calcTerme(moment(grossesse.ddr, 'YYYY-MM-DD'), grossesse.cycle));
            $('.ddg').text(ddg.format('DD/MM/YYYY'));
            $('.ddr').text(moment(grossesse.ddr, 'YYYY-MM-DD').format('DD/MM/YYYY'));
            $('.accouchement').text(calcDateAccouchement(moment(grossesse.ddr, 'YYYY-MM-DD'), grossesse.cycle));
            const ddr = moment(grossesse.ddr, 'YYYY-MM-DD');
            if (parametresCompte) {
                const pc = parametresCompte;
                let d1_1 = ddr.clone().add(7 * pc.gross_echo_datation_sa_1 + pc.gross_echo_datation_j_1, 'days');
                let d1_2 = ddr.clone().add(7 * pc.gross_echo_datation_sa_2 + pc.gross_echo_datation_j_2, 'days');
                $('#cal-echo-datation-int').text(`du ${d1_1.format("DD/MM/YY")} au ${d1_2.format("DD/MM/YY")}`);

                let d2_1 = ddr.clone().add(7 * pc.gross_echo_t1_sa_1 + pc.gross_echo_t1_j_1, 'days');
                let d2_2 = ddr.clone().add(7 * pc.gross_echo_t1_sa_2 + pc.gross_echo_t1_j_2, 'days');
                $('#cal-echo-1-int').text(`du ${d2_1.format("DD/MM/YY")} au ${d2_2.format("DD/MM/YY")}`);

                let d3_1 = ddr.clone().add(7 * pc.gross_echo_t2_sa_1 + pc.gross_echo_t2_j_1, 'days');
                let d3_2 = ddr.clone().add(7 * pc.gross_echo_t2_sa_2 + pc.gross_echo_t2_j_2, 'days');
                $('#cal-echo-2-int').text(`du ${d3_1.format("DD/MM/YY")} au ${d3_2.format("DD/MM/YY")}`);

                let d4_1 = ddr.clone().add(7 * pc.gross_echo_t3_sa_1 + pc.gross_echo_t3_j_1, 'days');
                let d4_2 = ddr.clone().add(7 * pc.gross_echo_t3_sa_2 + pc.gross_echo_t3_j_2, 'days');
                $('#cal-echo-3-int').text(`du ${d4_1.format("DD/MM/YY")} au ${d4_2.format("DD/MM/YY")}`);

                let d5 = ddr.clone().add(7 * pc.gross_12_sa + pc.gross_12_j, 'days');
                $('#cal-12-sa').text(`Le ${d5.format("DD/MM/YY")}`);

                let d6 = ddr.clone().add(7 * pc.gross_22_sa + pc.gross_22_j, 'days');
                $('#cal-22-sa').text(`Le ${d6.format("DD/MM/YY")}`);

                let d7 = ddr.clone().add(7 * pc.gross_32_sa + pc.gross_32_j, 'days');
                $('#cal-32-sa').text(`Le ${d7.format("DD/MM/YY")}`);

                let d8 = ddr.clone().add(7 * (pc.gross_32_sa+2) + pc.gross_32_j, 'days');
                $('#cal-34-sa').text(`Le ${d8.format("DD/MM/YY")}`);

                let d9 = ddr.clone().add(7 * (pc.gross_32_sa+3) + pc.gross_32_j, 'days');
                $('#cal-35-sa').text(`Le ${d9.format("DD/MM/YY")}`);

                let d8_1 = ddr.clone().add(7 * pc.gross_triso_2_sa_1 + pc.gross_triso_2_j_1, 'days');
                let d8_2 = ddr.clone().add(7 * pc.gross_triso_2_sa_2 + pc.gross_triso_2_j_2, 'days');
                $('#cal-triso-2-int').text(`du ${d8_1.format("DD/MM/YY")} au ${d8_2.format("DD/MM/YY")}`);

                let d81_1 = ddr.clone().add(7 * pc.gross_triso_1_sa_1 + pc.gross_triso_1_j_1, 'days');
                let d81_2 = ddr.clone().add(7 * pc.gross_triso_1_sa_2 + pc.gross_triso_1_j_2, 'days');
                $('#cal-triso-1-int').text(`du ${d81_1.format("DD/MM/YY")} au ${d81_2.format("DD/MM/YY")}`);

                let d9_1 = ddr.clone().add(7 * pc.gross_gly_sa_1 + pc.gross_gly_j_1, 'days');
                let d9_2 = ddr.clone().add(7 * pc.gross_gly_sa_2 + pc.gross_gly_j_2, 'days');
                $('#cal-gly-int').text(`du ${d9_1.format("DD/MM/YY")} au ${d9_2.format("DD/MM/YY")}`);
            }
        } else {
            $('.terme').text('-');
            $('.ddg').text('-');
            $('.ddr').text('');
            $('.accouchement').text('');
        }
    }

    $('.rdv_suivant_input').change(e => {
        let ddr = moment(grossesse.ddr, 'YYYY-MM-DD');
        if ($("#rdv_suivant_apres_sa").val()) {
            let sa = $("#rdv_suivant_apres_sa").val();
            let dt = ddr.clone().add(sa, 'weeks');
            if ($("#rdv_suivant_apres_jours").val()) {
                let jours = $("#rdv_suivant_apres_jours").val();
                dt = dt.add(jours, 'days');
            }
            $('#rdv_suivant_apres').text(dt.format('DD/MM/YYYY'));
            $('#id_rdv_suivant_apres').val(dt.format('YYYY-MM-DD'));
        }

        if ($("#rdv_suivant_avant_sa").val()) {
            let sa = $("#rdv_suivant_avant_sa").val();
            let dt = ddr.clone().add(sa, 'weeks');
            if ($("#rdv_suivant_avant_jours").val()) {
                let jours = $("#rdv_suivant_avant_jours").val();
                dt = dt.add(jours, 'days');
            }
            $('#id_rdv_suivant_avant').val(dt.format('YYYY-MM-DD'));
            $('#rdv_suivant_avant').text(dt.format('DD/MM/YYYY'));
        }
    });
});