from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.authentication import JWTAuthentication

from users_system.models import Usuario


class FuncionesGenerales:
    def obtenerUsuarioSesionToken(self, request):
        JWT_authenticator = JWTAuthentication()
        response = JWT_authenticator.authenticate(request)
        user, token = response
        usuario_descripcion = user.username
        usuario_id = token.payload["user_id"]
        data_response = {
            'username': usuario_descripcion,
            'id': usuario_id,
            'superuser': user.is_superuser
        }
        return data_response

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

    def switchDiasSemana(self, valor):
        if valor == "0":
            return "Lunes"
        if valor == "1":
            return "Martes"
        if valor == "2":
            return "Miercoles"
        if valor == "3":
            return "Jueves"
        if valor == "4":
            return "Viernes"
        if valor == "5":
            return "Sabado"
        if valor == "6":
            return "Domingo"
