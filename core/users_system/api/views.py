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


class ValidarSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data_response = {
            "estado_sesion": 'ok'
        }
        return Response(data=data_response, status=status.HTTP_200_OK)
