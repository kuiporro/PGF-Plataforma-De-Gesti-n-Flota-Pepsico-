# conftest.py
"""
Configuración global de pytest para el proyecto PGF.

Este archivo contiene fixtures compartidas que pueden ser usadas
en todos los tests del proyecto.
"""

import pytest
from django.contrib.auth import get_user_model
from apps.vehicles.models import Vehiculo
from apps.workorders.models import OrdenTrabajo
from datetime import datetime, timedelta
import uuid

User = get_user_model()


@pytest.fixture
def admin_user(db):
    """Crea un usuario administrador para pruebas."""
    return User.objects.create_user(
        username="admin_test",
        email="admin@test.com",
        password="testpass123",
        rol=User.Rol.ADMIN,
        is_active=True,
        rut="12345678-9"
    )


@pytest.fixture
def supervisor_user(db):
    """Crea un usuario supervisor para pruebas."""
    return User.objects.create_user(
        username="supervisor_test",
        email="supervisor@test.com",
        password="testpass123",
        rol=User.Rol.SUPERVISOR,
        is_active=True,
        rut="87654321-0"
    )


@pytest.fixture
def jefe_taller_user(db):
    """Crea un usuario jefe de taller para pruebas."""
    return User.objects.create_user(
        username="jefe_taller_test",
        email="jefe@test.com",
        password="testpass123",
        rol=User.Rol.JEFE_TALLER,
        is_active=True,
        rut="11111111-1"
    )


@pytest.fixture
def mecanico_user(db):
    """Crea un usuario mecánico para pruebas."""
    return User.objects.create_user(
        username="mecanico_test",
        email="mecanico@test.com",
        password="testpass123",
        rol=User.Rol.MECANICO,
        is_active=True,
        rut="22222222-2"
    )


@pytest.fixture
def vehiculo(db, supervisor_user):
    """Crea un vehículo de prueba."""
    return Vehiculo.objects.create(
        patente="TEST01",
        marca="Toyota",
        modelo="Hilux",
        anio=2020,
        tipo=Vehiculo.TIPOS[0][0],  # ELECTRICO
        estado=Vehiculo.ESTADOS[0][0],  # ACTIVO
        site="SITE_TEST",
        supervisor=supervisor_user,
        estado_operativo="OPERATIVO"
    )


@pytest.fixture
def orden_trabajo(db, vehiculo, supervisor_user, jefe_taller_user):
    """Crea una orden de trabajo de prueba."""
    return OrdenTrabajo.objects.create(
        vehiculo=vehiculo,
        supervisor=supervisor_user,
        jefe_taller=jefe_taller_user,
        motivo="Prueba de OT",
        estado=OrdenTrabajo.ESTADOS[0][0],  # ABIERTA
        site="SITE_TEST",
        apertura=datetime.now()
    )


@pytest.fixture
def api_client():
    """Cliente API de Django REST Framework."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, admin_user):
    """Cliente API autenticado como admin."""
    api_client.force_authenticate(user=admin_user)
    return api_client

