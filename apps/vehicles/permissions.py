from rest_framework.permissions import BasePermission

class VehiclePermission(BasePermission):

    def has_permission(self, request, view):
        if request.method in ("GET",):
            return request.user.is_authenticated

        return request.user.rol in ("ADMIN", "SUPERVISOR")
