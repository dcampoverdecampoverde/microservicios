from django.db import models
from django.contrib.auth.models import AbstractUser
from admin_app.models import Roles

class Usuario(AbstractUser):
    usuario_id = models.BigAutoField(primary_key=True)
    #rol_id = models.ForeignKey(Roles, on_delete=models.SET_NULL, null=True)
    #rol_descripcion = models.CharField(max_length=50, null=True)
    fecha_modificacion = models.DateTimeField(null=True)
    usuario_modificacion = models.CharField(max_length=15, null=True)
    ip_modificacion = models.CharField(max_length=20, null=True)
    rol_id = models.ForeignKey(Roles, on_delete=models.SET_NULL, null=True)
    rol_descripcion = models.CharField(max_length=50, null=True)
