# Generated by Django 3.2.18 on 2023-06-28 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lista_negra', '0013_auto_20230626_1126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log_aprov_eir',
            name='imsi',
            field=models.BigIntegerField(),
        ),
        migrations.AddIndex(
            model_name='log_aprov_eir',
            index=models.Index(fields=['imsi'], name='lista_negra_imsi_68f3b0_idx'),
        ),
    ]
