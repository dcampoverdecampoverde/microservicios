from lista_negra.models import log_aprov_eir
from users_system.models import Usuario


class RegistroLog():
    def grabar(self, accion, codigo_imsi, operadora, lista, razon, origen, descripcion, usuario_id,
               ip_usuario_transaccion):
        log_aprov_eir.objects.create(
            estado="A",
            accion=accion,
            imsi=codigo_imsi,
            operadora=operadora,
            lista=lista,
            razon=razon,
            origen=origen,
            descripcion=descripcion,
            usuario_id_id=Usuario.objects.get(username=usuario_id).usuario_id,
            ip_transaccion=ip_usuario_transaccion,
            usuario_descripcion=usuario_id
        )
