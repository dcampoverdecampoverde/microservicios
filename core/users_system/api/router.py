from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users_system.api.views import RegistroUsuarioView, UsuarioView, ValidarSessionView, LogoutView, ChangePasswordView, \
    UsuarioActualizaView, ValidarUsuarioBaseReplicaView

urlpatterns = [
    path('auth/register_user', RegistroUsuarioView.as_view()),
    path('auth/update_user', UsuarioActualizaView.as_view()),
    path('auth/login', TokenObtainPairView.as_view()),
    path('auth/logout', LogoutView.as_view()),
    path('auth/changepassword', ChangePasswordView.as_view()),
    path('auth/token/refresh', TokenRefreshView.as_view()),
    path('auth/list_users', UsuarioView.as_view()),
    path('auth/validate_session', ValidarSessionView.as_view()),
    path('auth/validate_user_master_replica', ValidarUsuarioBaseReplicaView.as_view())
]
