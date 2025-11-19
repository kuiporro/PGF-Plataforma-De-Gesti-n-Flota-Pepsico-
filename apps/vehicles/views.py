# apps/vehicles/views.py
"""
Vistas y ViewSets para gestión de vehículos.

Este módulo define todos los endpoints de la API relacionados con:
- Vehículos: CRUD de vehículos de la flota
- Ingresos: Registro de ingreso de vehículos al taller
- Evidencias de ingreso: Fotos/documentos del ingreso
- Historial: Historial completo del vehículo (OT, repuestos, ingresos)

Relaciones:
- Usa: apps/vehicles/models.py (Vehiculo, IngresoVehiculo, EvidenciaIngreso)
- Usa: apps/vehicles/serializers.py (serializers para validación)
- Usa: apps/vehicles/permissions.py (VehiclePermission)
- Usa: apps/workorders/models.py (OrdenTrabajo, Auditoria)
- Usa: apps/scheduling/models.py (Agenda)
- Conectado a: apps/vehicles/urls.py

Endpoints principales:
- /api/v1/vehicles/ → CRUD de vehículos
- /api/v1/vehicles/ingreso/ → Registrar ingreso rápido (Guardia)
- /api/v1/vehicles/{id}/ingreso/evidencias/ → Agregar evidencias al ingreso
- /api/v1/vehicles/{id}/historial/ → Historial completo del vehículo
"""

from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction  # Para transacciones atómicas
from django.utils import timezone  # Para timestamps
from drf_spectacular.utils import extend_schema  # Para documentación OpenAPI

from .models import Vehiculo, IngresoVehiculo, EvidenciaIngreso, HistorialVehiculo, BackupVehiculo
from apps.workorders.models import BloqueoVehiculo
from apps.workorders.serializers import BloqueoVehiculoSerializer
from .serializers import (
    VehiculoSerializer, VehiculoListSerializer,
    IngresoVehiculoSerializer, EvidenciaIngresoSerializer,
    HistorialVehiculoSerializer, BackupVehiculoSerializer
)
from .permissions import VehiclePermission
from apps.workorders.models import Auditoria
from apps.core.serializers import EmptySerializer


class VehiculoViewSet(viewsets.ModelViewSet):
    """
    ViewSet principal para gestión de vehículos.
    
    Proporciona endpoints CRUD completos y acciones personalizadas:
    - GET /api/v1/vehicles/ → Listar vehículos (serializer simplificado)
    - POST /api/v1/vehicles/ → Crear vehículo
    - GET /api/v1/vehicles/{id}/ → Ver vehículo (serializer completo)
    - PUT/PATCH /api/v1/vehicles/{id}/ → Editar vehículo
    - DELETE /api/v1/vehicles/{id}/ → Eliminar vehículo
    
    Acciones personalizadas:
    - POST /api/v1/vehicles/ingreso/ → Registrar ingreso rápido (Guardia)
    - POST /api/v1/vehicles/{id}/ingreso/evidencias/ → Agregar evidencias
    - GET /api/v1/vehicles/{id}/historial/ → Historial completo
    
    Permisos:
    - Usa VehiclePermission (permisos personalizados por rol)
    - Requiere autenticación
    
    Filtros:
    - Por estado (ACTIVO, EN_ESPERA, EN_MANTENIMIENTO, BAJA)
    - Por marca, año
    - Búsqueda por patente, marca, modelo, VIN
    - Ordenamiento por patente, año, marca
    """
    # QuerySet base ordenado por fecha de creación (más recientes primero)
    queryset = Vehiculo.objects.all().order_by("-created_at")
    serializer_class = VehiculoSerializer
    permission_classes = [permissions.IsAuthenticated, VehiclePermission]

    # Configuración de filtros
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Filtros exactos
    filterset_fields = ["estado", "marca", "anio"]
    
    # Búsqueda por texto (busca en múltiples campos)
    search_fields = ["patente", "marca", "modelo", "vin"]
    
    # Campos ordenables
    ordering_fields = ["patente", "anio", "marca"]

    def get_serializer_class(self):
        """
        Retorna el serializer apropiado según la acción.
        
        - list: Usa VehiculoListSerializer (menos campos, más rápido)
        - create/update/retrieve: Usa VehiculoSerializer (todos los campos)
        
        Esto optimiza el rendimiento en listados grandes.
        """
        if self.action == 'list':
            return VehiculoListSerializer  # Serializer simplificado para listado
        return VehiculoSerializer  # Serializer completo para detalle/edición

    @extend_schema(
        request=IngresoVehiculoSerializer,
        responses={201: IngresoVehiculoSerializer},
        description="Registra el ingreso rápido de un vehículo al taller (Guardia)"
    )
    @action(detail=False, methods=['post'], url_path='ingreso', permission_classes=[permissions.IsAuthenticated])
    @transaction.atomic
    def ingreso(self, request):
        """
        Registra el ingreso rápido de un vehículo al taller.
        
        Endpoint: POST /api/v1/vehicles/ingreso/
        
        Permisos:
        - Solo GUARDIA puede registrar ingresos
        
        Proceso:
        1. Valida que el usuario sea GUARDIA
        2. Busca o crea el vehículo por patente
        3. Cambia estado del vehículo a EN_ESPERA
        4. Crea registro de IngresoVehiculo
        5. Busca Agenda programada para el día
        6. Genera OT automáticamente (vinculada con Agenda si existe)
        7. Registra auditoría
        
        Body JSON:
        {
            "patente": "ABC123",
            "marca": "Toyota",  // Opcional si el vehículo ya existe
            "modelo": "Hilux",  // Opcional
            "anio": 2020,  // Opcional
            "vin": "123456789",  // Opcional
            "observaciones": "Vehículo con daños en parachoques",
            "kilometraje": 50000,  // Opcional
            "qr_code": "QR123",  // Opcional
            "motivo": "Reparación de parachoques",  // Opcional
            "prioridad": "ALTA",  // Opcional, default: MEDIA
            "zona": "Zona Norte"  // Opcional
        }
        
        Retorna:
        - 201: {
            "id": "...",
            "vehiculo": {...},
            "guardia": {...},
            "fecha_ingreso": "...",
            "ot_generada": {
                "id": "...",
                "estado": "ABIERTA",
                "motivo": "..."
            }
          }
        - 403: Si no es GUARDIA
        - 400: Si falta patente
        
        Características especiales:
        - Si el vehículo no existe, se crea automáticamente
        - Si hay una Agenda programada para hoy, se vincula con la OT
        - La OT se crea automáticamente con estado ABIERTA
        """
        # Verificar que el usuario sea GUARDIA
        if request.user.rol != "GUARDIA":
            return Response(
                {"detail": "Solo el Guardia puede registrar ingresos."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Obtener y normalizar patente (mayúsculas, sin espacios)
        patente = request.data.get("patente", "").strip().upper()
        if not patente:
            return Response(
                {"detail": "La patente es requerida."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar o crear vehículo
        # get_or_create retorna (objeto, created) donde created es True si se creó
        vehiculo, created = Vehiculo.objects.get_or_create(
            patente=patente,
            defaults={
                "marca": request.data.get("marca", ""),
                "modelo": request.data.get("modelo", ""),
                "anio": request.data.get("anio"),
                "vin": request.data.get("vin", ""),
            }
        )

        # Cambiar estado a EN_ESPERA (vehículo ingresado, esperando atención)
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
        
        # Buscar si hay una agenda programada para este vehículo hoy
        agenda = Agenda.objects.filter(
            vehiculo=vehiculo,
            estado__in=["PROGRAMADA", "CONFIRMADA"],  # Estados válidos
            fecha_programada__date=timezone.now().date()  # Solo del día actual
        ).first()
        
        # Obtener motivo del ingreso
        motivo = request.data.get("motivo", "")
        
        # Si hay agenda, usar su información
        if agenda:
            # Combinar motivo de agenda con motivo del ingreso
            motivo = f"{agenda.motivo}. {motivo}".strip()
            tipo_mantenimiento = agenda.tipo_mantenimiento
            # Cambiar estado de agenda a EN_PROCESO
            agenda.estado = "EN_PROCESO"
            agenda.ot_asociada = None  # Se asignará después de crear la OT
            agenda.save()
        else:
            # Si no hay agenda, determinar tipo según motivo
            # Si hay motivo → MANTENCION, si no → CORRECTIVO
            tipo_mantenimiento = "CORRECTIVO" if not motivo else "MANTENCION"
        
        # Buscar o crear chofer si se proporciona información
        chofer = None
        chofer_rut = request.data.get("chofer_rut", "").strip()
        chofer_nombre = request.data.get("chofer_nombre", "").strip()
        
        if chofer_rut or chofer_nombre:
            from apps.drivers.models import Chofer
            from apps.core.validators import validar_rut_chileno
            
            # Si se proporciona RUT, validarlo y buscar/crear chofer
            if chofer_rut:
                es_valido, rut_formateado = validar_rut_chileno(chofer_rut)
                if es_valido:
                    chofer, created = Chofer.objects.get_or_create(
                        rut=rut_formateado.replace("-", "").replace(".", ""),
                        defaults={
                            "nombre_completo": chofer_nombre or "Chofer sin nombre",
                            "activo": True,
                        }
                    )
                    # Si el chofer ya existía, actualizar nombre si se proporcionó
                    if not created and chofer_nombre:
                        chofer.nombre_completo = chofer_nombre
                        chofer.save(update_fields=["nombre_completo"])
                elif chofer_nombre:
                    # Si el RUT no es válido pero hay nombre, crear chofer sin RUT (no recomendado)
                    # Por ahora, no crear chofer si el RUT no es válido
                    pass
        
        # Crear OT automáticamente
        ot = OrdenTrabajo.objects.create(
            vehiculo=vehiculo,
            estado="ABIERTA",  # Estado inicial
            tipo=tipo_mantenimiento,
            motivo=motivo or "Ingreso al taller",
            prioridad=request.data.get("prioridad", "MEDIA"),
            zona=request.data.get("zona", vehiculo.zona or ""),
            site=request.data.get("site", vehiculo.site or ""),
            causa_ingreso=request.data.get("observaciones", ""),
            chofer=chofer,  # Asociar chofer si se proporcionó
        )
        
        # Registrar en historial y calcular SLA
        try:
            from apps.vehicles.utils import registrar_ot_creada, calcular_sla_ot
            registrar_ot_creada(ot, request.user)
            calcular_sla_ot(ot)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al registrar historial para OT {ot.id}: {e}")
        
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
                "vehiculo_creado": created,  # True si se creó el vehículo
                "ot_generada": str(ot.id)
            }
        )

        # TODO: Notificar al supervisor (implementar con Celery o signals)
        # from apps.workorders.tasks import notificar_ingreso_vehiculo
        # notificar_ingreso_vehiculo.delay(str(ingreso.id))

        # Retornar respuesta con información del ingreso y OT generada
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
        responses={200: None},
        description="Genera un PDF del ticket de ingreso de un vehículo"
    )
    @action(detail=False, methods=['get'], url_path='ingreso/(?P<ingreso_id>[^/.]+)/ticket', permission_classes=[permissions.IsAuthenticated])
    def generar_ticket_ingreso(self, request, ingreso_id=None):
        """
        Genera un PDF del ticket de ingreso de un vehículo.
        
        Endpoint: GET /api/v1/vehicles/ingreso/{ingreso_id}/ticket/
        
        Permisos:
        - Requiere autenticación
        
        Retorna:
        - PDF del ticket de ingreso
        """
        from apps.reports.pdf_generator import generar_ticket_ingreso_pdf
        from django.http import HttpResponse
        
        try:
            pdf_buffer = generar_ticket_ingreso_pdf(ingreso_id)
            
            # Crear respuesta HTTP con el PDF
            response = HttpResponse(
                pdf_buffer.getvalue(),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'inline; filename="ticket_ingreso_{ingreso_id[:8]}.pdf"'
            return response
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al generar ticket de ingreso: {e}")
            return Response(
                {"detail": "Error al generar el ticket de ingreso"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        request=EmptySerializer,
        responses={200: None},
        description="Registra la salida de un vehículo del taller"
    )
    @action(detail=False, methods=['post'], url_path='salida', permission_classes=[permissions.IsAuthenticated])
    @transaction.atomic
    def registrar_salida(self, request):
        """
        Registra la salida de un vehículo del taller.
        
        Endpoint: POST /api/v1/vehicles/salida/
        
        Permisos:
        - Solo GUARDIA puede registrar salidas
        
        Body JSON:
        {
            "ingreso_id": "uuid-del-ingreso",
            "observaciones_salida": "Observaciones opcionales",
            "kilometraje_salida": 50000  // Opcional
        }
        """
        # Verificar que el usuario sea GUARDIA
        if request.user.rol != "GUARDIA":
            return Response(
                {"detail": "Solo el Guardia puede registrar salidas."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        ingreso_id = request.data.get("ingreso_id")
        if not ingreso_id:
            return Response(
                {"detail": "El ID del ingreso es requerido."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ingreso = IngresoVehiculo.objects.get(id=ingreso_id)
        except IngresoVehiculo.DoesNotExist:
            return Response(
                {"detail": "Ingreso no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validar que el vehículo no haya salido ya
        if ingreso.salio:
            return Response(
                {"detail": "Este vehículo ya salió del taller."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que todas las OTs estén cerradas
        from apps.workorders.models import OrdenTrabajo
        ots_activas = OrdenTrabajo.objects.filter(
            vehiculo=ingreso.vehiculo,
            estado__in=["ABIERTA", "EN_DIAGNOSTICO", "EN_EJECUCION", "EN_PAUSA", "EN_QA"]
        ).exists()
        
        if ots_activas:
            return Response(
                {"detail": "El vehículo tiene OTs activas. Debe cerrarlas antes de registrar la salida."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Registrar salida
        ingreso.fecha_salida = timezone.now()
        ingreso.guardia_salida = request.user
        ingreso.observaciones_salida = request.data.get("observaciones_salida", "")
        ingreso.kilometraje_salida = request.data.get("kilometraje_salida")
        ingreso.salio = True
        ingreso.save()
        
        # Cambiar estado del vehículo
        ingreso.vehiculo.estado = "ACTIVO"
        ingreso.vehiculo.save(update_fields=["estado"])
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=request.user,
            accion="REGISTRAR_SALIDA_VEHICULO",
            objeto_tipo="IngresoVehiculo",
            objeto_id=str(ingreso.id),
            payload={
                "vehiculo_id": str(ingreso.vehiculo.id),
                "patente": ingreso.vehiculo.patente,
                "fecha_salida": ingreso.fecha_salida.isoformat()
            }
        )
        
        # Registrar en historial
        try:
            from apps.vehicles.utils import registrar_evento_historial
            registrar_evento_historial(
                vehiculo=ingreso.vehiculo,
                tipo_evento="SALIDA_TALLER",
                fecha_salida=ingreso.fecha_salida,
                fecha_ingreso=ingreso.fecha_ingreso,
                descripcion=f"Salida registrada por {request.user.get_full_name()}"
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al registrar historial de salida {ingreso.id}: {e}")
        
        serializer = IngresoVehiculoSerializer(ingreso)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Obtiene la lista de ingresos del día",
        responses={200: None}
    )
    @action(detail=False, methods=['get'], url_path='ingresos-hoy', permission_classes=[permissions.IsAuthenticated])
    def ingresos_hoy(self, request):
        """
        Obtiene la lista de ingresos del día actual.
        
        Endpoint: GET /api/v1/vehicles/ingresos-hoy/
        
        Permisos:
        - GUARDIA, ADMIN, SUPERVISOR
        
        Query params:
        - patente: Filtrar por patente (opcional)
        
        Retorna:
        - 200: Lista de ingresos del día con información completa
        """
        # Verificar permisos
        if request.user.rol not in ["GUARDIA", "ADMIN", "SUPERVISOR"]:
            return Response(
                {"detail": "No tiene permisos para ver ingresos."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Obtener fecha de hoy
        hoy = timezone.now().date()
        
        # Filtrar ingresos del día
        ingresos = IngresoVehiculo.objects.filter(
            fecha_ingreso__date=hoy
        ).select_related("vehiculo", "guardia", "guardia_salida").order_by("-fecha_ingreso")
        
        # Filtrar por patente si se proporciona
        patente = request.query_params.get("patente", "").strip().upper()
        if patente:
            ingresos = ingresos.filter(vehiculo__patente__icontains=patente)
        
        # Serializar
        serializer = IngresoVehiculoSerializer(ingresos, many=True)
        
        return Response({
            "fecha": hoy.isoformat(),
            "total": ingresos.count(),
            "ingresos": serializer.data
        })

    @extend_schema(
        request=EvidenciaIngresoSerializer,
        responses={201: EvidenciaIngresoSerializer},
        description="Agrega evidencia fotográfica al ingreso de un vehículo"
    )
    @action(detail=True, methods=['post'], url_path='ingreso/evidencias', permission_classes=[permissions.IsAuthenticated])
    def agregar_evidencia_ingreso(self, request, pk=None):
        """
        Agrega evidencia fotográfica al último ingreso de un vehículo.
        
        Endpoint: POST /api/v1/vehicles/{id}/ingreso/evidencias/
        
        Permisos:
        - GUARDIA, SUPERVISOR, ADMIN
        
        Proceso:
        1. Valida permisos
        2. Obtiene el vehículo
        3. Busca el último ingreso del vehículo
        4. Crea registro de EvidenciaIngreso
        
        Body JSON:
        {
            "url": "https://s3.../evidencia.jpg",
            "tipo": "FOTO_INGRESO",  // Opcional, default: FOTO_INGRESO
            "descripcion": "Foto del estado del vehículo al ingreso"  // Opcional
        }
        
        Retorna:
        - 201: EvidenciaIngreso serializada
        - 403: Si no tiene permisos
        - 404: Si no hay registro de ingreso
        
        Nota:
        - La URL debe ser de un archivo ya subido a S3
        - Se asocia con el último ingreso del vehículo
        """
        # Verificar permisos
        if request.user.rol not in ("GUARDIA", "SUPERVISOR", "ADMIN"):
            return Response(
                {"detail": "No autorizado para agregar evidencias de ingreso."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Obtener vehículo
        vehiculo = self.get_object()
        
        # Buscar el último ingreso del vehículo (más reciente)
        ultimo_ingreso = IngresoVehiculo.objects.filter(vehiculo=vehiculo).first()
        
        if not ultimo_ingreso:
            return Response(
                {"detail": "No hay registro de ingreso para este vehículo."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Crear evidencia
        evidencia = EvidenciaIngreso.objects.create(
            ingreso=ultimo_ingreso,
            url=request.data.get("url"),  # URL del archivo en S3
            tipo=request.data.get("tipo", EvidenciaIngreso.TipoEvidencia.FOTO_INGRESO),
            descripcion=request.data.get("descripcion", ""),
        )

        # Retornar evidencia serializada
        serializer = EvidenciaIngresoSerializer(evidencia)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        description="Obtiene el historial completo del vehículo (OT, repuestos, ingresos)",
        responses={200: None}
    )
    @action(detail=True, methods=['get'], url_path='historial')
    def historial(self, request, pk=None):
        """
        Retorna el historial completo del vehículo.
        
        Endpoint: GET /api/v1/vehicles/{id}/historial/
        
        Permisos:
        - Requiere autenticación
        
        Retorna:
        - 200: {
            "vehiculo": {...},
            "ordenes_trabajo": [...],
            "historial_repuestos": [...],
            "ingresos": [...],
            "total_ordenes": 10,
            "total_repuestos": 5,
            "total_ingresos": 8
          }
        
        Incluye:
        - Información del vehículo
        - Todas las OT asociadas (con items)
        - Historial de repuestos usados (si existe módulo de inventario)
        - Todos los ingresos al taller (con evidencias)
        
        Optimizaciones:
        - Usa select_related para reducir queries
        - Usa prefetch_related para items y evidencias
        """
        # Obtener vehículo
        vehiculo = self.get_object()
        
        # ==================== HISTORIAL DE OT ====================
        from apps.workorders.models import OrdenTrabajo, ItemOT
        
        # Obtener todas las OT del vehículo con optimizaciones
        ordenes = OrdenTrabajo.objects.filter(vehiculo=vehiculo).select_related(
            'responsable'  # Reducir queries para responsable
        ).prefetch_related('items').order_by('-apertura')  # Más recientes primero
        
        # Serializar OT con sus items
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
        
        # ==================== HISTORIAL DE REPUESTOS ====================
        historial_repuestos = []
        try:
            # Intentar obtener historial de repuestos (si existe módulo de inventario)
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
            # Si el módulo de inventario no existe, continuar sin errores
            pass
        
        # ==================== HISTORIAL DE INGRESOS ====================
        # Obtener todos los ingresos con optimizaciones
        ingresos = IngresoVehiculo.objects.filter(
            vehiculo=vehiculo
        ).select_related('guardia').prefetch_related('evidencias').order_by('-fecha_ingreso')
        
        # Serializar ingresos con evidencias
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
        
        # Retornar historial completo
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


class HistorialVehiculoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar historial de vehículos.
    
    Solo lectura (ReadOnly) porque el historial se crea automáticamente
    cuando ocurren eventos (OT creada, OT cerrada, backup asignado, etc.)
    
    Endpoints:
    - GET /api/v1/vehicles/historial/ → Listar todos los eventos de historial
    - GET /api/v1/vehicles/historial/{id}/ → Ver evento específico
    - GET /api/v1/vehicles/historial/?vehiculo={id} → Filtrar por vehículo
    - GET /api/v1/vehicles/historial/?tipo_evento=OT_CREADA → Filtrar por tipo
    """
    queryset = HistorialVehiculo.objects.all().select_related(
        'vehiculo', 'ot', 'supervisor', 'backup_utilizado'
    ).order_by('-creado_en')
    serializer_class = HistorialVehiculoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['vehiculo', 'tipo_evento', 'site']
    search_fields = ['descripcion', 'falla']
    ordering_fields = ['creado_en', 'fecha_ingreso', 'fecha_salida']


class BackupVehiculoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar backups de vehículos.
    
    Endpoints:
    - GET /api/v1/vehicles/backups/ → Listar todos los backups
    - POST /api/v1/vehicles/backups/ → Crear nuevo backup
    - GET /api/v1/vehicles/backups/{id}/ → Ver backup específico
    - PUT/PATCH /api/v1/vehicles/backups/{id}/ → Actualizar backup
    - DELETE /api/v1/vehicles/backups/{id}/ → Eliminar backup
    
    Acciones personalizadas:
    - POST /api/v1/vehicles/backups/{id}/devolver/ → Devolver backup
    """
    queryset = BackupVehiculo.objects.all().select_related(
        'vehiculo_principal', 'vehiculo_backup', 'ot', 'supervisor'
    ).order_by('-fecha_inicio')
    serializer_class = BackupVehiculoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['vehiculo_principal', 'vehiculo_backup', 'estado', 'site']
    search_fields = ['motivo', 'observaciones']
    ordering_fields = ['fecha_inicio', 'fecha_devolucion', 'duracion_dias']
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo backup y registra en historial.
        """
        response = super().create(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_201_CREATED:
            backup = BackupVehiculo.objects.get(id=response.data['id'])
            
            # Registrar en historial
            try:
                from apps.vehicles.utils import registrar_backup_asignado
                registrar_backup_asignado(backup)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error al registrar historial para backup {backup.id}: {e}")
        
        return response
    
    @extend_schema(
        description="Marca un backup como devuelto y calcula la duración",
        responses={200: BackupVehiculoSerializer}
    )
    @action(detail=True, methods=['post'], url_path='devolver')
    @transaction.atomic
    def devolver(self, request, pk=None):
        """
        Marca un backup como devuelto.
        
        Endpoint: POST /api/v1/vehicles/backups/{id}/devolver/
        
        Proceso:
        1. Valida que el backup esté activo
        2. Establece fecha_devolucion = ahora
        3. Cambia estado a DEVUELTO
        4. Calcula duración automáticamente
        5. Crea evento en historial del vehículo principal
        """
        backup = self.get_object()
        
        if backup.estado != "ACTIVO":
            return Response(
                {"detail": "Solo se pueden devolver backups activos."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Marcar como devuelto
        backup.fecha_devolucion = timezone.now()
        backup.estado = "DEVUELTO"
        backup.calcular_duracion()
        backup.save()
        
        # Crear evento en historial
        from apps.vehicles.utils import registrar_evento_historial
        registrar_evento_historial(
            vehiculo=backup.vehiculo_principal,
            tipo_evento="BACKUP_DEVUELTO",
            ot=backup.ot,
            supervisor=request.user,
            site=backup.site,
            descripcion=f"Backup {backup.vehiculo_backup.patente} devuelto. Duración: {backup.duracion_dias:.2f} días",
            fecha_salida=backup.fecha_devolucion,
            backup=backup,
        )
        
        # Si el vehículo principal no tiene más backups activos, cambiar estado a OPERATIVO
        backups_activos = BackupVehiculo.objects.filter(
            vehiculo_principal=backup.vehiculo_principal,
            estado="ACTIVO"
        ).exists()
        
        if not backups_activos:
            # Verificar si hay OTs abiertas
            from apps.workorders.models import OrdenTrabajo
            ots_abiertas = OrdenTrabajo.objects.filter(
                vehiculo=backup.vehiculo_principal,
                estado__in=["ABIERTA", "EN_DIAGNOSTICO", "EN_EJECUCION", "EN_PAUSA", "EN_QA"]
            ).exists()
            
            if not ots_abiertas:
                backup.vehiculo_principal.estado_operativo = "OPERATIVO"
                backup.vehiculo_principal.save(update_fields=["estado_operativo"])
        
        serializer = self.get_serializer(backup)
        return Response(serializer.data)




# ============== BLOQUEOS DE VEHÍCULOS =================
class BloqueoVehiculoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de bloqueos de vehículos.
    
    Endpoints:
    - GET /api/v1/vehicles/bloqueos/ → Listar bloqueos
    - POST /api/v1/vehicles/bloqueos/ → Crear bloqueo
    - GET /api/v1/vehicles/bloqueos/{id}/ → Ver bloqueo
    - PUT/PATCH /api/v1/vehicles/bloqueos/{id}/ → Editar bloqueo
    - DELETE /api/v1/vehicles/bloqueos/{id}/ → Eliminar bloqueo
    - POST /api/v1/vehicles/bloqueos/{id}/resolver/ → Resolver bloqueo
    """
    queryset = BloqueoVehiculo.objects.select_related("vehiculo", "creado_por", "resuelto_por").all().order_by("-creado_en")
    serializer_class = BloqueoVehiculoSerializer
    permission_classes = [VehiclePermission]
    
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["vehiculo", "tipo", "estado"]
    ordering_fields = ["creado_en"]
    
    def perform_create(self, serializer):
        """Asignar usuario automáticamente al crear bloqueo."""
        serializer.save(creado_por=self.request.user)
        
        # Registrar auditoría
        bloqueo = serializer.instance
        Auditoria.objects.create(
            usuario=self.request.user,
            accion="CREAR_BLOQUEO_VEHICULO",
            objeto_tipo="BloqueoVehiculo",
            objeto_id=str(bloqueo.id),
            payload={
                "vehiculo_id": str(bloqueo.vehiculo.id),
                "patente": bloqueo.vehiculo.patente,
                "tipo": bloqueo.tipo
            }
        )
    
    @extend_schema(
        request=EmptySerializer,
        responses={200: None},
        description="Resuelve un bloqueo de vehículo"
    )
    @action(detail=True, methods=['post'], url_path='resolver')
    @transaction.atomic
    def resolver(self, request, pk=None):
        """
        Resuelve un bloqueo de vehículo.
        
        Endpoint: POST /api/v1/vehicles/bloqueos/{id}/resolver/
        
        Permisos:
        - ADMIN, SUPERVISOR, JEFE_TALLER
        
        Body JSON:
        {
            "motivo_resolucion": "Motivo opcional"  // Opcional
        }
        """
        bloqueo = self.get_object()
        
        if bloqueo.estado != "ACTIVO":
            return Response(
                {"detail": "El bloqueo ya está resuelto o cancelado."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bloqueo.estado = "RESUELTO"
        bloqueo.resuelto_por = request.user
        bloqueo.resuelto_en = timezone.now()
        bloqueo.save()
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=request.user,
            accion="RESOLVER_BLOQUEO_VEHICULO",
            objeto_tipo="BloqueoVehiculo",
            objeto_id=str(bloqueo.id),
            payload={
                "vehiculo_id": str(bloqueo.vehiculo.id),
                "patente": bloqueo.vehiculo.patente
            }
        )
        
        return Response({
            "detail": "Bloqueo resuelto correctamente.",
            "bloqueo": BloqueoVehiculoSerializer(bloqueo).data
        })


