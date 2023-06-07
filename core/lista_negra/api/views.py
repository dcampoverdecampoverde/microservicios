from drf_yasg.openapi import FORMAT_DATE
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from lista_negra.models import *
from lista_negra.api.serializers import *
class ListaNegraViewSet(ViewSet):
    #permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['imsi','origen','usuario_id'],
            properties={
                'imsi': openapi.Schema(type=openapi.TYPE_STRING,
                                        description="Codigo IMSI que se va registrar",
                                        max_length=15),
                'operadora': openapi.Schema(type=openapi.TYPE_STRING,
                                       description="Se reciben valores {'claro','telefonica','cnt','otros' }",
                                       max_length=15),
                'lista': openapi.Schema(type=openapi.TYPE_STRING,
                                       description="Se reciben valores {'blanca','gris','negra'}",
                                       max_length=10),
                'razon': openapi.Schema(type=openapi.TYPE_STRING,
                                       description="Descripcion cual fue el motivo del bloqueo del codigo IMSI",
                                       max_length=1000),
                'origen': openapi.Schema(type=openapi.TYPE_STRING,
                                       description="Se reciben los siguientes valores: {'api','front','bulk'}",
                                       max_length=10),
                'usuario_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                       description="Codigo de usuario que debe estar registrado en el sistema y con permisos para ingresar IMSI")
                #'visit_at': openapi.Schema(type=openapi.TYPE_STRING,
                #                           format=FORMAT_DATE)
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'store': openapi.Schema(type=openapi.TYPE_STRING,
                                            max_length=255),
                    'has_milk': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                }
            )
        }
    )
    def create(self, request):
        info = request.POST if request.POST else request.data if request.data else None
        if len(info["imsi"]) <15 or len(info["imsi"]) >16:
            log_aprov_eir.objects.create(
                estado="A",
                accion="Ingreso",
                imsi=info["imsi"],
                operadora=info["operadora"],
                lista=info["lista"],
                razon=info["razon"],
                origen=info["source"],
                descripcion="error: El codigo IMSI tiene una longitud incorrecta",
                usuario_id=info["usuario_id"]
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": "El codigo IMSI tiene una longitud incorrecta"})

        serializer = ListaNegraRegistroSerializer(data=info)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            log_aprov_eir.objects.create(
                estado="A",
                accion="Ingreso",
                imsi=info["imsi"],
                operadora=info["operadora"],
                lista=info["lista"],
                razon=info["razon"],
                origen=info["source"],
                descripcion=None,
                usuario_id = info["usuario_id"]
            )
            return Response(status=status.HTTP_200_OK, data={"estado": "ok", "mensaje": "operacion correcta"})
        else:
            log_aprov_eir.objects.create(
                estado="A",
                accion="Ingreso",
                imsi=info["imsi"],
                operadora=info["operadora"],
                lista=info["lista"],
                razon=info["razon"],
                origen=info["source"],
                descripcion=serializer.errors,
                usuario_id=info["usuario_id"]
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    def retrieve(self, request, pk=None):
        info = request.POST if request.POST else request.data if request.data else None
        if len(info["imsi"]) <15 or len(info["imsi"]) >16:
            log_aprov_eir.objects.create(
                estado="A",
                accion="Ingreso",
                imsi=info["imsi"],
                operadora=info["operadora"],
                lista=info["lista"],
                razon=info["razon"],
                origen=info["source"],
                descripcion="error: El codigo IMSI tiene una longitud incorrecta",
                usuario_id=info["usuario_id"]
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": "El codigo IMSI tiene una longitud incorrecta"})

        try:
            serializer = ListaNegraSerializer(black_imsi.objects.get(pk=pk))
            log_aprov_eir.objects.create(
                estado="A",
                accion="Consulta",
                imsi=info["imsi"],
                operadora=info["operadora"],
                lista=info["lista"],
                razon=info["razon"],
                origen=info["source"],
                descripcion=None,
                usuario_id=info["usuario_id"]
            )
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except black_imsi.DoesNotExist as e:
            log_aprov_eir.objects.create(
                estado="A",
                accion="Consulta",
                imsi=info["imsi"],
                operadora=info["operadora"],
                lista=info["lista"],
                razon=info["razon"],
                origen=info["source"],
                descripcion="Codigo Imsi NO Existe",
                usuario_id=info["usuario_id"]
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": "Codigo Imsi NO Existe"})



    def destroy(self, request, *args, **kwargs):
        info = request.POST if request.POST else request.data if request.data else None
        if len(info["imsi"]) <15 or len(info["imsi"]) >16:
            log_aprov_eir.objects.create(
                estado="A",
                accion="Ingreso",
                imsi=info["imsi"],
                operadora=info["operadora"],
                lista=info["lista"],
                razon=info["razon"],
                origen=info["source"],
                descripcion="error: El codigo IMSI tiene una longitud incorrecta",
                usuario_id=info["usuario_id"]
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": "El codigo IMSI tiene una longitud incorrecta"})
        try:
            obj_listanegra = black_imsi.objects.get(pk=info["imsi"])
            obj_listanegra.delete()
            log_aprov_eir.objects.create(
                estado="A",
                accion="Eliminacion",
                imsi=info["imsi"],
                operadora=info["operadora"],
                lista=info["lista"],
                razon=info["razon"],
                origen=info["source"],
                descripcion=None,
                usuario_id=info["usuario_id"]
            )
            return Response(status=status.HTTP_200_OK, data={"estado": "ok", "mensaje": "operacion correcta"})
        except black_imsi.DoesNotExist as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": "Codigo Imsi NO Existe"})



