from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from admin_app.models import Roles, RolesMenu, MenuOpcion, Acciones
from admin_app.api.serializers import *

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

class RolesMenuViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    def list(self, request):
        serializer = RolesMenuSerializer(RolesMenu.objects.all(), many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def retrieve(self, request, roles_id):
        pass

    def create(self, request):
        info = request.POST if request.POST else request.data if request.data else None
        serializer = RolesMenuRegistroSerializer(data=info)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def partial_update(self, request, pk=None):
        info = request.POST if request.POST else request.data if request.data else None
        obj_rolesmenu = RolesMenu.objects.get(pk=pk)
        serializer = RolesMenuActualizarSerializer(obj_rolesmenu, data=info, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)