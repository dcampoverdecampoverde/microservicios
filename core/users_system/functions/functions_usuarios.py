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

    def obtenerIDUsuarioBaseReplica(self, usuario_sesion):
        usuario_id = 0
        try:
            obj_usuario = Usuario.objects.using('replica').filter(username=usuario_sesion).first()
            if obj_usuario is not None:
                usuario_id = obj_usuario.usuario_id
        except Exception as e:
            usuario_id = 0
        return usuario_id

    def obtenerDireccionIpRemota(self, request):
        user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if user_ip:
            ip_transaccion = user_ip.split(',')[0]
        else:
            ip_transaccion = request.META.get('REMOTE_ADDR')

        return ip_transaccion
