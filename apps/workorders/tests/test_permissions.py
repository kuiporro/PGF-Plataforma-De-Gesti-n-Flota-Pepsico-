# apps/workorders/tests/test_permissions.py
"""
Tests para los permisos de órdenes de trabajo.
"""

import pytest
from rest_framework import status
from apps.workorders.permissions import WorkOrderPermission, ALLOWED_ROLES_READ, ALLOWED_ROLES_WRITE
from apps.workorders.models import OrdenTrabajo


class TestWorkOrderPermission:
    """Tests para WorkOrderPermission"""
    
    @pytest.mark.permission
    def test_unauthenticated_user_denied(self, api_client):
        """Test que usuario no autenticado es denegado"""
        permission = WorkOrderPermission()
        request = type('Request', (), {'user': None, 'method': 'GET'})()
        assert permission.has_permission(request, None) is False
    
    @pytest.mark.permission
    def test_admin_can_read(self, admin_user):
        """Test que ADMIN puede leer"""
        permission = WorkOrderPermission()
        request = type('Request', (), {'user': admin_user, 'method': 'GET'})()
        assert permission.has_permission(request, None) is True
    
    @pytest.mark.permission
    def test_admin_can_write(self, admin_user):
        """Test que ADMIN puede escribir"""
        permission = WorkOrderPermission()
        request = type('Request', (), {'user': admin_user, 'method': 'POST'})()
        assert permission.has_permission(request, None) is True
    
    @pytest.mark.permission
    def test_supervisor_can_read(self, supervisor_user):
        """Test que SUPERVISOR puede leer"""
        permission = WorkOrderPermission()
        request = type('Request', (), {'user': supervisor_user, 'method': 'GET'})()
        assert permission.has_permission(request, None) is True
    
    @pytest.mark.permission
    def test_supervisor_can_write(self, supervisor_user):
        """Test que SUPERVISOR puede escribir"""
        permission = WorkOrderPermission()
        request = type('Request', (), {'user': supervisor_user, 'method': 'POST'})()
        assert permission.has_permission(request, None) is True
    
    @pytest.mark.permission
    def test_mecanico_can_read(self, mecanico_user):
        """Test que MECANICO puede leer"""
        permission = WorkOrderPermission()
        request = type('Request', (), {'user': mecanico_user, 'method': 'GET'})()
        assert permission.has_permission(request, None) is True
    
    @pytest.mark.permission
    def test_mecanico_can_write(self, mecanico_user):
        """Test que MECANICO puede escribir"""
        permission = WorkOrderPermission()
        request = type('Request', (), {'user': mecanico_user, 'method': 'POST'})()
        assert permission.has_permission(request, None) is True
    
    @pytest.mark.permission
    def test_guardia_can_read(self, db):
        """Test que GUARDIA puede leer"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        guardia = User.objects.create_user(
            username="guardia_test",
            email="guardia@test.com",
            password="testpass123",
            rol=User.Rol.GUARDIA,
            is_active=True
        )
        permission = WorkOrderPermission()
        request = type('Request', (), {'user': guardia, 'method': 'GET'})()
        assert permission.has_permission(request, None) is True
    
    @pytest.mark.permission
    def test_guardia_cannot_write(self, db):
        """Test que GUARDIA NO puede escribir"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        guardia = User.objects.create_user(
            username="guardia_test",
            email="guardia@test.com",
            password="testpass123",
            rol=User.Rol.GUARDIA,
            is_active=True
        )
        permission = WorkOrderPermission()
        request = type('Request', (), {'user': guardia, 'method': 'POST'})()
        assert permission.has_permission(request, None) is False
    
    @pytest.mark.permission
    def test_safe_methods_allowed_for_read_roles(self, supervisor_user):
        """Test que métodos seguros (GET, HEAD, OPTIONS) están permitidos para roles de lectura"""
        permission = WorkOrderPermission()
        for method in ['GET', 'HEAD', 'OPTIONS']:
            request = type('Request', (), {'user': supervisor_user, 'method': method})()
            assert permission.has_permission(request, None) is True
    
    @pytest.mark.permission
    def test_unsafe_methods_require_write_role(self, db):
        """Test que métodos no seguros requieren rol de escritura"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        guardia = User.objects.create_user(
            username="guardia_test",
            email="guardia@test.com",
            password="testpass123",
            rol=User.Rol.GUARDIA,
            is_active=True
        )
        permission = WorkOrderPermission()
        for method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            request = type('Request', (), {'user': guardia, 'method': method})()
            assert permission.has_permission(request, None) is False

