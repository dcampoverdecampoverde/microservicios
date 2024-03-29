from rest_framework.routers import DefaultRouter

from task_scheduler.api.views import *

router_task = DefaultRouter()

router_task.register(prefix='lista_jobs_existentes', basename='lista_jobs_existentes',
                     viewset=ConsultaListaJobsViewSet)
router_task.register(prefix='registrar_task_job', basename='registrar_task_job',
                     viewset=RegistrarProgramadorTareaViewSet)
router_task.register(prefix='listado_task_job', basename='listado_task_job',
                     viewset=ConsultarListadoTaskJobViewSet)
router_task.register(prefix='actualizar_task_job', basename='actualizar_task_job',
                     viewset=ActualizarTaskJobViewSet)
router_task.register(prefix='actualizar_estado_task_job', basename='actualizar_estado_task_job',
                     viewset=ActualizarEstadoTaskJobViewSet)
router_task.register(prefix='listado_parametros_target', basename='listado_parametros_target',
                     viewset=ConsultarListaParametrosTargetViewSet)
router_task.register(prefix='eliminar_task_job', basename='eliminar_task_job',
                     viewset=EliminarTaskJobViewSet)
