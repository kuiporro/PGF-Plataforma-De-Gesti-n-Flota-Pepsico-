from rest_framework.permissions import BasePermission, SAFE_METHODS

"""
Permisos para órdenes de trabajo según especificación de roles:

1. GUARDIA: Puede crear OT a través del flujo de ingreso de vehículos (es el primer actor del proceso)
2. CHOFER: Solo lectura de su vehículo/OT
3. MECANICO: Puede cambiar estados pero NO cerrar OT
4. JEFE_TALLER: Puede crear/editar/cerrar OT
5. SUPERVISOR: Solo lectura de OT de su zona (NO crear/cerrar)
6. COORDINADOR_ZONA: Puede ver OT de su zona (NO cerrar)
7. SPONSOR: Solo lectura completa (NO editar/cerrar)
8. ADMIN: Gestión técnica (NO operativa - no crear/editar OT)
"""

# Roles que pueden leer OT
ALLOWED_ROLES_READ = {
    "ADMIN", "SUPERVISOR", "MECANICO", "GUARDIA", "JEFE_TALLER", 
    "COORDINADOR_ZONA", "SPONSOR", "CHOFER", "EJECUTIVO"
}

# Roles que pueden crear OT directamente (Jefe de Taller y Admin)
# NOTA: GUARDIA puede crear OT a través del flujo de ingreso de vehículos,
# pero NO puede crear OT directamente desde el endpoint de creación
ALLOWED_ROLES_CREATE = {"JEFE_TALLER", "ADMIN"}

# Roles que pueden editar OT (solo Jefe de Taller)
ALLOWED_ROLES_UPDATE = {"JEFE_TALLER", "ADMIN"}

# Roles que pueden cerrar OT (solo Jefe de Taller)
ALLOWED_ROLES_CLOSE = {"JEFE_TALLER"}

# Roles que pueden cambiar estados (Mecánico y Jefe de Taller)
ALLOWED_ROLES_CHANGE_STATE = {"MECANICO", "JEFE_TALLER"}

# Roles que pueden asignar mecánicos (solo Jefe de Taller)
ALLOWED_ROLES_ASSIGN = {"JEFE_TALLER"}

# Roles que pueden crear evidencias (Mecánico, Supervisor, Admin, Guardia, Jefe de Taller)
ALLOWED_ROLES_CREATE_EVIDENCIA = {"MECANICO", "SUPERVISOR", "ADMIN", "GUARDIA", "JEFE_TALLER"}

# Roles que pueden ver/listar/descargar evidencias
# Jefe de Taller: todas las evidencias de su Site
# Supervisor Zonal: solo evidencias de su Site
# Administrador: todas las evidencias
# Mecánico: evidencias que él subió o de la OT en la que trabaja
# Guardia: evidencias iniciales que registró
ALLOWED_ROLES_VIEW_EVIDENCIA = {"JEFE_TALLER", "SUPERVISOR", "ADMIN", "MECANICO", "GUARDIA"}

# Roles que pueden crear comentarios (Mecánico, Supervisor, Admin, Jefe de Taller)
ALLOWED_ROLES_CREATE_COMENTARIO = {"MECANICO", "SUPERVISOR", "ADMIN", "JEFE_TALLER", "GUARDIA", "COORDINADOR_ZONA"}


class WorkOrderPermission(BasePermission):
    """
    Permisos para órdenes de trabajo según especificación detallada de roles.
    """
    message = "Permisos insuficientes."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        rol = getattr(user, "rol", None)

        # Métodos de lectura: todos los roles autorizados pueden leer
        if request.method in SAFE_METHODS:
            # Para evidencias, usar permisos específicos
            is_evidencia_view = False
            if view:
                serializer_class = getattr(view, 'serializer_class', None)
                if serializer_class:
                    serializer_name = serializer_class.__name__ if hasattr(serializer_class, '__name__') else ""
                    is_evidencia_view = "Evidencia" in serializer_name
                
                if not is_evidencia_view:
                    view_class_name = view.__class__.__name__ if hasattr(view, '__class__') else ""
                    is_evidencia_view = "Evidencia" in view_class_name
                
                if not is_evidencia_view:
                    queryset = getattr(view, 'queryset', None)
                    if queryset and hasattr(queryset, 'model'):
                        model_name = queryset.model.__name__ if hasattr(queryset.model, '__name__') else ""
                        is_evidencia_view = "Evidencia" in model_name
            
            if not is_evidencia_view and hasattr(request, 'path'):
                is_evidencia_view = "/evidencias/" in request.path or "/evidencia/" in request.path
            
            if is_evidencia_view:
                # ADMIN siempre tiene acceso total a evidencias
                if rol == "ADMIN":
                    return True
                return rol in ALLOWED_ROLES_VIEW_EVIDENCIA
            
            return rol in ALLOWED_ROLES_READ

        # Métodos de escritura: según el rol específico
        action = getattr(view, 'action', None) if view else None
        
        # Detectar si es EvidenciaViewSet
        # Método más confiable: verificar el serializer_class o el queryset
        is_evidencia_view = False
        is_comentario_view = False
        if view:
            # Método 1: Por serializer_class (más confiable)
            serializer_class = getattr(view, 'serializer_class', None)
            if serializer_class:
                serializer_name = serializer_class.__name__ if hasattr(serializer_class, '__name__') else ""
                is_evidencia_view = "Evidencia" in serializer_name
                is_comentario_view = "Comentario" in serializer_name
            
            # Método 2: Por nombre de clase
            if not is_evidencia_view and not is_comentario_view:
                view_class_name = view.__class__.__name__ if hasattr(view, '__class__') else ""
                is_evidencia_view = "Evidencia" in view_class_name
                is_comentario_view = "Comentario" in view_class_name
            
            # Método 3: Por queryset model
            if not is_evidencia_view and not is_comentario_view:
                queryset = getattr(view, 'queryset', None)
                if queryset and hasattr(queryset, 'model'):
                    model_name = queryset.model.__name__ if hasattr(queryset.model, '__name__') else ""
                    is_evidencia_view = "Evidencia" in model_name
                    is_comentario_view = "Comentario" in model_name
        
        # Método 4: Por path de la URL (fallback)
        if not is_evidencia_view and not is_comentario_view and hasattr(request, 'path'):
            is_evidencia_view = "/evidencias/" in request.path or "/evidencia/" in request.path
            is_comentario_view = "/comentarios/" in request.path or "/comentario/" in request.path
        
        # Crear evidencia: Mecánico, Supervisor, Admin, Guardia, Jefe de Taller
        if request.method == "POST" and action == "create" and is_evidencia_view:
            # ADMIN siempre puede crear evidencias
            if rol == "ADMIN":
                return True
            return rol in ALLOWED_ROLES_CREATE_EVIDENCIA
        
        # Crear comentario: Mecánico, Supervisor, Admin, Jefe de Taller, Guardia, Coordinador
        if request.method == "POST" and action == "create" and is_comentario_view:
            return rol in ALLOWED_ROLES_CREATE_COMENTARIO
        
        # Crear OT: solo Jefe de Taller y Admin
        if request.method == "POST" and action == "create":
            return rol in ALLOWED_ROLES_CREATE
        
        # Actualizar OT: solo Jefe de Taller y Admin
        if request.method in ("PUT", "PATCH") and action in ("update", "partial_update"):
            return rol in ALLOWED_ROLES_UPDATE
        
        # Eliminar OT: solo Admin (gestión técnica)
        if request.method == "DELETE":
            return rol == "ADMIN"
        
        # Acciones personalizadas se validan en has_object_permission
        # Permitir POST para acciones personalizadas (se validan en la view)
        if request.method == "POST" and action not in ("create",):
            # ADMIN siempre tiene acceso
            if rol == "ADMIN":
                return True
            return rol in ALLOWED_ROLES_READ  # Permitir acceso, validación en view
        
        # ADMIN siempre tiene acceso para otros métodos (PUT, PATCH, DELETE en evidencias)
        if rol == "ADMIN" and is_evidencia_view:
            return True
        
        return False

    def has_object_permission(self, request, view, obj):
        """
        Valida permisos a nivel de objeto para acciones específicas.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        rol = getattr(request.user, "rol", None)
        action = getattr(view, 'action', None) if view else None
        
        # Validar permisos específicos para evidencias
        from .models import Evidencia
        if isinstance(obj, Evidencia):
            # Jefe de Taller: puede ver todas las evidencias de su Site
            if rol == "JEFE_TALLER":
                if obj.ot and obj.ot.vehiculo:
                    # Verificar que el vehículo pertenezca al mismo Site del Jefe de Taller
                    user_site = getattr(request.user, 'profile', None)
                    if user_site and hasattr(user_site, 'site'):
                        return obj.ot.vehiculo.site == user_site.site
                    # Si no tiene site configurado, permitir acceso (fallback)
                    return True
                return True  # Permitir acceso a evidencias sin OT
            
            # Supervisor Zonal: solo evidencias de su Site
            if rol == "SUPERVISOR":
                if obj.ot and obj.ot.vehiculo:
                    user_site = getattr(request.user, 'profile', None)
                    if user_site and hasattr(user_site, 'site'):
                        return obj.ot.vehiculo.site == user_site.site
                    return False
                return False
            
            # Administrador: acceso total (siempre permitir)
            if rol == "ADMIN":
                return True
            
            # Mecánico: solo evidencias que él subió o de la OT en la que trabaja
            if rol == "MECANICO":
                # Puede ver si él la subió
                if obj.subido_por == request.user:
                    return True
                # Puede ver si es de una OT asignada a él
                if obj.ot and obj.ot.mecanico == request.user:
                    return True
                return False
            
            # Guardia: solo evidencias iniciales que registró
            if rol == "GUARDIA":
                # Puede ver si él la subió
                if obj.subido_por == request.user:
                    return True
                # Puede ver evidencias de ingreso/salida relacionadas con sus registros
                # (esto se puede refinar más adelante)
                return False
        
        # CHOFER solo puede ver OT de su vehículo asignado
        if rol == "CHOFER":
            # Verificar si el chofer tiene un vehículo asignado y si la OT es de ese vehículo
            # Esto requiere verificar la relación chofer-vehículo
            # Por ahora, permitir lectura básica (se puede refinar después)
            if request.method in SAFE_METHODS:
                return True
            return False
        
        # Para otros roles, usar has_permission
        return True
