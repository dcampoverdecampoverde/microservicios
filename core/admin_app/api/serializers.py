from rest_framework import serializers
from admin_app.models import RolesMenu, Roles, MenuOpcion, Acciones

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model=Roles
        fields=(
            'rol_id','estado','descripcion'
        )

class MenuOpcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuOpcion
        fields=(
            'menu_id',
            'estado',
            'descripcion'
        )

class AccionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acciones
        fields=(
            'accion_id',
            'estado',
            'descripcion'

        )

class RolesMenuRegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolesMenu
        fields=(
            'rolmenu_id',
            'estado',
            'rol_id',
            'rol_descripcion',
            'menu_id',
            'menu_descripcion',
            'fecha_creacion',
            'usuario_creacion',
            'ip_creacion')


class RolesMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model=RolesMenu
        fields =[
            'rolmenu_id',
            'estado',
            'rol_id_id',
            'rol_descripcion',
            'menu_id_id',
            'menu_descripcion',
            'fecha_creacion',
            'usuario_creacion',
            'ip_creacion',
            'fecha_modificacion',
            'usuario_modificacion',
            'ip_modificacion']

class RolesMenuActualizarSerializer(serializers.ModelSerializer):
    class Meta:
        model=RolesMenu
        fields =[
            'estado',
            'rol_id',
            'rol_descripcion',
            'menu_id',
            'menu_descripcion',
            'fecha_modificacion',
            'usuario_modificacion',
            'ip_modificacion']