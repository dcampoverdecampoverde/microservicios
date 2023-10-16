from imei.models import log_imei_eir


class RegistroLog():
    def grabar(self, accion, codigo_imei, operadora, lista, razon, origen, descripcion, usuario_id,
               ip_usuario_transaccion, log_file):
        log_imei_eir.objects.create(
            estado="A",
            accion=accion,
            imei=codigo_imei,
            operadora=operadora,
            lista=lista,
            razon=razon,
            origen=origen,
            descripcion=descripcion,
            ip_transaccion=ip_usuario_transaccion,
            usuario_descripcion=usuario_id
        )
