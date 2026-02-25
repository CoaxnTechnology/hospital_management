import datetime
from time import strftime

from apps.core.models import Reglement, Bordereau


class MissingDataException(Exception):
    pass


DATE_FMT = "%Y%m%d"


def generate_header(bordereau):
    header = "1"
    code_conventionnel = f"{0:012}"
    if bordereau.code_conventionnel:
        #header += f"{bordereau.code_conventionnel:012}"
        code_conventionnel = bordereau.code_conventionnel.replace("/", "").rjust(12, '0')
    header += code_conventionnel

    # Date dépot
    date_depot = datetime.date.today().strftime(DATE_FMT)
    header += date_depot

    if bordereau.periode_debut():
        header += bordereau.periode_debut().strftime(DATE_FMT)
    else:
        raise MissingDataException(f"Aucun règlement n'est associé au borderau")

    if bordereau.periode_fin():
        header += bordereau.periode_fin().strftime(DATE_FMT)
    else:
        raise MissingDataException(f"Aucun règlement n'est associé au borderau")

    reference = code_conventionnel + date_depot
    header += reference

    header += f"{bordereau.nombre_reglements:05}"

    header += f"{int(1000*bordereau.total):010}"
    header += f"{int(1000*bordereau.ticket_moderateur):010}"
    header += f"{int(1000*bordereau.prise_en_charge):010}"

    return header


def generate_line(counter, reglement):
    p = reglement.patient
    line = "2"
    line += f"{counter:05}"
    if p.caisse_affectation == "1":
        line += "2"
    if p.caisse_affectation == "2":
        line += "1"
    print('Carnet soin', p.num_carnet_soin, p.id)
    if p.num_carnet_soin:
        #line += f"{p.num_carnet_soin:10}"
        line += p.num_carnet_soin.rjust(10)
    else:
        #raise MissingDataException(f"N° carnet de soin non défini pour {p.nom_complet}")
        line += f"{0:010}"

    if p.lien_parente:
        line += f"{int(p.lien_parente)-1}"
    else:
        line += "0"

    """
        Rang
        = 0 si assuré, conjoint, père ou mère
        = 1..n rang enfant
    """
    line += "00"

    line += f"{p.nom_naissance} {p.prenom}".upper().ljust(60)

    line += p.date_naissance.strftime(DATE_FMT)

    if p.code_medecin_famille:
        #line += f"{p.code_medecin_famille:012}"
        line += p.code_medecin_famille.replace("/", "").rjust(12, '0')
    else:
        line += f"{0:012}"

    # Date prescription
    line += reglement.date_creation.strftime("%Y%m%d")

    # Total facture
    line += f"{int(1000*reglement.total):010}"

    # Montant consultation
    line += f"{int(1000*reglement.total):010}"

    # Ticket modérateur
    line += f"{int(1000*reglement.ticket_moderateur):010}"

    # Prise en charge CNAM
    line += f"{int(1000*reglement.prise_en_charge):010}"

    # Code APCI
    if p.code_apci:
        #line += f"{int(p.code_apci):04}"
        line += p.code_apci.rjust(4, '0')
    else:
        line += f"{0:04}"
        #raise MissingDataException(f"Code APCI non défini pour {p.nom_complet}")

    return line


def generate_report(bordereau_id):
    bordereau = Bordereau.objects.get(pk=bordereau_id)
    reglements = Reglement.objects.filter(bordereau=bordereau_id) \
            .select_related('patient')
    counter = 1
    content = ""
    content += generate_header(bordereau) + "\n"

    #print("Header", content)

    for reglement in reglements:
        line = generate_line(counter, reglement)
        #print('===========================')
        #print(line)
        content += line + "\n"
        #print('===========================')
        counter += 1
    return content


if __name__ == '__main__':
    generate_report(7)