import datetime

from django.contrib.auth import password_validation
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users_system.api.serializers import UsuarioRegistroSerializer, UsuarioSerializer, UsuarioActualizarSerializer
from users_system.functions.functions_usuarios import FunctionsUsuario
from users_system.models import Usuario


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        metodos = FunctionsUsuario()
        try:
            # Obtengo la informacion del usaurio q inicio sesion
            data_user = metodos.obtenerUsuarioSesionToken(request)

            usuario_sesion = Usuario.objects.get(username=data_user["username"])
            token = RefreshToken.for_user(usuario_sesion)
            token.blacklist()
            # info = request.POST if request.POST else request.data if request.data else None
            # refresh_token = info['refresh_token']
            # token = RefreshToken(refresh_token)
            # token.blacklist()
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
                "mensaje": "operacion correcta",
            }
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK, data=response)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = {
                "estado": "error",
                "mensaje": str(e),
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response)


class UsuarioActualizaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        metodos = FunctionsUsuario()
        try:
            info = request.POST if request.POST else request.data if request.data else None

            # Obtengo la informacion del usaurio q inicio sesion
            data_user = metodos.obtenerUsuarioSesionToken(request)

            # Obtengo la direccion IP remota
            ip_transaccion = metodos.obtenerDireccionIpRemota(request)

            obj_usuario = Usuario.objects.get(pk=info["id"])
            data_modificar = {
                'is_active': info['is_active'],
                'rol_id': info['rol_id'],
                'email': info['email'],
                'rol_descripcion': info['rol_descripcion'],
                'fecha_modificacion': datetime.datetime.now(),
                'usuario_modificacion': data_user['username'],
                'ip_modificacion': ip_transaccion

            }
            serializer = UsuarioActualizarSerializer(obj_usuario, data=data_modificar, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(status=status.HTTP_200_OK, data={'estado': 'ok', 'mensaje': 'operacion correcta'})
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'estado': 'error', 'mensaje': serializer.errors})
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'estado': 'error', 'mensaje': str(e)})


class UsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(Usuario.objects.all(), many=True)  # request.user
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        metodos = FunctionsUsuario()
        info = request.POST if request.POST else request.data if request.data else None
        try:
            # Obtengo la informacion del usaurio q inicio sesion
            data_user = metodos.obtenerUsuarioSesionToken(request)

            # Aqui se obtiene la direccion remota
            ip_transaccion = metodos.obtenerDireccionIpRemota(request)

            object_user = Usuario.objects.get(usuario_id=info["user_id"])
            validacion_clave = password_validation.validate_password(info["nueva_clave"], object_user)

            if validacion_clave is None:
                object_user.fecha_modificacion = datetime.datetime.now()
                object_user.usuario_modificacion = data_user["username"]
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


class ValidarUsuarioBaseReplicaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        metodos = FunctionsUsuario()
        # Obtengo la informacion del usaurio q inicio sesion
        data_user = metodos.obtenerUsuarioSesionToken(request)
        usuario_id_master = data_user["id"]
        usuario_id_replica = metodos.obtenerIDUsuarioBaseReplica(data_user["username"])
        if usuario_id_master == usuario_id_replica:
            data_response = {
                "estado": "ok",
                "mensaje": "ok"
            }
            return Response(data=data_response, status=status.HTTP_200_OK)
        else:
            data_response = {
                "estado": "error",
                "mensaje": "el ID de usuario no coincide entre la base master y replica. Por favor verifique"
            }
            return Response(data=data_response, status=status.HTTP_400_BAD_REQUEST)


class ValidarSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data_response = {
            "estado_sesion": 'ok'
        }
        return Response(data=data_response, status=status.HTTP_200_OK)
