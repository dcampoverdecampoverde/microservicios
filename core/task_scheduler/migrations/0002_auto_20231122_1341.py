# Generated by Django 3.2.18 on 2023-11-22 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_scheduler', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programador_jobs',
            name='dias_semana',
            field=models.CharField(max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='programador_jobs',
            name='horario_rango',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
