# apps/users/serializers.py
from rest_framework import serializers
from .models import (User, Profile)
from apps.vehicles.serializers import VehiculoSerializer
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password as validate_passw
from django.contrib.auth import authenticate



class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_passw])
    password2 = serializers.CharField(write_only=True, required=True)
    vehiculos = VehiculoSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'email','first_name', 'last_name', 'is_active', 'is_staff', 'vehiculos')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        password = attrs.get("password")
        user = self.instance or User(**{k: v for k, v in attrs.items() if k in ["username", "email"]})
        if password:
            validate_passw(password, user)  # ← usa tu alias
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create(
        username=validated_data['username'],
        first_name=validated_data['first_name'],
        last_name=validated_data['last_name'],
        is_active=validated_data.get('is_active', True),
        is_staff=validated_data.get('is_staff', False),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        validated_data.pop('password2', None)
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Profile
        fields = ('id', 'user', 'phone_number', 'first_name', 'last_name')
    def update(self, instance, validated_data):
        profile_data = validated_data
        for attr, value in profile_data.items():
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
        else:
            raise serializers.ValidationError("Se deben proporcionar ambos campos: 'username' y 'password'.", code='authorization')

        attrs['user'] = user
        return attrs
    
    

    
class UsuarioListSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()

    def get_nombre_completo(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "nombre_completo"]
