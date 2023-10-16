import csv
import logging as log

from django.db import DatabaseError
from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.openapi import FORMAT_DATE
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from imei.api.serializers import *
from imei.functions.function_listanegra_imei import FunctionsListaNegraImei
from imei.registro_log import RegistroLog
from imei.validators.imei_request_validator import *

log.basicConfig(level=log.DEBUG,
                format='%(asctime)s: %(levelname)s [%(filename)s:%(lineno)s] %(message)s',
                handlers=[
                    log.FileHandler(apps.get_app_config('lista_negra').path + r'/logs/log_api_lista_negra.log'),
                    log.StreamHandler()
                ])


class ImeiBlackRegistroViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para registrar un IMEI en lista negra',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['imei'],
            properties={
                'imei': openapi.Schema(type=openapi.TYPE_NUMBER,
                                       description="Codigo IMEI que se va registrar",
                                       example=123456789012345,
                                       max_length=15),
                'telco': openapi.Schema(type=openapi.TYPE_STRING,
                                        description="Se reciben valores {'claro','telefonica','cnt','otros','masivo' }",
                                        max_length=15),
                'list': openapi.Schema(type=openapi.TYPE_STRING,
                                       description="Se reciben valores {'blanca','gris','negra'}",
                                       max_length=10),
                'reason': openapi.Schema(type=openapi.TYPE_STRING,
                                         description="Descripcion cual fue el motivo del bloqueo del codigo IMEI",
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
        log_imei = RegistroLog()
        validator = ImeiRequestValidator()
        metodos = FunctionsListaNegraImei()
        info = request.POST if request.POST else request.data if request.data else None

        try:
            # registrando en log el request enviando
            log.info(f"request registro_imei: {str(info)}")

            # Obtengo la sesion del usuario que esta conectado
            data_user = metodos.obtenerUsuarioSesionToken(request)

            # Otengo la direccion remota
            ip_transaccion = metodos.obtenerDireccionIpRemota(request)

            """
            # Evaluando los parametros recibidos:
            estado_parametros = validator.validator_parameters(info,
                                                               ['imei', 'telco', 'reason', 'list', 'source'])

            if estado_parametros == False:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": "no se reconoce uno de los parametros enviados en la trama. Por favor revise la documentacion"})
            """

            # Evaluando que el valor reason tenga un valor
            """
            if len(info["reason"].strip()) <= 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": "falta ingresar un motivo"})
            """

            # Evaluando Operadora
            """
            message_validator_request_operadora = validator.validator_parameter_operadora(info['telco'])
            if len(message_validator_request_operadora) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": message_validator_request_operadora})
            """
            # Evaluando Origen
            """
            message_validator_request_origen = validator.validator_parameter_origen(info['source'])
            if len(message_validator_request_origen) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": message_validator_request_origen})
            """
            # Evaluando Lista
            """
            message_validator_request_lista = validator.validator_parameter_lista(info['list'])
            if len(message_validator_request_lista) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": message_validator_request_lista})
            """
            # Evaluando que el codigo IMSI sea solo numeros
            message_validator_request_onlynumber = validator.validator_onlynumber_imei(info['imei'])
            if len(message_validator_request_onlynumber) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": message_validator_request_onlynumber})

            # Evaluando longitud del codigo IMSI
            message_validator_length_imsi = validator.validator_length_imei(info['imei'])
            if len(message_validator_length_imsi) > 0:
                # log_imsi.grabar('INSERT', info["imsi"], info["telco"], info["list"], info["reason"], info["source"],
                #                "error: " + message_validator_length_imsi,
                #                data_user["username"], ip_transaccion)
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error", "mensaje": message_validator_length_imsi})

            serializer = ImeiRegistroSerializer(data=info)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                log_imei.grabar('INSERT', info["imei"], info["telco"], info["list"], info["reason"],
                                info["source"],
                                "Ingreso Ok",
                                data_user["username"],
                                ip_transaccion, log
                                )
                return Response(status=status.HTTP_200_OK, data={"estado": "ok", "mensaje": "operacion correcta"})
            else:
                log_imei.grabar('INSERT', info["imei"], info["telco"], info["list"], info["reason"],
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


class ImeiBlackConsultaViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para consultar IMEI registrado en lista negra',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['imei', 'source'],
            properties={
                'imsi': openapi.Schema(type=openapi.TYPE_NUMBER,
                                       description="Codigo IMEI que se va registrar",
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
                    'imei': openapi.Schema(type=openapi.TYPE_STRING),
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

        log_imei = RegistroLog()
        validator = ImeiRequestValidator()
        metodos = FunctionsListaNegraImei()
        info = request.POST if request.POST else request.data if request.data else None

        try:

            # registrando en log el request enviando
            log.info(f"request consulta_imei: {str(info)}")

            # Obtengo la sesion del usuario que esta conectado
            data_user = metodos.obtenerUsuarioSesionToken(request)

            # Otengo la direccion remota
            ip_transaccion = metodos.obtenerDireccionIpRemota(request)

            # Evaluando los parametros recibidos:
            estado_parametros = validator.validator_parameters(info, ['imei', 'source'])

            if estado_parametros == False:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": "no se reconoce uno de los parametros enviados en la trama. Por favor revise la documentacion"})

            # Evaluando que el codigo IMSI sea solo numeros
            message_validator_request_onlynumber = validator.validator_onlynumber_imei(info['imei'])
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
            message_validator_length_imsi = validator.validator_length_imei(info['imei'])
            if len(message_validator_length_imsi) > 0:
                # log_imsi.grabar('QUERY', info["imsi"], None, None, None, info["source"],
                #                "error: " + message_validator_length_imsi,
                #                data_user["username"], ip_transaccion)
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error", "mensaje": message_validator_length_imsi})

            # Validando si existe o no el IMSI
            value_validator_exists_imei = validator.validator_exists_imei(info['imei'])
            if value_validator_exists_imei:
                serializer_data_imsi = ImeiConsultarSerializer(black_gray_list.objects.filter(imei=info['imei']),
                                                               many=True)
                data_response = {
                    "estado": "ok",
                    "mensaje": "ok",
                    "data": serializer_data_imsi.data,
                }
                log_imei.grabar('QUERY', info["imei"], None, None, None, info["source"],
                                "Consulta Ok",
                                data_user["username"],
                                ip_transaccion, log
                                )
                return Response(status=status.HTTP_200_OK, data=data_response)
            else:
                data_response = {
                    "estado": "no_exists",
                    "mensaje": "Codigo IMEI No existe",
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
                                         'imei': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                description='Codigo IMEI'),
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
        metodos = FunctionsListaNegraImei()
        try:
            # serializer_data_imsi = ListaNegraSerializer(black_imsi.objects.all(), many=True)
            data_lista_negra = metodos.generarListaNegraTotal()
            return Response(status=status.HTTP_200_OK, data=data_lista_negra)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})


class ImeiBlackEliminarViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para eliminar IMEI registrado en lista negra',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['imei', 'source', 'reason'],
            properties={
                'imei': openapi.Schema(type=openapi.TYPE_NUMBER,
                                       description="Codigo IMEI que se va registrar",
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
        log_imei = RegistroLog()
        validator = ImeiRequestValidator()
        metodos = FunctionsListaNegraImei()
        info = request.POST if request.POST else request.data if request.data else None

        try:

            # registrando en log el request enviando
            log.info(f"request eliminar_imei: {str(info)}")

            # Obtengo la sesion del usuario que esta conectado
            data_user = metodos.obtenerUsuarioSesionToken(request)

            # Otengo la direccion remota
            ip_transaccion = metodos.obtenerDireccionIpRemota(request)

            # Evaluando los parametros recibidos:
            estado_parametros = validator.validator_parameters(info,
                                                               ['imei', 'source', 'reason'])

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
            message_validator_length_imei = validator.validator_length_imei(info['imei'])
            if len(message_validator_length_imei) > 0:
                # log_imsi.grabar('DELETE', info["imsi"], None, None, None, info["source"],
                #                "error: " + message_validator_length_imsi,
                #                data_user["username"],
                #                ip_transaccion
                #               )
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error", "mensaje": message_validator_length_imei})

            # Evaluando que el codigo IMSI sea solo numeros
            message_validator_request_onlynumber = validator.validator_onlynumber_imei(info['imei'])
            if len(message_validator_request_onlynumber) > 0:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error",
                                      "mensaje": message_validator_request_onlynumber})

            # Evaluando si existe el codigo IMSI
            value_validator_exists_imei = validator.validator_exists_imei(info['imei'])
            if value_validator_exists_imei:
                obj_listanegra = black_gray_list.objects.get(pk=info["imei"])
                obj_listanegra.delete()

                log_imei.grabar('DELETE', info["imei"], None, None, info["reason"], info["source"],
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
                    "mensaje": "Codigo IMEI No existe"
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
                                                                  description='Accion realizada sobre el codigo IMEI',
                                                                  example="INSERT"),
                                         'imei': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                description='Codigo IMEI', example=123456789012345),
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
        metodos = FunctionsListaNegraImei()
        try:

            # Obtengo la sesion del usuario que esta conectado
            data_user = metodos.obtenerUsuarioSesionToken(request)

            serializer_log = LogImeiSerializer(
                log_imei_eir.objects.filter(usuario_descripcion=data_user['username']).order_by('-fecha_bitacora')[
                0:100],
                many=True)
            return Response(status=status.HTTP_200_OK, data=serializer_log.data)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})


class ImeiBlackMasivoViewSet(ViewSet):
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
            serializer = ImeiMasivoSerializer(
                files_imei_bulk.objects.all().order_by('-fecha_archivo_procesando'),
                many=True)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except Exception as e:
            data_response = {
                'estado': 'error',
                'mensaje': str(e)
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data=data_response)

    @swagger_auto_schema(
        operation_description='API para registrar un IMEI masivo a Lista Negra',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['nombre_archivo_csv'],
            properties={
                'nombre_archivo_csv': openapi.Schema(type=openapi.TYPE_STRING,
                                                     description="Nombre archivo csv que se va a procesar",
                                                     example='mi_archivo.csv',
                                                     max_length=50),
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

        metodos = FunctionsListaNegraImei()
        info = request.POST if request.POST else request.data if request.data else None
        try:
            # registrando en log el request enviando
            log.info(f"request registro_imei_masivo: {str(info)}")

            # Obtengo la sesion del usuario conectado
            data_user = metodos.obtenerUsuarioSesionToken(request)

            # Otengo la direccion remota
            ip_transaccion = metodos.obtenerDireccionIpRemota(request)

            data_request = {
                'estado': 'pendiente',
                'archivo_csv': info['nombre_archivo_csv'],
                'usuario_registro': data_user['username'],
                'ip_registro': ip_transaccion
            }
            serializer = ImeiMasivoRegistroSerializer(data=data_request)
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
        metodos = FunctionsListaNegraImei()
        info = request.POST if request.POST else request.data if request.data else None
        try:
            # registrando en log el request enviando
            log.info(f"request actualizacion_imei_masivo: {str(info)}")

            # Obtengo la sesion del usuario conectado
            data_user = metodos.obtenerUsuarioSesionToken(request)

            # aqui se obtiene la direccion IP remota
            info["ip_actualizacion"] = metodos.obtenerDireccionIpRemota(request)
            info["usuario_actualizacion"] = data_user["username"]

            obj_fileprocessbulk = files_imei_bulk.objects.get(pk=pk)
            serializer = ImeiMasivoActualizarSerializer(obj_fileprocessbulk, data=info, partial=True)
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


class ImeiBlackReporteBloqueadoViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para generar archivo CSV de todos los IMEI bloqueados',
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
            funcion = FunctionsListaNegraImei()
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
                ['accion', 'imei', 'telco', 'list', 'reason', 'source', 'datetime_operation', 'detail', 'user_id',
                 'source_ip'])

            for item in valores_data["lista_valores"]:
                writer.writerow([
                    item["accion"],
                    item["imei"],
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


class ImeiBlackReporteDesbloqueadoViewSet(ViewSet):
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
            funcion = FunctionsListaNegraImei()
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
                ['accion', 'imei', 'telco', 'list', 'reason', 'source', 'datetime_operation', 'detail', 'user_id',
                 'source_ip'])

            for item in valores_data["lista_valores"]:
                writer.writerow([
                    item["accion"],
                    item["imei"],
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


class ImeiBlackReporteGeneralLogViewSet(ViewSet):
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
        funcion = FunctionsListaNegraImei()
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
            funcion = FunctionsListaNegraImei()
            valores_data = funcion.generarReporteGeneralLog(info)
            response = HttpResponse(
                content_type='text/csv',
            )
            response['Content-Disposition'] = 'attachment; filename="myfile.csv"'

            writer = csv.writer(response, delimiter="|")

            writer.writerow(
                ['accion', 'imei', 'telco', 'list', 'reason', 'source', 'datetime_operation', 'detail', 'user_id',
                 'source_ip'])

            for item in valores_data["lista_valores"]:
                writer.writerow([
                    item["accion"],
                    item["imei"],
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
