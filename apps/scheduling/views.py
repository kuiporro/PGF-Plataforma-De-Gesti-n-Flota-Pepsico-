# apps/scheduling/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q
from .models import Agenda, CupoDiario
from .serializers import AgendaSerializer, AgendaListSerializer, CupoDiarioSerializer
from apps.workorders.models import OrdenTrabajo


class AgendaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de agenda y programación"""
    queryset = Agenda.objects.select_related("vehiculo", "coordinador").all()
    serializer_class = AgendaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["estado", "tipo_mantenimiento", "zona"]
    search_fields = ["vehiculo__patente", "motivo"]
    ordering_fields = ["fecha_programada", "created_at"]
    ordering = ["fecha_programada"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return AgendaListSerializer
        return AgendaSerializer
    
    def get_queryset(self):
        """Filtrar según rol del usuario"""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Coordinador ve todas las agendas de su zona
        if user.rol == "COORDINADOR_ZONA":
            return queryset.filter(coordinador=user)
        
        # Supervisor ve todas las agendas
        if user.rol in ["SUPERVISOR", "ADMIN", "JEFE_TALLER"]:
            return queryset
        
        # Otros roles ven solo agendas relacionadas
        return queryset.none()
    
    def perform_create(self, serializer):
        """Al crear, verificar disponibilidad y asignar coordinador"""
        user = self.request.user
        
        # Solo coordinadores pueden crear agendas
        if user.rol != "COORDINADOR_ZONA":
            raise permissions.PermissionDenied("Solo coordinadores pueden crear agendas")
        
        fecha_programada = serializer.validated_data.get("fecha_programada")
        vehiculo = serializer.validated_data.get("vehiculo")
        zona = serializer.validated_data.get("zona", "")
        
        # Verificar que no haya solapamiento
        solapamiento = Agenda.objects.filter(
            vehiculo=vehiculo,
            fecha_programada__date=fecha_programada.date(),
            estado__in=["PROGRAMADA", "CONFIRMADA", "EN_PROCESO"]
        ).exists()
        
        if solapamiento:
            raise serializers.ValidationError(
                "Ya existe una agenda activa para este vehículo en esta fecha"
            )
        
        # Verificar cupos disponibles
        fecha = fecha_programada.date()
        cupo, _ = CupoDiario.objects.get_or_create(
            fecha=fecha,
            defaults={"cupos_totales": 10, "zona": zona}
        )
        
        if cupo.cupos_disponibles <= 0:
            raise serializers.ValidationError(
                "No hay cupos disponibles para esta fecha"
            )
        
        # Incrementar cupos ocupados
        cupo.cupos_ocupados += 1
        cupo.save()
        
        serializer.save(coordinador=user)
    
    @action(detail=True, methods=["post"])
    def reprogramar(self, request, pk=None):
        """Reprograma una agenda"""
        agenda = self.get_object()
        nueva_fecha = request.data.get("fecha_programada")
        
        if not nueva_fecha:
            return Response(
                {"detail": "Se requiere fecha_programada"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar disponibilidad
        # ... (lógica similar a perform_create)
        
        agenda.fecha_programada = nueva_fecha
        agenda.estado = "REPROGRAMADA"
        agenda.save()
        
        return Response(AgendaSerializer(agenda).data)
    
    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        """Cancela una agenda"""
        agenda = self.get_object()
        agenda.estado = "CANCELADA"
        agenda.save()
        
        # Liberar cupo
        fecha = agenda.fecha_programada.date()
        try:
            cupo = CupoDiario.objects.get(fecha=fecha)
            if cupo.cupos_ocupados > 0:
                cupo.cupos_ocupados -= 1
                cupo.save()
        except CupoDiario.DoesNotExist:
            pass
        
        return Response(AgendaSerializer(agenda).data)
    
    @action(detail=False, methods=["get"])
    def disponibilidad(self, request):
        """Verifica disponibilidad para una fecha"""
        fecha_str = request.query_params.get("fecha")
        if not fecha_str:
            return Response(
                {"detail": "Se requiere parámetro 'fecha' (YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from datetime import datetime
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Formato de fecha inválido. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cupo, _ = CupoDiario.objects.get_or_create(
            fecha=fecha,
            defaults={"cupos_totales": 10}
        )
        
        return Response({
            "fecha": fecha,
            "cupos_disponibles": cupo.cupos_disponibles,
            "cupos_totales": cupo.cupos_totales,
            "cupos_ocupados": cupo.cupos_ocupados
        })


class CupoDiarioViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet de solo lectura para cupos diarios"""
    queryset = CupoDiario.objects.all()
    serializer_class = CupoDiarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["fecha", "zona"]
    ordering = ["fecha"]

