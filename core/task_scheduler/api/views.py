import datetime
import json

from django.apps import apps
from drf_yasg import openapi
from drf_yasg.openapi import FORMAT_DATE
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from task_scheduler.api.functions import FuncionesGenerales
from task_scheduler.api.serializers import *


class ConsultaListaJobsViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para mostrar listado de jobs existentes en el sistema',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(type=openapi.TYPE_STRING)
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
        try:
            # Se hace lectura de archivo json de configuracion de lista de jobs
            path = apps.get_app_config('task_scheduler').path
            config = open(path + r'/config/data_config.json')
            data = json.load(config)
            tipo_seleccionado = request.GET.get("tipo")
            if tipo_seleccionado is None or tipo_seleccionado == '':
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data="Error, falta enviar el parametro {tipo} y/o tenga un valor")
            else:
                data_response = list(filter(lambda x: x["tipo"] == tipo_seleccionado, data["lista_jobs"]))
                return Response(status=status.HTTP_200_OK, data=data_response)

        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})


class RegistrarProgramadorTareaViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para actualizar estado de un registro del proceso masivo IMEI Bulk',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['estado', 'nombre_tarea', 'dias_semana', 'tipo_horario', 'horario_rango',
                      'job_ejecutar', 'job_descripcion', 'emails_notificacion', 'tipo',
                      'usuario_registro', 'terminal_registro'],
            properties={
                'estado': openapi.Schema(type=openapi.TYPE_STRING,
                                         description="Estado del proceso. Posible valores {A, I}"
                                         ),
                'nombre_tarea': openapi.Schema(type=openapi.TYPE_STRING,
                                               description="nombre de la tarea que se esta creando"),
                'dias_semana': openapi.Schema(type=openapi.TYPE_STRING,
                                              description="Arreglo de numeros donde se indica los dias semana",
                                              example="2,3,5"),
                'tipo_horario': openapi.Schema(type=openapi.TYPE_STRING,
                                               description="Tipo de horario. Posibles valores {U=unico, R=rango}",
                                               example="U"),
                'horario_rango': openapi.Schema(type=openapi.TYPE_STRING,
                                                description="Horario en rango, separado por simbolo ;",
                                                example="09:00;13:00"),
                'job_ejecutar': openapi.Schema(type=openapi.TYPE_STRING,
                                               description="Id de job seleccionado"),
                'job_descripcion': openapi.Schema(type=openapi.TYPE_STRING,
                                                  description="Nombde de job seleccionado"),
                'emails_notificacion': openapi.Schema(type=openapi.TYPE_STRING,
                                                      description="Listado de direcciones emails a quien se va a notificar la ejecucion de las tareas. Cada email debe estar por ,"),
                'tipo_job': openapi.Schema(type=openapi.TYPE_STRING,
                                           description="Tipo de Job que se esta registrando. Posible valores {imsi} o {imei}",
                                           example="imsi"),
                'usuario_registro': openapi.Schema(type=openapi.TYPE_STRING,
                                                   description="Usuario que esta realizando operacion. (Se tomara el usuario que tiene la sesion iniciada)"),
                'terminal_registro': openapi.Schema(type=openapi.TYPE_STRING,
                                                    description="Direccion IP donde se esta ejecutando el proceso. (Se tomara la direcion del usuario que tiene la sesion iniciada)"),
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
        info = request.POST if request.POST else request.data if request.data else None
        funciones = FuncionesGenerales()
        try:
            print(info)

            # Obtengo el usuario que ha iniciado sesion
            usuario_sesion = funciones.obtenerUsuarioSesionToken(request)

            # Obtengo la direccion ip de donde se hace la peticion
            direccion_ip = funciones.obtenerDireccionIpRemota(request)

            if info["id"] is None:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"estado": "error", "mensaje": "el campo ID no puede ir vacio"})

            # obj_programador = programador_jobs.objects.get(id=info["id"])
            # if obj_programador is None:
            data_request = {
                "estado": info["estado"],
                "nombre_tarea": info["nombre_tarea"],
                "dias_semana": info["dias_semana"],
                "tipo_horario": info["tipo_horario"],
                "horario_rango": info["horario_rango"],
                "job_ejecutar": info["job_ejecutar"],
                "job_descripcion": info["job_descripcion"],
                "emails_notificacion": info["emails_notificacion"],
                "tipo": info["tipo_job"],
                "usuario_registro": usuario_sesion["username"],
                "terminal_registro": direccion_ip,
                "num_veces": 1
            }
            serializer = TareaJobRegistroSerializer(data=data_request)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            return Response(status=status.HTTP_200_OK, data={"estado": "ok", "mensaje": "operacion correcta"})
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})


class ConsultarListadoTaskJobViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para consultar Listado Tareas registradas',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'data': openapi.Schema(type=openapi.TYPE_STRING),
                    'status': openapi.Schema(type=openapi.TYPE_STRING)
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
        funciones = FuncionesGenerales()
        try:

            serializer = TareaJobListaSerializer(programador_jobs.objects.all(), many=True)
            data_task = serializer.data
            dias_semana_nombres = ""
            indice = 0
            data_response = []
            for item in data_task:
                item["dias_semana_numeros"] = ""
                item["dias_semana_numeros"] = item["dias_semana"]

                dias_array = item["dias_semana"].split(",")
                for item_diaSemana in dias_array:
                    print(item_diaSemana)
                    if item_diaSemana is not None:
                        dias_semana_nombres = dias_semana_nombres + ", " + funciones.switchDiasSemana(item_diaSemana)
                item["dias_semana"] = dias_semana_nombres
                item_response = {
                    "id": item["id"],
                    "estado": item["estado"],
                    "estado_ejecucion": item["estado_ejecucion"],
                    "nombre_tarea": item["nombre_tarea"],
                    "dias_semana": item["dias_semana"],
                    "dias_semana_numeros": item["dias_semana_numeros"],
                    "tipo_horario": item["tipo_horario"],
                    "horario_rango": item["horario_rango"],
                    "job_descripcion": item["job_descripcion"],
                    "job_ejecutar": item["job_ejecutar"],
                    "emails_notificacion": item["emails_notificacion"],
                    "fecha_ultima_ejecucion": item["fecha_ultima_ejecucion"],
                    "observaciones": item["observaciones"],
                    "usuario_registro": item["usuario_registro"],
                    "terminal_registro": item["terminal_registro"],
                    "fecha_registro": item["fecha_registro"],
                    "usuario_modificacion": item["usuario_modificacion"],
                    "terminal_modificacion": item["terminal_modificacion"],
                    "fecha_modificacion": item["fecha_modificacion"],

                }
                data_response.append(item_response)
                dias_semana_nombres = ""

            return Response(status=status.HTTP_200_OK, data={"estado": "ok", "data": data_response})
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})


class ActualizarTaskJobViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para actualizar Tarea Progamada',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['estado', 'tipo_horario', 'dias_semana', 'horario_rango', 'emails_notificacion',
                      'usuario_modificacion', 'terminal_modificacion', 'fecha_modificacion'],
            properties={
                'estado': openapi.Schema(type=openapi.TYPE_STRING,
                                         description="Estado del proceso. Posible valores {procesando, finalizado, pendiente}"
                                         ),
                'dias_semana': openapi.Schema(type=openapi.TYPE_STRING,
                                              description="Arreglo de numeros donde se indica los dias semana",
                                              example="2,3,5"),
                'tipo_horario': openapi.Schema(type=openapi.TYPE_STRING,
                                               description="Tipo de horario. Posibles valores {U=unico, R=rango}",
                                               example="U"),
                'horario_rango': openapi.Schema(type=openapi.TYPE_STRING,
                                                description="Horario en rango, separado por simbolo ;",
                                                example="09:00;13:00"),
                'emails_notificacion': openapi.Schema(type=openapi.TYPE_STRING,
                                                      description="Listado de direcciones emails a quien se va a notificar la ejecucion de las tareas. Cada email debe estar por ,"),
                'usuario_modificacion': openapi.Schema(type=openapi.TYPE_STRING,
                                                       description="Usuario que esta realizando operacion. (Se tomara el usuario que tiene la sesion iniciada)"),
                'terminal_modificacion': openapi.Schema(type=openapi.TYPE_STRING,
                                                        description="Direccion IP donde se esta ejecutando el proceso. (Se tomara la direcion del usuario que tiene la sesion iniciada)"),
                'fecha_modificacion': openapi.Schema(type=openapi.TYPE_STRING, format=FORMAT_DATE,
                                                     description="Direccion IP donde se esta ejecutando el proceso. (Se tomara la direcion del usuario que tiene la sesion iniciada)")
                # 'visit_at': openapi.Schema(type=openapi.TYPE_STRING,
                #                           format=FORMAT_DATE)
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'data': openapi.Schema(type=openapi.TYPE_STRING),
                    'status': openapi.Schema(type=openapi.TYPE_STRING)
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
    def create(self, request, pk=None):
        info = request.POST if request.POST else request.data if request.data else None
        funciones = FuncionesGenerales()
        try:
            # usuario_sesion = funciones.obtenerUsuarioSesionToken(request)
            data_user = funciones.obtenerUsuarioSesionToken(request)
            obj_task = programador_jobs.objects.get(id=info["id"])
            if obj_task is None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=f"No existe una tarea con el ID {info['id']}")
            else:
                info["usuario_modificacion"] = data_user["username"]
                info["terminal_modificacion"] = funciones.obtenerDireccionIpRemota(request)
                info["fecha_modificacion"] = datetime.datetime.now()

                serializer = TareaJobActualizarSerializer(obj_task, data=info, partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response(status=status.HTTP_200_OK, data={"estado": "ok", "mensaje": "operacion correcta"})
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST,
                                    data={"estado": "error", "mensaje": serializer.errors})

        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))


class ActualizarEstadoTaskJobViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para actualizar estado de ejecucion de tarea',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'estado_ejecucion', 'fecha_modificacion', 'fecha_ultima_ejecucion'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING,
                                     description="Estado del proceso. Posible valores {procesando, finalizado, pendiente}"
                                     ),
                'estado_ejecucion': openapi.Schema(type=openapi.TYPE_STRING,
                                                   description="Estado de la tarea. Posible valores {'running'=en_proceso, ''=sin actividad}"),
                'fecha_modificacion': openapi.Schema(type=openapi.TYPE_STRING, format=FORMAT_DATE,
                                                     description="Fecha Modificacion"),
                'fecha_ultima_ejecucion': openapi.Schema(type=openapi.TYPE_STRING, format=FORMAT_DATE,
                                                         description="Fecha Ultima ejecucion tarea")
                # 'visit_at': openapi.Schema(type=openapi.TYPE_STRING,
                #                           format=FORMAT_DATE)
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'data': openapi.Schema(type=openapi.TYPE_STRING),
                    'status': openapi.Schema(type=openapi.TYPE_STRING)
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
    def create(self, request, pk=None):
        info = request.POST if request.POST else request.data if request.data else None
        funciones = FuncionesGenerales()
        try:
            # usuario_sesion = funciones.obtenerUsuarioSesionToken(request)
            data_user = funciones.obtenerUsuarioSesionToken(request)
            obj_task = programador_jobs.objects.get(id=info["id"])
            if obj_task is None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=f"No existe una tarea con el ID {info['id']}")
            else:
                obj_task.estado_ejecucion = info["estado_ejecucion"]
                obj_task.usuario_modificacion = data_user["username"]
                obj_task.terminal_modificacion = funciones.obtenerDireccionIpRemota(request)
                obj_task.fecha_modificacion = info["fecha_modificacion"]
                if info["fecha_ultima_ejecucion"] is not None:
                    obj_task.fecha_ultima_ejecucion = info["fecha_ultima_ejecucion"]
                obj_task.save()
                return Response(status=status.HTTP_200_OK, data="operacion correcta")

        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))


class ConsultarListaParametrosTargetViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para consultar Listado Parametros Target',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'data': openapi.Schema(type=openapi.TYPE_STRING),
                    'status': openapi.Schema(type=openapi.TYPE_STRING)
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
        try:
            path = apps.get_app_config('lista_negra').path
            config = open(path + r'/config/config.json')
            data = json.load(config)
            data_response = data["valores_target"]

            return Response(status=status.HTTP_200_OK, data={"estado": "ok", "data": data_response})
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})


class EliminarTaskJobViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='API para eliminar una tarea',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING,
                                     description="Id de la tarea"
                                     )
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'data': openapi.Schema(type=openapi.TYPE_STRING),
                    'status': openapi.Schema(type=openapi.TYPE_STRING)
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
    def create(self, request, pk=None):
        info = request.POST if request.POST else request.data if request.data else None
        funciones = FuncionesGenerales()
        try:
            # usuario_sesion = funciones.obtenerUsuarioSesionToken(request)
            data_user = funciones.obtenerUsuarioSesionToken(request)
            if data_user["superuser"] == False:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data="Solo el usuario que tien el rol de superuser puede eliminar una tarea.")

            obj_task = programador_jobs.objects.get(id=info["id"])
            if obj_task is None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=f"No existe una tarea con el ID {info['id']}")
            else:
                if obj_task.estado_ejecucion == "running":
                    return Response(status=status.HTTP_400_BAD_REQUEST,
                                    data=f"La tarea se encuentra en ejecucion y no puede ser eliminada. Intente despues")

                obj_task.estado = "E"
                obj_task.usuario_modificacion = data_user["username"]
                obj_task.terminal_modificacion = funciones.obtenerDireccionIpRemota(request)
                obj_task.fecha_modificacion = datetime.datetime.now()
                obj_task.save()
                return Response(status=status.HTTP_200_OK, data="operacion correcta")

        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))
