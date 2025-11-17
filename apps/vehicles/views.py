# apps/vehicles/views.py

from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from .models import Vehiculo, IngresoVehiculo, EvidenciaIngreso
from .serializers import (
    VehiculoSerializer, VehiculoListSerializer,
    IngresoVehiculoSerializer, EvidenciaIngresoSerializer
)
from .permissions import VehiclePermission
from apps.workorders.models import Auditoria


class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all().order_by("-created_at")
    serializer_class = VehiculoSerializer
    permission_classes = [permissions.IsAuthenticated, VehiclePermission]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ["estado", "marca", "anio"]
    search_fields = ["patente", "marca", "modelo", "vin"]
    ordering_fields = ["patente", "anio", "marca"]

    def get_serializer_class(self):
        if self.action == 'list':
            return VehiculoListSerializer
        return VehiculoSerializer

    @extend_schema(
        request=IngresoVehiculoSerializer,
        responses={201: IngresoVehiculoSerializer},
        description="Registra el ingreso rápido de un vehículo al taller (Guardia)"
    )
    @action(detail=False, methods=['post'], url_path='ingreso', permission_classes=[permissions.IsAuthenticated])
    @transaction.atomic
    def ingreso(self, request):
        """
        Endpoint para que el Guardia registre el ingreso rápido de un vehículo.
        - Si el vehículo no existe, se crea
        - Cambia el estado a EN_ESPERA
        - Crea registro de ingreso
        - Notifica al supervisor
        """
        if request.user.rol != "GUARDIA":
            return Response(
                {"detail": "Solo el Guardia puede registrar ingresos."},
                status=status.HTTP_403_FORBIDDEN
            )

        patente = request.data.get("patente", "").strip().upper()
        if not patente:
            return Response(
                {"detail": "La patente es requerida."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar o crear vehículo
        vehiculo, created = Vehiculo.objects.get_or_create(
            patente=patente,
            defaults={
                "marca": request.data.get("marca", ""),
                "modelo": request.data.get("modelo", ""),
                "anio": request.data.get("anio"),
                "vin": request.data.get("vin", ""),
            }
        )

        # Cambiar estado a EN_ESPERA
        vehiculo.estado = "EN_ESPERA"
        vehiculo.save(update_fields=["estado"])

        # Crear registro de ingreso
        ingreso = IngresoVehiculo.objects.create(
            vehiculo=vehiculo,
            guardia=request.user,
            observaciones=request.data.get("observaciones", ""),
            kilometraje=request.data.get("kilometraje"),
            qr_code=request.data.get("qr_code", ""),
        )

        # Generar OT automáticamente
        from apps.workorders.models import OrdenTrabajo
        from apps.scheduling.models import Agenda
        
        # Buscar si hay una agenda programada para este vehículo
        agenda = Agenda.objects.filter(
            vehiculo=vehiculo,
            estado__in=["PROGRAMADA", "CONFIRMADA"],
            fecha_programada__date=timezone.now().date()
        ).first()
        
        motivo = request.data.get("motivo", "")
        if agenda:
            motivo = f"{agenda.motivo}. {motivo}".strip()
            tipo_mantenimiento = agenda.tipo_mantenimiento
            agenda.estado = "EN_PROCESO"
            agenda.ot_asociada = None  # Se asignará después
            agenda.save()
        else:
            tipo_mantenimiento = "CORRECTIVO" if not motivo else "MANTENCION"
        
        # Crear OT
        ot = OrdenTrabajo.objects.create(
            vehiculo=vehiculo,
            estado="ABIERTA",
            tipo=tipo_mantenimiento,
            motivo=motivo or "Ingreso al taller",
            prioridad=request.data.get("prioridad", "MEDIA"),
            zona=request.data.get("zona", vehiculo.zona or ""),
        )
        
        # Vincular OT con agenda si existe
        if agenda:
            agenda.ot_asociada = ot
            agenda.save()
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=request.user,
            accion="REGISTRAR_INGRESO_VEHICULO",
            objeto_tipo="IngresoVehiculo",
            objeto_id=str(ingreso.id),
            payload={
                "vehiculo_id": str(vehiculo.id),
                "patente": patente,
                "vehiculo_creado": created,
                "ot_generada": str(ot.id)
            }
        )

        # TODO: Notificar al supervisor (implementar con Celery o signals)
        # from apps.workorders.tasks import notificar_ingreso_vehiculo
        # notificar_ingreso_vehiculo.delay(str(ingreso.id))

        serializer = IngresoVehiculoSerializer(ingreso)
        return Response({
            **serializer.data,
            "ot_generada": {
                "id": str(ot.id),
                "estado": ot.estado,
                "motivo": ot.motivo
            }
        }, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=EvidenciaIngresoSerializer,
        responses={201: EvidenciaIngresoSerializer},
        description="Agrega evidencia fotográfica al ingreso de un vehículo"
    )
    @action(detail=True, methods=['post'], url_path='ingreso/evidencias', permission_classes=[permissions.IsAuthenticated])
    def agregar_evidencia_ingreso(self, request, pk=None):
        """Agrega evidencia fotográfica al último ingreso del vehículo"""
        if request.user.rol not in ("GUARDIA", "SUPERVISOR", "ADMIN"):
            return Response(
                {"detail": "No autorizado para agregar evidencias de ingreso."},
                status=status.HTTP_403_FORBIDDEN
            )

        vehiculo = self.get_object()
        ultimo_ingreso = IngresoVehiculo.objects.filter(vehiculo=vehiculo).first()
        
        if not ultimo_ingreso:
            return Response(
                {"detail": "No hay registro de ingreso para este vehículo."},
                status=status.HTTP_404_NOT_FOUND
            )

        evidencia = EvidenciaIngreso.objects.create(
            ingreso=ultimo_ingreso,
            url=request.data.get("url"),
            tipo=request.data.get("tipo", EvidenciaIngreso.TipoEvidencia.FOTO_INGRESO),
            descripcion=request.data.get("descripcion", ""),
        )

        serializer = EvidenciaIngresoSerializer(evidencia)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        description="Obtiene el historial completo del vehículo (OT, repuestos, ingresos)",
        responses={200: None}
    )
    @action(detail=True, methods=['get'], url_path='historial')
    def historial(self, request, pk=None):
        """Retorna el historial completo del vehículo"""
        vehiculo = self.get_object()
        
        # Historial de OT
        from apps.workorders.models import OrdenTrabajo, ItemOT
        ordenes = OrdenTrabajo.objects.filter(vehiculo=vehiculo).select_related(
            'responsable'
        ).prefetch_related('items').order_by('-apertura')
        
        ordenes_data = []
        for ot in ordenes:
            ordenes_data.append({
                "id": str(ot.id),
                "estado": ot.estado,
                "tipo": ot.tipo,
                "prioridad": ot.prioridad,
                "motivo": ot.motivo,
                "responsable": f"{ot.responsable.first_name} {ot.responsable.last_name}" if ot.responsable else None,
                "apertura": ot.apertura.isoformat(),
                "cierre": ot.cierre.isoformat() if ot.cierre else None,
                "items": [{
                    "tipo": item.tipo,
                    "descripcion": item.descripcion,
                    "cantidad": item.cantidad,
                    "costo_unitario": str(item.costo_unitario),
                } for item in ot.items.all()],
            })
        
        # Historial de repuestos (si existe módulo de inventario)
        historial_repuestos = []
        try:
            from apps.inventory.models import HistorialRepuestoVehiculo
            repuestos = HistorialRepuestoVehiculo.objects.filter(
                vehiculo=vehiculo
            ).select_related('repuesto', 'ot').order_by('-fecha_uso')
            
            historial_repuestos = [{
                "repuesto_codigo": h.repuesto.codigo,
                "repuesto_nombre": h.repuesto.nombre,
                "cantidad": h.cantidad,
                "fecha_uso": h.fecha_uso.isoformat(),
                "ot_id": str(h.ot.id) if h.ot else None,
                "costo_unitario": str(h.costo_unitario) if h.costo_unitario else None,
            } for h in repuestos]
        except ImportError:
            pass
        
        # Historial de ingresos
        ingresos = IngresoVehiculo.objects.filter(
            vehiculo=vehiculo
        ).select_related('guardia').prefetch_related('evidencias').order_by('-fecha_ingreso')
        
        ingresos_data = [{
            "id": str(ing.id),
            "fecha_ingreso": ing.fecha_ingreso.isoformat(),
            "guardia": f"{ing.guardia.first_name} {ing.guardia.last_name}",
            "kilometraje": ing.kilometraje,
            "observaciones": ing.observaciones,
            "evidencias": [{
                "tipo": ev.tipo,
                "url": ev.url,
                "descripcion": ev.descripcion,
            } for ev in ing.evidencias.all()],
        } for ing in ingresos]
        
        return Response({
            "vehiculo": {
                "id": str(vehiculo.id),
                "patente": vehiculo.patente,
                "marca": vehiculo.marca,
                "modelo": vehiculo.modelo,
                "anio": vehiculo.anio,
                "estado": vehiculo.estado,
            },
            "ordenes_trabajo": ordenes_data,
            "historial_repuestos": historial_repuestos,
            "ingresos": ingresos_data,
            "total_ordenes": len(ordenes_data),
            "total_repuestos": len(historial_repuestos),
            "total_ingresos": len(ingresos_data),
        })