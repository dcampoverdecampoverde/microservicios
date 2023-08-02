from django.db.models import Q
from rest_framework_simplejwt.authentication import JWTAuthentication

from lista_negra.api.serializers import LogSerializer, TdrSerializer
from lista_negra.models import *


class FunctionsListaNegra():

    def obtenerUsuarioSesionToken(self, request):
        JWT_authenticator = JWTAuthentication()
        response = JWT_authenticator.authenticate(request)
        user, token = response
        usuario_descripcion = user.username
        usuario_id = token.payload["user_id"]
        data_response = {
            'username': usuario_descripcion,
            'id': usuario_id
        }
        return data_response

    def obtenerDireccionIpRemota(self, request):
        user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if user_ip:
            ip_transaccion = user_ip.split(',')[0]
        else:
            ip_transaccion = request.META.get('REMOTE_ADDR')

        return ip_transaccion

    def generarReporteDesbloqueados(self, data_request):
        serializer_log = LogSerializer(log_aprov_eir.objects.filter(
            Q(fecha_bitacora__date__range=[data_request["fecha_inicio"], data_request["fecha_fin"]])
            &
            Q(accion="DELETE"),
        ).order_by('-fecha_bitacora'), many=True)
        data_log = serializer_log.data
        lista_reporte = []
        for item_log in data_log:
            imsi_encontrado = black_imsi.objects.filter(imsi=item_log['imsi'])
            if len(imsi_encontrado) == 0:
                item_reporte = {
                    "accion": item_log['accion'],
                    "imsi": item_log['imsi'],
                    "operadora": item_log['operadora'],
                    "lista": item_log['lista'],
                    "razon": item_log['razon'],
                    "origen": item_log['origen'],
                    "fecha_bitacora": item_log['fecha_bitacora'],
                    "descripcion": item_log['descripcion'],
                    "usuario_descripcion": item_log['usuario_descripcion'],
                    "ip_transaccion": item_log['ip_transaccion']
                }
                lista_reporte.append(item_reporte)

        # keys = lista_reporte[0].keys()

        nombre_archivo_csv = "report_unblocked.csv"

        data_response = {
            "lista_valores": lista_reporte,
            "nombre_archivo": nombre_archivo_csv,
            "ruta_reporte": ""
        }
        return data_response

    def generarReporteBloqueados(self, data_request):
        serializer_log = LogSerializer(log_aprov_eir.objects.filter(
            Q(fecha_bitacora__date__range=[data_request["fecha_inicio"], data_request["fecha_fin"]])
            &
            Q(accion="INSERT")
            &
            Q(descripcion="Ingreso Ok")
        ).order_by('-fecha_bitacora'), many=True)
        data_log = serializer_log.data
        lista_reporte = []
        for item_log in data_log:
            imsi_encontrado = black_imsi.objects.filter(imsi=item_log['imsi'])
            if len(imsi_encontrado) == 1:
                item_reporte = {
                    "accion": item_log['accion'],
                    "imsi": item_log['imsi'],
                    "operadora": item_log['operadora'],
                    "lista": item_log['lista'],
                    "razon": item_log['razon'],
                    "origen": item_log['origen'],
                    "fecha_bitacora": item_log['fecha_bitacora'],
                    "descripcion": item_log['descripcion'],
                    "usuario_descripcion": item_log['usuario_descripcion'],
                    "ip_transaccion": item_log['ip_transaccion']
                }
                lista_reporte.append(item_reporte)

        nombre_archivo_csv = "report_blocked.csv"
        # dict_writer = None
        # with open(data_config["ruta_reportes"] + nombre_archivo_csv, 'w', newline='') as output_file:
        #    dict_writer = csv.DictWriter(output_file, keys, delimiter="|")
        #    dict_writer.writeheader()
        #    dict_writer.writerows(lista_reporte)

        data_response = {
            "lista_valores": lista_reporte,
            "nombre_archivo": nombre_archivo_csv,
            "ruta_reporte": ""
        }
        return data_response

    def generarReporteGeneralLog(self, data_request):
        serializer_log = LogSerializer(log_aprov_eir.objects.filter(
            Q(fecha_bitacora__date__range=[data_request["fecha_inicio"], data_request["fecha_fin"]])).order_by(
            '-fecha_bitacora'), many=True)
        data_log = serializer_log.data
        lista_reporte = []
        for item_log in data_log:
            item_reporte = {
                "accion": item_log['accion'],
                "imsi": item_log['imsi'],
                "operadora": item_log['operadora'],
                "lista": item_log['lista'],
                "razon": item_log['razon'],
                "origen": item_log['origen'],
                "fecha_bitacora": item_log['fecha_bitacora'],
                "descripcion": item_log['descripcion'],
                "usuario_descripcion": item_log['usuario_descripcion'],
                "ip_transaccion": item_log['ip_transaccion']
            }
            lista_reporte.append(item_reporte)

        # keys = lista_reporte[0].keys()

        nombre_archivo_csv = "report_log_blocked.csv"
        # dict_writer = None
        # with open(data_config["ruta_reportes"] + nombre_archivo_csv, 'w', newline='') as output_file:
        #    dict_writer = csv.DictWriter(output_file, keys, delimiter="|")
        #    dict_writer.writeheader()
        #    dict_writer.writerows(lista_reporte)

        data_response = {
            "lista_valores": lista_reporte,
            "nombre_archivo": nombre_archivo_csv,
            "ruta_reporte": ""
        }
        return data_response

    def generarSumario(self):
        # lista_imsi = black_imsi.objects.all()
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
        total_bloqueados = black_imsi.objects.all().count()
        total_desbloqueados = log_aprov_eir.objects.filter(accion="DELETE").count()
        total = total_bloqueados + total_desbloqueados
        data_response = {
            "total_imsi": total,
            "total_bloqueados": total_bloqueados,
            "total_desbloqueados": total_desbloqueados
        }
        return data_response

    def generarListaNegraTotal(self):
        logs = log_aprov_eir.objects.filter(
            Q(accion='INSERT')).distinct('imsi')

        data_response = []
        for item_log in logs:
            if black_imsi.objects.filter(imsi=item_log.imsi).exists():
                serializer_log = LogSerializer(
                    log_aprov_eir.objects.filter(Q(imsi=item_log.imsi) & Q(accion='INSERT')), many=True)
                data_log = serializer_log.data
                for item_serializer in data_log:
                    data = {
                        'imsi': item_serializer['imsi'],
                        'fecha': item_serializer['fecha_bitacora'],  # .strftime("%d/%m/%Y %H:%M:%S"),
                        'usuario': item_serializer['usuario_descripcion']
                    }
                data_response.append(data)

        return data_response

    def generarListaNegraDesbloqueadosTotal(self):
        logs = log_aprov_eir.objects.filter(Q(accion='DELETE')).distinct('imsi')
        data_response = []
        for item_log in logs:
            if not black_imsi.objects.filter(imsi=item_log.imsi).exists():
                serializer_log = LogSerializer(
                    log_aprov_eir.objects.filter(Q(imsi=item_log.imsi) & Q(accion='DELETE')), many=True)
                data_log = serializer_log.data
                for item_serializer in data_log:
                    data = {
                        'imsi': item_serializer['imsi'],
                        'fecha': item_serializer['fecha_bitacora'],  # .strftime("%d/%m/%Y %H:%M:%S"),
                        'usuario': item_serializer['usuario_descripcion']
                    }
                data_response.append(data)
        return data_response

    def generarSumarioDetallado(self, data_request):
        lista_resultados = []

        lista_log = log_aprov_eir.objects.filter(
            Q(fecha_bitacora__date__range=[data_request['fecha_inicio'], data_request['fecha_fin']])).distinct('imsi')
        for item_log in lista_log:
            total_insert = 0
            total_query = 0
            total_delete = 0
            total_insert = log_aprov_eir.objects.filter(Q(imsi=item_log.imsi) & Q(accion='INSERT') & Q(
                fecha_bitacora__date__range=[data_request['fecha_inicio'], data_request['fecha_fin']])).count()
            total_query = log_aprov_eir.objects.filter(Q(imsi=item_log.imsi) & Q(accion='QUERY') & Q(
                fecha_bitacora__date__range=[data_request['fecha_inicio'], data_request['fecha_fin']])).count()
            total_delete = log_aprov_eir.objects.filter(Q(imsi=item_log.imsi) & Q(accion='DELETE') & Q(
                fecha_bitacora__date__range=[data_request['fecha_inicio'], data_request['fecha_fin']])).count()
            data_resultados = {
                'imsi': item_log.imsi,
                'total_insert': total_insert,
                'total_query': total_query,
                'total_delete': total_delete
            }
            lista_resultados.append(data_resultados)

        return lista_resultados

    def consultarTdr(self, codigo_imsi, codigo_imei, fecha_desde, fecha_hasta):
        serializer_tdr = None
        try:

            conditions = []
            condicion_fecha = ('fecha', 'range', [fecha_desde, fecha_hasta])
            conditions.append(condicion_fecha)
            if len(codigo_imsi.strip()) != 0:
                conditions.append(('imsi', 'iexact', codigo_imsi))

            if len(codigo_imei.strip()) != 0:
                conditions.append(('imei', 'iexact', codigo_imei))

            filters = dict(map(self.get_filter, conditions))
            serializer_tdr = TdrSerializer(imei_imsi_block.objects.filter(**filters), many=True)

            return {"estado": "ok", "mensaje": serializer_tdr.data}
        except Exception as e:
            return {"estado": "error", "mensaje": str(e)}

    def get_filter(self, values):
        name, condition, value = values
        key = f"{name}__{condition}"
        return key, value
