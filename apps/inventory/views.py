# apps/inventory/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from .models import Repuesto, Stock, MovimientoStock, SolicitudRepuesto, HistorialRepuestoVehiculo
from .serializers import (
    RepuestoSerializer, StockSerializer, MovimientoStockSerializer,
    SolicitudRepuestoSerializer, HistorialRepuestoVehiculoSerializer
)
from apps.workorders.models import Auditoria


class RepuestoViewSet(viewsets.ModelViewSet):
    queryset = Repuesto.objects.filter(activo=True).select_related('stock')
    serializer_class = RepuestoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["categoria", "activo"]
    search_fields = ["codigo", "nombre", "marca", "descripcion"]
    ordering_fields = ["nombre", "codigo", "created_at"]


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.select_related('repuesto')
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["repuesto"]
    ordering_fields = ["cantidad_actual", "updated_at"]
    
    @extend_schema(
        description="Lista de repuestos que necesitan reorden"
    )
    @action(detail=False, methods=['get'])
    def necesitan_reorden(self, request):
        """Lista repuestos con stock por debajo del mínimo"""
        from django.db.models import F
        stocks = Stock.objects.filter(
            cantidad_actual__lte=F('cantidad_minima')
        ).select_related('repuesto')
        serializer = self.get_serializer(stocks, many=True)
        return Response(serializer.data)


class MovimientoStockViewSet(viewsets.ModelViewSet):
    queryset = MovimientoStock.objects.select_related(
        'repuesto', 'usuario', 'ot', 'vehiculo'
    )
    serializer_class = MovimientoStockSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["tipo", "repuesto", "ot", "vehiculo"]
    ordering_fields = ["fecha"]


class SolicitudRepuestoViewSet(viewsets.ModelViewSet):
    queryset = SolicitudRepuesto.objects.select_related(
        'ot', 'repuesto', 'solicitante', 'aprobador', 'entregador'
    )
    serializer_class = SolicitudRepuestoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["estado", "ot", "repuesto"]
    ordering_fields = ["fecha_solicitud"]
    
    def perform_create(self, serializer):
        """Al crear solicitud, se asigna el solicitante automáticamente"""
        solicitud = serializer.save(solicitante=self.request.user)
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=self.request.user,
            accion="CREAR_SOLICITUD_REPUESTO",
            objeto_tipo="SolicitudRepuesto",
            objeto_id=str(solicitud.id),
            payload={
                "ot_id": str(solicitud.ot.id),
                "repuesto_id": str(solicitud.repuesto.id),
                "cantidad": solicitud.cantidad_solicitada
            }
        )
    
    @extend_schema(
        description="Aprueba una solicitud de repuesto (Bodega/Supervisor)"
    )
    @action(detail=True, methods=['post'], url_path='aprobar')
    @transaction.atomic
    def aprobar(self, request, pk=None):
        """Aprueba una solicitud de repuesto"""
        if request.user.rol not in ("SUPERVISOR", "ADMIN", "JEFE_TALLER"):
            return Response(
                {"detail": "No autorizado para aprobar solicitudes."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        solicitud = self.get_object()
        
        if solicitud.estado != SolicitudRepuesto.Estado.PENDIENTE:
            return Response(
                {"detail": f"La solicitud ya está {solicitud.estado}."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar stock disponible
        stock = Stock.objects.get(repuesto=solicitud.repuesto)
        if stock.cantidad_actual < solicitud.cantidad_solicitada:
            return Response(
                {"detail": f"Stock insuficiente. Disponible: {stock.cantidad_actual}, Solicitado: {solicitud.cantidad_solicitada}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        solicitud.estado = SolicitudRepuesto.Estado.APROBADA
        solicitud.aprobador = request.user
        solicitud.fecha_aprobacion = timezone.now()
        solicitud.save()
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=request.user,
            accion="APROBAR_SOLICITUD_REPUESTO",
            objeto_tipo="SolicitudRepuesto",
            objeto_id=str(solicitud.id),
            payload={"ot_id": str(solicitud.ot.id)}
        )
        
        return Response(SolicitudRepuestoSerializer(solicitud).data)
    
    @extend_schema(
        description="Rechaza una solicitud de repuesto"
    )
    @action(detail=True, methods=['post'], url_path='rechazar')
    @transaction.atomic
    def rechazar(self, request, pk=None):
        """Rechaza una solicitud de repuesto"""
        if request.user.rol not in ("SUPERVISOR", "ADMIN", "JEFE_TALLER"):
            return Response(
                {"detail": "No autorizado para rechazar solicitudes."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        solicitud = self.get_object()
        
        if solicitud.estado != SolicitudRepuesto.Estado.PENDIENTE:
            return Response(
                {"detail": f"La solicitud ya está {solicitud.estado}."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        solicitud.estado = SolicitudRepuesto.Estado.RECHAZADA
        solicitud.aprobador = request.user
        solicitud.fecha_aprobacion = timezone.now()
        solicitud.motivo = request.data.get("motivo", "")
        solicitud.save()
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=request.user,
            accion="RECHAZAR_SOLICITUD_REPUESTO",
            objeto_tipo="SolicitudRepuesto",
            objeto_id=str(solicitud.id),
            payload={"motivo": solicitud.motivo}
        )
        
        return Response(SolicitudRepuestoSerializer(solicitud).data)
    
    @extend_schema(
        description="Registra la entrega de un repuesto (Bodega)"
    )
    @action(detail=True, methods=['post'], url_path='entregar')
    @transaction.atomic
    def entregar(self, request, pk=None):
        """Registra la entrega de un repuesto y actualiza el stock"""
        if request.user.rol not in ("SUPERVISOR", "ADMIN", "JEFE_TALLER"):
            return Response(
                {"detail": "No autorizado para entregar repuestos."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        solicitud = self.get_object()
        
        if solicitud.estado != SolicitudRepuesto.Estado.APROBADA:
            return Response(
                {"detail": "Solo se pueden entregar solicitudes aprobadas."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cantidad_entregada = request.data.get("cantidad_entregada", solicitud.cantidad_solicitada)
        
        if cantidad_entregada > solicitud.cantidad_solicitada:
            return Response(
                {"detail": "La cantidad entregada no puede ser mayor a la solicitada."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar stock
        stock = Stock.objects.get(repuesto=solicitud.repuesto)
        cantidad_anterior = stock.cantidad_actual
        
        if stock.cantidad_actual < cantidad_entregada:
            return Response(
                {"detail": f"Stock insuficiente. Disponible: {stock.cantidad_actual}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stock.cantidad_actual -= cantidad_entregada
        stock.save()
        
        # Registrar movimiento de stock
        MovimientoStock.objects.create(
            repuesto=solicitud.repuesto,
            tipo=MovimientoStock.TipoMovimiento.SALIDA,
            cantidad=cantidad_entregada,
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=stock.cantidad_actual,
            motivo=f"Entrega para OT {solicitud.ot.id}",
            usuario=request.user,
            ot=solicitud.ot,
            item_ot=solicitud.item_ot,
            vehiculo=solicitud.ot.vehiculo
        )
        
        # Registrar en historial del vehículo
        HistorialRepuestoVehiculo.objects.create(
            vehiculo=solicitud.ot.vehiculo,
            repuesto=solicitud.repuesto,
            cantidad=cantidad_entregada,
            ot=solicitud.ot,
            item_ot=solicitud.item_ot,
            costo_unitario=solicitud.repuesto.precio_referencia
        )
        
        # Actualizar solicitud
        solicitud.cantidad_entregada = cantidad_entregada
        solicitud.estado = SolicitudRepuesto.Estado.ENTREGADA
        solicitud.entregador = request.user
        solicitud.fecha_entrega = timezone.now()
        solicitud.save()
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=request.user,
            accion="ENTREGAR_REPUESTO",
            objeto_tipo="SolicitudRepuesto",
            objeto_id=str(solicitud.id),
            payload={
                "cantidad_entregada": cantidad_entregada,
                "ot_id": str(solicitud.ot.id)
            }
        )
        
        return Response(SolicitudRepuestoSerializer(solicitud).data)


class HistorialRepuestoVehiculoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HistorialRepuestoVehiculo.objects.select_related(
        'vehiculo', 'repuesto', 'ot'
    )
    serializer_class = HistorialRepuestoVehiculoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["vehiculo", "repuesto", "ot"]
    ordering_fields = ["fecha_uso"]

