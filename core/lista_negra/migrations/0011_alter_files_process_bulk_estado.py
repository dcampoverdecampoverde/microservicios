# Generated by Django 3.2.18 on 2023-06-23 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lista_negra', '0010_files_process_bulk'),
    ]

    operations = [
        migrations.AlterField(
            model_name='files_process_bulk',
            name='estado',
            field=models.CharField(max_length=50),
        ),
    ]