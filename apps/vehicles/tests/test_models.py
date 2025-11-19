# apps/vehicles/tests/test_models.py
"""
Tests para los modelos de vehículos.
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.vehicles.models import Vehiculo, HistorialVehiculo, BackupVehiculo
from apps.workorders.models import OrdenTrabajo


class TestVehiculoModel:
    """Tests para el modelo Vehiculo"""
    
    @pytest.mark.model
    def test_vehiculo_creation(self, vehiculo):
        """Test creación básica de vehículo"""
        assert vehiculo.patente == "TEST01"
        assert vehiculo.marca == "Toyota"
        assert vehiculo.modelo == "Hilux"
        assert vehiculo.anio == 2020
    
    @pytest.mark.model
    def test_vehiculo_patente_unique(self, db, supervisor_user):
        """Test que la patente debe ser única"""
        Vehiculo.objects.create(
            patente="UNIQUE01",
            marca="Toyota",
            modelo="Hilux",
            anio=2020,
            tipo=Vehiculo.TIPOS[0][0],
            estado=Vehiculo.ESTADOS[0][0],
            site="SITE_TEST",
            supervisor=supervisor_user,
            estado_operativo="OPERATIVO"
        )
        
        with pytest.raises(IntegrityError):
            Vehiculo.objects.create(
                patente="UNIQUE01",
                marca="Ford",
                modelo="Ranger",
                anio=2021,
                tipo=Vehiculo.TIPOS[0][0],
                estado=Vehiculo.ESTADOS[0][0],
                site="SITE_TEST",
                supervisor=supervisor_user,
                estado_operativo="OPERATIVO"
            )
    
    @pytest.mark.model
    def test_vehiculo_estado_transitions(self, vehiculo):
        """Test transiciones de estado"""
        assert vehiculo.estado == Vehiculo.ESTADOS[0][0]  # ACTIVO
        
        vehiculo.estado = Vehiculo.ESTADOS[1][0]  # EN_ESPERA
        vehiculo.save()
        assert vehiculo.estado == Vehiculo.ESTADOS[1][0]
    
    @pytest.mark.model
    def test_vehiculo_str_representation(self, vehiculo):
        """Test representación string del vehículo"""
        assert str(vehiculo) == "TEST01"


class TestHistorialVehiculoModel:
    """Tests para el modelo HistorialVehiculo"""
    
    @pytest.mark.model
    def test_historial_creation(self, db, vehiculo, supervisor_user):
        """Test creación de registro en historial"""
        historial = HistorialVehiculo.objects.create(
            vehiculo=vehiculo,
            tipo_evento="OT_CREADA",
            descripcion="OT de prueba creada",
            supervisor=supervisor_user,
            site="SITE_TEST"
        )
        assert historial.vehiculo == vehiculo
        assert historial.tipo_evento == "OT_CREADA"
        assert historial.supervisor == supervisor_user


class TestBackupVehiculoModel:
    """Tests para el modelo BackupVehiculo"""
    
    @pytest.mark.model
    def test_backup_creation(self, db, vehiculo, supervisor_user):
        """Test creación de backup"""
        # Crear vehículo backup
        vehiculo_backup = Vehiculo.objects.create(
            patente="BACKUP01",
            marca="Toyota",
            modelo="Hilux",
            anio=2020,
            tipo=Vehiculo.TIPOS[0][0],
            estado=Vehiculo.ESTADOS[0][0],
            site="SITE_TEST",
            supervisor=supervisor_user,
            estado_operativo="OPERATIVO"
        )
        
        from django.utils import timezone
        
        backup = BackupVehiculo.objects.create(
            vehiculo_principal=vehiculo,
            vehiculo_backup=vehiculo_backup,
            motivo="Prueba de backup",
            supervisor=supervisor_user,
            site="SITE_TEST",
            fecha_inicio=timezone.now()
        )
        assert backup.vehiculo_principal == vehiculo
        assert backup.vehiculo_backup == vehiculo_backup
        assert backup.estado == "ACTIVO"  # El estado por defecto es ACTIVO, no EN_USO

