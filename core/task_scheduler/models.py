from django.db import models


class programador_jobs(models.Model):
    id = models.BigAutoField(primary_key=True)
    estado = models.CharField(max_length=1, null=True)
    estado_ejecucion = models.CharField(max_length=50, null=True)
    nombre_tarea = models.CharField(max_length=100)
    dias_semana = models.CharField(max_length=300, null=True)
    tipo_horario = models.CharField(max_length=50, null=True)
    horario_rango = models.CharField(max_length=50, null=True)
    job_descripcion = models.CharField(max_length=100, null=True)
    job_ejecutar = models.CharField(max_length=200, null=True)
    emails_notificacion = models.CharField(max_length=500, null=True)
    fecha_ultima_ejecucion = models.DateTimeField(null=True)
    observaciones = models.CharField(max_length=500, null=True, blank=True)
    usuario_registro = models.CharField(max_length=20, null=True)
    terminal_registro = models.CharField(max_length=15, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True, null=True)
    usuario_modificacion = models.CharField(max_length=20, null=True)
    terminal_modificacion = models.CharField(max_length=15, null=True)
    fecha_modificacion = models.DateTimeField(null=True)
    tipo = models.CharField(max_length=10, null=True, blank=True)
    num_veces = models.IntegerField(null=True, blank=True)
