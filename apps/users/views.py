# apps/users/views.py
"""
Vistas y ViewSets para gestión de usuarios y autenticación.

Este módulo define:
- UserViewSet: CRUD de usuarios con permisos personalizados
- ProfileViewSet: Gestión de perfiles de usuario
- LoginView: Autenticación JWT con cookies
- RefreshCookieView: Renovación de tokens
- PasswordResetRequestView: Solicitud de recuperación de contraseña
- PasswordResetConfirmView: Confirmación y cambio de contraseña
- ChangePasswordView: Cambio de contraseña del usuario logueado
- AdminChangePasswordView: Cambio de contraseña por admin

Relaciones:
- Usa: apps/users/models.py (User, Profile, PasswordResetToken)
- Usa: apps/users/serializers.py (serializers para validación)
- Usa: apps/users/permissions.py (UserPermission)
- Usa: apps/workorders/models.py (Auditoria para logs)
- Conectado a: apps/users/urls.py y apps/users/auth_urls.py
"""

from django.shortcuts import render

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
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
    
    Proporciona endpoints CRUD completos:
    - GET /api/v1/users/ → Listar usuarios
    - POST /api/v1/users/ → Crear usuario (público)
    - GET /api/v1/users/{id}/ → Ver usuario
    - PUT/PATCH /api/v1/users/{id}/ → Editar usuario
    - DELETE /api/v1/users/{id}/ → Eliminar usuario
    - GET /api/v1/users/me/ → Ver perfil propio
    - PUT/PATCH /api/v1/users/me/ → Editar perfil propio
    
    Permisos:
    - Crear: Público (cualquiera puede registrarse)
    - Listar: Solo ADMIN y SUPERVISOR
    - Ver/Editar/Eliminar: ADMIN, SUPERVISOR, o el propio usuario
    - /me/: Cualquier usuario autenticado puede ver/editar su propio perfil
    
    Relaciones:
    - Usa UserPermission para control de acceso
    - Al eliminar, limpia relaciones con inventory (si existen)
    """
    queryset = User.objects.all().order_by('id')  # QuerySet base: todos los usuarios ordenados por ID
    serializer_class = UserSerializer  # Serializer por defecto
    permission_classes = [UserPermission]  # Permisos personalizados
    
    # Configuración de filtros
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['rol', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'rut']
    ordering_fields = ['username', 'email', 'date_joined']
    ordering = ['username']

    def get_queryset(self):
        """
        Filtra el queryset para ocultar el usuario 'admin' a todos excepto al propio admin.
        También aplica filtros de query params (rol, is_active, etc.)
        
        Reglas:
        - Solo el usuario con username 'admin' puede ver al usuario 'admin' en las listas
        - Todos los demás usuarios (incluso otros ADMIN) no verán al usuario 'admin'
        - Filtra por rol si se proporciona ?rol=MECANICO
        
        Retorna:
        - QuerySet filtrado según el usuario autenticado y query params
        """
        queryset = super().get_queryset()
        
        # Solo el usuario con username 'admin' puede ver al usuario 'admin'
        # Esto es más estricto que solo verificar el rol, ya que podría haber múltiples usuarios con rol ADMIN
        if self.request.user.is_authenticated and self.request.user.username != "admin":
            queryset = queryset.exclude(username="admin")
        
        # Aplicar filtro de rol si se proporciona
        rol = self.request.query_params.get('rol')
        if rol:
            queryset = queryset.filter(rol=rol)
        
        return queryset

    def perform_destroy(self, instance):
        """
        Eliminar usuario de forma segura.
        
        Este método se ejecuta antes de eliminar un usuario.
        Limpia relaciones con módulos que pueden no estar migrados
        (inventory) para evitar errores de ForeignKey.
        
        Parámetros:
        - instance: Instancia de User a eliminar
        
        Proceso:
        1. Intenta limpiar MovimientoStock relacionados (si existe la tabla)
        2. Intenta limpiar SolicitudRepuesto relacionadas (si existe la tabla)
        3. Elimina el usuario
        
        Nota: Usa try/except para que si las tablas no existen,
        la eliminación continúe sin errores.
        """
        try:
            # Intentar eliminar movimientos de stock relacionados
            # MovimientoStock puede tener ForeignKey a User
            from apps.inventory.models import MovimientoStock
            MovimientoStock.objects.filter(usuario=instance).update(usuario=None)
        except Exception:
            # Si la tabla no existe o hay error, continuar
            # Esto permite que el sistema funcione aunque inventory no esté migrado
            pass
        
        try:
            # Intentar eliminar solicitudes de repuestos relacionadas
            # SolicitudRepuesto puede tener ForeignKey a User en múltiples campos
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
        # Django automáticamente eliminará:
        # - Profile (OneToOne con CASCADE)
        # - PasswordResetToken (ForeignKey con CASCADE)
        instance.delete()

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request, *args, **kwargs):
        """
        Endpoint para obtener/editar el perfil del usuario logueado.
        
        URL: /api/v1/users/me/
        
        Métodos:
        - GET: Retorna información del usuario actual
        - PUT/PATCH: Actualiza información del usuario actual
        
        Permisos:
        - Requiere autenticación (cualquier usuario logueado)
        
        Funcionamiento:
        - Establece self.kwargs['pk'] = request.user.pk
        - Delega a retrieve() o update() según el método
        - Esto permite reutilizar la lógica de esos métodos
        
        Uso:
        - Frontend llama a /api/v1/users/me/ para obtener datos del usuario
        - Frontend llama a PUT /api/v1/users/me/ para actualizar perfil
        """
        # Establecer el ID del usuario actual como el ID a consultar
        # Esto permite usar los métodos retrieve() y update() existentes
        self.kwargs['pk'] = request.user.pk
        
        if request.method == 'GET':
            # Obtener información del usuario
            return self.retrieve(request, *args, **kwargs)
        elif request.method in ['PUT', 'PATCH']:
            # Actualizar información del usuario
            return self.update(request, *args, **kwargs)

class ProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet para perfiles de usuario.
    
    Generalmente se accede a través del endpoint /users/me/,
    pero este ViewSet permite gestión directa de perfiles si es necesario.
    
    Permisos:
    - Requiere autenticación
    - Usuario solo ve su propio perfil (a menos que sea staff/admin)
    
    Relaciones:
    - OneToOne con User (a través de AUTH_USER_MODEL)
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filtrar queryset según permisos.
        
        - Staff/Admin: Ven todos los perfiles
        - Usuario regular: Solo ve su propio perfil
        
        Retorna:
        - QuerySet filtrado según el usuario
        """
        if self.request.user.is_staff:
            return Profile.objects.all()
        return Profile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Crea un perfil asignando automáticamente el usuario actual.
        
        Si el usuario ya tiene un perfil, no se crea otro.
        """
        # Verificar si el usuario ya tiene un perfil
        if hasattr(self.request.user, 'profile'):
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "El usuario ya tiene un perfil."})
        
        # Asignar el usuario actual al perfil
        serializer.save(user=self.request.user)
    
class MeAPIView(APIView):
    """
    Vista alternativa para /me/.
    
    Endpoint simple que retorna información del usuario actual.
    Más simple que usar UserViewSet.me, pero con menos funcionalidades.
    
    URL: /api/v1/users/me/ (si está configurado en urls.py)
    
    Permisos:
    - Requiere autenticación
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retorna información del usuario actual incluyendo perfil con preferencias.
        
        Retorna:
        - JSON con datos del usuario serializados y perfil
        """
        serializer = UserSerializer(request.user)
        data = serializer.data
        
        # Incluir perfil con preferencias si existe
        if hasattr(request.user, 'profile'):
            profile_serializer = ProfileSerializer(request.user.profile)
            data['profile'] = profile_serializer.data
        
        return Response(data)
    

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

from .serializers import LoginSerializer, UserSerializer, ProfileSerializer, UsuarioListSerializer


class LoginView(APIView):
    """
    Vista de autenticación (login).
    
    Endpoint: POST /api/v1/auth/login/
    
    Permisos:
    - Público (AllowAny) - cualquiera puede intentar hacer login
    
    Funcionalidad:
    1. Valida credenciales (username/password)
    2. Verifica que el usuario esté activo
    3. Genera tokens JWT (access y refresh)
    4. Establece cookies con los tokens
    5. Registra auditoría de login exitoso
    6. Retorna información del usuario y tokens
    
    Cookies:
    - pgf_access: Token de acceso (expira en 1 hora)
    - pgf_refresh: Token de refresh (expira en 7 días)
    
    Relaciones:
    - Usa LoginSerializer para validar credenciales
    - Usa apps/workorders/models.py (Auditoria) para logs
    """
    permission_classes = [AllowAny]  # Público - cualquiera puede intentar login

    def post(self, request):
        """
        Procesa el login.
        
        Parámetros (body JSON):
        - username: Nombre de usuario
        - password: Contraseña
        
        Retorna:
        - 200: Login exitoso
          {
            "user": {...},
            "access": "token...",
            "refresh": "token..."
          }
        - 400: Credenciales inválidas o usuario inactivo
        - 401: Error de autenticación
        """
        # Validar datos de entrada
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Obtener usuario validado del serializer
        # LoginSerializer.validate() ya verificó credenciales y que esté activo
        user = serializer.validated_data["user"]
        
        # Logging para debugging (solo en desarrollo)
        import logging
        logger = logging.getLogger(__name__)
        if settings.DEBUG:
            logger.info(f"Login exitoso para usuario: {user.username}, rol: {user.rol}, activo: {user.is_active}")

        # Generar tokens JWT
        # RefreshToken.for_user() crea un par de tokens (refresh + access)
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token  # Token de acceso (corto plazo)

        # Registrar auditoría de acceso exitoso
        # Esto permite rastrear quién y cuándo accedió al sistema
        from apps.workorders.models import Auditoria
        from django.utils import timezone
        try:
            Auditoria.objects.create(
                usuario=user,
                accion="LOGIN_EXITOSO",
                objeto_tipo="User",
                objeto_id=str(user.id),
                payload={
                    "ip": self.get_client_ip(request),  # IP del cliente
                    "user_agent": request.META.get('HTTP_USER_AGENT', ''),  # Navegador
                    "timestamp": timezone.now().isoformat(),  # Fecha/hora
                    "rol": user.rol  # Agregar rol para debugging
                }
            )
        except Exception as e:
            # Si falla la auditoría, no bloquear el login
            # Solo loguear el error para debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error al registrar auditoría de login: {e}")

        # Preparar respuesta con datos del usuario y tokens
        res = Response({
            "user": UserSerializer(user).data,  # Datos del usuario serializados
            "access": str(access),              # Token de acceso (también en cookie)
            "refresh": str(refresh),            # Token de refresh (también en cookie)
        })

        # Configurar cookies con los tokens
        # secure: True solo en producción (HTTPS), False en desarrollo (HTTP)
        secure = not settings.DEBUG

        # Cookie con token de acceso
        res.set_cookie(
            "pgf_access",
            str(access),
            httponly=True,      # No accesible desde JavaScript (protección XSS)
            samesite="Lax",     # Protección CSRF
            secure=secure,      # Solo enviar por HTTPS en producción
            path="/",           # Disponible en todo el sitio
            max_age=3600,       # Expira en 1 hora (3600 segundos)
        )

        # Cookie con token de refresh
        res.set_cookie(
            "pgf_refresh",
            str(refresh),
            httponly=True,
            samesite="Lax",
            secure=secure,
            path="/",
            max_age=3600 * 24 * 7,  # Expira en 7 días
        )

        return res
    
    def get_client_ip(self, request):
        """
        Obtiene la IP real del cliente.
        
        Considera proxies y load balancers que pueden agregar
        headers como X-Forwarded-For.
        
        Parámetros:
        - request: Objeto HttpRequest de Django
        
        Retorna:
        - str: IP del cliente
        
        Uso:
        - Llamado desde post() para registrar en auditoría
        """
        # Verificar header X-Forwarded-For (usado por proxies)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # X-Forwarded-For puede tener múltiples IPs separadas por coma
            # La primera es la IP original del cliente
            ip = x_forwarded_for.split(',')[0]
        else:
            # Si no hay X-Forwarded-For, usar REMOTE_ADDR
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RefreshCookieView(APIView):
    """
    Vista para renovar el token de acceso usando el refresh token.
    
    Endpoint: POST /api/v1/auth/refresh/
    
    Permisos:
    - Público (AllowAny) - pero requiere refresh token válido en cookie
    
    Funcionalidad:
    1. Lee el refresh token de las cookies
    2. Valida el token
    3. Genera un nuevo access token
    4. Establece cookie con el nuevo access token
    5. Retorna el nuevo access token
    
    Uso:
    - Llamado automáticamente cuando el access token expira
    - Permite mantener la sesión activa sin requerir login nuevamente
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Renueva el token de acceso.
        
        Retorna:
        - 200: Token renovado
          {
            "access": "nuevo_token..."
          }
        - 401: Refresh token inválido o no encontrado
        """
        # Obtener refresh token de las cookies
        refresh_token = request.COOKIES.get("pgf_refresh")

        if not refresh_token:
            return Response({"detail": "No refresh token found"}, status=401)

        try:
            # Validar y generar nuevo access token
            refresh = RefreshToken(refresh_token)
            access = refresh.access_token  # Nuevo token de acceso
        except Exception:
            # Si el token es inválido o expiró
            return Response({"detail": "Invalid refresh token"}, status=401)

        # Preparar respuesta con nuevo token
        res = Response({"access": str(access)})

        # Configurar cookie con nuevo access token
        secure = not settings.DEBUG

        res.set_cookie(
            "pgf_access",
            str(access),
            httponly=True,
            samesite="Lax",
            secure=secure,
            path="/",
            max_age=3600,  # 1 hora
        )

        return res



class UsuarioListViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para listar usuarios.
    
    Útil cuando solo se necesita listar usuarios sin permitir
    crear, editar o eliminar.
    
    Endpoints:
    - GET /api/v1/users/ → Lista usuarios (serializer simplificado)
    - GET /api/v1/users/{id}/ → Ver usuario
    
    Permisos:
    - Requiere autenticación
    """
    queryset = User.objects.all().order_by('id')
    serializer_class = UsuarioListSerializer  # Serializer simplificado (menos campos)
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filtra el queryset para ocultar el usuario 'admin' a todos excepto al propio admin.
        
        Reglas:
        - Solo el usuario con username 'admin' puede ver al usuario 'admin' en las listas
        - Todos los demás usuarios (incluso otros ADMIN) no verán al usuario 'admin'
        
        Retorna:
        - QuerySet filtrado según el usuario autenticado
        """
        queryset = super().get_queryset()
        
        # Solo el usuario con username 'admin' puede ver al usuario 'admin'
        # Esto es más estricto que solo verificar el rol, ya que podría haber múltiples usuarios con rol ADMIN
        if self.request.user.is_authenticated and self.request.user.username != "admin":
            queryset = queryset.exclude(username="admin")
        
        return queryset


class PasswordResetRequestView(APIView):
    """
    Vista para solicitar recuperación de contraseña.
    
    Endpoint: POST /api/v1/auth/password-reset/
    
    Permisos:
    - Público (AllowAny) - cualquiera puede solicitar reset
    
    Funcionalidad:
    1. Valida que el email existe y el usuario está activo
    2. Genera un token de reset único
    3. Envía email con link de recuperación
    4. Retorna éxito (sin exponer si el email existe o no)
    
    Seguridad:
    - Siempre retorna 200 para no revelar si un email existe
    - Token expira en 24 horas
    - Solo un token activo por usuario (invalida anteriores)
    
    Relaciones:
    - Usa PasswordResetToken.generate_token() para crear token
    - Envía email usando Django send_mail
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Procesa la solicitud de reset de contraseña.
        
        Parámetros (body JSON):
        - email: Email del usuario
        
        Retorna:
        - 200: Siempre (por seguridad, no revela si el email existe)
        - 400: Error de validación (email inválido)
        """
        from .serializers import PasswordResetRequestSerializer
        from .models import PasswordResetToken
        from django.core.mail import send_mail
        from django.conf import settings
        
        # Validar email
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            # Buscar usuario activo con ese email
            user = User.objects.get(email=email, is_active=True)
            
            # Generar token de reset
            # Esto invalida automáticamente tokens anteriores
            reset_token = PasswordResetToken.generate_token(user)
            
            # Construir URL de reset
            # El frontend debe tener una página en /auth/reset-password
            frontend_url = settings.FRONTEND_URL or 'http://localhost:3000'
            reset_url = f"{frontend_url}/auth/reset-password?token={reset_token.token}"
            
            try:
                # Enviar email con el link de reset
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
                
                # Enviar email
                send_mail(
                    subject="Recuperación de Contraseña - PGF",
                    message=strip_tags(html_message),  # Versión texto plano
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=html_message,  # Versión HTML
                    fail_silently=False,
                )
            except Exception as e:
                # Si falla el envío de email, registrar error pero no fallar la request
                # Esto evita revelar si el email existe
                print(f"Error enviando email de reset: {e}")
        
        except User.DoesNotExist:
            # Usuario no encontrado o inactivo
            # No revelar esto por seguridad (timing attack prevention)
            pass
        
        # Siempre retornar éxito (por seguridad)
        # No revelar si el email existe o no en el sistema
        return Response({
            "message": "Si el email existe, se envió un enlace de recuperación."
        }, status=200)


class PasswordResetConfirmView(APIView):
    """
    Vista para confirmar y cambiar la contraseña con token.
    
    Endpoint: POST /api/v1/auth/password-reset/confirm/
    
    Permisos:
    - Público (AllowAny) - pero requiere token válido
    
    Funcionalidad:
    1. Valida el token de reset
    2. Verifica que el token no haya expirado ni sido usado
    3. Valida la nueva contraseña
    4. Cambia la contraseña del usuario
    5. Marca el token como usado
    6. Retorna éxito
    
    Relaciones:
    - Usa PasswordResetToken para validar token
    - Usa User.set_password() para cambiar contraseña
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Confirma el reset de contraseña.
        
        Parámetros (body JSON):
        - token: Token de reset obtenido del email
        - new_password: Nueva contraseña
        - confirm_password: Confirmación de nueva contraseña
        
        Retorna:
        - 200: Contraseña cambiada exitosamente
        - 400: Token inválido, expirado, o contraseñas no coinciden
        """
        from .serializers import PasswordResetConfirmSerializer
        from .models import PasswordResetToken
        from django.utils import timezone
        
        # Validar datos
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token_str = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            # Buscar token
            reset_token = PasswordResetToken.objects.get(
                token=token_str,
                used=False
            )
            
            # Verificar que no haya expirado
            if not reset_token.is_valid():
                return Response(
                    {"detail": "El token ha expirado o ya fue usado."},
                    status=400
                )
            
            # Cambiar contraseña
            user = reset_token.user
            user.set_password(new_password)  # Hashea la contraseña automáticamente
            user.save()
            
            # Marcar token como usado
            reset_token.used = True
            reset_token.save()
            
            # Registrar auditoría
            from apps.workorders.models import Auditoria
            Auditoria.objects.create(
                usuario=user,
                accion="PASSWORD_RESET",
                objeto_tipo="User",
                objeto_id=str(user.id),
                payload={}
            )
            
            return Response({"message": "Contraseña actualizada correctamente."})
        
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"detail": "Token inválido."},
                status=400
            )


class ChangePasswordView(APIView):
    """
    Vista para que un usuario cambie su propia contraseña.
    
    Endpoint: POST /api/v1/auth/change-password/
    
    Permisos:
    - Requiere autenticación (IsAuthenticated)
    
    Funcionalidad:
    1. Verifica la contraseña actual
    2. Valida la nueva contraseña
    3. Cambia la contraseña
    4. Actualiza la sesión para evitar logout
    5. Registra auditoría
    
    Uso:
    - Llamado desde /profile/change-password en el frontend
    - Permite a usuarios cambiar su contraseña sin recuperación
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Cambia la contraseña del usuario logueado.
        
        Parámetros (body JSON):
        - current_password: Contraseña actual (para verificar)
        - new_password: Nueva contraseña
        - confirm_password: Confirmación de nueva contraseña
        
        Retorna:
        - 200: Contraseña cambiada exitosamente
        - 400: Contraseña actual incorrecta o validación falla
        """
        from .serializers import ChangePasswordSerializer
        from django.contrib.auth import update_session_auth_hash
        from rest_framework import status
        
        # Validar datos
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
        # Esto mantiene al usuario autenticado después del cambio
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
    """
    Vista para que un admin cambie la contraseña de otro usuario.
    
    Endpoint: POST /api/v1/users/{user_id}/change-password/
    
    Permisos:
    - Requiere autenticación
    - Solo ADMIN o SUPERVISOR pueden cambiar contraseñas de otros
    
    Funcionalidad:
    1. Verifica que el usuario sea ADMIN o SUPERVISOR
    2. Busca el usuario objetivo
    3. Valida la nueva contraseña
    4. Cambia la contraseña
    5. Registra auditoría
    
    Uso:
    - Llamado desde /users/{id}/change-password en el frontend
    - Permite a admins resetear contraseñas sin conocer la actual
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id=None):
        """
        Cambia la contraseña de otro usuario.
        
        Parámetros:
        - user_id: ID del usuario cuya contraseña se cambiará (path parameter)
        
        Body JSON:
        - new_password: Nueva contraseña
        - confirm_password: Confirmación de nueva contraseña
        
        Retorna:
        - 200: Contraseña cambiada exitosamente
        - 403: Usuario no tiene permisos
        - 404: Usuario objetivo no encontrado
        - 400: Error de validación
        """
        from .serializers import AdminChangePasswordSerializer
        from rest_framework import status
        
        # Verificar que el usuario sea ADMIN o SUPERVISOR
        if request.user.rol not in ("ADMIN", "SUPERVISOR"):
            return Response(
                {"detail": "No tienes permisos para cambiar contraseñas de otros usuarios."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validar datos
        serializer = AdminChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Buscar usuario objetivo
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
            usuario=request.user,  # Quien hizo el cambio
            accion="ADMIN_CAMBIAR_PASSWORD",
            objeto_tipo="User",
            objeto_id=str(target_user.id),
            payload={"target_user": target_user.username}  # Usuario afectado
        )
        
        return Response({"message": f"Contraseña de {target_user.username} actualizada correctamente."})
