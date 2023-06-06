from rest_framework.routers import DefaultRouter
from lista_negra.api.views import *

router_default_LN = DefaultRouter()
router_default_LN.register(prefix='lista_negra',basename='lista_negra', viewset=ListaNegraViewSet)