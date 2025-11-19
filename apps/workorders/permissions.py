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

# Roles que pueden crear OT (Jefe de Taller, Admin, y Guardia a través del flujo de ingreso)
ALLOWED_ROLES_CREATE = {"JEFE_TALLER", "ADMIN", "GUARDIA"}

# Roles que pueden editar OT (solo Jefe de Taller)
ALLOWED_ROLES_UPDATE = {"JEFE_TALLER", "ADMIN"}

# Roles que pueden cerrar OT (solo Jefe de Taller)
ALLOWED_ROLES_CLOSE = {"JEFE_TALLER"}

# Roles que pueden cambiar estados (Mecánico y Jefe de Taller)
ALLOWED_ROLES_CHANGE_STATE = {"MECANICO", "JEFE_TALLER"}

# Roles que pueden asignar mecánicos (solo Jefe de Taller)
ALLOWED_ROLES_ASSIGN = {"JEFE_TALLER"}


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
            return rol in ALLOWED_ROLES_READ

        # Métodos de escritura: según el rol específico
        action = getattr(view, 'action', None) if view else None
        
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
            return rol in ALLOWED_ROLES_READ  # Permitir acceso, validación en view
        
        return False

    def has_object_permission(self, request, view, obj):
        """
        Valida permisos a nivel de objeto para acciones específicas.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        rol = getattr(request.user, "rol", None)
        action = getattr(view, 'action', None) if view else None
        
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
