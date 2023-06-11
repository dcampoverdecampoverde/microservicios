from rest_framework import serializers
from lista_negra.models import *

class ListaNegraRegistroSerializer(serializers.ModelSerializer):
    operadora = serializers.SerializerMethodField()
    lista = serializers.SerializerMethodField()
    razon = serializers.SerializerMethodField()
    usuario_id = serializers.SerializerMethodField()
    class Meta:
        model=black_imsi
        fields=(
            'imsi','source','operadora','lista','razon','usuario_id'
        )
    def get_operadora(self, obj):
        return obj
    def get_lista(self, obj):
        return obj
    def get_razon(self, obj):
        return obj
    def get_usuario_id(self, obj):
        return obj

class ListaNegraEliminarSerializer(serializers.ModelSerializer):
    class Meta:
        model=black_imsi
        fields =[
            'imsi',
            'source',
            'register',
            ]

class ListaNegraSerializer(serializers.ModelSerializer):
    class Meta:
        model=black_imsi
        fields =[
            'imsi',
            'source',
            'register',
            ]

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model=log_aprov_eir
        fields =[
            'accion',
            'imsi',
            'operadora',
            'lista',
            'razon',
            'origen',
            'fecha_bitacora',
            'descripcion',
            'usuario_descripcion',
            ]