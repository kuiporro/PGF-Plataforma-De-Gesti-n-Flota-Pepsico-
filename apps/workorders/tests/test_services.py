# apps/workorders/tests/test_services.py
"""
Tests para servicios de workorders (transiciones de estado).
"""

import pytest
from apps.workorders.services import can_transition, transition, do_transition
from apps.workorders.models import OrdenTrabajo


class TestCanTransition:
    """Tests para la función can_transition"""
    
    @pytest.mark.service
    def test_can_transition_abierta_to_en_diagnostico(self):
        """Test transición válida: ABIERTA → EN_DIAGNOSTICO"""
        assert can_transition("ABIERTA", "EN_DIAGNOSTICO") is True
    
    @pytest.mark.service
    def test_can_transition_abierta_to_en_ejecucion(self):
        """Test transición válida: ABIERTA → EN_EJECUCION"""
        assert can_transition("ABIERTA", "EN_EJECUCION") is True
    
    @pytest.mark.service
    def test_can_transition_en_ejecucion_to_en_pausa(self):
        """Test transición válida: EN_EJECUCION → EN_PAUSA"""
        assert can_transition("EN_EJECUCION", "EN_PAUSA") is True
    
    @pytest.mark.service
    def test_can_transition_en_pausa_to_en_ejecucion(self):
        """Test transición válida: EN_PAUSA → EN_EJECUCION"""
        assert can_transition("EN_PAUSA", "EN_EJECUCION") is True
    
    @pytest.mark.service
    def test_can_transition_en_ejecucion_to_en_qa(self):
        """Test transición válida: EN_EJECUCION → EN_QA"""
        assert can_transition("EN_EJECUCION", "EN_QA") is True
    
    @pytest.mark.service
    def test_can_transition_en_qa_to_cerrada(self):
        """Test transición válida: EN_QA → CERRADA"""
        assert can_transition("EN_QA", "CERRADA") is True
    
    @pytest.mark.service
    def test_can_transition_invalid_cerrada_to_abierta(self):
        """Test transición inválida: CERRADA → ABIERTA"""
        assert can_transition("CERRADA", "ABIERTA") is False
    
    @pytest.mark.service
    def test_can_transition_invalid_abierta_to_cerrada(self):
        """Test transición inválida: ABIERTA → CERRADA"""
        assert can_transition("ABIERTA", "CERRADA") is False
    
    @pytest.mark.service
    def test_can_transition_invalid_en_pausa_to_cerrada(self):
        """Test transición inválida: EN_PAUSA → CERRADA"""
        assert can_transition("EN_PAUSA", "CERRADA") is False


class TestTransition:
    """Tests para la función transition"""
    
    @pytest.mark.service
    def test_transition_abierta_to_en_diagnostico(self, orden_trabajo):
        """Test transición exitosa: ABIERTA → EN_DIAGNOSTICO"""
        orden_trabajo.estado = "ABIERTA"
        orden_trabajo.save()
        
        success, error = transition(orden_trabajo, "EN_DIAGNOSTICO")
        
        assert success is True
        assert error is None
        assert orden_trabajo.estado == "EN_DIAGNOSTICO"
        assert orden_trabajo.fecha_diagnostico is not None
    
    @pytest.mark.service
    def test_transition_en_ejecucion_to_en_pausa(self, orden_trabajo):
        """Test transición exitosa: EN_EJECUCION → EN_PAUSA"""
        orden_trabajo.estado = "EN_EJECUCION"
        orden_trabajo.save()
        
        success, error = transition(orden_trabajo, "EN_PAUSA")
        
        assert success is True
        assert error is None
        assert orden_trabajo.estado == "EN_PAUSA"
    
    @pytest.mark.service
    def test_transition_en_ejecucion_sets_fecha_inicio(self, orden_trabajo):
        """Test que EN_EJECUCION establece fecha_inicio_ejecucion"""
        orden_trabajo.estado = "ABIERTA"
        orden_trabajo.fecha_inicio_ejecucion = None
        orden_trabajo.save()
        
        success, error = transition(orden_trabajo, "EN_EJECUCION")
        
        assert success is True
        assert orden_trabajo.fecha_inicio_ejecucion is not None
    
    @pytest.mark.service
    def test_transition_cerrada_sets_cierre(self, orden_trabajo):
        """Test que CERRADA establece fecha de cierre"""
        orden_trabajo.estado = "EN_QA"
        orden_trabajo.cierre = None
        orden_trabajo.save()
        
        success, error = transition(orden_trabajo, "CERRADA")
        
        assert success is True
        assert orden_trabajo.cierre is not None
    
    @pytest.mark.service
    def test_transition_invalid_returns_false(self, orden_trabajo):
        """Test transición inválida retorna False"""
        orden_trabajo.estado = "CERRADA"
        orden_trabajo.save()
        
        success, error = transition(orden_trabajo, "ABIERTA")
        
        assert success is False
        assert error is not None
        assert "inválida" in error.lower() or "invalid" in error.lower()


class TestDoTransition:
    """Tests para la función do_transition"""
    
    @pytest.mark.service
    def test_do_transition_success(self, orden_trabajo):
        """Test do_transition exitosa"""
        orden_trabajo.estado = "ABIERTA"
        orden_trabajo.save()
        
        # No debe lanzar excepción
        do_transition(orden_trabajo, "EN_DIAGNOSTICO")
        
        assert orden_trabajo.estado == "EN_DIAGNOSTICO"
    
    @pytest.mark.service
    def test_do_transition_invalid_raises_exception(self, orden_trabajo):
        """Test do_transition inválida lanza ValueError"""
        orden_trabajo.estado = "CERRADA"
        orden_trabajo.save()
        
        with pytest.raises(ValueError):
            do_transition(orden_trabajo, "ABIERTA")

