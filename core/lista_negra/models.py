from django.db import models
from django.utils.timezone import now

from users_system.models import Usuario


class black_imsi(models.Model):
    imsi = models.BigIntegerField(primary_key=True, error_messages={'unique': 'Codigo IMSI ya se encuentra registrado'})
    source = models.CharField(max_length=50, null=True)
    register = models.DateTimeField(auto_now_add=True, null=True)


class log_aprov_eir(models.Model):
    log_id = models.BigAutoField(primary_key=True)
    estado = models.CharField(max_length=1)
    accion = models.CharField(max_length=50)
    imsi = models.BigIntegerField()
    operadora = models.CharField(max_length=50, null=True)  # la telefonica que envia el codigo
    lista = models.CharField(max_length=50, null=True)  # que tipo de lista es, blanca, negra
    razon = models.CharField(max_length=1000, null=True)  # motivo por el cual fue enviado a lista negra
    origen = models.CharField(max_length=50, null=True)  # origen: si vino del front-end, proceso masivo
    fecha_bitacora = models.DateTimeField(default=now)
    descripcion = models.CharField(max_length=500, null=True)
    usuario_id = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    usuario_descripcion = models.CharField(max_length=50, null=True)
    ip_transaccion = models.CharField(max_length=20, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['imsi', ]),
        ]


class files_process_bulk(models.Model):
    id = models.BigAutoField(primary_key=True)
    estado = models.CharField(max_length=50)
    archivo_csv = models.CharField(max_length=50)
    total_encontrado = models.IntegerField(null=True, blank=True)
    total_error = models.IntegerField(null=True, blank=True)
    total_ok = models.IntegerField(null=True, blank=True)
    observacion = models.CharField(null=True, blank=True, max_length=100)
    fecha_archivo_procesando = models.DateTimeField(null=True, blank=True)
    fecha_archivo_finalizado = models.DateTimeField(null=True, blank=True)
    fecha_registro = models.DateTimeField(default=now)
    usuario_registro = models.CharField(max_length=20)
    ip_registro = models.CharField(max_length=50)
    fecha_actualizacion = models.DateTimeField(null=True, blank=True)
    usuario_actualizacion = models.CharField(max_length=50, blank=True, null=True)
    ip_actualizacion = models.CharField(max_length=50, blank=True, null=True)
