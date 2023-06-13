from lista_negra.api.views import *
from rest_framework.routers import DefaultRouter

router_default_LN = DefaultRouter()
router_default_LN.register(prefix='lista_negra_registro', basename='lista_negra_registro',
                           viewset=ListaNegraRegistroViewSet)
router_default_LN.register(prefix='lista_negra_consulta', basename='lista_negra_consulta',
                           viewset=ListaNegraConsultaViewSet)
router_default_LN.register(prefix='lista_negra_eliminar', basename='lista_negra_eliminar',
                           viewset=ListaNegraEliminarViewSet)
router_default_LN.register(prefix='parametros_operadora', basename='parametros_operadora',
                           viewset=ParametrosOperadoraView)
router_default_LN.register(prefix='log_consulta_usuario', basename='log_consulta_usuario',
                           viewset=LogXUsuarioViewSet)
router_default_LN.register(prefix='log_consulta_imsi', basename='log_consulta_usuario',
                           viewset=LogXIMSIViewSet)
