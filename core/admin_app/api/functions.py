from django.db.models import Q

from admin_app.api.serializers import *
from admin_app.functions.functionsAdmin import FunctionsAdminApp
from users_system.models import Usuario


class FuncionesAdminApp():
    def listaRoles(self):
        serializer = RolesSerializer(Roles.objects.all(), many=True)
        return serializer

    def listaMenu(self):
        serializer = MenuOpcionSerializer(MenuOpcion.objects.all(), many=True)
        return serializer

    def listaAcciones(self):
        serializer = AccionesSerializer(Acciones.objects.all(), many=True)
        return serializer

    def consultaMenuOpciones(self, usuario_id):

        usuario_login = Usuario.objects.get(username=usuario_id)
        menu_opciones_usuario = []

        if usuario_login.rol_id is None:
            menu_opcion = MenuOpcion.objects.filter(estado="A")
            for item_opcion in menu_opcion:
                item_menu = {
                    "descripcion": item_opcion.descripcion,
                    "url_page": item_opcion.url_page
                }
                menu_opciones_usuario.append(item_menu)
        else:
            menu_encontrados = RolesMenu.objects.filter(
                Q(estado="A") & Q(rol_id_id=usuario_login.rol_id_id))
            for item_rolmenu in menu_encontrados:
                menu = MenuOpcion.objects.get(menu_id=item_rolmenu.menu_id_id)
                data_menu_encontrado = {
                    "descripcion": menu.descripcion,
                    "url_page": menu.url_page
                }
                menu_opciones_usuario.append(data_menu_encontrado)

        return menu_opciones_usuario

    def consultarMenuXRolUsuario(self):
        data_response = []
        lista_rol = Roles.objects.filter(estado="A")
        for item in lista_rol:
            total_menu = RolesMenu.objects.filter(
                Q(estado__contains="A") & Q(rol_descripcion=item.descripcion)).count()
            data_encontrado = {
                "rol": item.descripcion,
                "total_menu_asignados": total_menu
            }
            data_response.append(data_encontrado)
        return data_response

    def listMenuXRol(self, rol_usuario):
        data_response = []
        menu_encontrado = RolesMenu.objects.filter(
            Q(estado__contains="A") & Q(rol_descripcion=rol_usuario))
        for item in menu_encontrado:
            data_encontrado = {
                "menu_id": item.menu_id_id,
                "menu_descripcion": item.menu_descripcion
            }
            data_response.append(data_encontrado)

        return data_response

    def registrarRolMenu(self, request_data, request):

        metodos = FunctionsAdminApp()
        # obtengo la info del usuario conectado
        data_user = metodos.obtenerUsuarioSesionToken(request)

        # obtengo la direccion ip remota
        ip_transaccion = metodos.obtenerDireccionIpRemota(request)

        # elimino los menus asignados al rol escogido
        RolesMenu.objects.filter(rol_id_id=request_data["rol_id"]).delete()

        for item in request_data["listado_menu"]:
            obj_menu = MenuOpcion.objects.get(menu_id=item["menu_id"])
            obj_rol = Roles.objects.get(rol_id=request_data["rol_id"])
            if obj_menu is not None and obj_rol is not None:
                data_menu = {
                    'estado': 'A',
                    'rol_id': request_data["rol_id"],
                    'rol_descripcion': obj_rol.descripcion,
                    'menu_id': item["menu_id"],
                    'menu_descripcion': obj_menu.descripcion,
                    'usuario_creacion': data_user["username"],
                    'ip_creacion': ip_transaccion
                }
            serializer = RolesMenuRegistroSerializer(data=data_menu)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

        data_response = {
            "estado": 'ok',
            'mensaje': 'operacion correcta'
        }
        return data_response
