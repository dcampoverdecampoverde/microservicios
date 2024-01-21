import datetime
import json

from django.apps import apps
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from task_scheduler.api.functions import FuncionesGenerales
from task_scheduler.api.serializers import *


class ConsultaListaJobsViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        try:
            # Se hace lectura de archivo json de configuracion de lista de jobs
            path = apps.get_app_config('task_scheduler').path
            config = open(path + r'/config/data_config.json')
            data = json.load(config)
            data_response = data["lista_jobs"]
            return Response(status=status.HTTP_200_OK, data=data_response)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})


class RegistrarProgramadorTareaViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

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
                "usuario_registro": usuario_sesion["username"],
                "terminal_registro": direccion_ip
            }
            serializer = TareaJobRegistroSerializer(data=data_request)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            return Response(status=status.HTTP_200_OK, data={"estado": "ok", "mensaje": "operacion correcta"})
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"estado": "error", "mensaje": str(e)})


class ConsultarListadoTaskJobViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

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
