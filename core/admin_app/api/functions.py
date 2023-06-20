from admin_app.api.serializers import *


class FuncionesAdmin():
    def listaRoles(self):
        serializer = RolesSerializer(Roles.objects.all(), many=True)
