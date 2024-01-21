import csv
import json
import logging as log

from django.apps import apps
from django.db import DatabaseError
from django.db.models import Q
from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.openapi import FORMAT_DATE
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from lista_negra.api.serializers import *
from lista_negra.functions.functions_lista_negra import FunctionsListaNegra
from lista_negra.functions.functions_log import RegistroLog
from lista_negra.models import *
from lista_negra.validators.validator_lista_negra import ValidatorListaNegra

log.basicConfig(level=log.DEBUG,
                format='%(asctime)s: %(levelname)s [%(filename)s:%(lineno)s] %(message)s',
                handlers=[
                    log.FileHandler(apps.get_app_config('lista_negra').path + r'/logs/log_api_lista_negra.log'),
                    log.StreamHandler()
                ])


class ListaNegraRegistroViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para registrar un IMSI en lista negra',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['imsi', 'source'],
            properties={
                'imsi': openapi.Schema(type=openapi.TYPE_NUMBER,
                                       description="Codigo IMSI que se va registrar",
                                       example=123456789012345,
                                       max_length=15),
                'telco': openapi.Schema(type=openapi.TYPE_STRING,
                                        description="Se reciben valores {'claro','telefonica','cnt','otros','masivo' }",
                                        max_length=15),
                'list': openapi.Schema(type=openapi.TYPE_STRING,
                                       description="Se reciben valores {'blanca','gris','negra'}",
                                       max_length=10),
                'reason': openapi.Schema(type=openapi.TYPE_STRING,
                                         description="Descripcion cual fue el motivo del bloqueo del codigo IMSI",
                                         max_length=1000),
                'source': openapi.Schema(type=openapi.TYPE_STRING,
                                         description="Origen de la transaccion, se reciben los siguientes valores: {'api','front','bulk'}",
                                         max_length=10)
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
        metodos = FunctionsListaNegra()
        info = request.POST if request.POST else request.data if request.data else None

        try:
            # registrando en log el request enviando
            log.info(f"request registro_imsi: {str(info)}")

            path = apps.get_app_config('lista_negra').path
            config = open(path + r'/config/config.json')
            data = json.load(config)
            target_imsi = data["target_imsi"]
            action_api_insert = data["action_api_registrar"]

            # Obtengo la sesion del usuario que esta conectado
            data_user = metodos.obtenerUsuarioSesionToken(request)

            # Aqui se valida si el usuario que inicio sesion, tiene acceso a esta accion y endpoint
            usuario_accion_permitida = metodos.validarAccionApiUsuario(data_user["username"], target_imsi,
                                                                       action_api_insert)
            if usuario_accion_permitida is False:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": "Su usuario no tiene permisos para acceder a esta accion : Ingreso -> Imsi"})

            # Otengo la direccion remota
            ip_transaccion = metodos.obtenerDireccionIpRemota(request)

            # Evaluando los parametros recibidos:
            estado_parametros = validator.validator_parameters(info,
                                                               ['imsi', 'telco', 'reason', 'list', 'source'])

            if estado_parametros == False:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": "no se reconoce uno de los parametros enviados en la trama. Por favor revise la documentacion"})

            # Evaluando que el valor reason tenga un valor
            if len(info["reason"].strip()) <= 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": "falta ingresar un motivo"})

            # Evaluando Operadora
            message_validator_request_operadora = validator.validator_parameter_operadora(info['telco'])
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
            message_validator_request_lista = validator.validator_parameter_lista(info['list'])
            if len(message_validator_request_lista) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": message_validator_request_lista})

            # Evaluando que el codigo IMSI sea solo numeros
            message_validator_request_onlynumber = validator.validator_onlynumber_imsi(info['imsi'])
            if len(message_validator_request_onlynumber) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": message_validator_request_onlynumber})

            # Evaluando longitud del codigo IMSI
            message_validator_length_imsi = validator.validator_length_imsi(info['imsi'])
            if len(message_validator_length_imsi) > 0:
                # log_imsi.grabar('INSERT', info["imsi"], info["telco"], info["list"], info["reason"], info["source"],
                #                "error: " + message_validator_length_imsi,
                #                data_user["username"], ip_transaccion)
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error", "mensaje": message_validator_length_imsi})

            serializer = ListaNegraRegistroSerializer(data=info)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                """
                Aqui se va a ingresar el nuevo IMSI en la base REPLIC      
                Queda desactivado
                                try:
                    black_imsi.objects.using('replica').create(
                        imsi=info['imsi'],
                        source=info['source']
                    )
                except Exception as e1:
                    log.error(f"Fallo la insercion IMSI con la base Replica: {str(e1)}")          
                """

                log_imsi.grabar('INSERT', info["imsi"], info["telco"], info["list"], info["reason"],
                                info["source"],
                                "Ingreso Ok",
                                data_user["username"],
                                ip_transaccion, log
                                )
                return Response(status=status.HTTP_200_OK, data={"estado": "ok", "mensaje": "operacion correcta"})
            else:
                log_imsi.grabar('INSERT', info["imsi"], info["telco"], info["list"], info["reason"],
                                info["source"],
                                serializer.errors,
                                data_user["username"],
                                ip_transaccion, log
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
        operation_description='API para consultar IMSI registrado en lista negra',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['imsi', 'source'],
            properties={
                'imsi': openapi.Schema(type=openapi.TYPE_NUMBER,
                                       description="Codigo IMSI que se va registrar",
                                       example=123456789012345,
                                       max_length=15),
                'source': openapi.Schema(type=openapi.TYPE_STRING,
                                         description="Se reciben los siguientes valores: {'api','front','bulk'}",
                                         max_length=10)
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
        metodos = FunctionsListaNegra()
        info = request.POST if request.POST else request.data if request.data else None

        try:

            # registrando en log el request enviando
            log.info(f"request consulta_imsi: {str(info)}")

            path = apps.get_app_config('lista_negra').path
            config = open(path + r'/config/config.json')
            data = json.load(config)
            target_imsi = data["target_imsi"]
            action_api_select = data["action_api_consultar"]

            # Obtengo la sesion del usuario que esta conectado
            data_user = metodos.obtenerUsuarioSesionToken(request)

            # Aqui se valida si el usuario que inicio sesion, tiene acceso a esta accion y endpoint
            usuario_accion_permitida = metodos.validarAccionApiUsuario(data_user["username"], target_imsi,
                                                                       action_api_select)
            if usuario_accion_permitida is False:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": "Su usuario no tiene permisos para acceder a esta accion : Consulta -> Imsi"})

            # Otengo la direccion remota
            ip_transaccion = metodos.obtenerDireccionIpRemota(request)

            # Evaluando los parametros recibidos:
            estado_parametros = validator.validator_parameters(info, ['imsi', 'source'])

            if estado_parametros == False:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": "no se reconoce uno de los parametros enviados en la trama. Por favor revise la documentacion"})

            # Evaluando que el codigo IMSI sea solo numeros
            message_validator_request_onlynumber = validator.validator_onlynumber_imsi(info['imsi'])
            if len(message_validator_request_onlynumber) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": message_validator_request_onlynumber})

            # Validando valor origen
            message_validator_request_origen = validator.validator_parameter_origen(info['source'])
            if len(message_validator_request_origen) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": message_validator_request_origen})

            # Validando longitud IMSI
            message_validator_length_imsi = validator.validator_length_imsi(info['imsi'])
            if len(message_validator_length_imsi) > 0:
                # log_imsi.grabar('QUERY', info["imsi"], None, None, None, info["source"],
                #                "error: " + message_validator_length_imsi,
                #                data_user["username"], ip_transaccion)
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error", "mensaje": message_validator_length_imsi})

            # Validando si existe o no el IMSI
            value_validator_exists_imsi = validator.validator_exists_imsi(info['imsi'])
            if value_validator_exists_imsi:
                serializer_data_imsi = ListaNegraSerializer(black_imsi.objects.filter(imsi=info['imsi']), many=True)
                data_response = {
                    "estado": "ok",
                    "mensaje": "ok",
                    "data": serializer_data_imsi.data,
                }
                log_imsi.grabar('QUERY', info["imsi"], None, None, None, info["source"],
                                "Consulta Ok",
                                data_user["username"],
                                ip_transaccion, log
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

    @swagger_auto_schema(
        operation_description='API para obtener todos los registros de Lista Negra',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                     properties={
                                         'imsi': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                description='Codigo IMSI'),
                                         'fecha': openapi.Schema(type=openapi.TYPE_STRING,
                                                                 description='Fecha cuando registrado el codigo IMSI',
                                                                 ),
                                         'usuario': openapi.Schema(type=openapi.TYPE_STRING, format=FORMAT_DATE,
                                                                   description='Usuario que registro el ingreso del codigo IMSI',
                                                                   ),

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
        metodos = FunctionsListaNegra()
        try:
            # serializer_data_imsi = ListaNegraSerializer(black_imsi.objects.all(), many=True)
            data_lista_negra = metodos.generarListaNegraTotal()
            return Response(status=status.HTTP_200_OK, data=data_lista_negra)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})


class ListaNegraEliminarViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para eliminar IMSI registrado en lista negra',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['imsi', 'source', 'reason'],
            properties={
                'imsi': openapi.Schema(type=openapi.TYPE_NUMBER,
                                       description="Codigo IMSI que se va registrar",
                                       example=123456789012345,
                                       max_length=15),
                'source': openapi.Schema(type=openapi.TYPE_STRING,
                                         description="Se reciben los siguientes valores: {'api','front','bulk'}",
                                         max_length=10),
                'reason': openapi.Schema(type=openapi.TYPE_STRING,
                                         description="Se indica el motivo por el caul se elimina el codigo IMSI",
                                         max_length=10)
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
        metodos = FunctionsListaNegra()
        info = request.POST if request.POST else request.data if request.data else None

        try:

            # registrando en log el request enviando
            log.info(f"request eliminar_imsi: {str(info)}")

            path = apps.get_app_config('lista_negra').path
            config = open(path + r'/config/config.json')
            data = json.load(config)
            target_imsi = data["target_imsi"]
            action_api_delete = data["action_api_eliminar"]

            # Obtengo la sesion del usuario que esta conectado
            data_user = metodos.obtenerUsuarioSesionToken(request)

            # Aqui se valida si el usuario que inicio sesion, tiene acceso a esta accion y endpoint
            usuario_accion_permitida = metodos.validarAccionApiUsuario(data_user["username"], target_imsi,
                                                                       action_api_delete)
            if usuario_accion_permitida is False:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": "Su usuario no tiene permisos para acceder a esta accion : Eliminar -> Imsi"})

            # Otengo la direccion remota
            ip_transaccion = metodos.obtenerDireccionIpRemota(request)

            # Evaluando los parametros recibidos:
            estado_parametros = validator.validator_parameters(info,
                                                               ['imsi', 'source', 'reason'])

            if estado_parametros == False:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": "no se reconoce uno de los parametros enviados en la trama JSON (BodyRequest). Por favor revise la documentacion"})

            # Evaluando que llegue un valor de motivo
            if len(info["reason"].strip()) <= 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": "falta ingresar un motivo"})

            # Evaluando valor del campo Origen
            message_validator_request_origen = validator.validator_parameter_origen(info['source'])
            if len(message_validator_request_origen) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": message_validator_request_origen})

            # Evaluando longitud del codigo IMSI
            message_validator_length_imsi = validator.validator_length_imsi(info['imsi'])
            if len(message_validator_length_imsi) > 0:
                # log_imsi.grabar('DELETE', info["imsi"], None, None, None, info["source"],
                #                "error: " + message_validator_length_imsi,
                #                data_user["username"],
                #                ip_transaccion
                #               )
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error", "mensaje": message_validator_length_imsi})

            # Evaluando que el codigo IMSI sea solo numeros
            message_validator_request_onlynumber = validator.validator_onlynumber_imsi(info['imsi'])
            if len(message_validator_request_onlynumber) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": message_validator_request_onlynumber})

            # Evaluando si existe el codigo IMSI
            value_validator_exists_imsi = validator.validator_exists_imsi(info['imsi'])
            if value_validator_exists_imsi:
                obj_listanegra = black_imsi.objects.get(pk=info["imsi"])
                obj_listanegra.delete()
                """
                Aqui se elimina el registro que se encuentra en la base REPLICA
                
                """
                try:
                    obj_listanegra_replica = black_imsi.objects.using('replica').get(pk=info["imsi"])
                    obj_listanegra_replica.delete()
                except Exception as e:
                    log.error(f"Fallo la eliminacion IMSI en la base Replica: {str(e)}")

                log_imsi.grabar('DELETE', info["imsi"], None, None, info["reason"], info["source"],
                                "Eliminacion Ok",
                                data_user["username"],
                                ip_transaccion, log
                                )
                data_response = {
                    "estado": "ok",
                    "mensaje": "Operacion Correcta"
                }
                return Response(status=status.HTTP_200_OK, data=data_response)
            else:
                data_response = {
                    "estado": "no_exists",
                    "mensaje": "Codigo IMSI No existe"
                }
                return Response(status=status.HTTP_200_OK, data=data_response)

        except DatabaseError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})
        except Exception as e1:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e1)})


class LogXUsuarioViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para consulta de los primeros 100 LOGS mas recientes realizados por la sesion del usuario conectado',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                     properties={
                                         'accion': openapi.Schema(type=openapi.TYPE_STRING,
                                                                  description='Accion realizada sobre el codigo IMSI',
                                                                  example="INSERT"),
                                         'imsi': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                description='Codigo IMSI', example=123456789012345),
                                         'operadora': openapi.Schema(type=openapi.TYPE_STRING,
                                                                     description='Operador telefonico',
                                                                     example='claro'),
                                         'lista': openapi.Schema(type=openapi.TYPE_STRING,
                                                                 description='Tipo lista',
                                                                 example='negra'),
                                         'razon': openapi.Schema(type=openapi.TYPE_STRING,
                                                                 description='Motivo de la transaccion sobre el codigo IMSI registrado',
                                                                 example='Fue bloqueado'),
                                         'origen': openapi.Schema(type=openapi.TYPE_STRING,
                                                                  description='Origen de la transaccion',
                                                                  example='api'),
                                         'fecha_bitacora': openapi.Schema(type=openapi.TYPE_STRING, format=FORMAT_DATE,
                                                                          description='Fecha transaccion',
                                                                          ),
                                         'usuario_descripcion': openapi.Schema(type=openapi.TYPE_STRING,
                                                                               description='Usuario que realizo transaccion con el codigo IMSI',
                                                                               ),
                                         'ip_transaccion': openapi.Schema(type=openapi.TYPE_STRING,
                                                                          description='Direccion IP de donde se realizo la transaccion',
                                                                          ),
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
        validator = ValidatorListaNegra()
        metodos = FunctionsListaNegra()
        try:

            # Obtengo la sesion del usuario que esta conectado
            data_user = metodos.obtenerUsuarioSesionToken(request)

            serializer_log = LogSerializer(
                log_aprov_eir.objects.filter(usuario_descripcion=data_user['username']).order_by('-fecha_bitacora')[
                0:100],
                many=True)
            return Response(status=status.HTTP_200_OK, data=serializer_log.data)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})


class LogXIMSIViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para consulta de todos los LOGS de un codigo IMSI ingresado',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['imsi'],
            properties={
                'imsi': openapi.Schema(type=openapi.TYPE_NUMBER,
                                       description="Codigo IMSI que se va registrar",
                                       example=123456789012345,
                                       max_length=15),
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                     properties={
                                         'accion': openapi.Schema(type=openapi.TYPE_STRING,
                                                                  description='Accion realizada sobre el codigo IMSI',
                                                                  example="INSERT"),
                                         'imsi': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                description='Codigo IMSI', example=123456789012345),
                                         'operadora': openapi.Schema(type=openapi.TYPE_STRING,
                                                                     description='Operador telefonico',
                                                                     example='claro'),
                                         'lista': openapi.Schema(type=openapi.TYPE_STRING,
                                                                 description='Tipo lista',
                                                                 example='negra'),
                                         'razon': openapi.Schema(type=openapi.TYPE_STRING,
                                                                 description='Motivo de la transaccion sobre el codigo IMSI registrado',
                                                                 example='Fue bloqueado'),
                                         'origen': openapi.Schema(type=openapi.TYPE_STRING,
                                                                  description='Origen de la transaccion',
                                                                  example='api'),
                                         'fecha_bitacora': openapi.Schema(type=openapi.TYPE_STRING, format=FORMAT_DATE,
                                                                          description='Fecha transaccion',
                                                                          ),
                                         'usuario_descripcion': openapi.Schema(type=openapi.TYPE_STRING,
                                                                               description='Usuario que realizo transaccion con el codigo IMSI',
                                                                               ),
                                         'ip_transaccion': openapi.Schema(type=openapi.TYPE_STRING,
                                                                          description='Direccion IP de donde se realizo la transaccion',
                                                                          ),
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
        validator = ValidatorListaNegra()
        try:
            info = request.POST if request.POST else request.data if request.data else None

            # Evaluando longitud del codigo IMSI
            message_validator_length_imsi = validator.validator_length_imsi(info['imsi'])
            if len(message_validator_length_imsi) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error", "mensaje": message_validator_length_imsi})

            # Evaluando que el codigo IMSI sea solo numeros
            message_validator_request_onlynumber = validator.validator_onlynumber_imsi(info['imsi'])
            if len(message_validator_request_onlynumber) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": message_validator_request_onlynumber})

            serializer_log = LogSerializer(
                log_aprov_eir.objects.filter(imsi=info['imsi']).order_by('-fecha_bitacora'),
                many=True)
            return Response(status=status.HTTP_200_OK, data=serializer_log.data)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})


class LogXFechasViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para consulta de todos los LOGS por un rango de fecha determinado',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['fecha_desde', 'fecha_hasta'],
            properties={
                'fecha_desde': openapi.Schema(type=openapi.TYPE_STRING,
                                              format=FORMAT_DATE,
                                              description="Fecha de inicio de busqueda"),
                'fecha_hasta': openapi.Schema(type=openapi.TYPE_STRING,
                                              format=FORMAT_DATE,
                                              description="Fecha de fin de busqueda")
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                     properties={
                                         'accion': openapi.Schema(type=openapi.TYPE_STRING,
                                                                  description='Accion realizada sobre el codigo IMSI',
                                                                  example="INSERT"),
                                         'imsi': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                description='Codigo IMSI', example=123456789012345),
                                         'operadora': openapi.Schema(type=openapi.TYPE_STRING,
                                                                     description='Operador telefonico',
                                                                     example='claro'),
                                         'lista': openapi.Schema(type=openapi.TYPE_STRING,
                                                                 description='Tipo lista',
                                                                 example='negra'),
                                         'razon': openapi.Schema(type=openapi.TYPE_STRING,
                                                                 description='Motivo de la transaccion sobre el codigo IMSI registrado',
                                                                 example='Fue bloqueado'),
                                         'origen': openapi.Schema(type=openapi.TYPE_STRING,
                                                                  description='Origen de la transaccion',
                                                                  example='api'),
                                         'fecha_bitacora': openapi.Schema(type=openapi.TYPE_STRING, format=FORMAT_DATE,
                                                                          description='Fecha transaccion',
                                                                          ),
                                         'usuario_descripcion': openapi.Schema(type=openapi.TYPE_STRING,
                                                                               description='Usuario que realizo transaccion con el codigo IMSI',
                                                                               ),
                                         'ip_transaccion': openapi.Schema(type=openapi.TYPE_STRING,
                                                                          description='Direccion IP de donde se realizo la transaccion',
                                                                          ),
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
        try:
            info = request.POST if request.POST else request.data if request.data else None

            serializer_log = LogSerializer(
                log_aprov_eir.objects.filter(Q(fecha_bitacora__date__range=[info['fecha_desde'], info['fecha_hasta']])),
                many=True)
            return Response(status=status.HTTP_200_OK, data=serializer_log.data)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})


class ParametrosOperadoraView(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para obtener el listado de valores de Operadora',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                     properties={
                                         'valor': openapi.Schema(type=openapi.TYPE_STRING,
                                                                 description='Valor de operadora',
                                                                 example="claro"),
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
            # Se hace una validacion de los parametros lista, operadora y origen
            # para verificar si se esta recibiendo los calores que corresponden
            # segun lo definido en el config.json
            path = apps.get_app_config('lista_negra').path
            config = open(path + r'/config/config.json')
            data = json.load(config)
            data_response = data["valores_operadora"]
            return Response(status=status.HTTP_200_OK, data=data_response)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})


class ParametrosRutaFtpView(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para obtener la ruta FTP configurada en el archivo config.json',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                     properties={
                                         'valor': openapi.Schema(type=openapi.TYPE_STRING,
                                                                 description='Valor de operadora',
                                                                 example="claro"),
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
            path = apps.get_app_config('lista_negra').path
            config = open(path + r'/config/config.json')
            data = json.load(config)
            ruta_config_jobmasivo = data["ruta_ftp_job_masivo"]
            # Una vez obtenida la lectura
            config_job = open(fr'{data["ruta_ftp_job_masivo"]}')
            data_job = json.load(config_job)

            data_response = data
            data_response = {
                "estado": "ok",
                "mensaje": data_job["PATH_FTP_CSV"]
            }
            return Response(status=status.HTTP_200_OK, data=data_response)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})


class ArchivoMasivoViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para obtener el listado de archivos masivos registrados desde UI',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                     properties={
                                         'id': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                              description='ID de la tabla',
                                                              ),
                                         'estado': openapi.Schema(type=openapi.TYPE_STRING,
                                                                  description='Estado del registro',
                                                                  ),
                                         'archivo_csv': openapi.Schema(type=openapi.TYPE_STRING,
                                                                       description='Nombre archivo CSV registrado',
                                                                       ),
                                         'total_encontrado': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                            description='Total IMSI encontrados en el archivo csv a procesar',
                                                                            ),
                                         'total_error': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                       description='Total de IMSI encontrados con error',
                                                                       ),
                                         'total_ok': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                    description='Total de IMSI procesados correctamente a lista negra',
                                                                    ),
                                         'observacion': openapi.Schema(type=openapi.TYPE_STRING,
                                                                       description='Detalle de alguna observacion para el caso que el archivo csv no fue encontrado',
                                                                       example="claro"),
                                         'fecha_archivo_procesando': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                    description='Fecha desde que inicio el proceso de ingreso a lista negra',
                                                                                    ),
                                         'fecha_archivo_finalizado': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                    description='Fecha de fin de operacion de ingreso de IMSI a lista negra',
                                                                                    ),
                                         'fecha_registro': openapi.Schema(type=openapi.TYPE_STRING,
                                                                          description='Fecha que se ingreso la transaccion',
                                                                          example="claro"),
                                         'usuario_registro': openapi.Schema(type=openapi.TYPE_STRING,
                                                                            description='Usuario que realizo la operacion de ingreso de archivos masivos',
                                                                            example="claro"),
                                         'ip_registro': openapi.Schema(type=openapi.TYPE_STRING,
                                                                       description='Direccion IP de donde se esta consumiento el Api',
                                                                       ),
                                         'fecha_actualizacion': openapi.Schema(type=openapi.TYPE_STRING,
                                                                               description='Fecha de actualizacion del registro',
                                                                               ),
                                         'usuario_actualizacion': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                 description='Usuario que realizo alguna modificacion sobre los registros',
                                                                                 ),
                                         'ip_actualizacion': openapi.Schema(type=openapi.TYPE_STRING,
                                                                            description='Direccion IP de donde se esta consumiento el Api',
                                                                            ),
                                         'accion': openapi.Schema(type=openapi.TYPE_STRING,
                                                                  description='Accion que se va a realizar con el proceso masivo. {I} : Ingreso {D}: Eliminacion',
                                                                  )
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
            serializer = FileProcessSerializer(
                files_process_bulk.objects.all().order_by('-fecha_archivo_procesando'),
                many=True)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except Exception as e:
            data_response = {
                'estado': 'error',
                'mensaje': str(e)
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data=data_response)

    @swagger_auto_schema(
        operation_description='API para registrar un IMSI masivo a Lista Negra',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['nombre_archivo_csv'],
            properties={
                'nombre_archivo_csv': openapi.Schema(type=openapi.TYPE_STRING,
                                                     description="Nombre archivo csv que se va a procesar",
                                                     example='mi_archivo.csv',
                                                     required=1,
                                                     max_length=50),
                'accion': openapi.Schema(type=openapi.TYPE_STRING,
                                         description="Accion que se va a realizar con el proceso masivo. {I} : Ingreso {D}: Eliminacion",
                                         example='I',
                                         required=1,
                                         max_length=1),
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
        metodos = FunctionsListaNegra()
        info = request.POST if request.POST else request.data if request.data else None
        try:
            # registrando en log el request enviando
            log.info(f"request registro_imsi_masivo: {str(info)}")

            # Obtengo la sesion del usuario conectado
            data_user = metodos.obtenerUsuarioSesionToken(request)

            # Otengo la direccion remota
            ip_transaccion = metodos.obtenerDireccionIpRemota(request)

            data_request = {
                'estado': 'pendiente',
                'archivo_csv': info['nombre_archivo_csv'],
                'usuario_registro': data_user['username'],
                'accion': info['accion'],
                'ip_registro': ip_transaccion
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
            data_response = {
                'estado': 'error',
                'mensaje': str(e)
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data=data_response)

    def partial_update(self, request, pk=None):
        metodos = FunctionsListaNegra()
        info = request.POST if request.POST else request.data if request.data else None
        try:
            # registrando en log el request enviando
            log.info(f"request actualizacion_imsi_masivo: {str(info)}")

            # Obtengo la sesion del usuario conectado
            data_user = metodos.obtenerUsuarioSesionToken(request)

            # aqui se obtiene la direccion IP remota
            info["ip_actualizacion"] = metodos.obtenerDireccionIpRemota(request)
            info["usuario_actualizacion"] = data_user["username"]

            obj_fileprocessbulk = files_process_bulk.objects.get(pk=pk)
            serializer = FileProcessActualizarSerializer(obj_fileprocessbulk, data=info, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(status=status.HTTP_200_OK, data=serializer.data)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        except Exception as e:
            data_response = {
                'estado': 'error',
                'mensaje': str(e)
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data=data_response)


class ReporteBloqueadoViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para generar archivo CSV de todos los IMSI bloqueados',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['fecha_inicio', 'fecha_fin'],
            properties={
                'fecha_inicio': openapi.Schema(type=openapi.TYPE_STRING, format=FORMAT_DATE,
                                               description="Fecha desde a buscar en la tabla de lista negra",
                                               ),
                'fecha_fin': openapi.Schema(type=openapi.TYPE_STRING, format=FORMAT_DATE,
                                            description="Fecha fin a buscar en la tabla de lista negra",
                                            ),
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_FILE,
                content_type='text/csv',
                content_disposition='attachment; filename="blocked.csv"'
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
            funcion = FunctionsListaNegra()
            valores_data = funcion.generarReporteBloqueados(info)

            # file_download = open(ruta_archivo, 'r')
            # response = HttpResponse(file_download, content_type='text/csv')
            # response['Content-Disposition'] = 'attachment; filename="{}"'.format(valores_data["nombre_archivo"])
            response = HttpResponse(
                content_type='text/csv',
            )
            response['Content-Disposition'] = 'attachment; filename="myfile.csv"'

            writer = csv.writer(response, delimiter="|")

            writer.writerow(
                ['accion', 'imsi', 'telco', 'list', 'reason', 'source', 'datetime_operation', 'detail', 'user_id',
                 'source_ip'])

            for item in valores_data["lista_valores"]:
                writer.writerow([
                    item["accion"],
                    item["imsi"],
                    item["operadora"],
                    item["lista"],
                    item["razon"],
                    item["origen"],
                    item["fecha_bitacora"],
                    item["descripcion"],
                    item["usuario_descripcion"],
                    item["ip_transaccion"]
                ])
            return response
            # return Response(data={"estado": "ok", "mensaje": nombre_csv_creado}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"estado": "error", "mensaje": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ReporteDesbloqueadoViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para generar archivo CSV de todos los IMSI desbloqueados',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['fecha_inicio', 'fecha_fin'],
            properties={
                'fecha_inicio': openapi.Schema(type=openapi.TYPE_STRING, format=FORMAT_DATE,
                                               description="Fecha desde a buscar en la tabla de lista negra",
                                               ),
                'fecha_fin': openapi.Schema(type=openapi.TYPE_STRING, format=FORMAT_DATE,
                                            description="Fecha fin a buscar en la tabla de lista negra",
                                            ),
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_FILE,
                content_type='text/csv',
                content_disposition='attachment; filename="unblocked.csv"'
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
            funcion = FunctionsListaNegra()
            valores_data = funcion.generarReporteDesbloqueados(info)

            # file_download = open(ruta_archivo, 'r')
            # response = HttpResponse(file_download, content_type='text/csv')
            # response['Content-Disposition'] = 'attachment; filename="{}"'.format(valores_data["nombre_archivo"])
            response = HttpResponse(
                content_type='text/csv',
            )
            response['Content-Disposition'] = 'attachment; filename="myfile.csv"'

            writer = csv.writer(response, delimiter="|")

            writer.writerow(
                ['accion', 'imsi', 'telco', 'list', 'reason', 'source', 'datetime_operation', 'detail', 'user_id',
                 'source_ip'])

            for item in valores_data["lista_valores"]:
                writer.writerow([
                    item["accion"],
                    item["imsi"],
                    item["operadora"],
                    item["lista"],
                    item["razon"],
                    item["origen"],
                    item["fecha_bitacora"],
                    item["descripcion"],
                    item["usuario_descripcion"],
                    item["ip_transaccion"]
                ])
            return response
            # return Response(data={"estado": "ok", "mensaje": nombre_csv_creado}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"estado": "error", "mensaje": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ReporteGeneralLogViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para generar un Sumario General Resumido',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'estado': openapi.Schema(type=openapi.TYPE_STRING, description='estado de la transaccion'),
                    'mensaje': openapi.Schema(type=openapi.TYPE_STRING,
                                              description='data con el sumario general resumido')
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
    def list(self, request):
        funcion = FunctionsListaNegra()
        try:
            data = funcion.generarSumario()
            return Response(data={"estado": "ok", "mensaje": data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"estado": "error", "mensaje": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description='API para generar archivo CSV de todos los LOG de los IMSI ingresados, consultados y eliminados',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['fecha_inicio', 'fecha_fin'],
            properties={
                'fecha_inicio': openapi.Schema(type=openapi.TYPE_STRING, format=FORMAT_DATE,
                                               description="Fecha desde a buscar en la tabla de logs",
                                               ),
                'fecha_fin': openapi.Schema(type=openapi.TYPE_STRING, format=FORMAT_DATE,
                                            description="Fecha fin a buscar en la tabla de logs",
                                            ),
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_FILE,
                content_type='text/csv',
                content_disposition='attachment; filename="logs.csv"'
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
            funcion = FunctionsListaNegra()
            valores_data = funcion.generarReporteGeneralLog(info)
            response = HttpResponse(
                content_type='text/csv',
            )
            response['Content-Disposition'] = 'attachment; filename="myfile.csv"'

            writer = csv.writer(response, delimiter="|")

            writer.writerow(
                ['accion', 'imsi', 'telco', 'list', 'reason', 'source', 'datetime_operation', 'detail', 'user_id',
                 'source_ip'])

            for item in valores_data["lista_valores"]:
                writer.writerow([
                    item["accion"],
                    item["imsi"],
                    item["operadora"],
                    item["lista"],
                    item["razon"],
                    item["origen"],
                    item["fecha_bitacora"],
                    item["descripcion"],
                    item["usuario_descripcion"],
                    item["ip_transaccion"]
                ])
            return response
            # return Response(data={"estado": "ok", "mensaje": nombre_csv_creado}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"estado": "error", "mensaje": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ReporteSumarioDetalladoView(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para generar archivo CSV um sumario detallado de todos los IMSI registrados',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['fecha_inicio', 'fecha_fin'],
            properties={
                'fecha_inicio': openapi.Schema(type=openapi.TYPE_STRING, format=FORMAT_DATE,
                                               description="Fecha desde a buscar en la tabla de logs",
                                               ),
                'fecha_fin': openapi.Schema(type=openapi.TYPE_STRING, format=FORMAT_DATE,
                                            description="Fecha fin a buscar en la tabla de logs",
                                            ),
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_FILE,
                content_type='text/csv',
                content_disposition='attachment; filename="summary.csv"'
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
            funcion = FunctionsListaNegra()
            valores_data = funcion.generarSumarioDetallado(info)

            # ordenamiento
            valores_data.sort(key=lambda x: x.get('imsi'), reverse=True)
            valores_data.sort(key=lambda x: x.get('total_insert'), reverse=True)
            valores_data.sort(key=lambda x: x.get('total_query'), reverse=True)
            valores_data.sort(key=lambda x: x.get('total_delete'), reverse=True)

            response = HttpResponse(
                content_type='text/csv',
            )
            response['Content-Disposition'] = 'attachment; filename="myfile.csv"'

            writer = csv.writer(response, delimiter="|")

            writer.writerow(
                ['imsi', 'total_insert', 'total_query', 'total_delete'])

            for item in valores_data:
                writer.writerow([
                    item["imsi"],
                    item["total_insert"],
                    item["total_query"],
                    item["total_delete"]
                ])
            return response
            # return Response(data={"estado": "ok", "mensaje": nombre_csv_creado}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"estado": "error", "mensaje": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ConsultarTDRViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        info = request.POST if request.POST else request.data if request.data else None
        # obtengo los parametros enviados en el request:
        codigo_imsi = info['imsi']
        codigo_imei = info['imei']
        fecha_desde = info['fecha_desde']
        fecha_hasta = info['fecha_hasta']

        if len(fecha_desde.strip()) == 0 or len(fecha_hasta.strip()) == 0:
            return Response(data='Los campos de fecha son obligatorios', status=status.HTTP_400_BAD_REQUEST)

        funcion = FunctionsListaNegra()
        data_response = funcion.consultarTdr(codigo_imsi, codigo_imei, fecha_desde, fecha_hasta)
        if data_response["estado"] == "ok":
            return Response(data=data_response, status=status.HTTP_200_OK)
        else:
            return Response(data=data_response, status=status.HTTP_400_BAD_REQUEST)


class ReporteTDRViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        info = request.POST if request.POST else request.data if request.data else None
        try:
            codigo_imsi = info['imsi']
            codigo_imei = info['imei']
            fecha_desde = info['fecha_desde']
            fecha_hasta = info['fecha_hasta']

            if len(fecha_desde.strip()) == 0 or len(fecha_hasta.strip()) == 0:
                return Response(data='Los campos de fecha son obligatorios', status=status.HTTP_400_BAD_REQUEST)

            funcion = FunctionsListaNegra()
            data_response = funcion.consultarTdr(codigo_imsi, codigo_imei, fecha_desde, fecha_hasta)
            if data_response["estado"] == "ok":

                response = HttpResponse(
                    content_type='text/csv',
                )
                response['Content-Disposition'] = 'attachment; filename="myfile.csv"'

                writer = csv.writer(response, delimiter="|")

                writer.writerow(
                    ['id', 'fecha', 'hora', 'central', 'imei', 'imsi', 'codigo1', 'codigo2', 'tecnologia'])

                for item in data_response['mensaje']:
                    writer.writerow([
                        item["id"],
                        item["fecha"],
                        item["hora"],
                        item["central"],
                        item["imei"],
                        item["imsi"],
                        item["codigo1"],
                        item["codigo2"],
                        item["tecnologia"]
                    ])
                return response
            else:
                return Response(data=data_response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={"estado": "error", "mensaje": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ConsultarDesBloquedosViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        funcion = FunctionsListaNegra()
        try:
            data_response = funcion.generarListaNegraDesbloqueadosTotal()
            return Response(data=data_response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"estado": "error", "mensaje": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ListaUsuariosApiActionsViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        funcion = FunctionsListaNegra()
        try:
            data_response = funcion.listaAccionApiUsuarios()
            return Response(data=data_response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"estado": "error", "mensaje": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UsuariosApiActionsViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        funcion = FunctionsListaNegra()
        info = request.POST if request.POST else request.data if request.data else None
        try:
            # Otengo la direccion remota
            ip_transaccion = funcion.obtenerDireccionIpRemota(request)
            data_response = funcion.registrarAccionApiUsuarios(info, ip_transaccion)
            return Response(data=data_response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"estado": "error", "mensaje": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UsuariosModificarApiActionsViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        funcion = FunctionsListaNegra()
        info = request.POST if request.POST else request.data if request.data else None
        try:
            # Otengo la direccion remota
            ip_transaccion = funcion.obtenerDireccionIpRemota(request)
            data_response = funcion.modificarAccionApiUsuarios(info, ip_transaccion)
            return Response(data=data_response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"estado": "error", "mensaje": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TopImsiFrequentlyViewSet(ViewSet):
    def list(self, request):
        funcion = FunctionsListaNegra()
        try:
            data = funcion.generarTopImsiTransaccionados()
            return Response(data={"estado": "ok", "data": data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"estado": "error", "mensaje": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ServiceCheckHeathViewSet(ViewSet):
    def list(self, request):
        funcion = FunctionsListaNegra()
        try:
            ip_remota = funcion.obtenerDireccionIpRemota(request)
            return Response(data={"estado": "ok", "ip": ip_remota}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"estado": "error", "mensaje": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
