# apps/users/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Profile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "rut", "first_name", "last_name", "rol", "is_active", "date_joined"]
        read_only_fields = ["id", "date_joined"]

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ["user"]

    def update(self, instance, validated_data):
        # Actualizar campos del perfil
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)   
    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                raise serializers.ValidationError("Credenciales incorrectas.", code='authorization')
            
            # Verificar que el usuario esté activo
            if not user.is_active:
                raise serializers.ValidationError("Tu cuenta está desactivada. Contacta al administrador.", code='authorization')
        else:
            raise serializers.ValidationError("Se deben proporcionar ambos campos: 'username' y 'password'.", code='authorization')

        attrs['user'] = user
        return attrs
    

    
class UsuarioListSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ["id", "username", "email", "rut", "first_name", "last_name", "nombre_completo", "rol", "is_active"]
    
    def get_nombre_completo(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("No existe un usuario activo con este email.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8, write_only=True)
    confirm_password = serializers.CharField(required=True, min_length=8, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para cambiar contraseña (requiere contraseña actual)"""
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, min_length=8, write_only=True)
    confirm_password = serializers.CharField(required=True, min_length=8, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return attrs


class AdminChangePasswordSerializer(serializers.Serializer):
    """Serializer para que admin cambie contraseña de otro usuario (sin contraseña actual)"""
    new_password = serializers.CharField(required=True, min_length=8, write_only=True)
    confirm_password = serializers.CharField(required=True, min_length=8, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return attrs
