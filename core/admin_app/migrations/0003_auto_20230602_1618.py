# Generated by Django 3.2.18 on 2023-06-02 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0002_alter_roles_estado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acciones',
            name='fecha_modificacion',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='acciones',
            name='ip_modificacion',
            field=models.CharField(default=None, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='acciones',
            name='usuario_modificacion',
            field=models.CharField(default=None, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='menuopcion',
            name='fecha_modificacion',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='menuopcion',
            name='ip_modificacion',
            field=models.CharField(default=None, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='menuopcion',
            name='usuario_modificacion',
            field=models.CharField(default=None, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='roles',
            name='fecha_modificacion',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='roles',
            name='ip_modificacion',
            field=models.CharField(default=None, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='roles',
            name='usuario_modificacion',
            field=models.CharField(default=None, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='rolesmenu',
            name='fecha_modificacion',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='rolesmenu',
            name='ip_modificacion',
            field=models.CharField(default=None, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='rolesmenu',
            name='usuario_modificacion',
            field=models.CharField(default=None, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='rolesmenuaccion',
            name='fecha_modificacion',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='rolesmenuaccion',
            name='ip_modificacion',
            field=models.CharField(default=None, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='rolesmenuaccion',
            name='usuario_modificacion',
            field=models.CharField(default=None, max_length=15, null=True),
        ),
    ]
