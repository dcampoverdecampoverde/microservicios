from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from admin_app.api.functions import FuncionesAdminApp
from admin_app.api.serializers import *
from admin_app.models import *


# <editor-fold desc="Serializadores utilizados para los parametrizadores de RolesMenu y RolesMenuAccion">

class RolesViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

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

    def list(self, request):
        try:
            function = FuncionesAdminApp()
            serializer = function.listaMenu()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"estado": "error",
                                  "mensaje": str(e)})


class AccionesViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

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

    def create(self, request):
        info = request.POST if request.POST else request.data if request.data else None
        function = FuncionesAdminApp()
        try:
            # buscando el rol del usuario
            menu_opciones_usuario = function.consultaMenuOpciones(info["usuario_id"])
            return Response(status=status.HTTP_200_OK, data=menu_opciones_usuario)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"estado": "error",
                                  "mensaje": str(e)})


class RolesMenuViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

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

    # @extend_schema(responses=RolesMenuRegistroSerializer)
    def create(self, request):
        info = request.POST if request.POST else request.data if request.data else None
        try:
            function = FuncionesAdminApp()
            data_response = function.registrarRolMenu(info)
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
