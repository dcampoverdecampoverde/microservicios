from django.db import models


class Roles(models.Model):
    rol_id = models.BigAutoField(primary_key=True)
    estado = models.CharField(max_length=1, default="A")
    descripcion = models.CharField(max_length=50)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.CharField(max_length=15)
    ip_creacion = models.CharField(max_length=20)
    fecha_modificacion = models.DateTimeField(null=True, default=None, blank=True)
    usuario_modificacion = models.CharField(max_length=15, default=None, blank=True)
    ip_modificacion = models.CharField(max_length=20, default=None, blank=True)

class MenuOpcion(models.Model):
    menu_id = models.BigAutoField(primary_key=True)
    estado = models.CharField(max_length=1)
    descripcion = models.CharField(max_length=50)
    url_page = models.CharField(max_length=100)
    id_componente_html = models.CharField(max_length=50)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.CharField(max_length=15)
    ip_creacion = models.CharField(max_length=20)
    fecha_modificacion = models.DateTimeField(null=True, default=None, blank=True)
    usuario_modificacion = models.CharField(max_length=15, default=None, blank=True)
    ip_modificacion = models.CharField(max_length=20, default=None, blank=True)

class Acciones(models.Model):
    accion_id = models.BigAutoField(primary_key=True)
    estado = models.CharField(max_length=1)
    descripcion = models.CharField(max_length=50)
    id_componente_html = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.CharField(max_length=15)
    ip_creacion = models.CharField(max_length=20)
    fecha_modificacion = models.DateTimeField(null=True, default=None, blank=True)
    usuario_modificacion = models.CharField(max_length=15, default=None, blank=True)
    ip_modificacion = models.CharField(max_length=20, default=None, blank=True)

class RolesMenu(models.Model):
    rolmenu_id = models.BigAutoField(primary_key=True)
    estado = models.CharField(max_length=1)
    rol_id = models.ForeignKey(Roles, on_delete=models.SET_NULL, null=True)
    rol_descripcion = models.CharField(max_length=50, null=True)
    menu_id = models.ForeignKey(MenuOpcion, on_delete=models.SET_NULL, null=True)
    menu_descripcion = models.CharField(max_length=50)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.CharField(max_length=15)
    ip_creacion = models.CharField(max_length=20)
    fecha_modificacion = models.DateTimeField(null=True, default=None, blank=True)
    usuario_modificacion = models.CharField(max_length=15, null=True, default=None, blank=True)
    ip_modificacion = models.CharField(max_length=20, null=True, default=None, blank=True)

class RolesMenuAccion(models.Model):
    rolmenuaccion_id = models.BigAutoField(primary_key=True)
    estado = models.CharField(max_length=1)
    rolmenu_id = models.ForeignKey(RolesMenu, on_delete=models.SET_NULL, null=True)
    accion_id = models.ForeignKey(Acciones, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.CharField(max_length=15)
    ip_creacion = models.CharField(max_length=20)
    fecha_modificacion = models.DateTimeField(null=True, default=None, blank=True)
    usuario_modificacion = models.CharField(max_length=15, null=True, default=None, blank=True)
    ip_modificacion = models.CharField(max_length=20, null=True, default=None, blank=True)
