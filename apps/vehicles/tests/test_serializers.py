# apps/vehicles/tests/test_serializers.py
"""
Tests para los serializers de vehículos.
"""

import pytest
from apps.vehicles.serializers import VehiculoSerializer, IngresoVehiculoSerializer, BackupVehiculoSerializer
from apps.vehicles.models import Vehiculo, IngresoVehiculo, BackupVehiculo
from datetime import datetime


class TestVehiculoSerializer:
    """Tests para VehiculoSerializer"""
    
    @pytest.mark.serializer
    def test_vehiculo_serializer_creation(self, db, supervisor_user):
        """Test creación de vehículo a través del serializer"""
        data = {
            "patente": "NEW001",
            "marca": "Toyota",
            "modelo": "Hilux",
            "anio": 2020,
            "tipo_vehiculo": "ELECTRICO",
            "tipo_motor": "ELECTRICO",
            "estado": "ACTIVO",
            "site": "SITE_TEST",
            "supervisor": supervisor_user.id,
            "estado_operativo": "OPERATIVO"
        }
        serializer = VehiculoSerializer(data=data)
        assert serializer.is_valid() is True
        
        vehiculo = serializer.save()
        assert vehiculo.patente == "NEW001"
        assert vehiculo.marca == "Toyota"
    
    @pytest.mark.serializer
    def test_vehiculo_serializer_patente_validation(self, db, supervisor_user):
        """Test validación de formato de patente"""
        data = {
            "patente": "INVALID",  # Formato inválido
            "marca": "Toyota",
            "modelo": "Hilux",
            "anio": 2020,
            "tipo_vehiculo": "ELECTRICO",
            "tipo_motor": "ELECTRICO",
            "estado": "ACTIVO",
            "site": "SITE_TEST",
            "supervisor": supervisor_user.id,
            "estado_operativo": "OPERATIVO"
        }
        serializer = VehiculoSerializer(data=data)
        assert serializer.is_valid() is False
        assert "patente" in serializer.errors
    
    @pytest.mark.serializer
    def test_vehiculo_serializer_patente_unique(self, db, vehiculo, supervisor_user):
        """Test que la patente debe ser única"""
        data = {
            "patente": vehiculo.patente,  # Patente existente
            "marca": "Ford",
            "modelo": "Ranger",
            "anio": 2021,
            "tipo_vehiculo": "ELECTRICO",
            "tipo_motor": "ELECTRICO",
            "estado": "ACTIVO",
            "site": "SITE_TEST",
            "supervisor": supervisor_user.id,
            "estado_operativo": "OPERATIVO"
        }
        serializer = VehiculoSerializer(data=data)
        assert serializer.is_valid() is False
        assert "patente" in serializer.errors
    
    @pytest.mark.serializer
    def test_vehiculo_serializer_ano_validation(self, db, supervisor_user):
        """Test validación de año"""
        # Año menor a 2000
        data = {
            "patente": "TEST02",
            "marca": "Toyota",
            "modelo": "Hilux",
            "anio": 1999,
            "tipo_vehiculo": "ELECTRICO",
            "tipo_motor": "ELECTRICO",
            "estado": "ACTIVO",
            "site": "SITE_TEST",
            "supervisor": supervisor_user.id,
            "estado_operativo": "OPERATIVO"
        }
        serializer = VehiculoSerializer(data=data)
        assert serializer.is_valid() is False
        assert "anio" in serializer.errors
    
    @pytest.mark.serializer
    def test_vehiculo_serializer_required_fields(self, db, supervisor_user):
        """Test que los campos requeridos son validados"""
        data = {
            "patente": "TEST03",
            # Faltan campos requeridos
        }
        serializer = VehiculoSerializer(data=data)
        assert serializer.is_valid() is False
        # Debe tener errores en campos requeridos
        assert len(serializer.errors) > 0


class TestIngresoVehiculoSerializer:
    """Tests para IngresoVehiculoSerializer"""
    
    @pytest.mark.serializer
    def test_ingreso_serializer_creation(self, db, vehiculo, supervisor_user):
        """Test creación de ingreso a través del serializer"""
        data = {
            "vehiculo": vehiculo.id,
            "nombre_conductor": "Juan Pérez",
            "rut_conductor": "12345678-9",
            "fecha_ingreso": datetime.now().isoformat(),
            "site": "SITE_TEST"
        }
        serializer = IngresoVehiculoSerializer(data=data)
        assert serializer.is_valid() is True
        
        ingreso = serializer.save()
        assert ingreso.vehiculo == vehiculo
        assert ingreso.nombre_conductor == "Juan Pérez"
    
    @pytest.mark.serializer
    def test_ingreso_serializer_rut_conductor_validation(self, db, vehiculo):
        """Test validación de RUT del conductor"""
        data = {
            "vehiculo": vehiculo.id,
            "nombre_conductor": "Juan Pérez",
            "rut_conductor": "12345678-0",  # RUT inválido
            "fecha_ingreso": datetime.now().isoformat(),
            "site": "SITE_TEST"
        }
        serializer = IngresoVehiculoSerializer(data=data)
        assert serializer.is_valid() is False
        assert "rut_conductor" in serializer.errors or "non_field_errors" in serializer.errors


class TestBackupVehiculoSerializer:
    """Tests para BackupVehiculoSerializer"""
    
    @pytest.mark.serializer
    def test_backup_serializer_creation(self, db, vehiculo, supervisor_user):
        """Test creación de backup a través del serializer"""
        # Crear vehículo backup
        vehiculo_backup = Vehiculo.objects.create(
            patente="BACKUP02",
            marca="Toyota",
            modelo="Hilux",
            anio=2020,
            tipo_vehiculo=Vehiculo.TIPOS[0][0],
            tipo_motor=Vehiculo.TIPOS[0][0],
            estado=Vehiculo.ESTADOS[0][0],
            site="SITE_TEST",
            supervisor=supervisor_user,
            estado_operativo="OPERATIVO"
        )
        
        data = {
            "vehiculo_principal": vehiculo.id,
            "vehiculo_backup": vehiculo_backup.id,
            "fecha_inicio": datetime.now().isoformat(),
            "motivo": "Prueba de backup",
            "site": "SITE_TEST"
        }
        serializer = BackupVehiculoSerializer(data=data)
        assert serializer.is_valid() is True
        
        backup = serializer.save()
        assert backup.vehiculo_principal == vehiculo
        assert backup.vehiculo_backup == vehiculo_backup
    
    @pytest.mark.serializer
    def test_backup_serializer_same_vehicle_validation(self, db, vehiculo):
        """Test que no se puede usar el mismo vehículo como backup"""
        data = {
            "vehiculo_principal": vehiculo.id,
            "vehiculo_backup": vehiculo.id,  # Mismo vehículo
            "fecha_inicio": datetime.now().isoformat(),
            "motivo": "Prueba",
            "site": "SITE_TEST"
        }
        serializer = BackupVehiculoSerializer(data=data)
        assert serializer.is_valid() is False
        assert "non_field_errors" in serializer.errors

