from users_system.models import Usuario
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from users_system.api.serializers import UsuarioRegistroSerializer, UsuarioSerializer

class RegistroUsuarioView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = UsuarioRegistroSerializer(data=request.data)
        response ={
            "estado":"ok",
            "descripcion": "ok",
        }
        if serializer.is_valid():
            serializer.save()
            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UsuarioView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = UsuarioSerializer(Usuario.objects.all(), many=True) #request.user
        return Response(serializer.data)