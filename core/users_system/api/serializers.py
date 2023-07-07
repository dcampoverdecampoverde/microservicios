from rest_framework import serializers

from users_system.models import Usuario


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('usuario_id', 'username', 'email', 'password', 'rol_id', 'rol_descripcion')

    # Aqui se esta haciendo un Override al metodo create
    # esto con el fin de que la clave se grabe de forma enccriptada
    # esto lo hace el propio framework django
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UsuarioSerializer(serializers.ModelSerializer):
    fecha_modificacion = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
    date_joined = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
    last_login = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')

    class Meta:
        model = Usuario
        fields = ['usuario_id', 'username', 'email', 'is_active', 'last_login', 'date_joined', 'fecha_modificacion',
                  'usuario_modificacion', 'ip_modificacion', 'rol_descripcion', 'rol_id_id']


class UsuarioActualizarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'is_active',
            'rol_id',
            'email',
            'rol_descripcion',
            'fecha_modificacion',
            'usuario_modificacion',
            'ip_modificacion'
        ]
