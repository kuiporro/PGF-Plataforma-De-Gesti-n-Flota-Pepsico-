# apps/users/views.py
from django.shortcuts import render

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from .models import User, Profile
from .serializers import UserSerializer, ProfileSerializer
from .permissions import UserPermission
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer , LoginSerializer, ProfileSerializer, UsuarioListSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Usuarios.
    - El registro es público.
    - La gestión (listar, editar, borrar) es solo para admins/supervisores.
    - Un usuario puede editar sus propios datos.
    """
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [UserPermission]

    # Esta es la acción para /api/users/me/
    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request, *args, **kwargs):
        self.kwargs['pk'] = request.user.pk
        if request.method == 'GET':
            return self.retrieve(request, *args, **kwargs)
        elif request.method in ['PUT', 'PATCH']:
            return self.update(request, *args, **kwargs)

class ProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet para perfiles. Generalmente se accede a través del endpoint /me/.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated] # Añade permisos más granulares si es necesario

    def get_queryset(self):
        # Un usuario solo debería ver su propio perfil, a menos que sea admin
        if self.request.user.is_staff:
            return Profile.objects.all()
        return Profile.objects.filter(user=self.request.user)
    
class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
    

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

from .serializers import LoginSerializer, UserSerializer, ProfileSerializer, UsuarioListSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        res = Response({
            "user": UserSerializer(user).data,
            "access": str(access),
            "refresh": str(refresh),
        })

        # 🟩 Cookies correctas para LOCAL y PROD
        secure = not settings.DEBUG  # secure=True solo en producción

        res.set_cookie(
            "pgf_access",
            str(access),
            httponly=True,
            samesite="Lax",
            secure=secure,
            path="/",
            max_age=3600,
        )

        res.set_cookie(
            "pgf_refresh",
            str(refresh),
            httponly=True,
            samesite="Lax",
            secure=secure,
            path="/",
            max_age=3600 * 24 * 7,
        )

        return res


class RefreshCookieView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("pgf_refresh")

        if not refresh_token:
            return Response({"detail": "No refresh token found"}, status=401)

        try:
            refresh = RefreshToken(refresh_token)
            access = refresh.access_token
        except Exception:
            return Response({"detail": "Invalid refresh token"}, status=401)

        res = Response({"access": str(access)})

        secure = not settings.DEBUG

        res.set_cookie(
            "pgf_access",
            str(access),
            httponly=True,
            samesite="Lax",
            secure=secure,
            path="/",
            max_age=3600,
        )

        return res



class UsuarioListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UsuarioListSerializer
    permission_classes = [permissions.IsAuthenticated]