# Generated by Django 3.2.18 on 2023-06-23 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lista_negra', '0008_auto_20230622_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='black_imsi',
            name='imsi',
            field=models.BigIntegerField(error_messages={'unique': 'Codigo IMSI ya se encuentra registrado'}, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='log_aprov_eir',
            name='imsi',
            field=models.BigIntegerField(null=True),
        ),
    ]