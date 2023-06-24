import json

from django.apps import apps
from django.db import DatabaseError
from drf_yasg import openapi
from drf_yasg.openapi import FORMAT_DATE
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from clases.registro_log import RegistroLog
from lista_negra.api.serializers import *
from lista_negra.models import *
from lista_negra.validators.validator_lista_negra import ValidatorListaNegra


class ListaNegraRegistroViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['imsi', 'origen', 'usuario_id'],
            properties={
                'imsi': openapi.Schema(type=openapi.TYPE_STRING,
                                       description="Codigo IMSI que se va registrar",
                                       max_length=15),
                'operadora': openapi.Schema(type=openapi.TYPE_STRING,
                                            description="Se reciben valores {'claro','telefonica','cnt','otros','masivo' }",
                                            max_length=15),
                'lista': openapi.Schema(type=openapi.TYPE_STRING,
                                        description="Se reciben valores {'blanca','gris','negra'}",
                                        max_length=10),
                'razon': openapi.Schema(type=openapi.TYPE_STRING,
                                        description="Descripcion cual fue el motivo del bloqueo del codigo IMSI",
                                        max_length=1000),
                'source': openapi.Schema(type=openapi.TYPE_STRING,
                                         description="Origen de la transaccion, se reciben los siguientes valores: {'api','front','bulk'}",
                                         max_length=10),
                'usuario_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                             description="Codigo de usuario que debe estar registrado en el sistema y con permisos para ingresar IMSI")
                # 'visit_at': openapi.Schema(type=openapi.TYPE_STRING,
                #                           format=FORMAT_DATE)
            }
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
        log_imsi = RegistroLog()
        validator = ValidatorListaNegra()
        info = request.POST if request.POST else request.data if request.data else None

        try:

            # Evaluando Operadora
            message_validator_request_operadora = validator.validator_parameter_operadora(info['operadora'])
            if len(message_validator_request_operadora) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": message_validator_request_operadora})

            # Evaluando Origen
            message_validator_request_origen = validator.validator_parameter_origen(info['source'])
            if len(message_validator_request_origen) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": message_validator_request_origen})

            # Evaluando Lista
            message_validator_request_lista = validator.validator_parameter_lista(info['lista'])
            if len(message_validator_request_lista) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": message_validator_request_lista})

            message_validator_length_imsi = validator.validator_length_imsi(info['imsi'])
            if len(message_validator_length_imsi) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error", "mensaje": message_validator_length_imsi})

            serializer = ListaNegraRegistroSerializer(data=info)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                log_imsi.grabar('Ingreso', info["imsi"], info["operadora"], info["lista"], info["razon"],
                                info["source"],
                                "Ingreso Ok",
                                info["usuario_id"]
                                )
                return Response(status=status.HTTP_200_OK, data={"estado": "ok", "mensaje": "operacion correcta"})
            else:
                log_imsi.grabar('Ingreso', info["imsi"], info["operadora"], info["lista"], info["razon"],
                                info["source"],
                                serializer.errors,
                                info["usuario_id"]
                                )

                return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


        except DatabaseError as e:

            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})
        except FileNotFoundError as e:

            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"estado": "error", "mensaje": "archivo config.json no ha podido ser encontrado"})
        except Exception as e1:

            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e1)})

    # def destroy(self, request, *args, **kwargs):


class ListaNegraConsultaViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['imsi', 'origen', 'usuario_id'],
            properties={
                'imsi': openapi.Schema(type=openapi.TYPE_STRING,
                                       description="Codigo IMSI que se va registrar",
                                       max_length=15),
                'origen': openapi.Schema(type=openapi.TYPE_STRING,
                                         description="Se reciben los siguientes valores: {'api','front','bulk'}",
                                         max_length=10),
                'usuario_id': openapi.Schema(type=openapi.TYPE_STRING,
                                             description="Codigo de usuario que debe estar registrado en el sistema y con permisos para consultar IMSI",
                                             max_length=50)
                # 'visit_at': openapi.Schema(type=openapi.TYPE_STRING,
                #                           format=FORMAT_DATE)
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'imsi': openapi.Schema(type=openapi.TYPE_STRING),
                    'source': openapi.Schema(type=openapi.TYPE_STRING),
                    'register': openapi.Schema(type=openapi.TYPE_STRING, format=FORMAT_DATE)
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

        log_imsi = RegistroLog()
        validator = ValidatorListaNegra()
        info = request.POST if request.POST else request.data if request.data else None

        try:

            message_validator_request_origen = validator.validator_parameter_origen(info['origen'])
            if len(message_validator_request_origen) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": message_validator_request_origen})

            message_validator_length_imsi = validator.validator_length_imsi(info['imsi'])
            if len(message_validator_length_imsi) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error", "mensaje": message_validator_length_imsi})

            # log_imsi.grabar('Consulta', info["imsi"], None, None, None, info["origen"],
            #                "error: El codigo IMSI tiene una longitud incorrecta",
            #                info["usuario_id"]
            #                )
            value_validator_exists_imsi = validator.validator_exists_imsi(info['imsi'])
            if value_validator_exists_imsi:
                serializer_data_imsi = ListaNegraSerializer(black_imsi.objects.filter(imsi=info['imsi']), many=True)
                data_response = {
                    "estado": "ok",
                    "mensaje": "ok",
                    "data": serializer_data_imsi.data,
                }
                log_imsi.grabar('Consulta', info["imsi"], None, None, None, info["origen"],
                                "Consulta Ok",
                                info["usuario_id"]
                                )
                return Response(status=status.HTTP_200_OK, data=data_response)
            else:
                data_response = {
                    "estado": "no_exists",
                    "mensaje": "Codigo IMSI No existe",
                    "data": None,
                }
                return Response(status=status.HTTP_200_OK, data=data_response)

        except DatabaseError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})
        except FileNotFoundError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"estado": "error", "mensaje": "archivo config.json no ha podido ser encontrado"})
        except Exception as e1:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e1)})


class ListaNegraEliminarViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['imsi', 'origen', 'usuario_id'],
            properties={
                'imsi': openapi.Schema(type=openapi.TYPE_STRING,
                                       description="Codigo IMSI que se va registrar",
                                       max_length=15),
                'origen': openapi.Schema(type=openapi.TYPE_STRING,
                                         description="Se reciben los siguientes valores: {'api','front','bulk'}",
                                         max_length=10),
                'usuario_id': openapi.Schema(type=openapi.TYPE_STRING,
                                             description="Codigo de usuario que debe estar registrado en el sistema y con permisos para eliminar IMSI",
                                             max_length=50)
                # 'visit_at': openapi.Schema(type=openapi.TYPE_STRING,
                #                           format=FORMAT_DATE)
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'estado': openapi.Schema(type=openapi.TYPE_STRING),
                    'mensaje': openapi.Schema(type=openapi.TYPE_STRING),
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
        log_imsi = RegistroLog()
        validator = ValidatorListaNegra()
        info = request.POST if request.POST else request.data if request.data else None

        try:

            message_validator_request_origen = validator.validator_parameter_origen(info['origen'])
            if len(message_validator_request_origen) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": message_validator_request_origen})

            message_validator_length_imsi = validator.validator_length_imsi(info['imsi'])
            if len(message_validator_length_imsi) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error", "mensaje": message_validator_length_imsi})

            value_validator_exists_imsi = validator.validator_exists_imsi(info['imsi'])
            if value_validator_exists_imsi:
                obj_listanegra = black_imsi.objects.get(pk=info["imsi"])
                obj_listanegra.delete()
                log_imsi.grabar('Eliminar', info["imsi"], None, None, None, info["origen"],
                                "Eliminacion Ok",
                                info["usuario_id"]
                                )
                data_response = {
                    "estado": "ok",
                    "mensaje": "Operacion Correcta",
                    "data": None,
                }
                return Response(status=status.HTTP_200_OK, data=data_response)
            else:
                data_response = {
                    "estado": "no_exists",
                    "mensaje": "Codigo IMSI No existe",
                    "data": None,
                }
                return Response(status=status.HTTP_200_OK, data=data_response)

        except DatabaseError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})
        except Exception as e1:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e1)})


class LogXUsuarioViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        info = request.POST if request.POST else request.data if request.data else None
        serializer_log = LogSerializer(
            log_aprov_eir.objects.filter(usuario_descripcion=info['usuario_id']).order_by('-fecha_bitacora')[0:100],
            many=True)
        return Response(status=status.HTTP_200_OK, data=serializer_log.data)


class LogXIMSIViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        info = request.POST if request.POST else request.data if request.data else None
        serializer_log = LogSerializer(
            log_aprov_eir.objects.filter(imsi=info['imsi']),
            many=True)
        return Response(status=status.HTTP_200_OK, data=serializer_log.data)


class ParametrosOperadoraView(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, reques):
        try:
            # Se hace una validacion de los parametros lista, operadora y origen
            # para verificar si se esta recibiendo los calores que corresponden
            # segun lo definido en el config.json
            path = apps.get_app_config('lista_negra').path
            config = open(path + '\\config\\config.json')
            data = json.load(config)
            data_response = data["valores_operadora"]
            return Response(status=status.HTTP_200_OK, data=data_response)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})


class ArchivoMasivoViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        try:
            serializer = FileProcessSerializer(
                files_process_bulk.objects.all(),
                many=True)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except Exception as e:
            data_response = {
                'estado': 'error',
                'mensaje': str(e)
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data=data_response)

    def create(self, request):
        info = request.POST if request.POST else request.data if request.data else None
        try:
            data_request = {
                'estado': 'pendiente',
                'archivo_csv': info['nombre_archivo_csv'],
                'usuario_registro': info['usuario_id'],
                'ip_registro': '0.0.0.0'
            }
            serializer = FileProcessRegistroSerializer(data=data_request)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            data_response = {
                'estado': 'ok',
                'mensaje': 'operacion correcta'
            }
            return Response(data=data_response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        info = request.POST if request.POST else request.data if request.data else None
        obj_fileprocessbulk = files_process_bulk.objects.get(pk=pk)
        serializer = FileProcessActualizarSerializer(obj_fileprocessbulk, data=info, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
