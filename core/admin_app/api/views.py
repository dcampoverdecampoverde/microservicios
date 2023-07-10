from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from admin_app.api.functions import FuncionesAdminApp
from admin_app.api.serializers import *
from admin_app.functions.functionsAdmin import FunctionsAdminApp
from admin_app.models import *


# <editor-fold desc="Serializadores utilizados para los parametrizadores de RolesMenu y RolesMenuAccion">

class RolesViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API que consulta tabla maestra de Roles',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                     properties={
                                         'rol_id': openapi.Schema(type=openapi.TYPE_STRING,
                                                                  description='Identificador del Rol'),
                                         'estado': openapi.Schema(type=openapi.TYPE_STRING,
                                                                  description='Estado del Rol'),
                                         'descripcion': openapi.Schema(type=openapi.TYPE_STRING,
                                                                       description='Descripcion del Rol'),
                                     }
                                     )
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'estado': openapi.Schema(type=openapi.TYPE_STRING),
                    'mensaje': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            401: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING,
                                             description="Se notifica si no tiene acceso o si el token de acceso, expiro")
                }
            )
        }
    )
    def list(self, request):
        try:
            function = FuncionesAdminApp()
            serializer = function.listaRoles()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"estado": "error",
                                  "mensaje": str(e)})


class MenuOpcionViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API que consulta tabla maestra de Menu',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                     properties={
                                         'seleccionado': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                        description='Muestra si se encuentra asignago al un Rol Determinado'),
                                         'menu_id': openapi.Schema(type=openapi.TYPE_STRING,
                                                                   description='Identificador del Menu'),
                                         'descripcion': openapi.Schema(type=openapi.TYPE_STRING,
                                                                       description='Descripcion del Menu'),
                                     }
                                     )
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'estado': openapi.Schema(type=openapi.TYPE_STRING),
                    'mensaje': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            401: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING,
                                             description="Se notifica si no tiene acceso o si el token de acceso, expiro")
                }
            )
        }
    )
    def list(self, request):
        function = FuncionesAdminApp()
        try:

            codigo_rol_seleccionado = request.GET.get("id")
            if codigo_rol_seleccionado is not None or 0:
                menu_opciones = MenuOpcion.objects.filter(estado="A")
                data_response = []
                for item_menu in menu_opciones:
                    existe_menu = RolesMenu.objects.filter(
                        Q(rol_id_id=codigo_rol_seleccionado) & Q(menu_id_id=item_menu.menu_id)).exists()
                    item_response = {
                        "seleccionado": int(existe_menu),
                        "menu_id": item_menu.menu_id,
                        "descripcion": item_menu.descripcion
                    }
                    data_response.append(item_response)

            # serializer = function.listaMenu()
            return Response(status=status.HTTP_200_OK, data=data_response)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"estado": "error",
                                  "mensaje": str(e)})


class AccionesViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API que consulta tabla maestra de Acciones',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                     properties={
                                         'accion_id': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                     description='Identificador de accion'),
                                         'estado': openapi.Schema(type=openapi.TYPE_STRING,
                                                                  description='Estado de la accion'),
                                         'descripcion': openapi.Schema(type=openapi.TYPE_STRING,
                                                                       description='Descripcion de la accion'),
                                     }
                                     )
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'estado': openapi.Schema(type=openapi.TYPE_STRING),
                    'mensaje': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            401: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING,
                                             description="Se notifica si no tiene acceso o si el token de acceso, expiro")
                }
            )
        }
    )
    def list(self, request):
        try:
            function = FuncionesAdminApp()
            serializer = function.listaAcciones()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"estado": "error",
                                  "mensaje": str(e)})


# </editor-fold>

# Esta consulta se utiliza para obtener el menu izquierdo que se visualiza en el front-end
class RolesMenuUsuarioViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API que muestra el menu de opciones asignado segun su rol configurado',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                     properties={
                                         'descripcion': openapi.Schema(type=openapi.TYPE_STRING,
                                                                       description='Descripcion del menu opcion'),
                                         'url_page': openapi.Schema(type=openapi.TYPE_STRING,
                                                                    description='Url de acceso al menu'),
                                     }
                                     )
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'estado': openapi.Schema(type=openapi.TYPE_STRING),
                    'mensaje': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            401: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING,
                                             description="Se notifica si no tiene acceso o si el token de acceso, expiro")
                }
            )
        }
    )
    def create(self, request):
        info = request.POST if request.POST else request.data if request.data else None
        function = FuncionesAdminApp()
        metodos = FunctionsAdminApp()
        try:
            # Obtengo la sesion del usuario conectado
            data_user = metodos.obtenerUsuarioSesionToken(request)

            # buscando el rol del usuario
            menu_opciones_usuario = function.consultaMenuOpciones(data_user["username"])
            return Response(status=status.HTTP_200_OK, data=menu_opciones_usuario)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"estado": "error",
                                  "mensaje": str(e)})


class RolesMenuViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API que consulta la cantidad de menu asignados por el Rol de Usuario',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                     properties={
                                         'rol': openapi.Schema(type=openapi.TYPE_STRING,
                                                               description='Descripcion del Rol'),
                                         'total_menu_asignados': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                                description='Cantidad de menu asignados'),
                                     }
                                     )
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'estado': openapi.Schema(type=openapi.TYPE_STRING),
                    'mensaje': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            401: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING,
                                             description="Se notifica si no tiene acceso o si el token de acceso, expiro")
                }
            )
        }
    )
    def list(self, request):
        try:
            function = FuncionesAdminApp()
            data_response = function.consultarMenuXRolUsuario()
            return Response(status=status.HTTP_200_OK, data=data_response)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"estado": "error",
                                  "mensaje": str(e)})

    # def retrieve(self, request, roles_id):
    #    pass

    @swagger_auto_schema(
        operation_description='API que permite asignar menu de opciones a un rol seleccionado',
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                 properties={
                                     'listado_menu': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                    description='Lista de los ID del menu opciones que se van a asignar'),
                                     'rol_id': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                              description='ID del rol seleccionado'),
                                 }
                                 )
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'estado': openapi.Schema(type=openapi.TYPE_STRING),
                    'mensaje': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'estado': openapi.Schema(type=openapi.TYPE_STRING),
                    'mensaje': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            401: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING,
                                             description="Se notifica si no tiene acceso o si el token de acceso, expiro")
                }
            )
        }
    )
    def create(self, request):
        info = request.POST if request.POST else request.data if request.data else None
        try:
            function = FuncionesAdminApp()
            data_response = function.registrarRolMenu(info, request)
            return Response(status=status.HTTP_200_OK, data=data_response)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"estado": "error",
                                  "mensaje": str(e)})

    # @extend_schema(responses=RolesMenuActualizarSerializer)
    def partial_update(self, request, pk=None):
        info = request.POST if request.POST else request.data if request.data else None
        obj_rolesmenuaccion = RolesMenu.objects.get(pk=pk)
        serializer = RolesMenuActualizarSerializer(obj_rolesmenuaccion, data=info, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class MenuAsignadoViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        try:
            info = request.POST if request.POST else request.data if request.data else None
            function = FuncionesAdminApp()
            data_response = function.listMenuXRol(info["rol"])
            return Response(status=status.HTTP_200_OK, data=data_response)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"estado": "error",
                                  "mensaje": str(e)})


class RolesMenuAccionViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    # @extend_schema(responses=RolesMenuAccionSerializer)
    def list(self, request):
        serializer = RolesMenuAccionSerializer(RolesMenuAccion.objects.all(), many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    # @extend_schema(responses=RolesMenuAccionRegistroSerializer)
    async def create(self, request):
        info = request.POST if request.POST else request.data if request.data else None
        serializer = RolesMenuAccionRegistroSerializer(data=info)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    # @extend_schema(responses=RolesMenuAccionActualizarSerializer)
    def partial_update(self, request, pk=None):
        info = request.POST if request.POST else request.data if request.data else None
        obj_rolesmenu = RolesMenuAccion.objects.get(pk=pk)
        serializer = RolesMenuAccionActualizarSerializer(obj_rolesmenu, data=info, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
