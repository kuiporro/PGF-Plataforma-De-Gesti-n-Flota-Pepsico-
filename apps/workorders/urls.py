from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    OrdenTrabajoViewSet, ItemOTViewSet, PresupuestoViewSet, DetallePresupViewSet,
    AprobacionViewSet, PausaViewSet, ChecklistViewSet, EvidenciaViewSet,
    PingView,   
)

router = DefaultRouter()

# 🔥 PREFIJO CORRECTO PARA QUE EL FRONT FUNCIONE
router.register(r'ordenes', OrdenTrabajoViewSet, basename='orden-trabajo')
router.register(r'items', ItemOTViewSet, basename='item-ot')
router.register(r'presupuestos', PresupuestoViewSet, basename='presupuesto')
router.register(r'detalles-presupuesto', DetallePresupViewSet, basename='detalle-presupuesto')
router.register(r'aprobaciones', AprobacionViewSet, basename='aprobacion')
router.register(r'pausas', PausaViewSet, basename='pausa')
router.register(r'checklists', ChecklistViewSet, basename='checklist')
router.register(r'evidencias', EvidenciaViewSet, basename='evidencia')

urlpatterns = router.urls
