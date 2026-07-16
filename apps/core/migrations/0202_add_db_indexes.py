from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0201_alter_patient_origine'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='rdv',
            index=models.Index(fields=['compte', 'debut'], name='core_rdv_compte_debut_idx'),
        ),
        migrations.AddIndex(
            model_name='rdv',
            index=models.Index(fields=['compte', 'ancien_debut'], name='core_rdv_compte_ancien_debut_idx'),
        ),
        migrations.AddIndex(
            model_name='consultation',
            index=models.Index(fields=['patient', 'date'], name='core_consultation_patient_date_idx'),
        ),
        migrations.AddIndex(
            model_name='admission',
            index=models.Index(fields=['patient', 'date'], name='core_admission_patient_date_idx'),
        ),
    ]
