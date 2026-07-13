from django.core.management import BaseCommand

from apps.core.models import Compte, TypeOrdonnance, Ordonnance

types = [
    {'libelle': 'Traitements', 'modele': '<div style="text-align: center;"><h4 style="font-size: 24pt;">Ordonnance m&eacute;dicale</h4></div><p><span style="margin-top: 10px;">&nbsp;</span></p><p><strong>&lt;%= civilite %&gt; &lt;%= nom_patient %&gt;</strong></p><p>&nbsp;</p>'},
    {'libelle': 'Examens', 'modele': '<div style="text-align: center;"><h4 style="font-size: 24pt;">Ordonnance m&eacute;dicale</h4></div><p><span style="margin-top: 10px;">&nbsp;</span></p><p><strong>&lt;%= civilite %&gt; &lt;%= nom_patient %&gt;</strong></p><p>&nbsp;</p>'},
    {'libelle': 'Trisomie 21 1er trimestre', 'modele': '<div style="text-align: center;"><h4 style="font-size: 24pt;">D&eacute;pistage de la trisomie 21 (T1)</h4></div><p><span style="margin-top: 10px;">&nbsp;</span></p><p><span style="font-size: 18pt;">&lt;%= civilite %&gt; &lt;%= nom_patient %&gt;</span></p><p><span style="font-size: 18pt;">Date de naissance: &lt;%= date_naissance %&gt;</span></p><table style="border-collapse: collapse; width: 100%;" border="0" data-pdfmake="{&quot;layout&quot;:&quot;noBorders&quot;}"><tbody><tr><td style="width: 48.4289%;"><span style="font-size: 18pt;">Poids : &lt;%= poids %&gt;</span></td><td style="width: 48.4289%;"><span style="font-size: 18pt;">Tabac : &lt;%= fumeur %&gt;</span></td></tr><tr><td style="width: 48.4289%;"><span style="font-size: 18pt;">Diab&egrave;te : &lt;%= diabete %&gt;</span></td><td style="width: 48.4289%;"><span style="font-size: 18pt;">ATCD de T21 :&nbsp;</span></td></tr><tr><td style="width: 48.4289%;"><span style="font-size: 18pt;">DDR: &lt;%= ddr %&gt;</span></td><td style="width: 48.4289%;"><span style="font-size: 18pt;">FIV : &lt;%= fiv %&gt;</span></td></tr><tr><td style="width: 48.4289%;" colspan="2"><span style="font-size: 18pt;">Echo T1 faite le &lt;%= date_echo_t1 %&gt;<br /></span></td></tr><tr><td style="width: 48.4289%;"><span style="font-size: 18pt;">LCC : &lt;%= lcc %&gt;</span></td><td style="width: 48.4289%;"><span style="font-size: 18pt;">CN : &lt;%= cn %&gt;</span></td></tr><tr><td style="width: 48.4289%;" colspan="2"><span style="font-size: 18pt;">Os propres du nez :&nbsp;</span></td></tr></tbody></table><p>&nbsp;</p>'},
    {'libelle': 'Trisomie 21 2ème trimestre', 'modele': '<div style="text-align: center;"><h4 style="font-size: 24pt;">D&eacute;pistage de la trisomie 21 (T2)</h4></div><p><span style="margin-top: 10px;">&nbsp;</span></p><p><span style="font-size: 18pt;">&lt;%= civilite %&gt; &lt;%= nom_patient %&gt;</span></p><p><span style="font-size: 18pt;">Date de naissance: &lt;%= date_naissance %&gt;</span></p><table style="border-collapse: collapse; width: 100%;" border="0" data-pdfmake="{&quot;layout&quot;:&quot;noBorders&quot;}"><tbody><tr><td style="width: 48.4289%;"><span style="font-size: 18pt;">Poids : &lt;%= poids %&gt;</span></td><td style="width: 48.4289%;"><span style="font-size: 18pt;">Tabac : &lt;%= fumeur %&gt;</span></td></tr><tr><td style="width: 48.4289%;"><span style="font-size: 18pt;">Diab&egrave;te : &lt;%= diabete %&gt;</span></td><td style="width: 48.4289%;"><span style="font-size: 18pt;">ATCD de T21 :&nbsp;</span></td></tr><tr><td style="width: 48.4289%;"><span style="font-size: 18pt;">DDR: &lt;%= ddr %&gt;</span></td><td style="width: 48.4289%;"><span style="font-size: 18pt;">FIV : &lt;%= fiv %&gt;</span></td></tr><tr><td style="width: 48.4289%;" colspan="2"><span style="font-size: 18pt;">Echo T1 faite le &lt;%= date_echo_t1 %&gt;<br /></span></td></tr><tr><td style="width: 48.4289%;"><span style="font-size: 18pt;">LCC : &lt;%= lcc %&gt;</span></td><td style="width: 48.4289%;"><span style="font-size: 18pt;">CN : &lt;%= cn %&gt;</span></td></tr><tr><td style="width: 48.4289%;" colspan="2"><span style="font-size: 18pt;">Os propres du nez :&nbsp;</span></td></tr></tbody></table><p>&nbsp;</p>'},
    {'libelle': 'Echographie morphologique', 'modele': '<div style="text-align: center;"><h4 style="font-size: 24pt;">Demande d\'&eacute;chographie morphologique</h4></div><p><span style="margin-top: 10px;">&nbsp;</span></p><p><span style="font-size: 18pt;">&lt;%= civilite %&gt; &lt;%= nom_patient %&gt;</span></p><table style="border-collapse: collapse; width: 100%;" border="1" data-pdfmake="{&quot;layout&quot;:&quot;noBorders&quot;}"><tbody><tr><td style="width: 48.4289%;"><span style="font-size: 18pt;">Age: &lt;%= age %&gt;</span></td><td style="width: 48.4289%;"><span style="font-size: 18pt;">Poids : &lt;%= poids %&gt;</span></td></tr><tr><td style="width: 48.4289%;"><span style="font-size: 18pt;">DDR: &lt;%= ddr %&gt;</span></td><td style="width: 48.4289%;"><span style="font-size: 18pt;">FIV : &lt;%= fiv %&gt;</span></td></tr><tr><td style="width: 48.4289%;" colspan="2"><span style="font-size: 18pt;">Echo T1 faite le &lt;%= date_echo_t1 %&gt;<br /></span></td></tr><tr><td style="width: 48.4289%;"><span style="font-size: 18pt;">LCC : &lt;%= lcc %&gt;</span></td><td style="width: 48.4289%;"><span style="font-size: 18pt;">CN : &lt;%= cn %&gt;</span></td></tr><tr><td style="width: 48.4289%;" colspan="2"><span style="font-size: 18pt;">D&eacute;pistage de la Trisomie 21 : &lt;%= risque_t21 %&gt;</span></td></tr></tbody></table><p>&nbsp;</p>'},
]


class Command(BaseCommand):
    help = "Créer les types d'ordonnances de base"

    def handle(self, *args, **options):
        while True:
            id = input('ID du compte: ')
            try:
                compte = Compte.objects.get(id=id)
            except Compte.DoesNotExist as x:
                print('Compte introuvable')
                continue
            print(f"Création des types d'ordonnances pour le compte '{compte.raison_sociale}'")
            if input('Continuer (y/n)? ') == 'y':
                break

        # Créer les types
        first = None
        for type in types:
            obj = TypeOrdonnance.objects.create(compte_id=id, libelle=type['libelle'], modele=type['modele'])
            if first is None:
                first = obj
        Ordonnance.objects.update(type=first)

        print('Opération terminée')
