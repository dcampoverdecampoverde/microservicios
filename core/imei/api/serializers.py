from rest_framework import serializers

from imei.models import *


class ImeiRegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = black_gray_list
        fields = (
            'imei',
        )


class ImeiEliminarSerializer(serializers.ModelSerializer):
    class Meta:
        model = black_gray_list
        fields = [
            'imei',
            'list',
            'operator_code',
        ]


class ImeiConsultarSerializer(serializers.ModelSerializer):
    class Meta:
        model = black_gray_list
        fields = [
            'imei',
            'list',
            'last_imsi',
            'operator_code',
            'actvt_date',
            'actvt_obs',
            'code',
        ]


class LogImeiSerializer(serializers.ModelSerializer):
    fecha_bitacora = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')

    class Meta:
        model = log_imei_eir
        fields = [
            'accion',
            'imei',
            'operadora',
            'lista',
            'razon',
            'origen',
            'fecha_bitacora',
            'descripcion',
            'usuario_descripcion',
            'ip_transaccion',
        ]


class ImeiMasivoSerializer(serializers.ModelSerializer):
    # Con esto se le da formato a los campos que son DateTimeField
    fecha_archivo_procesando = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
    fecha_archivo_finalizado = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
    fecha_actualizacion = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
    fecha_registro = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')

    class Meta:
        model = files_imei_bulk
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


class ImeiMasivoRegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = files_imei_bulk
        fields = [
            'estado',
            'archivo_csv',
            'estado',
            'usuario_registro',
            'ip_registro'
        ]


class ImeiMasivoActualizarSerializer(serializers.ModelSerializer):
    class Meta:
        model = files_imei_bulk
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
