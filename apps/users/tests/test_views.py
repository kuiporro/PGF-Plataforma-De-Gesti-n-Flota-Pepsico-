# apps/users/tests/test_views.py
"""
Tests para las views de usuarios.
"""

import pytest
from django.urls import reverse
from rest_framework import status


class TestUserViewSet:
    """Tests para UserViewSet"""
    
    @pytest.mark.view
    @pytest.mark.api
    def test_user_list_requires_authentication(self, api_client):
        """Test que listar usuarios requiere autenticación"""
        url = "/api/v1/users/"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.view
    @pytest.mark.api
    def test_user_list_admin_access(self, authenticated_client):
        """Test que admin puede listar usuarios"""
        url = "/api/v1/users/"
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.view
    @pytest.mark.api
    def test_user_create(self, authenticated_client):
        """Test creación de usuario"""
        url = "/api/v1/users/"
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "testpass123",
            "rol": "ADMIN"
        }
        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["username"] == "newuser"
    
    @pytest.mark.view
    @pytest.mark.api
    def test_user_update(self, authenticated_client, admin_user):
        """Test actualización de usuario"""
        url = f"/api/v1/users/{admin_user.id}/"
        data = {
            "email": "updated@example.com",
            "rol": "SUPERVISOR"
        }
        response = authenticated_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "updated@example.com"
    
    @pytest.mark.view
    @pytest.mark.api
    def test_user_delete(self, authenticated_client, admin_user):
        """Test eliminación de usuario"""
        url = f"/api/v1/users/{admin_user.id}/"
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestAuthenticationViews:
    """Tests para vistas de autenticación"""
    
    @pytest.mark.view
    @pytest.mark.api
    def test_login_view_success(self, api_client, admin_user):
        """Test login exitoso"""
        url = "/api/v1/auth/login/"
        data = {
            "username": admin_user.username,
            "password": "testpass123"
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
    
    @pytest.mark.view
    @pytest.mark.api
    def test_login_view_invalid_credentials(self, api_client):
        """Test login con credenciales inválidas"""
        url = "/api/v1/auth/login/"
        data = {
            "username": "nonexistent",
            "password": "wrongpass"
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.view
    @pytest.mark.api
    def test_login_view_inactive_user(self, api_client, db):
        """Test login con usuario inactivo"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user = User.objects.create_user(
            username="inactive",
            email="inactive@example.com",
            password="testpass123",
            is_active=False
        )
        
        url = "/api/v1/auth/login/"
        data = {
            "username": user.username,
            "password": "testpass123"
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

