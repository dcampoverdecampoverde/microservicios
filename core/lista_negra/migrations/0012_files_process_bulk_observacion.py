# Generated by Django 3.2.18 on 2023-06-26 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lista_negra', '0011_alter_files_process_bulk_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='files_process_bulk',
            name='observacion',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
