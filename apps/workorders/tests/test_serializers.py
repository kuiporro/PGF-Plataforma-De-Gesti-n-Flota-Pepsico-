# apps/workorders/tests/test_serializers.py
"""
Tests para los serializers de órdenes de trabajo.
"""

import pytest
from datetime import datetime
from apps.workorders.serializers import OrdenTrabajoSerializer, PausaSerializer
from apps.workorders.models import OrdenTrabajo


class TestOrdenTrabajoSerializer:
    """Tests para OrdenTrabajoSerializer"""
    
    @pytest.mark.serializer
    def test_orden_trabajo_serializer_creation(self, db, vehiculo, supervisor_user, jefe_taller_user):
        """Test creación de OT a través del serializer"""
        data = {
            "vehiculo": vehiculo.id,
            "supervisor": supervisor_user.id,
            "jefe_taller": jefe_taller_user.id,
            "motivo_ingreso": "Prueba de OT",
            "site": "SITE_TEST",
            "fecha_apertura": datetime.now().isoformat()
        }
        serializer = OrdenTrabajoSerializer(data=data)
        assert serializer.is_valid() is True
        
        ot = serializer.save()
        assert ot.vehiculo == vehiculo
        assert ot.motivo_ingreso == "Prueba de OT"
    
    @pytest.mark.serializer
    def test_orden_trabajo_serializer_vehiculo_required(self, db, supervisor_user):
        """Test que el vehículo es requerido"""
        data = {
            "supervisor": supervisor_user.id,
            "motivo_ingreso": "Prueba",
            "site": "SITE_TEST"
        }
        serializer = OrdenTrabajoSerializer(data=data)
        assert serializer.is_valid() is False
        assert "vehiculo" in serializer.errors
    
    @pytest.mark.serializer
    def test_orden_trabajo_serializer_no_duplicate_active_ot(self, db, orden_trabajo, vehiculo, supervisor_user, jefe_taller_user):
        """Test que no se puede crear OT duplicada para vehículo con OT activa"""
        # orden_trabajo ya existe y está ABIERTA
        data = {
            "vehiculo": vehiculo.id,
            "supervisor": supervisor_user.id,
            "jefe_taller": jefe_taller_user.id,
            "motivo_ingreso": "Segunda OT",
            "site": "SITE_TEST",
            "fecha_apertura": datetime.now().isoformat()
        }
        serializer = OrdenTrabajoSerializer(data=data)
        assert serializer.is_valid() is False
        assert "non_field_errors" in serializer.errors or "vehiculo" in serializer.errors


class TestPausaSerializer:
    """Tests para PausaSerializer"""
    
    @pytest.mark.serializer
    def test_pausa_serializer_creation(self, db, orden_trabajo, supervisor_user):
        """Test creación de pausa a través del serializer"""
        # Cambiar estado a EN_EJECUCION para poder pausar
        orden_trabajo.estado = "EN_EJECUCION"
        orden_trabajo.save()
        
        data = {
            "ot": orden_trabajo.id,
            "motivo": "Prueba de pausa",
            "usuario_pausa": supervisor_user.id
        }
        serializer = PausaSerializer(data=data)
        assert serializer.is_valid() is True
        
        pausa = serializer.save()
        assert pausa.ot == orden_trabajo
        assert pausa.motivo == "Prueba de pausa"
    
    @pytest.mark.serializer
    def test_pausa_serializer_only_if_en_ejecucion(self, db, orden_trabajo, supervisor_user):
        """Test que solo se puede pausar si está EN_EJECUCION"""
        # orden_trabajo está en ABIERTA por defecto
        data = {
            "ot": orden_trabajo.id,
            "motivo": "Prueba",
            "usuario_pausa": supervisor_user.id
        }
        serializer = PausaSerializer(data=data)
        assert serializer.is_valid() is False
        assert "non_field_errors" in serializer.errors

