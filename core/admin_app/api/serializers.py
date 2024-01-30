from rest_framework import serializers

from admin_app.models import *


class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = (
            'rol_id', 'estado', 'descripcion'
        )


class MenuOpcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuOpcion
        fields = (
            'menu_id',
            'estado',
            'descripcion'
        )


class AccionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acciones
        fields = (
            'accion_id',
            'estado',
            'descripcion'

        )


# Serializador que permite registrar un nuevo registro
class RolesMenuRegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolesMenu
        fields = (
            'rolmenu_id',
            'estado',
            'rol_id',
            'rol_descripcion',
            'menu_id',
            'menu_descripcion',
            'fecha_creacion',
            'usuario_creacion',
            'ip_creacion')


# Serializador que permite consultar listado
class RolesMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolesMenu
        fields = [
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


# Serializador que permite actualizar un registro
class RolesMenuActualizarSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolesMenu
        fields = [
            'estado',
            'rol_id',
            'rol_descripcion',
            'menu_id',
            'menu_descripcion',
            'fecha_modificacion',
            'usuario_modificacion',
            'ip_modificacion']


class RolesMenuAccionRegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolesMenuAccion
        fields = [
            'rolmenuaccion_id',
            'estado',
            'rolmenu_id',
            'accion_id',
            'usuario_creacion',
            'ip_creacion'
        ]


class RolesMenuAccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolesMenuAccion
        fields = [
            'rolmenuaccion_id',
            'estado',
            'rolmenu_id',
            'accion_id',
            'usuario_creacion',
            'ip_creacion',
            'fecha_modificacion',
            'usuario_modificacion',
            'ip_modificacion'
        ]


class RolesMenuAccionActualizarSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolesMenuAccion
        fields = [
            'estado',
            'rolmenu_id',
            'accion_id',
            'fecha_modificacion',
            'usuario_modificacion',
            'ip_modificacion'
        ]


class MenuOpcionPadreSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuOpcionPadre
        fields = (
            'menu_padre_id',
            'estado',
            'descripcion'

        )
