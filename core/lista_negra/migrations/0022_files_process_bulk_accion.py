# Generated by Django 3.2.18 on 2024-01-20 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lista_negra', '0021_user_api_actions'),
    ]

    operations = [
        migrations.AddField(
            model_name='files_process_bulk',
            name='accion',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
    ]