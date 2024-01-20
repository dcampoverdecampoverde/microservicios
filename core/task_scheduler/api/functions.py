from rest_framework_simplejwt.authentication import JWTAuthentication

class FuncionesGenerales:
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

