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
            Q(fecha_bitacora__date__range=[data_request["fecha_inicio"], data_request["fecha_fin"]])
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
                    "fecha_bitacora": item_log.fecha_bitacora.strftime("%d/%m/%Y %H:%M:%S"),
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
                    "fecha_bitacora": item_log.fecha_bitacora.strftime("%d/%m/%Y %H:%M:%S"),
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

    def generarReporteGeneralLog(self, data_request):
        listado_log_bloqueados = log_aprov_eir.objects.filter(
            Q(fecha_bitacora__date__range=[data_request["fecha_inicio"], data_request["fecha_fin"]]))
        lista_reporte = []
        for item_log in listado_log_bloqueados:
            item_reporte = {
                "accion": item_log.accion,
                "imsi": item_log.imsi,
                "operadora": item_log.operadora,
                "lista": item_log.lista,
                "razon": item_log.razon,
                "origen": item_log.origen,
                "fecha_bitacora": item_log.fecha_bitacora.strftime("%d/%m/%Y %H:%M:%S"),
                "descripcion": item_log.descripcion,
                "usuario_descripcion": item_log.usuario_descripcion,
                "ip_transaccion": item_log.ip_transaccion
            }
            lista_reporte.append(item_reporte)

        # keys = lista_reporte[0].keys()

        path = apps.get_app_config('lista_negra').path
        config = open(path + r'/config/config.json')
        data_config = json.load(config)

        nombre_archivo_csv = "report_log_blocked_" + datetime.datetime.now().strftime(
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

    def generarSumario(self):
        lista_imsi = black_imsi.objects.all()
        # ahora se busca en logs, todos los insert y q existan en la tabla
        # lista_logs = log_aprov_eir.objects.all()
        contador_bloqueados = 0
        contador_desbloqueados = 0

        # for item in lista_logs:
        #     # existe = item.imsi in lista_imsi
        #     if item.accion == "INSERT" and item.descripcion == "Ingreso Ok":
        #         contador_bloqueados = contador_bloqueados + 1
        #     if lista_logs.filter(imsi=item.imsi).exists() and item.accion == "DELETE":
        #         contador_desbloqueados = contador_desbloqueados + 1
        total_bloqueados = log_aprov_eir.objects.filter(Q(accion="INSERT") & Q(descripcion="Ingreso Ok")).count()
        total_desbloqueados = log_aprov_eir.objects.filter(accion="DELETE").count()
        total = total_bloqueados + total_desbloqueados
        data_response = {
            "total_imsi": total,
            "total_bloqueados": total_bloqueados,
            "total_desbloqueados": total_desbloqueados
        }
        return data_response

    def generarSumarioDetallado(self, data_request):
        lista_resultados = []

        lista_log = log_aprov_eir.objects.filter(
            Q(fecha_bitacora__date__range=[data_request['fecha_inicio'], data_request['fecha_fin']]))
        for item_log in lista_log:
            total_insert = 0
            total_query = 0
            total_delete = 0
            if item_log.accion == 'INSERT' and item_log.descripcion == 'Ingreso Ok':
                total_insert = log_aprov_eir.objects.filter(
                    Q(imsi=item_log.imsi) & Q(accion='INSERT') & Q(descripcion='Ingreso Ok')).count()
            if item_log.accion == 'QUERY':
                total_query = log_aprov_eir.objects.filter(Q(imsi=item_log.imsi) & Q(accion='QUERY')).count()
            if item_log.accion == 'DELETE':
                total_delete = log_aprov_eir.objects.filter(Q(imsi=item_log.imsi) & Q(accion='DELETE')).count()
            data_resultados = {
                'imsi': item_log.imsi,
                'total_insert': total_insert,
                'total_query': total_query,
                'total_delete': total_delete
            }
            lista_resultados.append(data_resultados)

        return lista_resultados
