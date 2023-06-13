import json

from clases.registro_log import RegistroLog
from django.apps import apps
from django.db import DatabaseError
from drf_yasg import openapi
from drf_yasg.openapi import FORMAT_DATE
from drf_yasg.utils import swagger_auto_schema
from lista_negra.api.serializers import *
from lista_negra.models import *
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


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
                                            description="Se reciben valores {'claro','telefonica','cnt','otros' }",
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
        info = request.POST if request.POST else request.data if request.data else None

        try:
            # Se hace una validacion de los parametros lista, operadora y origen
            # para verificar si se esta recibiendo los calores que corresponden
            # segun lo definido en el config.json
            path = apps.get_app_config('lista_negra').path
            config = open(path + '\\config\\config.json')
            data = json.load(config)

            # Evaluando Operadora
            existe_lista = list(filter(lambda x: x["valor"] == info['lista'], data["valores_lista"]))
            if len(existe_lista) <= 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": "El parametro {lista} tiene un valor que no es reconocible en la configuracion de los posibles valores que puede recibir. Revisar la documentacion"})

            # Evaluando Origen
            existe_origen = list(filter(lambda x: x["valor"] == info['source'], data["valores_origen"]))
            if len(existe_origen) <= 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": "El parametro {origen} tiene un valor que no es reconocible en la configuracion de los posibles valores que puede recibir. Revisar la documentacion"})

            # Evaluando Operadora
            existe_operadora = list(filter(lambda x: x["valor"] == info['operadora'], data["valores_operadora"]))
            if len(existe_operadora) <= 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": "El parametro {operadora} tiene un valor que no es reconocible en la configuracion de los posibles valores que puede recibir. Revisar la documentacion"})

            if len(info["imsi"]) < 15 or len(info["imsi"]) > 16:
                log_imsi.grabar('Ingreso', info["imsi"], info["operadora"], info["lista"], info["razon"],
                                info["source"],
                                "error: El codigo IMSI tiene una longitud incorrecta",
                                info["usuario_id"]
                                )
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error", "mensaje": "El codigo IMSI tiene una longitud incorrecta"})

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
    # permission_classes = [IsAuthenticated]
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
        info = request.POST if request.POST else request.data if request.data else None

        try:

            # Se hace una validacion de los parametros lista, operadora y origen
            # para verificar si se esta recibiendo los calores que corresponden
            # segun lo definido en el config.json
            path = apps.get_app_config('lista_negra').path
            config = open(path + '\\config\\config.json')
            data = json.load(config)

            # Evaluando Origen
            existe_origen = list(filter(lambda x: x["valor"] == info['origen'], data["valores_origen"]))
            if len(existe_origen) <= 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": "El parametro origen tiene un valor que no es reconocible en la configuracion de los posibles valores que puede recibir. Revisar la documentacion"})

            if len(info["imsi"]) < 15 or len(info["imsi"]) > 16:
                log_imsi.grabar('Consulta', info["imsi"], None, None, None, info["origen"],
                                "error: El codigo IMSI tiene una longitud incorrecta",
                                info["usuario_id"]
                                )
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error", "mensaje": "El codigo IMSI tiene una longitud incorrecta"})

            serializer = ListaNegraSerializer(black_imsi.objects.get(pk=info['imsi']), many=True)
            # data_log = list(log_aprov_eir.objects.filter(imsi=info['imsi']))
            # serializer_log = LogSerializer(log_aprov_eir.objects.filter(imsi=info['imsi']), many=True)
            # data_response = {
            #    "imsi": lista_encontrada.imsi,
            #    "origen": lista_encontrada.source,
            #   "register": lista_encontrada.register,
            #    "data_log": serializer_log.data
            # }

            log_imsi.grabar('Consulta', info["imsi"], None, None, None, info["origen"],
                            "Consulta Ok",
                            info["usuario_id"]
                            )
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except black_imsi.DoesNotExist as e:
            log_imsi.grabar('Consulta', info["imsi"], None, None, None, info["origen"],
                            "Codigo Imsi NO Existe",
                            info["usuario_id"]
                            )
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"estado": "error", "mensaje": "Codigo Imsi NO Existe"})
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
        info = request.POST if request.POST else request.data if request.data else None

        try:

            # Se hace una validacion de los parametros lista, operadora y origen
            # para verificar si se esta recibiendo los calores que corresponden
            # segun lo definido en el config.json
            path = apps.get_app_config('lista_negra').path
            config = open(path + '\\config\\config.json')
            data = json.load(config)

            # Evaluando Origen
            existe_origen = list(filter(lambda x: x["valor"] == info['origen'], data["valores_origen"]))
            if len(existe_origen) <= 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": "El parametro origen tiene un valor que no es reconocible en la configuracion de los posibles valores que puede recibir. Revisar la documentacion"})

            if len(info["imsi"]) < 15 or len(info["imsi"]) > 16:
                log_imsi.grabar('Eliminar', info["imsi"], None, None, None, info["origen"],
                                "error: El codigo IMSI tiene una longitud incorrecta",
                                info["usuario_id"]
                                )
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error", "mensaje": "El codigo IMSI tiene una longitud incorrecta"})

            obj_listanegra = black_imsi.objects.get(pk=info["imsi"])
            obj_listanegra.delete()
            log_imsi.grabar('Eliminar', info["imsi"], None, None, None, info["origen"],
                            "Eliminacion Ok",
                            info["usuario_id"]
                            )
            return Response(status=status.HTTP_200_OK, data={"estado": "ok", "mensaje": "operacion correcta"})
        except black_imsi.DoesNotExist as e:
            log_imsi.grabar('Eliminar', info["imsi"], None, None, None, info["origen"],
                            "error: codigo IMSI no existe",
                            info["usuario_id"]
                            )
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"estado": "error", "mensaje": "Codigo Imsi NO Existe"})
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
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e1)})
