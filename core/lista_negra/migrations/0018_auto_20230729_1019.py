# Generated by Django 3.2.18 on 2023-07-29 15:19

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('lista_negra', '0017_auto_20230728_1723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imei_imsi_block',
            name='fecha',
            field=models.DateField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='imei_imsi_block',
            name='imei',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='imei_imsi_block',
            name='imsi',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]