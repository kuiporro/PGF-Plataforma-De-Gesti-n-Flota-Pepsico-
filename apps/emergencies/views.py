# apps/emergencies/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q
from .models import EmergenciaRuta
from .serializers import (
    EmergenciaRutaSerializer,
    EmergenciaRutaListSerializer,
    EmergenciaRutaCreateSerializer
)
from apps.workorders.models import OrdenTrabajo


class EmergenciaRutaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de emergencias en ruta"""
    queryset = EmergenciaRuta.objects.select_related(
        "vehiculo", "solicitante", "aprobador",
        "supervisor_asignado", "mecanico_asignado"
    ).all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["estado", "prioridad", "zona"]
    search_fields = ["vehiculo__patente", "descripcion", "ubicacion"]
    ordering_fields = ["fecha_solicitud", "prioridad"]
    ordering = ["-fecha_solicitud"]
    
    def get_serializer_class(self):
        if self.action == "create":
            return EmergenciaRutaCreateSerializer
        if self.action == "list":
            return EmergenciaRutaListSerializer
        return EmergenciaRutaSerializer
    
    def get_queryset(self):
        """Filtrar según rol del usuario"""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Mecánico ve solo sus emergencias asignadas
        if user.rol == "MECANICO":
            return queryset.filter(mecanico_asignado=user)
        
        # Supervisor ve emergencias de su zona
        if user.rol == "SUPERVISOR":
            return queryset.filter(supervisor_asignado=user)
        
        # Coordinador ve emergencias que solicitó o de su zona
        if user.rol == "COORDINADOR_ZONA":
            return queryset.filter(
                Q(solicitante=user) | Q(zona=user.profile.zona if hasattr(user, 'profile') else "")
            )
        
        # Jefe de Taller, Admin ven todas
        if user.rol in ["JEFE_TALLER", "ADMIN"]:
            return queryset
        
        return queryset.none()
    
    def perform_create(self, serializer):
        """Al crear, asignar solicitante"""
        user = self.request.user
        
        # Solo Supervisor o Coordinador pueden solicitar
        if user.rol not in ["SUPERVISOR", "COORDINADOR_ZONA"]:
            raise permissions.PermissionDenied(
                "Solo Supervisores o Coordinadores pueden solicitar emergencias"
            )
        
        serializer.save(solicitante=user, estado="SOLICITADA")
    
    @action(detail=True, methods=["post"])
    def aprobar(self, request, pk=None):
        """Aprueba una emergencia (Jefe de Taller o Subgerencia)"""
        emergencia = self.get_object()
        user = request.user
        
        # Solo Jefe de Taller, Admin o roles superiores pueden aprobar
        if user.rol not in ["JEFE_TALLER", "ADMIN", "EJECUTIVO", "SPONSOR"]:
            return Response(
                {"detail": "No tienes permisos para aprobar emergencias"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if emergencia.estado != "SOLICITADA":
            return Response(
                {"detail": f"La emergencia está en estado {emergencia.estado}, no se puede aprobar"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        emergencia.estado = "APROBADA"
        emergencia.aprobador = user
        emergencia.fecha_aprobacion = timezone.now()
        emergencia.save()
        
        return Response(EmergenciaRutaSerializer(emergencia).data)
    
    @action(detail=True, methods=["post"])
    def asignar_supervisor(self, request, pk=None):
        """Asigna un supervisor a la emergencia"""
        emergencia = self.get_object()
        user = request.user
        supervisor_id = request.data.get("supervisor_id")
        
        # Solo Coordinador o Supervisor pueden asignar
        if user.rol not in ["COORDINADOR_ZONA", "SUPERVISOR", "ADMIN"]:
            return Response(
                {"detail": "No tienes permisos para asignar supervisor"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not supervisor_id:
            return Response(
                {"detail": "Se requiere supervisor_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.users.models import User
        try:
            supervisor = User.objects.get(id=supervisor_id, rol__in=["SUPERVISOR", "COORDINADOR_ZONA"])
        except User.DoesNotExist:
            return Response(
                {"detail": "Supervisor no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        emergencia.supervisor_asignado = supervisor
        if emergencia.estado == "APROBADA":
            emergencia.estado = "ASIGNADA"
            emergencia.fecha_asignacion = timezone.now()
        emergencia.save()
        
        return Response(EmergenciaRutaSerializer(emergencia).data)
    
    @action(detail=True, methods=["post"])
    def asignar_mecanico(self, request, pk=None):
        """Asigna un mecánico a la emergencia (Supervisor)"""
        emergencia = self.get_object()
        user = request.user
        mecanico_id = request.data.get("mecanico_id")
        
        # Solo Supervisor puede asignar mecánico
        if user.rol not in ["SUPERVISOR", "ADMIN"]:
            return Response(
                {"detail": "Solo Supervisores pueden asignar mecánicos"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not mecanico_id:
            return Response(
                {"detail": "Se requiere mecanico_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.users.models import User
        try:
            mecanico = User.objects.get(id=mecanico_id, rol="MECANICO")
        except User.DoesNotExist:
            return Response(
                {"detail": "Mecánico no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        emergencia.mecanico_asignado = mecanico
        emergencia.estado = "ASIGNADA"
        emergencia.fecha_asignacion = timezone.now()
        emergencia.save()
        
        # Crear OT asociada automáticamente
        ot = OrdenTrabajo.objects.create(
            vehiculo=emergencia.vehiculo,
            supervisor=emergencia.supervisor_asignado,
            mecanico=mecanico,
            estado="EN_EJECUCION",
            tipo="EMERGENCIA",
            prioridad=emergencia.prioridad,
            motivo=f"Emergencia en ruta: {emergencia.descripcion}",
            zona=emergencia.zona
        )
        
        emergencia.ot_asociada = ot
        emergencia.save()
        
        return Response(EmergenciaRutaSerializer(emergencia).data)
    
    @action(detail=True, methods=["post"])
    def resolver(self, request, pk=None):
        """Marca la emergencia como resuelta (Mecánico)"""
        emergencia = self.get_object()
        user = request.user
        
        # Solo el mecánico asignado puede resolver
        if emergencia.mecanico_asignado != user:
            return Response(
                {"detail": "Solo el mecánico asignado puede resolver la emergencia"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        emergencia.estado = "RESUELTA"
        emergencia.fecha_resolucion = timezone.now()
        emergencia.save()
        
        return Response(EmergenciaRutaSerializer(emergencia).data)
    
    @action(detail=True, methods=["post"])
    def cerrar(self, request, pk=None):
        """Cierra la emergencia (Supervisor)"""
        emergencia = self.get_object()
        user = request.user
        
        # Solo Supervisor puede cerrar
        if user.rol not in ["SUPERVISOR", "ADMIN"]:
            return Response(
                {"detail": "Solo Supervisores pueden cerrar emergencias"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if emergencia.estado != "RESUELTA":
            return Response(
                {"detail": "La emergencia debe estar resuelta para cerrarse"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        emergencia.estado = "CERRADA"
        emergencia.fecha_cierre = timezone.now()
        emergencia.save()
        
        # Cerrar OT asociada si existe
        if emergencia.ot_asociada:
            emergencia.ot_asociada.estado = "CERRADA"
            emergencia.ot_asociada.cierre = timezone.now()
            emergencia.ot_asociada.save()
        
        return Response(EmergenciaRutaSerializer(emergencia).data)
    
    @action(detail=True, methods=["post"])
    def rechazar(self, request, pk=None):
        """Rechaza una emergencia (Aprobador)"""
        emergencia = self.get_object()
        user = request.user
        
        # Solo quien puede aprobar puede rechazar
        if user.rol not in ["JEFE_TALLER", "ADMIN", "EJECUTIVO", "SPONSOR"]:
            return Response(
                {"detail": "No tienes permisos para rechazar emergencias"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        motivo = request.data.get("motivo", "")
        emergencia.estado = "RECHAZADA"
        emergencia.observaciones = f"Rechazada: {motivo}"
        emergencia.save()
        
        return Response(EmergenciaRutaSerializer(emergencia).data)

