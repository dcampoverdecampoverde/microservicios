# Generated by Django 3.2.18 on 2023-06-11 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0006_alter_acciones_accion_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roles',
            name='rol_id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
