# Generated by Django 3.2.18 on 2023-07-03 22:07

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('lista_negra', '0015_log_aprov_eir_ip_transaccion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='files_process_bulk',
            name='fecha_registro',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='log_aprov_eir',
            name='fecha_bitacora',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]