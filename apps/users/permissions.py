from rest_framework.permissions import BasePermission

class UserPermission(BasePermission):
    def has_permission(self, request, view):
        # Registro público
        if view.action == 'create':
            return True

        # /me requiere autenticación (la view ya lo valida, pero por si acaso)
        if getattr(view, 'action', None) == 'me':
            return request.user and request.user.is_authenticated

        # Listar todos solo admin/supervisor
        if view.action == 'list':
            return request.user and request.user.is_authenticated and request.user.rol in ["ADMIN", "SUPERVISOR"]

        # Resto: autenticado
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Restricción especial: ningún usuario puede ver/editar el usuario 'admin' excepto el propio admin
        if obj.username == "admin" and request.user.rol != "ADMIN":
            return False

        if request.user.rol in ["ADMIN", "SUPERVISOR"]:
            return True

        # Un usuario puede ver/editar su propio objeto
        if view.action in ['retrieve', 'update', 'partial_update', 'me', 'destroy']:
            return obj == request.user

        return False
# Nota: destroy solo admin/supervisor, no lo permitimos a usuarios normales