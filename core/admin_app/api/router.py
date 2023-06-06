from rest_framework.routers import DefaultRouter
from admin_app.api.views import *

router_default = DefaultRouter()
router_default.register(prefix='roles_menu',basename='roles_menu', viewset=RolesMenuViewSet)
router_default.register(prefix='roles_menuaccion',basename='roles_menuaccion', viewset=RolesMenuAccionViewSet)
router_default.register(prefix='roles',basename='roles', viewset=RolesViewSet)
router_default.register(prefix='menu_opcion',basename='menu_opcion', viewset=MenuOpcionViewSet)
router_default.register(prefix='acciones',basename='acciones', viewset=AccionesViewSet)