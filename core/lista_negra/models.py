from django.db import models
from users_system.models import Usuario

class black_imsi(models.Model):
    imsi = models.CharField(max_length=15, primary_key=True, error_messages={'unique':'Codigo IMSI ya se encuentra registrado'})
    source = models.CharField(max_length=50, null=True)
    register = models.DateTimeField(auto_now_add=True, null=True)

class log_aprov_eir(models.Model):
    log_id = models.BigAutoField(primary_key=True)
    estado = models.CharField(max_length=1)
    accion = models.CharField(max_length=50)
    imsi = models.CharField(max_length=15, null=True)
    operadora = models.CharField(max_length=50, null=True) #la telefonica que envia el codigo
    lista = models.CharField(max_length=50, null=True) #que tipo de lista es, blanca, negra
    razon = models.CharField(max_length=1000, null=True) #motivo por el cual fue enviado a lista negra
    origen = models.CharField(max_length=50, null=True) #origen: si vino del front-end, proceso masivo
    fecha_bitacora = models.DateTimeField(auto_now_add=True)
    descripcion = models.CharField(max_length=500, null=True)
    usuario_id = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    usuario_descripcion = models.CharField(max_length=50, null=True)
