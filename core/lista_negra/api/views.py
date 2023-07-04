import csv
import json

from django.apps import apps
from django.db import DatabaseError
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


class ListaNegraRegistroViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['imsi', 'source', 'user_id'],
            properties={
                'imsi': openapi.Schema(type=openapi.TYPE_STRING,
                                       description="Codigo IMSI que se va registrar",
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
                                         max_length=10),
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER,
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
        metodos = FunctionsListaNegra()
        info = request.POST if request.POST else request.data if request.data else None

        try:
            # Otengo la direccion remota
            ip_transaccion = metodos.obtenerDireccionIpRemota(request)

            # Evaluando los parametros recibidos:
            estado_parametros = validator.validator_parameters(info,
                                                               ['imsi', 'telco', 'reason', 'list', 'source', 'user_id'])

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
                log_imsi.grabar('INSERT', info["imsi"], info["telco"], info["list"], info["reason"], info["source"],
                                "error: " + message_validator_length_imsi,
                                info["user_id"], ip_transaccion)
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error", "mensaje": message_validator_length_imsi})

            serializer = ListaNegraRegistroSerializer(data=info)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                log_imsi.grabar('INSERT', info["imsi"], info["telco"], info["list"], info["reason"],
                                info["source"],
                                "Ingreso Ok",
                                info["user_id"],
                                ip_transaccion
                                )
                return Response(status=status.HTTP_200_OK, data={"estado": "ok", "mensaje": "operacion correcta"})
            else:
                log_imsi.grabar('INSERT', info["imsi"], info["telco"], info["list"], info["reason"],
                                info["source"],
                                serializer.errors,
                                info["user_id"],
                                ip_transaccion
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
            required=['imsi', 'source', 'user_id'],
            properties={
                'imsi': openapi.Schema(type=openapi.TYPE_STRING,
                                       description="Codigo IMSI que se va registrar",
                                       max_length=15),
                'source': openapi.Schema(type=openapi.TYPE_STRING,
                                         description="Se reciben los siguientes valores: {'api','front','bulk'}",
                                         max_length=10),
                'user_id': openapi.Schema(type=openapi.TYPE_STRING,
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
        metodos = FunctionsListaNegra()
        info = request.POST if request.POST else request.data if request.data else None

        try:

            # Otengo la direccion remota
            ip_transaccion = metodos.obtenerDireccionIpRemota(request)

            # Evaluando los parametros recibidos:
            estado_parametros = validator.validator_parameters(info,
                                                               ['imsi', 'source', 'user_id'])

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
                log_imsi.grabar('QUERY', info["imsi"], None, None, None, info["source"],
                                "error: " + message_validator_length_imsi,
                                info["user_id"], ip_transaccion)
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
                                info["user_id"],
                                ip_transaccion
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

    def list(self, request):
        try:
            serializer_data_imsi = ListaNegraSerializer(black_imsi.objects.all(), many=True)
            return Response(status=status.HTTP_200_OK, data=serializer_data_imsi.data)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})


class ListaNegraEliminarViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['imsi', 'source', 'reason', 'user_id'],
            properties={
                'imsi': openapi.Schema(type=openapi.TYPE_STRING,
                                       description="Codigo IMSI que se va registrar",
                                       max_length=15),
                'source': openapi.Schema(type=openapi.TYPE_STRING,
                                         description="Se reciben los siguientes valores: {'api','front','bulk'}",
                                         max_length=10),
                'reason': openapi.Schema(type=openapi.TYPE_STRING,
                                         description="Se indica el motivo por el caul se elimina el codigo IMSI",
                                         max_length=10),
                'user_id': openapi.Schema(type=openapi.TYPE_STRING,
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
        metodos = FunctionsListaNegra()
        info = request.POST if request.POST else request.data if request.data else None

        try:

            # Otengo la direccion remota
            ip_transaccion = metodos.obtenerDireccionIpRemota(request)

            # Evaluando los parametros recibidos:
            estado_parametros = validator.validator_parameters(info,
                                                               ['imsi', 'source', 'reason', 'user_id'])

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
                log_imsi.grabar('DELETE', info["imsi"], None, None, None, info["source"],
                                "error: " + message_validator_length_imsi,
                                info["user_id"],
                                ip_transaccion
                                )
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
                log_imsi.grabar('DELETE', info["imsi"], None, None, info["reason"], info["source"],
                                "Eliminacion Ok",
                                info["user_id"],
                                ip_transaccion
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

    def create(self, request):
        validator = ValidatorListaNegra()
        try:
            info = request.POST if request.POST else request.data if request.data else None

            serializer_log = LogSerializer(
                log_aprov_eir.objects.filter(usuario_descripcion=info['usuario_id']).order_by('-fecha_bitacora')[0:100],
                many=True)
            return Response(status=status.HTTP_200_OK, data=serializer_log.data)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})


class LogXIMSIViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

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
                log_aprov_eir.objects.filter(imsi=info['imsi']),
                many=True)
            return Response(status=status.HTTP_200_OK, data=serializer_log.data)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})


class ParametrosOperadoraView(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, reques):
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

    def list(self, reques):
        try:
            # Se hace una validacion de los parametros lista, operadora y origen
            # para verificar si se esta recibiendo los calores que corresponden
            # segun lo definido en el config.json
            # Windows
            # config = open(r'C:/Users/dcamp/OneDrive/Documentos/Proyecto_CLARO/Aplicativo/Job_Masivo/config.json')
            # Linux
            config = open(r'/var/www/html/jobs/config.json')
            data = json.load(config)
            data_response = {
                "estado": "ok",
                "mensaje": data["PATH_FTP_CSV"]
            }
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
        metodos = FunctionsListaNegra()
        info = request.POST if request.POST else request.data if request.data else None
        try:
            # Otengo la direccion remota
            ip_transaccion = metodos.obtenerDireccionIpRemota(request)

            data_request = {
                'estado': 'pendiente',
                'archivo_csv': info['nombre_archivo_csv'],
                'usuario_registro': info['usuario_id'],
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
            info["ip_actualizacion"] = metodos.obtenerDireccionIpRemota(request)
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

    def create(self, request):
        info = request.POST if request.POST else request.data if request.data else None
        try:
            funcion = FunctionsListaNegra()
            valores_data = funcion.generarReporteBloqueados(info)
            ruta_archivo = valores_data["ruta_reporte"] + valores_data["nombre_archivo"]
            # file_download = open(ruta_archivo, 'r')
            # response = HttpResponse(file_download, content_type='text/csv')
            # response['Content-Disposition'] = 'attachment; filename="{}"'.format(valores_data["nombre_archivo"])
            response = HttpResponse(
                content_type='text/csv',
            )
            response['Content-Disposition'] = 'attachment; filename="myfile.csv"'

            writer = csv.writer(response, delimiter="|")

            writer.writerow(
                ['accion', 'imsi', 'telco', 'list', 'reason', 'souce', 'datetime_operation', 'detail', 'user_id',
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

    def create(self, request):
        info = request.POST if request.POST else request.data if request.data else None
        try:
            funcion = FunctionsListaNegra()
            valores_data = funcion.generarReporteDesbloqueados(info)
            ruta_archivo = valores_data["ruta_reporte"] + valores_data["nombre_archivo"]
            # file_download = open(ruta_archivo, 'r')
            # response = HttpResponse(file_download, content_type='text/csv')
            # response['Content-Disposition'] = 'attachment; filename="{}"'.format(valores_data["nombre_archivo"])
            response = HttpResponse(
                content_type='text/csv',
            )
            response['Content-Disposition'] = 'attachment; filename="myfile.csv"'

            writer = csv.writer(response, delimiter="|")

            writer.writerow(
                ['accion', 'imsi', 'telco', 'list', 'reason', 'souce', 'datetime_operation', 'detail', 'user_id',
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

    def list(self, request):
        funcion = FunctionsListaNegra()
        try:
            data = funcion.generarSumario()
            return Response(data={"estado": "ok", "mensaje": data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"estado": "error", "mensaje": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        info = request.POST if request.POST else request.data if request.data else None
        try:
            funcion = FunctionsListaNegra()
            valores_data = funcion.generarReporteGeneralLog(info)
            ruta_archivo = valores_data["ruta_reporte"] + valores_data["nombre_archivo"]
            # file_download = open(ruta_archivo, 'r')
            # response = HttpResponse(file_download, content_type='text/csv')
            # response['Content-Disposition'] = 'attachment; filename="{}"'.format(valores_data["nombre_archivo"])
            response = HttpResponse(
                content_type='text/csv',
            )
            response['Content-Disposition'] = 'attachment; filename="myfile.csv"'

            writer = csv.writer(response, delimiter="|")

            writer.writerow(
                ['accion', 'imsi', 'telco', 'list', 'reason', 'souce', 'datetime_operation', 'detail', 'user_id',
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

    def create(self, request):
        info = request.POST if request.POST else request.data if request.data else None
        try:
            funcion = FunctionsListaNegra()
            valores_data = funcion.generarSumarioDetallado(info)

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
