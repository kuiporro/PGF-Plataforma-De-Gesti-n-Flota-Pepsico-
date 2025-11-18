# apps/drivers/views.py
"""
Vistas y ViewSets para gestión de choferes.

Este módulo define todos los endpoints de la API relacionados con:
- Choferes: CRUD de choferes (conductores de vehículos)
- Historial de asignaciones: Registro de asignaciones de vehículos a choferes

Relaciones:
- Usa: apps/drivers/models.py (Chofer, HistorialAsignacionVehiculo)
- Usa: apps/drivers/serializers.py (serializers para validación)
- Usa: apps/vehicles/models.py (Vehiculo)
- Conectado a: apps/drivers/urls.py

Endpoints principales:
- /api/v1/drivers/choferes/ → CRUD de choferes
- /api/v1/drivers/choferes/{id}/asignar-vehiculo/ → Asignar vehículo a chofer
- /api/v1/drivers/choferes/{id}/historial/ → Historial de asignaciones
- /api/v1/drivers/historial/ → Listar historial de asignaciones
"""

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Chofer, HistorialAsignacionVehiculo
from .serializers import (
    ChoferSerializer, ChoferListSerializer,
    HistorialAsignacionVehiculoSerializer
)


class ChoferViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de choferes.
    
    Proporciona endpoints CRUD completos y acciones personalizadas:
    - GET /api/v1/drivers/choferes/ → Listar choferes (serializer simplificado)
    - POST /api/v1/drivers/choferes/ → Crear chofer
    - GET /api/v1/drivers/choferes/{id}/ → Ver chofer (serializer completo)
    - PUT/PATCH /api/v1/drivers/choferes/{id}/ → Editar chofer
    - DELETE /api/v1/drivers/choferes/{id}/ → Eliminar chofer
    
    Acciones personalizadas:
    - POST /api/v1/drivers/choferes/{id}/asignar-vehiculo/ → Asignar vehículo
    - GET /api/v1/drivers/choferes/{id}/historial/ → Historial de asignaciones
    
    Permisos:
    - Requiere autenticación
    
    Filtros:
    - Por activo, zona, sucursal
    - Búsqueda por nombre_completo, rut, telefono
    - Ordenamiento por nombre, fecha_ingreso, created_at
    """
    # QuerySet con optimización (select_related reduce queries)
    queryset = Chofer.objects.select_related("vehiculo_asignado").all()
    serializer_class = ChoferSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Configuración de filtros
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["activo", "zona", "sucursal"]
    search_fields = ["nombre_completo", "rut", "telefono"]
    ordering_fields = ["nombre_completo", "fecha_ingreso", "created_at"]
    ordering = ["nombre_completo"]  # Orden por defecto
    
    def get_serializer_class(self):
        """
        Retorna el serializer apropiado según la acción.
        
        - list: Usa ChoferListSerializer (menos campos, más rápido)
        - create/update/retrieve: Usa ChoferSerializer (todos los campos)
        """
        if self.action == "list":
            return ChoferListSerializer
        return ChoferSerializer
    
    @action(detail=True, methods=["post"])
    def asignar_vehiculo(self, request, pk=None):
        """
        Asigna un vehículo a un chofer.
        
        Endpoint: POST /api/v1/drivers/choferes/{id}/asignar-vehiculo/
        
        Permisos:
        - Requiere autenticación
        
        Proceso:
        1. Obtiene el chofer
        2. Valida que se proporcione vehiculo_id
        3. Busca el vehículo
        4. Finaliza asignación anterior (si existe)
        5. Asigna nuevo vehículo
        6. Crea registro en historial
        
        Body JSON:
        {
            "vehiculo_id": "uuid-del-vehiculo"
        }
        
        Retorna:
        - 200: Chofer serializado con vehículo asignado
        - 400: Si falta vehiculo_id
        - 404: Si el vehículo no existe
        """
        chofer = self.get_object()
        vehiculo_id = request.data.get("vehiculo_id")
        
        if not vehiculo_id:
            return Response(
                {"detail": "Se requiere vehiculo_id"},
                status=400
            )
        
        # Buscar vehículo
        from apps.vehicles.models import Vehiculo
        try:
            vehiculo = Vehiculo.objects.get(id=vehiculo_id)
        except Vehiculo.DoesNotExist:
            return Response(
                {"detail": "Vehículo no encontrado"},
                status=404
            )
        
        # Finalizar asignación anterior si existe
        if chofer.vehiculo_asignado:
            HistorialAsignacionVehiculo.objects.filter(
                chofer=chofer,
                vehiculo=chofer.vehiculo_asignado,
                activa=True
            ).update(activa=False, motivo_fin="Reasignación")
        
        # Asignar nuevo vehículo
        chofer.vehiculo_asignado = vehiculo
        chofer.save()
        
        # Crear registro en historial
        HistorialAsignacionVehiculo.objects.create(
            chofer=chofer,
            vehiculo=vehiculo,
            activa=True
        )
        
        return Response(ChoferSerializer(chofer).data)
    
    @action(detail=True, methods=["get"])
    def historial(self, request, pk=None):
        """
        Obtiene el historial de asignaciones de un chofer.
        
        Endpoint: GET /api/v1/drivers/choferes/{id}/historial/
        
        Permisos:
        - Requiere autenticación
        
        Retorna:
        - 200: Array de asignaciones serializadas (más recientes primero)
        
        Incluye:
        - Todas las asignaciones del chofer (activas e inactivas)
        - Información del vehículo asignado
        - Fechas de asignación y fin
        - Motivo de fin (si aplica)
        """
        chofer = self.get_object()
        
        # Obtener historial con optimización
        historial = HistorialAsignacionVehiculo.objects.filter(
            chofer=chofer
        ).select_related("vehiculo").order_by("-fecha_asignacion")
        
        serializer = HistorialAsignacionVehiculoSerializer(historial, many=True)
        return Response(serializer.data)


class HistorialAsignacionVehiculoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para historial de asignaciones.
    
    Endpoints:
    - GET /api/v1/drivers/historial/ → Listar todas las asignaciones
    - GET /api/v1/drivers/historial/{id}/ → Ver asignación específica
    
    Permisos:
    - Requiere autenticación
    
    Filtros:
    - Por chofer, vehiculo, activa
    - Ordenamiento por fecha_asignacion (más recientes primero)
    
    Nota:
    - Solo lectura (no permite crear/editar/eliminar)
    - Las asignaciones se crean automáticamente al asignar vehículo
    """
    queryset = HistorialAsignacionVehiculo.objects.select_related(
        "chofer", "vehiculo"
    ).all()
    serializer_class = HistorialAsignacionVehiculoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["chofer", "vehiculo", "activa"]
    ordering = ["-fecha_asignacion"]  # Más recientes primero
