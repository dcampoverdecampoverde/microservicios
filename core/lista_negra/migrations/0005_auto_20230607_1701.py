# Generated by Django 3.2.18 on 2023-06-07 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lista_negra', '0004_alter_black_imsi_imsi'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log_aprov_eir',
            name='imsi',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='log_aprov_eir',
            name='lista',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='log_aprov_eir',
            name='operadora',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='log_aprov_eir',
            name='origen',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='log_aprov_eir',
            name='razon',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
