from django.db import migrations, models


def set_categorie_from_libelle(apps, schema_editor):
    TypeOrdonnance = apps.get_model('core', 'TypeOrdonnance')
    for obj in TypeOrdonnance.objects.all():
        libelle = obj.libelle.lower()
        if 'traitement' in libelle or 'médic' in libelle or 'medic' in libelle:
            obj.categorie = 'traitement'
        elif 'examen' in libelle:
            obj.categorie = 'examen'
        else:
            obj.categorie = 'autre'
        obj.save(update_fields=['categorie'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0207_doctorsignuprequest_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='typeordonnance',
            name='categorie',
            field=models.CharField(
                choices=[
                    ('traitement', 'Traitement médicamenteux'),
                    ('examen', 'Examens complémentaires'),
                    ('autre', 'Autre'),
                ],
                default='autre',
                max_length=32,
            ),
        ),
        migrations.RunPython(set_categorie_from_libelle, migrations.RunPython.noop),
    ]
