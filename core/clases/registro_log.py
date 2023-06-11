from users_system.models import Usuario
from lista_negra.models import log_aprov_eir
class RegistroLog():
    def grabar(self, accion, codigo_imsi, operadora, lista, razon, origen, descripcion, usuario_id):
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
            usuario_descripcion=usuario_id
        )