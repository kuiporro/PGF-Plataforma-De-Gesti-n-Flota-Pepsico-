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

    def perform_destroy(self, instance):
        """Eliminar usuario sin intentar eliminar relaciones de inventory que pueden no existir"""
        try:
            # Intentar eliminar movimientos de stock relacionados
            from apps.inventory.models import MovimientoStock
            MovimientoStock.objects.filter(usuario=instance).update(usuario=None)
        except Exception:
            # Si la tabla no existe o hay error, continuar
            pass
        
        try:
            # Intentar eliminar solicitudes relacionadas
            from apps.inventory.models import SolicitudRepuesto
            SolicitudRepuesto.objects.filter(
                solicitante=instance
            ).update(solicitante=None)
            SolicitudRepuesto.objects.filter(
                aprobador=instance
            ).update(aprobador=None)
            SolicitudRepuesto.objects.filter(
                entregador=instance
            ).update(entregador=None)
        except Exception:
            # Si la tabla no existe o hay error, continuar
            pass
        
        # Eliminar el usuario
        instance.delete()

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

        # Registrar auditoría de acceso exitoso
        from apps.workorders.models import Auditoria
        from django.utils import timezone
        Auditoria.objects.create(
            usuario=user,
            accion="LOGIN_EXITOSO",
            objeto_tipo="User",
            objeto_id=str(user.id),
            payload={
                "ip": self.get_client_ip(request),
                "user_agent": request.META.get('HTTP_USER_AGENT', ''),
                "timestamp": timezone.now().isoformat()
            }
        )

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
    
    def get_client_ip(self, request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


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


class PasswordResetRequestView(APIView):
    """Solicita recuperación de contraseña"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        from .serializers import PasswordResetRequestSerializer
        from .models import PasswordResetToken
        from django.core.mail import send_mail
        from django.conf import settings
        
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email, is_active=True)
            reset_token = PasswordResetToken.generate_token(user)
            
            # Enviar email con el token
            reset_url = f"{settings.FRONTEND_URL or 'http://localhost:3000'}/auth/reset-password?token={reset_token.token}"
            
            try:
                from django.core.mail import send_mail
                from django.template.loader import render_to_string
                from django.utils.html import strip_tags
                
                # Crear mensaje HTML
                html_message = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #1e40af;">Recuperación de Contraseña - PGF</h2>
                        <p>Hola,</p>
                        <p>Has solicitado recuperar tu contraseña. Para continuar, haz clic en el siguiente enlace:</p>
                        <p style="text-align: center; margin: 30px 0;">
                            <a href="{reset_url}" 
                               style="background-color: #1e40af; color: white; padding: 12px 24px; 
                                      text-decoration: none; border-radius: 5px; display: inline-block;">
                                Recuperar Contraseña
                            </a>
                        </p>
                        <p>O copia y pega este enlace en tu navegador:</p>
                        <p style="word-break: break-all; color: #666; font-size: 12px;">{reset_url}</p>
                        <p><strong>Este enlace expirará en 24 horas.</strong></p>
                        <p>Si no solicitaste este cambio, puedes ignorar este email.</p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                        <p style="color: #666; font-size: 12px;">Sistema PGF - Plataforma de Gestión de Flota</p>
                    </div>
                </body>
                </html>
                """
                
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject='Recuperación de Contraseña - PGF',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as e:
                # Si falla el envío de email, registrar error pero no fallar la solicitud
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error enviando email de recuperación de contraseña: {e}")
                # En desarrollo, retornar el token en la respuesta
                if settings.DEBUG:
                    return Response({
                        "message": "Si el email existe, se ha enviado un enlace de recuperación.",
                        "token": reset_token.token,  # Solo en desarrollo
                        "error": str(e)
                    })
            
            # Registrar auditoría
            from apps.workorders.models import Auditoria
            Auditoria.objects.create(
                usuario=user,
                accion="SOLICITAR_RESET_PASSWORD",
                objeto_tipo="PasswordResetToken",
                objeto_id=str(reset_token.id),
                payload={"email": email}
            )
            
            return Response({
                "message": "Si el email existe, se ha enviado un enlace de recuperación.",
                # En desarrollo, retornar el token (eliminar en producción)
                "token": reset_token.token if settings.DEBUG else None
            })
        except User.DoesNotExist:
            # Por seguridad, no revelamos si el email existe o no
            return Response({
                "message": "Si el email existe, se ha enviado un enlace de recuperación."
            })


class PasswordResetConfirmView(APIView):
    """Confirma y cambia la contraseña con el token"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        from .serializers import PasswordResetConfirmSerializer
        from .models import PasswordResetToken
        from django.utils import timezone
        
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token_str = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            reset_token = PasswordResetToken.objects.get(token=token_str, used=False)
            
            if not reset_token.is_valid():
                return Response(
                    {"detail": "El token ha expirado o ya fue usado."},
                    status=400
                )
            
            # Cambiar contraseña
            user = reset_token.user
            user.set_password(new_password)
            user.save()
            
            # Marcar token como usado
            reset_token.used = True
            reset_token.save()
            
            # Registrar auditoría
            from apps.workorders.models import Auditoria
            Auditoria.objects.create(
                usuario=user,
                accion="RESET_PASSWORD_COMPLETADO",
                objeto_tipo="PasswordResetToken",
                objeto_id=str(reset_token.id),
                payload={}
            )
            
            return Response({"message": "Contraseña actualizada correctamente."})
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"detail": "Token inválido."},
                status=400
            )


class ChangePasswordView(APIView):
    """Permite a un usuario cambiar su propia contraseña"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        from .serializers import ChangePasswordSerializer
        from django.contrib.auth import update_session_auth_hash
        from rest_framework import status
        
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        # Verificar contraseña actual
        if not user.check_password(serializer.validated_data['current_password']):
            return Response(
                {"detail": "La contraseña actual es incorrecta."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cambiar contraseña
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Actualizar sesión para evitar logout
        update_session_auth_hash(request, user)
        
        # Registrar auditoría
        from apps.workorders.models import Auditoria
        Auditoria.objects.create(
            usuario=user,
            accion="CAMBIAR_PASSWORD",
            objeto_tipo="User",
            objeto_id=str(user.id),
            payload={}
        )
        
        return Response({"message": "Contraseña actualizada correctamente."})


class AdminChangePasswordView(APIView):
    """Permite a un admin cambiar la contraseña de otro usuario"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id=None):
        from .serializers import AdminChangePasswordSerializer
        from rest_framework import status
        
        # Verificar que el usuario sea ADMIN o SUPERVISOR
        if request.user.rol not in ("ADMIN", "SUPERVISOR"):
            return Response(
                {"detail": "No tienes permisos para cambiar contraseñas de otros usuarios."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = AdminChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Cambiar contraseña
        target_user.set_password(serializer.validated_data['new_password'])
        target_user.save()
        
        # Registrar auditoría
        from apps.workorders.models import Auditoria
        Auditoria.objects.create(
            usuario=request.user,
            accion="ADMIN_CAMBIAR_PASSWORD",
            objeto_tipo="User",
            objeto_id=str(target_user.id),
            payload={"target_user": target_user.username}
        )
        
        return Response({"message": f"Contraseña de {target_user.username} actualizada correctamente."})