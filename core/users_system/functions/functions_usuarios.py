from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.authentication import JWTAuthentication

from users_system.models import Usuario


class FunctionsUsuario():
    def obtenerUsuarioSesionToken(self, request):
        JWT_authenticator = JWTAuthentication()
        response = JWT_authenticator.authenticate(request)
        user, token = response
        usuario_descripcion = user.username
        usuario_id = token.payload["user_id"]
        data_response = {
            'username': usuario_descripcion,
            'id': usuario_id
        }
        return data_response

    # def obtenerIDUsuarioBaseReplica(self, usuario_sesion):
    #    usuario_id = 0
    #    try:
    #        obj_usuario = Usuario.objects.using('replica').filter(username=usuario_sesion).first()
    #        if obj_usuario is not None:
    #            usuario_id = obj_usuario.usuario_id
    #    except Exception as e:
    #        usuario_id = 0
    #    return usuario_id

    def validarUsuarioClaveExisten(self, user, pwd):
        if user is None or pwd is None:
            return "No se han encontrado los parametros (X-User y/o X-pwd) valor autentificarse"

        if user.strip() == '':
            return "El parametro X-User no tiene valor"

        if pwd.strip() == '':
            return "El parametro X-Pwd no tiene valor"

        data_usuario = Usuario.objects.filter(username=user).first()
        if data_usuario is None:
            return "Usuario no se encontro registrado en el sistema"
        else:
            if check_password(pwd, data_usuario.password):
                return "ok"
            else:
                return "Clave ingresada es invalida"

    def obtenerDireccionIpRemota(self, request):
        user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if user_ip:
            ip_transaccion = user_ip.split(',')[0]
        else:
            ip_transaccion = request.META.get('REMOTE_ADDR')

        return ip_transaccion
