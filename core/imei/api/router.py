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
router_imei.register(prefix='logimei', basename='logimei',
                     viewset=LogXImeiViewSet)
router_imei.register(prefix='top_imei_frequently', basename='top_imei_frequently',
                     viewset=TopImeiFrequentlyViewSet)
router_imei.register(prefix='reporte_logs', basename='reporte_logs',
                     viewset=ImeiBlackReporteGeneralLogViewSet)
router_imei.register(prefix='reporte_blocked', basename='reporte_blocked',
                     viewset=ImeiBlackReporteBloqueadoViewSet)
router_imei.register(prefix='reporte_unblocked', basename='reporte_unblocked',
                     viewset=ImeiBlackReporteDesbloqueadoViewSet)
router_imei.register(prefix='reporte_summary', basename='reporte_summary',
                     viewset=ReporteSumarioDetalladoView)
router_imei.register(prefix='report_blocked_rangedate', basename='report_blocked_rangedate',
                     viewset=ConsultaImeiBloqueadoXFechaViewSet)
router_imei.register(prefix='report_unblocked_rangedate', basename='report_unblocked_rangedate',
                     viewset=ConsultaImeiDesBloqueadoXFechaViewSet)
router_imei.register(prefix='consulta_todo_desbloqueados', basename='consulta_todo_desbloqueados',
                     viewset=ConsultarDesBloquedosViewSet)
router_imei.register(prefix='log_consulta_fechas', basename='log_consulta_fechas',
                     viewset=LogXFechasViewSet)
