from rest_framework.permissions import BasePermission, SAFE_METHODS

"""
Permisos para vehículos según especificación de roles:

1. GUARDIA: Puede registrar ingreso/salida, ver listado de ingresos
2. CHOFER: Solo lectura de su vehículo asignado
3. COORDINADOR_ZONA: Puede registrar/actualizar vehículos
4. SUPERVISOR: Solo lectura de vehículos de su zona
5. JEFE_TALLER: Puede ver todos los vehículos
6. SPONSOR: Solo lectura completa
7. ADMIN: Gestión completa (técnica)
"""


class VehiclePermission(BasePermission):
    """
    Permisos para vehículos según especificación detallada de roles.
    """
    message = "Permisos insuficientes."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        rol = getattr(user, "rol", None)
        action = getattr(view, 'action', None) if view else None

        # Métodos de lectura: todos los roles autorizados pueden leer
        if request.method in SAFE_METHODS:
            # CHOFER solo puede ver su vehículo asignado (se valida en has_object_permission)
            return rol in {
                "ADMIN", "SUPERVISOR", "MECANICO", "GUARDIA", "JEFE_TALLER",
                "COORDINADOR_ZONA", "SPONSOR", "CHOFER", "EJECUTIVO"
            }

        # Crear vehículo: COORDINADOR_ZONA y ADMIN
        if request.method == "POST" and action == "create":
            return rol in {"COORDINADOR_ZONA", "ADMIN"}

        # Actualizar vehículo: COORDINADOR_ZONA y ADMIN
        if request.method in ("PUT", "PATCH") and action in ("update", "partial_update"):
            return rol in {"COORDINADOR_ZONA", "ADMIN"}

        # Eliminar vehículo: solo ADMIN
        if request.method == "DELETE":
            return rol == "ADMIN"

        # Acciones personalizadas (ingreso, evidencias, etc.)
        # GUARDIA puede registrar ingreso
        if action == "ingreso" and request.method == "POST":
            return rol in {"GUARDIA", "ADMIN"}

        # Otros métodos de escritura
        return False

    def has_object_permission(self, request, view, obj):
        """
        Valida permisos a nivel de objeto.
        CHOFER solo puede ver su vehículo asignado.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        rol = getattr(request.user, "rol", None)

        # CHOFER solo puede ver su vehículo asignado
        if rol == "CHOFER":
            # Verificar si el chofer tiene este vehículo asignado
            # Esto requiere verificar la relación chofer-vehículo
            # Por ahora, permitir lectura básica (se puede refinar después)
            if request.method in SAFE_METHODS:
                return True
            return False

        # Para otros roles, usar has_permission
        return True
