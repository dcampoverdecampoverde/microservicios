import datetime
import json

from django.apps import apps
from django.db.models import Q

from lista_negra.models import *


class FunctionsListaNegra():
    def obtenerDireccionIpRemota(self, request):
        user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if user_ip:
            ip_transaccion = user_ip.split(',')[0]
        else:
            ip_transaccion = request.META.get('REMOTE_ADDR')

        return ip_transaccion

    def generarReporteDesbloqueados(self, data_request):
        listado_log_bloqueados = log_aprov_eir.objects.filter(
            Q(fecha_bitacora__range=[data_request["fecha_inicio"], data_request["fecha_fin"]])
            &
            Q(accion="DELETE")
        )
        lista_reporte = []
        for item_log in listado_log_bloqueados:
            imsi_encontrado = black_imsi.objects.filter(imsi=item_log.imsi)
            if len(imsi_encontrado) == 0:
                item_reporte = {
                    "accion": item_log.accion,
                    "imsi": item_log.imsi,
                    "operadora": item_log.operadora,
                    "lista": item_log.lista,
                    "razon": item_log.razon,
                    "origen": item_log.origen,
                    "fecha_bitacora": item_log.fecha_bitacora,
                    "descripcion": item_log.descripcion,
                    "usuario_descripcion": item_log.usuario_descripcion,
                    "ip_transaccion": item_log.ip_transaccion
                }
                lista_reporte.append(item_reporte)

        # keys = lista_reporte[0].keys()

        path = apps.get_app_config('lista_negra').path
        config = open(path + r'/config/config.json')
        data_config = json.load(config)

        nombre_archivo_csv = "report_unblocked_" + datetime.datetime.now().strftime(
            "%Y%m%d%H%M%S") + ".csv"
        # dict_writer = None
        # with open(data_config["ruta_reportes"] + nombre_archivo_csv, 'w', newline='') as output_file:
        #    dict_writer = csv.DictWriter(output_file, keys, delimiter="|")
        #    dict_writer.writeheader()
        #    dict_writer.writerows(lista_reporte)

        data_response = {
            "lista_valores": lista_reporte,
            "nombre_archivo": nombre_archivo_csv,
            "ruta_reporte": data_config["ruta_reportes"]
        }
        return data_response

    def generarReporteBloqueados(self, data_request):
        listado_log_bloqueados = log_aprov_eir.objects.filter(
            Q(fecha_bitacora__date__range=[data_request["fecha_inicio"], data_request["fecha_fin"]])
            &
            Q(accion="INSERT")
        )
        lista_reporte = []
        for item_log in listado_log_bloqueados:
            imsi_encontrado = black_imsi.objects.filter(imsi=item_log.imsi)
            if len(imsi_encontrado) == 1:
                item_reporte = {
                    "accion": item_log.accion,
                    "imsi": item_log.imsi,
                    "operadora": item_log.operadora,
                    "lista": item_log.lista,
                    "razon": item_log.razon,
                    "origen": item_log.origen,
                    "fecha_bitacora": item_log.fecha_bitacora,
                    "descripcion": item_log.descripcion,
                    "usuario_descripcion": item_log.usuario_descripcion,
                    "ip_transaccion": item_log.ip_transaccion
                }
                lista_reporte.append(item_reporte)

        # keys = lista_reporte[0].keys()

        path = apps.get_app_config('lista_negra').path
        config = open(path + r'/config/config.json')
        data_config = json.load(config)

        nombre_archivo_csv = "report_blocked_" + datetime.datetime.now().strftime(
            "%Y%m%d%H%M%S") + ".csv"
        # dict_writer = None
        # with open(data_config["ruta_reportes"] + nombre_archivo_csv, 'w', newline='') as output_file:
        #    dict_writer = csv.DictWriter(output_file, keys, delimiter="|")
        #    dict_writer.writeheader()
        #    dict_writer.writerows(lista_reporte)

        data_response = {
            "lista_valores": lista_reporte,
            "nombre_archivo": nombre_archivo_csv,
            "ruta_reporte": data_config["ruta_reportes"]
        }
        return data_response
