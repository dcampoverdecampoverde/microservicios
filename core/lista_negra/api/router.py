from rest_framework.routers import DefaultRouter

from lista_negra.api.views import *

router_default_LN = DefaultRouter()
router_default_LN.register(prefix='lista_negra_registro', basename='lista_negra_registro',
                           viewset=ListaNegraRegistroViewSet)
router_default_LN.register(prefix='lista_negra_consulta', basename='lista_negra_consulta',
                           viewset=ListaNegraConsultaViewSet)
router_default_LN.register(prefix='lista_negra_eliminar', basename='lista_negra_eliminar',
                           viewset=ListaNegraEliminarViewSet)
router_default_LN.register(prefix='parametros_operadora', basename='parametros_operadora',
                           viewset=ParametrosOperadoraView)
router_default_LN.register(prefix='parametros_ruta_ftp', basename='parametros_ruta_ftp',
                           viewset=ParametrosRutaFtpView)
router_default_LN.register(prefix='log_consulta_usuario', basename='log_consulta_usuario',
                           viewset=LogXUsuarioViewSet)
router_default_LN.register(prefix='log_consulta_imsi', basename='log_consulta_usuario',
                           viewset=LogXIMSIViewSet)
router_default_LN.register(prefix='log_consulta_fechas', basename='log_consulta_fechas',
                           viewset=LogXFechasViewSet)
router_default_LN.register(prefix='archivo_masivo', basename='archivo_masivo',
                           viewset=ArchivoMasivoViewSet)
router_default_LN.register(prefix='reporte_blocked', basename='reporte_blocked',
                           viewset=ReporteBloqueadoViewSet)
router_default_LN.register(prefix='reporte_unblocked', basename='reporte_unblocked',
                           viewset=ReporteDesbloqueadoViewSet)
router_default_LN.register(prefix='reporte_logs', basename='reporte_logs',
                           viewset=ReporteGeneralLogViewSet)
router_default_LN.register(prefix='reporte_summary', basename='reporte_summary',
                           viewset=ReporteSumarioDetalladoView)
router_default_LN.register(prefix='consulta_tdr', basename='consultar_tdr',
                           viewset=ConsultarTDRViewSet)
router_default_LN.register(prefix='reporte_tdr', basename='reporte_tdr',
                           viewset=ReporteTDRViewSet)
router_default_LN.register(prefix='consulta_todo_desbloqueados', basename='consulta_todo_desbloqueados',
                           viewset=ConsultarDesBloquedosViewSet)
router_default_LN.register(prefix='lista_api_actions_user', basename='lista_api_actions_user',
                           viewset=ListaUsuariosApiActionsViewSet)
router_default_LN.register(prefix='api_actions_user_registro', basename='api_actions_user_registro',
                           viewset=UsuariosApiActionsViewSet)
router_default_LN.register(prefix='modificar_actions_user_registro', basename='modificar_actions_user_registro',
                           viewset=UsuariosModificarApiActionsViewSet)
router_default_LN.register(prefix='service_check_health', basename='service_check_health',
                           viewset=ServiceCheckHeathViewSet)
router_default_LN.register(prefix='top_imsi_frequently', basename='top_imsi_frequently',
                           viewset=TopImsiFrequentlyViewSet)
