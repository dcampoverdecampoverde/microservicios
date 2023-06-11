from rest_framework.routers import DefaultRouter
from lista_negra.api.views import *

router_default_LN = DefaultRouter()
router_default_LN.register(prefix='lista_negra_registro',basename='lista_negra_registro', viewset=ListaNegraRegistroViewSet)
router_default_LN.register(prefix='lista_negra_consulta',basename='lista_negra_consulta', viewset=ListaNegraConsultaViewSet)
router_default_LN.register(prefix='lista_negra_eliminar',basename='lista_negra_eliminar', viewset=ListaNegraEliminarViewSet)