from rest_framework.routers import DefaultRouter

from imei.api.views import *

router_imei = DefaultRouter()

router_imei.register(prefix='imeiblack_registro', basename='imeiblack_registro',
                     viewset=ImeiBlackRegistroViewSet)
router_imei.register(prefix='imeiblack_consulta', basename='imeiblack_consulta',
                     viewset=ImeiBlackConsultaViewSet)
router_imei.register(prefix='imeiblack_eliminar', basename='imeiblack_eliminar',
                     viewset=ImeiBlackEliminarViewSet)
router_imei.register(prefix='logimei_usuario', basename='logimei_usuario',
                     viewset=LogXUsuarioViewSet)
router_imei.register(prefix='imeiblack_masivo', basename='imeiblack_masivo',
                     viewset=ImeiBlackMasivoViewSet)
router_imei.register(prefix='imeiblack_reportebloqueado', basename='imeiblack_reportebloqueado',
                     viewset=ImeiBlackReporteBloqueadoViewSet)
router_imei.register(prefix='imeiblack_reportedesbloqueado', basename='imeiblack_reportedesbloqueado',
                     viewset=ImeiBlackReporteDesbloqueadoViewSet)
router_imei.register(prefix='imeiblack_reporteloggeneral', basename='imeiblack_reporteloggeneral',
                     viewset=ImeiBlackReporteGeneralLogViewSet)
