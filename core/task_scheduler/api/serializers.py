from rest_framework import serializers

from task_scheduler.models import *


class TareaJobRegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = programador_jobs
        fields = [
            'estado',
            'nombre_tarea',
            'dias_semana',
            'tipo_horario',
            'horario_rango',
            'job_descripcion',
            'job_ejecutar',
            'emails_notificacion',
            'usuario_registro',
            'terminal_registro'
        ]


class TareaJobListaSerializer(serializers.ModelSerializer):
    fecha_registro = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
    fecha_modificacion = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
    fecha_ultima_ejecucion = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
    dias_semana_numeros = serializers.SerializerMethodField()

    class Meta:
        model = programador_jobs
        fields = [
            'id',
            'estado',
            'estado_ejecucion',
            'nombre_tarea',
            'dias_semana',
            'dias_semana_numeros',
            'tipo_horario',
            'horario_rango',
            'job_descripcion',
            'job_ejecutar',
            'emails_notificacion',
            'fecha_ultima_ejecucion',
            'observaciones',
            'usuario_registro',
            'terminal_registro',
            'fecha_registro',
            'usuario_modificacion',
            'terminal_modificacion',
            'fecha_modificacion'
        ]

    def get_dias_semana_numeros(self, obj):
        return obj


class TareaJobActualizarSerializer(serializers.ModelSerializer):
    class Meta:
        model = programador_jobs
        fields = [
            'estado',
            'tipo_horario',
            'dias_semana',
            'horario_rango',
            'emails_notificacion',
            'usuario_modificacion',
            'terminal_modificacion',
            'fecha_modificacion'

        ]


class TareaJobActualizarEjecucionSerializer(serializers.ModelSerializer):
    class Meta:
        model = programador_jobs
        fields = [
            'estado_ejecucion',
            'usuario_modificacion',
            'terminal_modificacion',
            'fecha_modificacion'
            'fecha_ultima_ejecucion'
        ]
