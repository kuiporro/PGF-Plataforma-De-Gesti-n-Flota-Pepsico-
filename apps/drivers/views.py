# apps/drivers/views.py
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
    """ViewSet para gestión de choferes"""
    queryset = Chofer.objects.select_related("vehiculo_asignado").all()
    serializer_class = ChoferSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["activo", "zona", "sucursal"]
    search_fields = ["nombre_completo", "rut", "telefono"]
    ordering_fields = ["nombre_completo", "fecha_ingreso", "created_at"]
    ordering = ["nombre_completo"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return ChoferListSerializer
        return ChoferSerializer
    
    @action(detail=True, methods=["post"])
    def asignar_vehiculo(self, request, pk=None):
        """Asigna un vehículo a un chofer"""
        chofer = self.get_object()
        vehiculo_id = request.data.get("vehiculo_id")
        
        if not vehiculo_id:
            return Response(
                {"detail": "Se requiere vehiculo_id"},
                status=400
            )
        
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
        """Obtiene el historial de asignaciones de un chofer"""
        chofer = self.get_object()
        historial = HistorialAsignacionVehiculo.objects.filter(
            chofer=chofer
        ).select_related("vehiculo").order_by("-fecha_asignacion")
        
        serializer = HistorialAsignacionVehiculoSerializer(historial, many=True)
        return Response(serializer.data)


class HistorialAsignacionVehiculoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet de solo lectura para historial de asignaciones"""
    queryset = HistorialAsignacionVehiculo.objects.select_related(
        "chofer", "vehiculo"
    ).all()
    serializer_class = HistorialAsignacionVehiculoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["chofer", "vehiculo", "activa"]
    ordering = ["-fecha_asignacion"]

