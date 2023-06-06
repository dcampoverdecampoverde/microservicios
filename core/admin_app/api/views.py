import coreschema
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from admin_app.models import *
from admin_app.api.serializers import *

#<editor-fold desc="Serializadores utilizados para los parametrizadores de RolesMenu y RolesMenuAccion">

class RolesViewSet(ViewSet):
    def list(self, request):
        serializer = RolesSerializer(Roles.objects.all(), many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

class MenuOpcionViewSet(ViewSet):
    def list(self, request):
        serializer = MenuOpcionSerializer(MenuOpcion.objects.all(), many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

class AccionesViewSet(ViewSet):
    def list(self, request):
        serializer = AccionesSerializer(Acciones.objects.all(), many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

#</editor-fold>

class RolesMenuViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=RolesMenuSerializer)
    def list(self, request):
        serializer = RolesMenuSerializer(RolesMenu.objects.all(), many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    #def retrieve(self, request, roles_id):
    #    pass

    @extend_schema(responses=RolesMenuRegistroSerializer)
    def create(self, request):
        info = request.POST if request.POST else request.data if request.data else None
        serializer = RolesMenuRegistroSerializer(data=info)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @extend_schema(responses=RolesMenuActualizarSerializer)
    def partial_update(self, request, pk=None):
        info = request.POST if request.POST else request.data if request.data else None
        obj_rolesmenuaccion = RolesMenu.objects.get(pk=pk)
        serializer = RolesMenuActualizarSerializer(obj_rolesmenuaccion, data=info, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

class RolesMenuAccionViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=RolesMenuAccionSerializer)
    def list(self, request):
        serializer = RolesMenuAccionSerializer(RolesMenuAccion.objects.all(), many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @extend_schema(responses=RolesMenuAccionRegistroSerializer)
    async def create(self, request):
        info = request.POST if request.POST else request.data if request.data else None
        serializer = RolesMenuAccionRegistroSerializer(data=info)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @extend_schema(responses=RolesMenuAccionActualizarSerializer)
    def partial_update(self, request, pk=None):
        info = request.POST if request.POST else request.data if request.data else None
        obj_rolesmenu = RolesMenuAccion.objects.get(pk=pk)
        serializer = RolesMenuAccionActualizarSerializer(obj_rolesmenu, data=info, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)