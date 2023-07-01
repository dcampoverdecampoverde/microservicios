import datetime

from django.contrib.auth import password_validation
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users_system.api.serializers import UsuarioRegistroSerializer, UsuarioSerializer
from users_system.models import Usuario


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            info = request.POST if request.POST else request.data if request.data else None
            refresh_token = info['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))


class RegistroUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = UsuarioRegistroSerializer(data=request.data)
            response = {
                "estado": "ok",
                "descripcion": "operacion correcta",
            }
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK, data=response)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = {
                "estado": "error",
                "descripcion": str(e),
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response)


class UsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(Usuario.objects.all(), many=True)  # request.user
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        info = request.POST if request.POST else request.data if request.data else None
        try:
            # Aqui se obtiene la direccion remota
            user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if user_ip:
                ip_transaccion = user_ip.split(',')[0]
            else:
                ip_transaccion = request.META.get('REMOTE_ADDR')

            object_user = Usuario.objects.get(usuario_id=info["user_id"])
            validacion_clave = password_validation.validate_password(info["nueva_clave"], object_user)

            if validacion_clave is None:
                object_user.fecha_modificacion = datetime.datetime.now()
                object_user.usuario_modificacion = info["usuario_transaccion"]
                object_user.ip_modificacion = ip_transaccion
                object_user.set_password(info["nueva_clave"])
                object_user.save()
                data_response = {
                    "estado": 'ok',
                    "mensaje": "operacion correcta"
                }
                return Response(data=data_response, status=status.HTTP_200_OK)
            else:
                data_response = {
                    "estado": 'error',
                    "mensaje": validacion_clave
                }
                return Response(data=data_response, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as e:
            data_response = {
                "estado": 'error',
                "mensaje": "User not exists"
            }
            return Response(data=data_response, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as val_err:
            data_response = {
                "estado": 'error',
                "mensaje": val_err.messages
            }
            return Response(data=data_response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data_response = {
                "estado": 'error',
                "mensaje": str(e)
            }
            return Response(data=data_response, status=status.HTTP_400_BAD_REQUEST)


class ValidarSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data_response = {
            "estado_sesion": 'ok'
        }
        return Response(data=data_response, status=status.HTTP_200_OK)
