from django.db import migrations

MODELE_TRAITEMENT = (
    '<p>Je soussigné(e), Dr <%= nom_praticien %>, certifie avoir examiné ce jour '
    '<strong><%= nom_patient %></strong>, né(e) le <%= date_naissance %> (<%= age %>), '
    'et lui prescris le traitement suivant :</p>'
    '<div id="content-container"></div>'
)

MODELE_EXAMEN = (
    '<p>Je soussigné(e), Dr <%= nom_praticien %>, prescris à '
    '<strong><%= nom_patient %></strong>, né(e) le <%= date_naissance %> (<%= age %>), '
    'les examens complémentaires suivants :</p>'
    '<div id="content-container"></div>'
)

MODELE_AUTRE = (
    '<p><strong><%= nom_patient %></strong>, né(e) le <%= date_naissance %> (<%= age %>)</p>'
    '<div id="content-container"></div>'
)

CATEGORIE_MODELE_MAP = {
    'traitement': MODELE_TRAITEMENT,
    'examen': MODELE_EXAMEN,
    'autre': MODELE_AUTRE,
}


def set_default_modeles(apps, schema_editor):
    TypeOrdonnance = apps.get_model('core', 'TypeOrdonnance')
    for obj in TypeOrdonnance.objects.filter(modele=''):
        default = CATEGORIE_MODELE_MAP.get(obj.categorie, MODELE_AUTRE)
        obj.modele = default
        obj.save(update_fields=['modele'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0208_typeordonnance_categorie'),
    ]

    operations = [
        migrations.RunPython(set_default_modeles, migrations.RunPython.noop),
    ]
