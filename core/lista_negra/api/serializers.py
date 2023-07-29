from rest_framework import serializers

from lista_negra.models import *


class ListaNegraRegistroSerializer(serializers.ModelSerializer):
    operadora = serializers.SerializerMethodField()
    lista = serializers.SerializerMethodField()
    razon = serializers.SerializerMethodField()
    usuario_id = serializers.SerializerMethodField()

    class Meta:
        model = black_imsi
        fields = (
            'imsi', 'source', 'operadora', 'lista', 'razon', 'usuario_id'
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
        model = black_imsi
        fields = [
            'imsi',
            'source',
            'register',
        ]


class ListaNegraSerializer(serializers.ModelSerializer):
    register = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')

    class Meta:
        model = black_imsi
        fields = [
            'imsi',
            'source',
            'register',
        ]


class LogSerializer(serializers.ModelSerializer):
    fecha_bitacora = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')

    class Meta:
        model = log_aprov_eir
        fields = [
            'accion',
            'imsi',
            'operadora',
            'lista',
            'razon',
            'origen',
            'fecha_bitacora',
            'descripcion',
            'usuario_descripcion',
            'ip_transaccion',
        ]


class FileProcessSerializer(serializers.ModelSerializer):
    # Con esto se le da formato a los campos que son DateTimeField
    fecha_archivo_procesando = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
    fecha_archivo_finalizado = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
    fecha_actualizacion = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
    fecha_registro = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')

    class Meta:
        model = files_process_bulk
        fields = [
            'id',
            'estado',
            'archivo_csv',
            'total_encontrado',
            'total_error',
            'total_ok',
            'observacion',
            'fecha_archivo_procesando',
            'fecha_archivo_finalizado',
            'fecha_registro',
            'usuario_registro',
            'ip_registro',
            'fecha_actualizacion',
            'usuario_actualizacion',
            'ip_actualizacion',
        ]


class FileProcessRegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = files_process_bulk
        fields = [
            'estado',
            'archivo_csv',
            'estado',
            'usuario_registro',
            'ip_registro'
        ]


class FileProcessActualizarSerializer(serializers.ModelSerializer):
    class Meta:
        model = files_process_bulk
        fields = [
            'estado',
            'total_encontrado',
            'total_error',
            'total_ok',
            'observacion',
            'fecha_archivo_procesando',
            'fecha_archivo_finalizado',
            'fecha_actualizacion',
            'usuario_actualizacion',
            'ip_actualizacion',
        ]


class TdrSerializer(serializers.ModelSerializer):
    fecha = serializers.DateField(format='%d/%m/%Y')
    hora = serializers.TimeField(format='%H:%M:%S')

    class Meta:
        model = imei_imsi_block
        fields = [
            'id',
            'fecha',
            'hora',
            'central',
            'imei',
            'imsi',
            'codigo1',
            'codigo2'
        ]
