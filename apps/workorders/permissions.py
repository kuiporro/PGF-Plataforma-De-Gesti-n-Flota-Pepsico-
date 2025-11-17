from rest_framework.permissions import BasePermission, SAFE_METHODS

ALLOWED_ROLES_READ = {"ADMIN", "SUPERVISOR", "MECANICO", "GUARDIA"}
ALLOWED_ROLES_WRITE = {"ADMIN", "SUPERVISOR", "MECANICO"}


class WorkOrderPermission(BasePermission):
    message = "Permisos insuficientes."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        rol = getattr(user, "rol", None)

        if request.method in SAFE_METHODS:
            return rol in ALLOWED_ROLES_READ

        return rol in ALLOWED_ROLES_WRITE
