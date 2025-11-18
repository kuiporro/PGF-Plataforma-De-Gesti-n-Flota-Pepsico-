# apps/workorders/tests/test_models.py
"""
Tests para los modelos de órdenes de trabajo.
"""

import pytest
from datetime import datetime, timedelta
from apps.workorders.models import OrdenTrabajo, Pausa, Evidencia
from apps.vehicles.models import Vehiculo


class TestOrdenTrabajoModel:
    """Tests para el modelo OrdenTrabajo"""
    
    @pytest.mark.model
    def test_orden_trabajo_creation(self, orden_trabajo):
        """Test creación básica de orden de trabajo"""
        assert orden_trabajo.estado == OrdenTrabajo.ESTADOS[0][0]  # ABIERTA
        assert orden_trabajo.motivo_ingreso == "Prueba de OT"
    
    @pytest.mark.model
    def test_orden_trabajo_estado_transitions(self, orden_trabajo):
        """Test transiciones de estado"""
        assert orden_trabajo.estado == "ABIERTA"
        
        orden_trabajo.estado = "EN_DIAGNOSTICO"
        orden_trabajo.save()
        assert orden_trabajo.estado == "EN_DIAGNOSTICO"
    
    @pytest.mark.model
    def test_orden_trabajo_str_representation(self, orden_trabajo):
        """Test representación string de la OT"""
        assert str(orden_trabajo) == f"OT-{orden_trabajo.numero_ot}"


class TestPausaModel:
    """Tests para el modelo Pausa"""
    
    @pytest.mark.model
    def test_pausa_creation(self, db, orden_trabajo, supervisor_user):
        """Test creación de pausa"""
        pausa = Pausa.objects.create(
            ot=orden_trabajo,
            motivo="Colación",
            usuario_pausa=supervisor_user
        )
        assert pausa.ot == orden_trabajo
        assert pausa.motivo == "Colación"
        assert pausa.usuario_pausa == supervisor_user
    
    @pytest.mark.model
    def test_pausa_duracion_calculation(self, db, orden_trabajo, supervisor_user):
        """Test cálculo de duración de pausa"""
        inicio = datetime.now()
        fin = inicio + timedelta(hours=1)
        
        pausa = Pausa.objects.create(
            ot=orden_trabajo,
            motivo="Prueba",
            usuario_pausa=supervisor_user,
            inicio=inicio,
            fin=fin
        )
        
        # La duración debería ser aproximadamente 1 hora
        assert pausa.duracion_minutos is not None
        assert pausa.duracion_minutos >= 59  # Permitir pequeña diferencia


class TestEvidenciaModel:
    """Tests para el modelo Evidencia"""
    
    @pytest.mark.model
    def test_evidencia_creation(self, db, orden_trabajo, supervisor_user):
        """Test creación de evidencia"""
        evidencia = Evidencia.objects.create(
            ot=orden_trabajo,
            tipo="FOTO",
            url="https://example.com/evidencia.jpg",
            descripcion="Evidencia de prueba",
            usuario_subida=supervisor_user
        )
        assert evidencia.ot == orden_trabajo
        assert evidencia.tipo == "FOTO"
        assert evidencia.descripcion == "Evidencia de prueba"

