"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from admin_app.api.router import router_default
from imei.api.router import router_imei
from lista_negra.api.router import router_default_LN

schema_view = get_schema_view(
    openapi.Info(
        title="MicroServicios Admin IMSI",
        default_version="1",
        description="Las funciones para realizar transacciones en el sitio de admin imsi",
        terms_of_service="https://www.google.com/policies/terms",
        contact=openapi.Contact(email="dcampoverdecampoverde@gmail.com"),
        license=openapi.License(name="BSD Licence")
    ),
    public=True
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redocs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # Aqui se llama al router del Usuario
    path('api/', include('users_system.api.router')),
    path('api/', include(router_default.urls)),
    path('api/transaction/', include(router_default_LN.urls)),
    path('api/imei/', include(router_imei.urls)),
    # path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # path('schema/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
]
