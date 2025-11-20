# apps/workorders/views.py
"""
Vistas y ViewSets para gestión de Órdenes de Trabajo.

Este módulo define todos los endpoints de la API relacionados con:
- Órdenes de Trabajo (OT): CRUD y transiciones de estado
- Items de OT: Repuestos y servicios
- Presupuestos: Gestión de presupuestos y aprobaciones
- Pausas: Gestión de pausas durante ejecución (incluye colación automática)
- Checklists: Control de calidad (QA)
- Evidencias: Subida de fotos/documentos a S3

Relaciones:
- Usa: apps/workorders/models.py (todos los modelos)
- Usa: apps/workorders/serializers.py (serializers para validación)
- Usa: apps/workorders/services.py (transiciones de estado)
- Usa: apps/workorders/permissions.py (WorkOrderPermission)
- Usa: apps/workorders/filters.py (OrdenTrabajoFilter)
- Conectado a: apps/workorders/urls.py

Endpoints principales:
- /api/v1/work/ordenes/ → CRUD de OT
- /api/v1/work/ordenes/{id}/diagnostico/ → Diagnóstico por Jefe de Taller
- /api/v1/work/ordenes/{id}/aprobar-asignacion/ → Aprobación de asignación
- /api/v1/work/items/ → CRUD de items
- /api/v1/work/presupuestos/ → CRUD de presupuestos
- /api/v1/work/pausas/ → CRUD de pausas
- /api/v1/work/checklists/ → CRUD de checklists
- /api/v1/work/evidencias/ → CRUD de evidencias
"""

import os  # Para variables de entorno
import uuid  # Para generar IDs únicos
import mimetypes  # Para detectar tipos MIME de archivos
import re  # Para expresiones regulares
from decimal import Decimal  # Para cálculos precisos de dinero
from urllib.parse import urlparse, urlunparse  # Para manipular URLs

import boto3  # Cliente AWS S3
from botocore.config import Config  # Configuración de boto3

from django.db import transaction  # Para transacciones atómicas
from django.utils import timezone  # Para timestamps

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from drf_spectacular.utils import extend_schema  # Para documentación OpenAPI

from apps.core.serializers import EmptySerializer
from .filters import OrdenTrabajoFilter
from .permissions import WorkOrderPermission
from .services import transition, do_transition
from .serializers import OrdenTrabajoListSerializer

from .models import (
    OrdenTrabajo, ItemOT, Presupuesto, DetallePresup,
    Aprobacion, Pausa, Checklist, Evidencia, Auditoria,
    ComentarioOT, BloqueoVehiculo, VersionEvidencia
)
from .serializers import (
    OrdenTrabajoSerializer, ItemOTSerializer,
    PresupuestoSerializer, DetallePresupSerializer,
    AprobacionSerializer, PausaSerializer,
    ChecklistSerializer, EvidenciaSerializer,
    ComentarioOTSerializer, BloqueoVehiculoSerializer, VersionEvidenciaSerializer
)


class PingView(APIView):
    """
    Vista simple para verificar que el servidor está funcionando.
    
    Endpoint: POST /api/v1/work/ping/
    
    Permisos:
    - Requiere autenticación (IsAuthenticated)
    
    Uso:
    - Healthcheck del sistema
    - Verificar que el token JWT es válido
    - Testing de conectividad
    
    Retorna:
    - 200: {"ok": True} si el servidor está funcionando
    - 401: Si no hay token o es inválido
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmptySerializer
    http_method_names = ["post"]  # Solo acepta POST

    @extend_schema(
        request=EmptySerializer,
        responses={200: None},
        description="Ping de salud autenticado"
    )
    def post(self, request, *args, **kwargs):
        """
        Retorna OK si el servidor está funcionando y el usuario está autenticado.
        
        Parámetros:
        - request: HttpRequest con usuario autenticado
        
        Retorna:
        - Response con {"ok": True}
        """
        return Response({"ok": True})


# ============== ORDENES DE TRABAJO =================
class OrdenTrabajoViewSet(viewsets.ModelViewSet):
    """
    ViewSet principal para gestión de Órdenes de Trabajo.
    
    Proporciona endpoints CRUD completos y acciones personalizadas:
    - GET /api/v1/work/ordenes/ → Listar OT
    - POST /api/v1/work/ordenes/ → Crear OT
    - GET /api/v1/work/ordenes/{id}/ → Ver OT
    - PUT/PATCH /api/v1/work/ordenes/{id}/ → Editar OT
    - DELETE /api/v1/work/ordenes/{id}/ → Eliminar OT
    
    Acciones personalizadas:
    - POST /api/v1/work/ordenes/{id}/en-ejecucion/ → Cambiar a EN_EJECUCION
    - POST /api/v1/work/ordenes/{id}/en-qa/ → Cambiar a EN_QA
    - POST /api/v1/work/ordenes/{id}/en-pausa/ → Cambiar a EN_PAUSA
    - POST /api/v1/work/ordenes/{id}/cerrar/ → Cerrar OT
    - POST /api/v1/work/ordenes/{id}/anular/ → Anular OT
    - POST /api/v1/work/ordenes/{id}/diagnostico/ → Realizar diagnóstico
    - POST /api/v1/work/ordenes/{id}/aprobar-asignacion/ → Aprobar asignación
    - POST /api/v1/work/ordenes/{id}/retrabajo/ → Marcar como retrabajo
    
    Permisos:
    - Usa WorkOrderPermission (permisos personalizados por rol)
    
    Filtros:
    - Por estado, vehículo, supervisor, mecánico, etc.
    - Búsqueda por patente de vehículo
    - Ordenamiento por fecha, estado, etc.
    """
    # QuerySet base con optimización (select_related reduce queries)
    queryset = OrdenTrabajo.objects.select_related("vehiculo", "responsable").all().order_by("-apertura")
    serializer_class = OrdenTrabajoSerializer

    # Configuración de filtros
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = OrdenTrabajoFilter  # Usar el filtro personalizado
    ordering_fields = ["id", "apertura", "cierre", "estado"]  # Campos ordenables
    search_fields = ["vehiculo__patente"]  # Búsqueda por patente

    def create(self, request, *args, **kwargs):
        """
        Crea una nueva OT y envía notificaciones a usuarios relevantes.
        
        Sobrescribe el método create del ModelViewSet para agregar
        lógica de notificaciones y registro de historial cuando se crea una nueva OT.
        
        Flujo según rol:
        - GUARDIA: Crea OT cuando el vehículo llega al taller, estado ABIERTA
        - SUPERVISOR/ADMIN: Pueden crear OT con supervisor asignado
        """
        # Validar que solo JEFE_TALLER, ADMIN o GUARDIA pueden crear OT
        # GUARDIA solo puede crear OT a través del flujo de ingreso de vehículos
        # (que se maneja en apps/vehicles/views.py), pero permitimos aquí para consistencia
        if request.user.rol not in ("JEFE_TALLER", "ADMIN", "GUARDIA"):
            return Response(
                {"detail": "Solo JEFE_TALLER, ADMIN o GUARDIA pueden crear OT."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Crear la OT usando el método del padre
        response = super().create(request, *args, **kwargs)
        
        # Si la creación fue exitosa, crear notificaciones y registrar historial
        if response.status_code == status.HTTP_201_CREATED:
            ot = OrdenTrabajo.objects.get(id=response.data['id'])
            
            # Asegurar que el estado sea ABIERTA por defecto
            if ot.estado != "ABIERTA":
                ot.estado = "ABIERTA"
                ot.save(update_fields=["estado"])
            
            # Registrar en historial del vehículo
            try:
                from apps.vehicles.utils import registrar_ot_creada, calcular_sla_ot
                registrar_ot_creada(ot, request.user)
                calcular_sla_ot(ot)  # Calcular SLA automáticamente
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error al registrar historial para OT {ot.id}: {e}")
            
            # Crear notificaciones para usuarios relevantes
            try:
                from apps.notifications.utils import crear_notificacion_ot_creada
                crear_notificacion_ot_creada(ot, request.user)
            except Exception as e:
                # Si falla la creación de notificaciones, no fallar la creación de OT
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error al crear notificaciones para OT {ot.id}: {e}")
        
        return response

    def perform_destroy(self, instance):
        """
        Eliminar OT de forma segura.
        
        Este método se ejecuta antes de eliminar una OT.
        Limpia relaciones con módulos que pueden no estar migrados
        (inventory) para evitar errores de ForeignKey.
        
        Parámetros:
        - instance: Instancia de OrdenTrabajo a eliminar
        
        Proceso:
        1. Intenta eliminar SolicitudRepuesto relacionadas (si existe la tabla)
        2. Intenta limpiar MovimientoStock relacionados (si existe la tabla)
        3. Elimina la OT (esto elimina automáticamente items, pausas, evidencias, etc.)
        
        Nota: Usa try/except para que si las tablas no existen,
        la eliminación continúe sin errores.
        """
        try:
            # Intentar eliminar solicitudes de repuestos relacionadas
            from apps.inventory.models import SolicitudRepuesto
            SolicitudRepuesto.objects.filter(ot=instance).delete()
        except Exception:
            # Si la tabla no existe o hay error, continuar
            pass
        
        try:
            # Intentar limpiar movimientos de stock relacionados
            from apps.inventory.models import MovimientoStock
            MovimientoStock.objects.filter(ot=instance).update(ot=None)
        except Exception:
            # Si la tabla no existe o hay error, continuar
            pass
        
        # Eliminar la OT
        # Django automáticamente eliminará:
        # - Items (CASCADE)
        # - Pausas (CASCADE)
        # - Evidencias (CASCADE)
        # - Checklists (CASCADE)
        instance.delete()

    @extend_schema(request=EmptySerializer, responses={200: None})
    @action(detail=True, methods=['post'], url_path='en-ejecucion')
    def en_ejecucion(self, request, pk=None):
        """
        Cambia el estado de la OT a EN_EJECUCION.
        
        Endpoint: POST /api/v1/work/ordenes/{id}/en-ejecucion/
        
        Permisos:
        - Solo SUPERVISOR, ADMIN o MECANICO
        
        Flujo:
        1. Verifica permisos
        2. Obtiene la OT
        3. Ejecuta transición de estado (valida que sea válida)
        4. Retorna nuevo estado
        
        Retorna:
        - 200: {"estado": "EN_EJECUCION"}
        - 403: Si no tiene permisos
        - 400: Si la transición no es válida
        """
        # Solo MECANICO y JEFE_TALLER pueden cambiar a EN_EJECUCION
        if request.user.rol not in ("MECANICO", "JEFE_TALLER"):
            return Response(
                {"detail": "Solo MECANICO o JEFE_TALLER pueden iniciar la ejecución."},
                status=status.HTTP_403_FORBIDDEN
            )
        ot = self.get_object()
        do_transition(ot, "EN_EJECUCION")  # Valida y ejecuta transición
        return Response({"estado": ot.estado})

    @extend_schema(request=EmptySerializer, responses={200: None})
    @action(detail=True, methods=['post'], url_path='en-qa')
    def en_qa(self, request, pk=None):
        """
        Cambia el estado de la OT a EN_QA (Control de Calidad).
        
        Endpoint: POST /api/v1/work/ordenes/{id}/en-qa/
        
        Permisos:
        - Solo SUPERVISOR o ADMIN
        
        Uso:
        - Cuando el mecánico termina el trabajo y necesita revisión de calidad
        
        Retorna:
        - 200: {"estado": "EN_QA"}
        - 403: Si no tiene permisos
        """
        # Solo MECANICO y JEFE_TALLER pueden mover a QA
        if request.user.rol not in ("MECANICO", "JEFE_TALLER"):
            return Response(
                {"detail": "Solo MECANICO o JEFE_TALLER pueden mover a QA."},
                status=status.HTTP_403_FORBIDDEN
            )
        ot = self.get_object()
        do_transition(ot, "EN_QA")
        return Response({"estado": ot.estado})

    @extend_schema(request=EmptySerializer, responses={200: None})
    @action(detail=True, methods=['post'], url_path='en-pausa')
    @transaction.atomic
    def en_pausa(self, request, pk=None):
        """
        Cambia el estado de la OT a EN_PAUSA.
        
        Endpoint: POST /api/v1/work/ordenes/{id}/en-pausa/
        
        Permisos:
        - MECANICO, SUPERVISOR, ADMIN, JEFE_TALLER
        
        Nota:
        - Alternativa a crear una Pausa explícita
        - Útil para pausas rápidas sin necesidad de registrar motivo
        
        Retorna:
        - 200: {"estado": "EN_PAUSA"}
        - 403: Si no tiene permisos
        """
        # Solo MECANICO y JEFE_TALLER pueden pausar
        if request.user.rol not in ("MECANICO", "JEFE_TALLER"):
            return Response(
                {"detail": "Solo MECANICO o JEFE_TALLER pueden pausar OT."},
                status=status.HTTP_403_FORBIDDEN
            )
        ot = self.get_object()
        do_transition(ot, "EN_PAUSA")
        return Response({"estado": ot.estado})

    @extend_schema(request=EmptySerializer, responses={200: None})
    @action(detail=True, methods=['post'], url_path='cerrar')
    @transaction.atomic
    def cerrar(self, request, pk=None):
        """
        Cierra la OT definitivamente.
        
        Endpoint: POST /api/v1/work/ordenes/{id}/cerrar/
        
        Permisos:
        - Solo SUPERVISOR, ADMIN o JEFE_TALLER
        
        Requisitos:
        - La OT debe estar en EN_QA o CERRADA
        - Debe incluir fecha_cierre, diagnostico_final y estado_final = CERRADA
        
        Proceso:
        1. Valida estado
        2. Valida campos obligatorios (fecha_cierre, diagnostico_final)
        3. Ejecuta transición a CERRADA
        4. Genera PDF de cierre (tarea Celery asíncrona)
        5. Registra auditoría
        
        Retorna:
        - 200: {"estado": "CERRADA", "cierre": "2024-01-15T10:30:00Z"}
        - 403: Si no tiene permisos
        - 400: Si el estado no permite cerrar o faltan campos obligatorios
        """
        # Solo JEFE_TALLER puede cerrar OT
        if request.user.rol != "JEFE_TALLER":
            return Response(
                {"detail": "Solo JEFE_TALLER puede cerrar la OT."},
                status=status.HTTP_403_FORBIDDEN
            )
        ot = self.get_object()
        
        # Validar que el estado permita cerrar
        if ot.estado not in ("EN_QA", "CERRADA"):
            return Response(
                {"detail": f"No se puede cerrar una OT en estado {ot.estado}. Debe estar en EN_QA."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar campos obligatorios para el cierre
        diagnostico_final = request.data.get('diagnostico_final') or request.data.get('diagnostico')
        fecha_cierre = request.data.get('fecha_cierre') or request.data.get('cierre')
        
        if not diagnostico_final:
            return Response(
                {"detail": "El campo diagnostico_final es obligatorio para cerrar la OT."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not fecha_cierre:
            return Response(
                {"detail": "El campo fecha_cierre es obligatorio para cerrar la OT."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar diagnóstico y fecha de cierre
        ot.diagnostico = diagnostico_final
        if fecha_cierre:
            from django.utils.dateparse import parse_datetime
            fecha_parsed = parse_datetime(fecha_cierre)
            if fecha_parsed:
                ot.cierre = fecha_parsed
            else:
                return Response(
                    {"detail": "El formato de fecha_cierre es inválido. Use formato ISO 8601."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Ejecutar transición (actualiza estado y fecha de cierre)
        do_transition(ot, "CERRADA")
        
        # Registrar en historial del vehículo y calcular tiempos
        try:
            from apps.vehicles.utils import registrar_ot_cerrada
            registrar_ot_cerrada(ot, request.user)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al registrar historial para OT {ot.id}: {e}")
        
        # Generar PDF de cierre automáticamente (tarea asíncrona)
        try:
            from .tasks import generar_pdf_cierre
            generar_pdf_cierre.delay(str(ot.id), request.user.id)
        except Exception:
            # Si no existe la tarea, continuar sin error
            pass
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=request.user,
            accion="CERRAR_OT",
            objeto_tipo="OrdenTrabajo",
            objeto_id=str(ot.id),
            payload={}
        )
        
        # Crear notificaciones
        try:
            from apps.notifications.utils import crear_notificacion_ot_cerrada
            crear_notificacion_ot_cerrada(ot, request.user)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al crear notificaciones para OT cerrada {ot.id}: {e}")
        
        return Response({"estado": ot.estado, "cierre": ot.cierre})

    @extend_schema(request=EmptySerializer, responses={200: None})
    @action(detail=True, methods=['post'], url_path='anular')
    def anular(self, request, pk=None):
        """
        Anula la OT (cancela antes de completarse).
        
        Endpoint: POST /api/v1/work/ordenes/{id}/anular/
        
        Permisos:
        - Solo SUPERVISOR o ADMIN
        
        Uso:
        - Cuando se detecta que la OT fue creada por error
        - Cuando el vehículo ya no necesita reparación
        
        Retorna:
        - 200: {"estado": "ANULADA"}
        - 403: Si no tiene permisos
        """
        # Solo JEFE_TALLER puede anular OT
        if request.user.rol != "JEFE_TALLER":
            return Response(
                {"detail": "Solo JEFE_TALLER puede anular la OT."},
                status=status.HTTP_403_FORBIDDEN
            )
        ot = self.get_object()
        do_transition(ot, "ANULADA")
        return Response({"estado": ot.estado})
    
    @extend_schema(
        request={"type": "object", "properties": {"diagnostico": {"type": "string"}}},
        responses={200: None}
    )
    @action(detail=True, methods=['post'], url_path='diagnostico')
    @transaction.atomic
    def diagnostico(self, request, pk=None):
        """
        Jefe de Taller realiza diagnóstico de la OT.
        
        Endpoint: POST /api/v1/work/ordenes/{id}/diagnostico/
        
        Permisos:
        - Solo JEFE_TALLER o ADMIN
        
        Requisitos:
        - La OT debe estar en ABIERTA o EN_DIAGNOSTICO
        - Se debe proporcionar el texto del diagnóstico
        
        Proceso:
        1. Valida permisos y estado
        2. Guarda diagnóstico y asigna jefe_taller
        3. Establece fecha_diagnostico
        4. Cambia estado a EN_DIAGNOSTICO
        5. Registra auditoría
        
        Body JSON:
        {
            "diagnostico": "Texto del diagnóstico técnico"
        }
        
        Retorna:
        - 200: {"estado": "EN_DIAGNOSTICO", "diagnostico": "..."}
        - 403: Si no tiene permisos
        - 400: Si falta diagnóstico o estado inválido
        """
        if request.user.rol not in ("JEFE_TALLER", "ADMIN"):
            return Response(
                {"detail": "Solo JEFE_TALLER puede realizar diagnóstico."},
                status=status.HTTP_403_FORBIDDEN
            )
        ot = self.get_object()
        
        # Validar estado
        if ot.estado not in ("ABIERTA", "EN_DIAGNOSTICO"):
            return Response(
                {"detail": f"La OT debe estar en ABIERTA o EN_DIAGNOSTICO para realizar diagnóstico."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener diagnóstico del body
        diagnostico_texto = request.data.get("diagnostico", "")
        if not diagnostico_texto:
            return Response(
                {"detail": "El diagnóstico es requerido."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Guardar diagnóstico y asignar jefe de taller
        ot.diagnostico = diagnostico_texto
        ot.jefe_taller = request.user
        ot.fecha_diagnostico = timezone.now()
        
        # Cambiar estado (actualiza fecha_diagnostico automáticamente)
        do_transition(ot, "EN_DIAGNOSTICO")
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=request.user,
            accion="DIAGNOSTICO_OT",
            objeto_tipo="OrdenTrabajo",
            objeto_id=str(ot.id),
            payload={"diagnostico": diagnostico_texto}
        )
        
        return Response({"estado": ot.estado, "diagnostico": ot.diagnostico})
    
    @extend_schema(
        request={"type": "object", "properties": {
            "mecanico_id": {"type": "string"},
            "prioridad": {"type": "string"}
        }},
        responses={200: None}
    )
    @action(detail=True, methods=['post'], url_path='aprobar-asignacion')
    @transaction.atomic
    def aprobar_asignacion(self, request, pk=None):
        """
        Supervisor aprueba la asignación de un mecánico a la OT.
        
        Endpoint: POST /api/v1/work/ordenes/{id}/aprobar-asignacion/
        
        Permisos:
        - Solo SUPERVISOR, ADMIN o COORDINADOR_ZONA
        
        Requisitos:
        - La OT debe estar en EN_DIAGNOSTICO
        - Se debe proporcionar mecanico_id
        
        Proceso:
        1. Valida permisos y estado
        2. Busca el mecánico (debe tener rol MECANICO)
        3. Asigna mecánico y supervisor
        4. Establece fechas de aprobación y asignación
        5. Ajusta prioridad si se proporciona
        6. Cambia estado a EN_EJECUCION
        7. Registra auditoría
        
        Body JSON:
        {
            "mecanico_id": "uuid-del-mecanico",
            "prioridad": "ALTA"  // Opcional
        }
        
        Retorna:
        - 200: {"estado": "EN_EJECUCION", "mecanico": "...", "supervisor": "..."}
        - 403: Si no tiene permisos
        - 400: Si falta mecanico_id o estado inválido
        - 404: Si el mecánico no existe
        """
        # JEFE_TALLER y ADMIN pueden asignar mecánicos
        if request.user.rol not in ["JEFE_TALLER", "ADMIN"]:
            return Response(
                {"detail": "Solo JEFE_TALLER o ADMIN pueden asignar mecánicos."},
                status=status.HTTP_403_FORBIDDEN
            )
        ot = self.get_object()
        
        # Validar estado - permitir asignar desde ABIERTA o EN_DIAGNOSTICO
        if ot.estado not in ["ABIERTA", "EN_DIAGNOSTICO"]:
            return Response(
                {"detail": f"La OT debe estar en ABIERTA o EN_DIAGNOSTICO para asignar mecánico. Estado actual: {ot.estado}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener ID del mecánico
        mecanico_id = request.data.get("mecanico_id")
        if not mecanico_id:
            return Response(
                {"detail": "Se requiere mecanico_id."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar mecánico (debe tener rol MECANICO)
        from apps.users.models import User
        try:
            mecanico = User.objects.get(id=mecanico_id, rol="MECANICO")
        except User.DoesNotExist:
            return Response(
                {"detail": "Mecánico no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Asignar mecánico
        ot.mecanico = mecanico
        
        # Si no tiene supervisor, asignar el usuario actual si es supervisor
        if not ot.supervisor and request.user.rol in ["SUPERVISOR", "COORDINADOR_ZONA", "ADMIN"]:
            ot.supervisor = request.user
            ot.fecha_aprobacion_supervisor = timezone.now()
        elif ot.supervisor:
            # Si ya tiene supervisor, actualizar fecha de aprobación
            ot.fecha_aprobacion_supervisor = timezone.now()
        
        ot.fecha_asignacion_mecanico = timezone.now()
        
        # Ajustar prioridad si se proporciona
        nueva_prioridad = request.data.get("prioridad")
        if nueva_prioridad:
            ot.prioridad = nueva_prioridad
        
        # Cambiar estado a EN_EJECUCION
        do_transition(ot, "EN_EJECUCION")
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=request.user,
            accion="APROBAR_ASIGNACION_OT",
            objeto_tipo="OrdenTrabajo",
            objeto_id=str(ot.id),
            payload={"mecanico_id": str(mecanico.id), "mecanico": mecanico.username}
        )
        
        # Crear notificaciones
        try:
            from apps.notifications.utils import crear_notificacion_ot_asignada
            crear_notificacion_ot_asignada(ot, mecanico)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al crear notificaciones para OT asignada {ot.id}: {e}")
        
        return Response({
            "estado": ot.estado,
            "mecanico": mecanico.username,
            "supervisor": request.user.username
        })
    
    @action(detail=True, methods=['post'], url_path='retrabajo')
    @transaction.atomic
    def retrabajo(self, request, pk=None):
        """
        Marca la OT como retrabajo (requiere corrección después de QA).
        
        Endpoint: POST /api/v1/work/ordenes/{id}/retrabajo/
        
        Permisos:
        - Solo SUPERVISOR, ADMIN o JEFE_TALLER
        
        Requisitos:
        - La OT debe estar en EN_QA
        
        Proceso:
        1. Valida permisos y estado
        2. Cambia estado a RETRABAJO
        3. Registra auditoría con motivo
        
        Body JSON:
        {
            "motivo": "Retrabajo por calidad"  // Opcional
        }
        
        Retorna:
        - 200: {"estado": "RETRABAJO", "motivo": "..."}
        - 403: Si no tiene permisos
        - 400: Si el estado no permite retrabajo
        """
        # Solo JEFE_TALLER puede aprobar QA y marcar retrabajo
        if request.user.rol != "JEFE_TALLER":
            return Response(
                {"detail": "Solo JEFE_TALLER puede marcar como retrabajo."},
                status=status.HTTP_403_FORBIDDEN
            )
        ot = self.get_object()
        
        # Validar estado
        if ot.estado != "EN_QA":
            return Response(
                {"detail": "Solo se puede marcar como retrabajo desde EN_QA."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener motivo (opcional)
        motivo = request.data.get("motivo", "Retrabajo por calidad")
        
        # Cambiar estado
        do_transition(ot, "RETRABAJO")
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=request.user,
            accion="RETRABAJO_OT",
            objeto_tipo="OrdenTrabajo",
            objeto_id=str(ot.id),
            payload={"motivo": motivo}
        )
        
        return Response({"estado": ot.estado, "motivo": motivo})


# ============== ITEMS =================
class ItemOTViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Items de OT (repuestos y servicios).
    
    Endpoints:
    - GET /api/v1/work/items/ → Listar items
    - POST /api/v1/work/items/ → Crear item
    - GET /api/v1/work/items/{id}/ → Ver item
    - PUT/PATCH /api/v1/work/items/{id}/ → Editar item
    - DELETE /api/v1/work/items/{id}/ → Eliminar item
    
    Permisos:
    - Usa WorkOrderPermission
    
    Filtros:
    - Por tipo (REPUESTO/SERVICIO)
    - Por OT
    - Búsqueda por descripción
    - Ordenamiento por costo, cantidad
    """
    queryset = ItemOT.objects.select_related("ot")  # Optimización: reduce queries
    serializer_class = ItemOTSerializer
    permission_classes = [WorkOrderPermission]

    # Configuración de filtros
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["tipo", "ot"]  # Filtros por tipo y OT
    search_fields = ["descripcion"]  # Búsqueda por descripción
    ordering_fields = ["costo_unitario", "cantidad"]  # Campos ordenables
    ordering = ["-id"]  # Orden por defecto: más recientes primero


# ============== PRESUPUESTO =================
class PresupuestoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Presupuestos.
    
    Endpoints:
    - GET /api/v1/work/presupuestos/ → Listar presupuestos
    - POST /api/v1/work/presupuestos/ → Crear presupuesto (con detalles)
    - GET /api/v1/work/presupuestos/{id}/ → Ver presupuesto
    - PUT/PATCH /api/v1/work/presupuestos/{id}/ → Editar presupuesto
    - DELETE /api/v1/work/presupuestos/{id}/ → Eliminar presupuesto
    
    Permisos:
    - Usa WorkOrderPermission
    
    Filtros:
    - Por requiere_aprobacion
    - Por OT
    - Ordenamiento por total, fecha
    
    Nota:
    - Al crear, se calcula el total automáticamente
    - Si total > umbral (1000), requiere_aprobacion = True
    """
    queryset = Presupuesto.objects.select_related("ot")
    serializer_class = PresupuestoSerializer
    permission_classes = [WorkOrderPermission]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["requiere_aprobacion", "ot"]
    ordering_fields = ["total", "creado_en"]

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Crea un presupuesto con sus detalles.
        
        Este método se ejecuta al crear un presupuesto.
        Calcula el total sumando todos los detalles y determina
        si requiere aprobación según el umbral.
        
        Body JSON esperado:
        {
            "ot": "uuid-de-ot",
            "detalles_data": [
                {
                    "concepto": "Repuesto X",
                    "cantidad": 2,
                    "precio": 150.00
                },
                ...
            ]
        }
        
        Proceso:
        1. Calcula total sumando cantidad * precio de cada detalle
        2. Determina si requiere aprobación (total > umbral)
        3. Crea el presupuesto
        4. Crea los detalles asociados
        
        Umbral:
        - Por defecto: $1000.00
        - Si total > umbral → requiere_aprobacion = True
        """
        # Obtener detalles del body
        detalles_data = self.request.data.get('detalles_data', [])
        total = Decimal('0')  # Usar Decimal para precisión en dinero
        normalizados = []
        
        # Calcular total y normalizar datos
        for d in detalles_data:
            cantidad = Decimal(str(d.get('cantidad', '0')))
            precio = Decimal(str(d.get('precio', '0')))
            total += cantidad * precio  # Sumar al total
            
            # Normalizar para crear detalles
            normalizados.append({
                "concepto": d.get("concepto", ""),
                "cantidad": int(cantidad),
                "precio": precio
            })

        # Umbral para requerir aprobación
        UMBRAL = Decimal('1000.00')
        
        # Crear presupuesto con total calculado
        presupuesto = serializer.save(
            total=total,
            requiere_aprobacion=(total > UMBRAL),  # Requiere aprobación si supera umbral
            umbral=UMBRAL
        )
        
        # Crear detalles asociados
        for nd in normalizados:
            DetallePresup.objects.create(presupuesto=presupuesto, **nd)


# ============== DETALLES PRESUP =================
class DetallePresupViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Detalles de Presupuesto.
    
    Endpoints:
    - GET /api/v1/work/detalles-presup/ → Listar detalles
    - POST /api/v1/work/detalles-presup/ → Crear detalle
    - GET /api/v1/work/detalles-presup/{id}/ → Ver detalle
    - PUT/PATCH /api/v1/work/detalles-presup/{id}/ → Editar detalle
    - DELETE /api/v1/work/detalles-presup/{id}/ → Eliminar detalle
    
    Permisos:
    - Requiere autenticación
    
    Filtros:
    - Por presupuesto
    - Búsqueda por concepto
    - Ordenamiento por precio, cantidad
    """
    queryset = DetallePresup.objects.select_related("presupuesto").all()
    serializer_class = DetallePresupSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["presupuesto"]
    search_fields = ["concepto"]
    ordering_fields = ["precio", "cantidad", "id"]
    ordering = ["-id"]


# ============== APROBACIONES (SPONSOR) =================
class AprobacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Aprobaciones de Presupuesto por Sponsor.
    
    Endpoints:
    - GET /api/v1/work/aprobaciones/ → Listar aprobaciones
    - POST /api/v1/work/aprobaciones/ → Crear aprobación
    - GET /api/v1/work/aprobaciones/{id}/ → Ver aprobación
    - PUT/PATCH /api/v1/work/aprobaciones/{id}/ → Editar aprobación
    - DELETE /api/v1/work/aprobaciones/{id}/ → Eliminar aprobación
    
    Acciones personalizadas:
    - POST /api/v1/work/aprobaciones/{id}/aprobar/ → Aprobar presupuesto
    - POST /api/v1/work/aprobaciones/{id}/rechazar/ → Rechazar presupuesto
    
    Permisos:
    - Usa WorkOrderPermission
    - Solo SPONSOR/ADMIN pueden aprobar/rechazar
    
    Filtros:
    - Por estado (PENDIENTE/APROBADO/RECHAZADO)
    - Por sponsor
    - Por presupuesto
    - Ordenamiento por fecha
    """
    queryset = Aprobacion.objects.select_related("presupuesto", "sponsor")
    serializer_class = AprobacionSerializer
    permission_classes = [WorkOrderPermission]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["estado", "sponsor", "presupuesto"]
    ordering_fields = ["fecha"]

    @extend_schema(request=EmptySerializer, responses={200: None})
    @action(detail=True, methods=['post'], url_path='aprobar')
    @transaction.atomic
    def aprobar(self, request, pk=None):
        """
        Aprueba un presupuesto.
        
        Endpoint: POST /api/v1/work/aprobaciones/{id}/aprobar/
        
        Permisos:
        - Solo SPONSOR o ADMIN
        
        Proceso:
        1. Valida permisos
        2. Cambia estado a APROBADO
        3. Registra auditoría
        
        Retorna:
        - 200: {"estado": "APROBADO"}
        - 403: Si no tiene permisos
        """
        if request.user.rol not in ("SPONSOR", "ADMIN"):
            return Response(
                {"detail": "Solo SPONSOR/ADMIN pueden aprobar."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        ap = self.get_object()
        ap.estado = "APROBADO"
        ap.save(update_fields=["estado"])
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=request.user,
            accion="APROBAR_PRESUPUESTO",
            objeto_tipo="Aprobacion",
            objeto_id=str(ap.id),
            payload={"presupuesto": str(ap.presupuesto_id)}
        )
        return Response({"estado": ap.estado})

    @extend_schema(request=EmptySerializer, responses={200: None})
    @action(detail=True, methods=['post'], url_path='rechazar')
    @transaction.atomic
    def rechazar(self, request, pk=None):
        """
        Rechaza un presupuesto.
        
        Endpoint: POST /api/v1/work/aprobaciones/{id}/rechazar/
        
        Permisos:
        - Solo SPONSOR o ADMIN
        
        Proceso:
        1. Valida permisos
        2. Cambia estado a RECHAZADO
        3. Registra auditoría
        
        Retorna:
        - 200: {"estado": "RECHAZADO"}
        - 403: Si no tiene permisos
        """
        if request.user.rol not in ("SPONSOR", "ADMIN"):
            return Response(
                {"detail": "Solo SPONSOR/ADMIN pueden rechazar."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        ap = self.get_object()
        ap.estado = "RECHAZADO"
        ap.save(update_fields=["estado"])
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=request.user,
            accion="RECHAZAR_PRESUPUESTO",
            objeto_tipo="Aprobacion",
            objeto_id=str(ap.id),
            payload={"presupuesto": str(ap.presupuesto_id)}
        )
        return Response({"estado": ap.estado})


# ============== PAUSAS =================
class PausaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Pausas durante la ejecución de OT.
    
    Endpoints:
    - GET /api/v1/work/pausas/ → Listar pausas
    - POST /api/v1/work/pausas/ → Crear pausa
    - GET /api/v1/work/pausas/{id}/ → Ver pausa
    - PUT/PATCH /api/v1/work/pausas/{id}/ → Editar pausa
    - DELETE /api/v1/work/pausas/{id}/ → Eliminar pausa
    
    Acciones personalizadas:
    - POST /api/v1/work/pausas/{id}/reanudar/ → Reanudar pausa
    
    Características especiales:
    - Detección automática de colación (12:30-13:15)
    - Cambio automático de estado de OT a EN_PAUSA al crear
    - Cambio automático de estado de OT a EN_EJECUCION al reanudar
    
    Permisos:
    - Usa WorkOrderPermission
    
    Filtros:
    - Por OT
    - Por usuario
    - Ordenamiento por inicio, fin
    """
    queryset = Pausa.objects.select_related("ot", "usuario")
    serializer_class = PausaSerializer
    permission_classes = [WorkOrderPermission]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["ot", "usuario"]
    ordering_fields = ["inicio", "fin"]

    @extend_schema(request=EmptySerializer, responses={200: None})
    @action(detail=True, methods=['post'], url_path='reanudar')
    @transaction.atomic
    def reanudar(self, request, pk=None):
        """
        Reanuda una pausa activa.
        
        Endpoint: POST /api/v1/work/pausas/{id}/reanudar/
        
        Permisos:
        - MECANICO, SUPERVISOR, ADMIN, JEFE_TALLER
        
        Proceso:
        1. Valida que la pausa esté activa (fin es None)
        2. Establece fecha de fin
        3. Si la OT está en EN_PAUSA, cambia a EN_EJECUCION
        4. Registra auditoría
        
        Retorna:
        - 200: {"pausa": {...}, "ot_estado": "EN_EJECUCION"}
        - 403: Si no tiene permisos
        - 400: Si la pausa ya fue reanudada
        """
        if request.user.rol not in ("MECANICO", "SUPERVISOR", "ADMIN", "JEFE_TALLER"):
            return Response(
                {"detail": "No autorizado para reanudar pausas."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        pausa = self.get_object()
        
        # Validar que la pausa esté activa
        if pausa.fin is not None:
            return Response(
                {"detail": "Esta pausa ya fue reanudada."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Establecer fecha de fin
        pausa.fin = timezone.now()
        pausa.save(update_fields=["fin"])
        
        # Cambiar estado de OT a EN_EJECUCION si estaba en EN_PAUSA
        ot = pausa.ot
        if ot.estado == "EN_PAUSA":
            do_transition(ot, "EN_EJECUCION")
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=request.user,
            accion="REANUDAR_PAUSA",
            objeto_tipo="Pausa",
            objeto_id=str(pausa.id),
            payload={"ot_id": str(ot.id)}
        )
        
        return Response({
            "pausa": PausaSerializer(pausa).data,
            "ot_estado": ot.estado
        })

    def perform_create(self, serializer):
        """
        Crea una pausa y cambia el estado de la OT automáticamente.
        
        Este método se ejecuta al crear una pausa.
        
        Características:
        - Detecta automáticamente si es horario de colación (12:30-13:15)
        - Si es colación y no se especifica tipo, asigna tipo COLACION automáticamente
        - Cambia el estado de la OT a EN_PAUSA si está en EN_EJECUCION
        - Registra auditoría
        
        Body JSON esperado:
        {
            "ot": "uuid-de-ot",
            "tipo": "COLACION",  // Opcional, se detecta automáticamente
            "motivo": "Pausa para colación"
        }
        """
        # Detectar si es colación automática (12:30-13:15)
        ahora = timezone.now()
        hora_actual = ahora.hour * 60 + ahora.minute  # Convertir a minutos
        hora_colacion_inicio = 12 * 60 + 30  # 12:30 = 750 minutos
        hora_colacion_fin = 13 * 60 + 15     # 13:15 = 795 minutos
        
        es_colacion = hora_actual >= hora_colacion_inicio and hora_actual <= hora_colacion_fin
        
        # Si no se especifica tipo y es horario de colación, asignar automáticamente
        tipo_pausa = serializer.validated_data.get("tipo", "OTRO")
        if es_colacion and tipo_pausa == "OTRO":
            tipo_pausa = "COLACION"
            serializer.validated_data["tipo"] = "COLACION"
            serializer.validated_data["es_automatica"] = True
        
        # Crear pausa (asignar usuario automáticamente)
        pausa = serializer.save(usuario=self.request.user)
        ot = pausa.ot
        
        # Solo cambiar a EN_PAUSA si está en EN_EJECUCION
        if ot.estado == "EN_EJECUCION":
            do_transition(ot, "EN_PAUSA")
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=self.request.user,
            accion="CREAR_PAUSA",
            objeto_tipo="Pausa",
            objeto_id=str(pausa.id),
            payload={
                "ot_id": str(ot.id),
                "motivo": pausa.motivo,
                "tipo": pausa.tipo,
                "es_automatica": pausa.es_automatica
            }
        )


# ============== CHECKLIST =================
class ChecklistViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Checklists de Calidad (QA).
    
    Endpoints:
    - GET /api/v1/work/checklists/ → Listar checklists
    - POST /api/v1/work/checklists/ → Crear checklist
    - GET /api/v1/work/checklists/{id}/ → Ver checklist
    - PUT/PATCH /api/v1/work/checklists/{id}/ → Editar checklist
    - DELETE /api/v1/work/checklists/{id}/ → Eliminar checklist
    
    Acciones personalizadas:
    - POST /api/v1/work/checklists/{id}/aprobar-qa/ → Aprobar QA y cerrar OT
    - POST /api/v1/work/checklists/{id}/rechazar-qa/ → Rechazar QA y devolver a EN_EJECUCION
    
    Permisos:
    - Usa WorkOrderPermission
    - Solo SUPERVISOR/ADMIN/JEFE_TALLER pueden aprobar/rechazar QA
    
    Filtros:
    - Por resultado (OK/NO_OK)
    - Por OT
    - Búsqueda por observaciones
    - Ordenamiento por fecha
    """
    queryset = Checklist.objects.select_related("ot", "verificador")
    serializer_class = ChecklistSerializer
    permission_classes = [WorkOrderPermission]

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["resultado", "ot"]
    ordering_fields = ["fecha"]
    search_fields = ["observaciones"]
    
    def perform_create(self, serializer):
        """
        Crea un checklist y asigna el verificador automáticamente.
        
        Este método se ejecuta al crear un checklist.
        Asigna el usuario actual como verificador.
        
        Body JSON esperado:
        {
            "ot": "uuid-de-ot",
            "resultado": "OK",  // o "NO_OK"
            "observaciones": "Checklist completado"
        }
        """
        # Crear checklist (asignar verificador automáticamente)
        checklist = serializer.save(verificador=self.request.user)
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=self.request.user,
            accion="CREAR_CHECKLIST_QA",
            objeto_tipo="Checklist",
            objeto_id=str(checklist.id),
            payload={"ot_id": str(checklist.ot.id), "resultado": checklist.resultado}
        )
    
    @extend_schema(request=EmptySerializer, responses={200: None})
    @action(detail=True, methods=['post'], url_path='aprobar-qa')
    @transaction.atomic
    def aprobar_qa(self, request, pk=None):
        """
        Aprueba QA y cierra la OT.
        
        Endpoint: POST /api/v1/work/checklists/{id}/aprobar-qa/
        
        Permisos:
        - Solo SUPERVISOR, ADMIN o JEFE_TALLER
        
        Requisitos:
        - La OT debe estar en EN_QA
        
        Proceso:
        1. Valida permisos y estado
        2. Actualiza checklist a resultado OK (si no lo está)
        3. Cierra la OT (cambia a CERRADA)
        4. Registra auditoría
        
        Retorna:
        - 200: {"checklist": {...}, "ot_estado": "CERRADA", "mensaje": "..."}
        - 403: Si no tiene permisos
        - 400: Si el estado no permite aprobar QA
        """
        if request.user.rol not in ("SUPERVISOR", "ADMIN", "JEFE_TALLER"):
            return Response(
                {"detail": "Solo SUPERVISOR/ADMIN/JEFE_TALLER pueden aprobar QA."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        checklist = self.get_object()
        ot = checklist.ot
        
        # Validar estado
        if ot.estado != "EN_QA":
            return Response(
                {"detail": f"La OT no está en estado EN_QA. Estado actual: {ot.estado}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar checklist si no tiene resultado OK
        if checklist.resultado != "OK":
            checklist.resultado = "OK"
            checklist.observaciones = request.data.get("observaciones", checklist.observaciones)
            checklist.save()
        
        # Cerrar la OT
        do_transition(ot, "CERRADA")
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=request.user,
            accion="APROBAR_QA",
            objeto_tipo="Checklist",
            objeto_id=str(checklist.id),
            payload={"ot_id": str(ot.id)}
        )
        
        # Crear notificaciones (la OT fue cerrada y aprobada)
        try:
            from apps.notifications.utils import crear_notificacion_ot_cerrada, crear_notificacion_ot_aprobada
            crear_notificacion_ot_cerrada(ot, request.user)
            crear_notificacion_ot_aprobada(ot, request.user)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al crear notificaciones para OT aprobada {ot.id}: {e}")
        
        return Response({
            "checklist": ChecklistSerializer(checklist).data,
            "ot_estado": ot.estado,
            "mensaje": "QA aprobada y OT cerrada"
        })
    
    @extend_schema(request=EmptySerializer, responses={200: None})
    @action(detail=True, methods=['post'], url_path='rechazar-qa')
    @transaction.atomic
    def rechazar_qa(self, request, pk=None):
        """
        Rechaza QA y devuelve la OT a EN_EJECUCION para corrección.
        
        Endpoint: POST /api/v1/work/checklists/{id}/rechazar-qa/
        
        Permisos:
        - Solo SUPERVISOR, ADMIN o JEFE_TALLER
        
        Requisitos:
        - La OT debe estar en EN_QA
        
        Proceso:
        1. Valida permisos y estado
        2. Actualiza checklist a resultado NO_OK
        3. Agrega observaciones (si se proporcionan)
        4. Devuelve OT a EN_EJECUCION
        5. Registra auditoría
        
        Body JSON:
        {
            "observaciones": "Motivo del rechazo"  // Opcional
        }
        
        Retorna:
        - 200: {"checklist": {...}, "ot_estado": "EN_EJECUCION", "mensaje": "..."}
        - 403: Si no tiene permisos
        - 400: Si el estado no permite rechazar QA
        """
        if request.user.rol not in ("SUPERVISOR", "ADMIN", "JEFE_TALLER"):
            return Response(
                {"detail": "Solo SUPERVISOR/ADMIN/JEFE_TALLER pueden rechazar QA."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        checklist = self.get_object()
        ot = checklist.ot
        
        # Validar estado
        if ot.estado != "EN_QA":
            return Response(
                {"detail": f"La OT no está en estado EN_QA. Estado actual: {ot.estado}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar checklist con resultado NO_OK y observaciones
        checklist.resultado = "NO_OK"
        checklist.observaciones = request.data.get("observaciones", checklist.observaciones)
        if not checklist.observaciones:
            checklist.observaciones = "QA rechazada - requiere corrección"
        checklist.save()
        
        # Devolver OT a EN_EJECUCION
        do_transition(ot, "EN_EJECUCION")
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=request.user,
            accion="RECHAZAR_QA",
            objeto_tipo="Checklist",
            objeto_id=str(checklist.id),
            payload={
                "ot_id": str(ot.id),
                "observaciones": checklist.observaciones
            }
        )
        
        # Crear notificaciones
        try:
            from apps.notifications.utils import crear_notificacion_ot_rechazada
            crear_notificacion_ot_rechazada(ot, request.user)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al crear notificaciones para OT rechazada {ot.id}: {e}")
        
        return Response({
            "checklist": ChecklistSerializer(checklist).data,
            "ot_estado": ot.estado,
            "mensaje": "QA rechazada. OT devuelta a EN_EJECUCION para corrección"
        })


# ============== EVIDENCIAS (incluye presigned S3) =================
class EvidenciaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Evidencias (fotos/documentos).
    
    Endpoints:
    - GET /api/v1/work/evidencias/ → Listar evidencias
    - POST /api/v1/work/evidencias/ → Crear evidencia (después de subir a S3)
    - GET /api/v1/work/evidencias/{id}/ → Ver evidencia
    - PUT/PATCH /api/v1/work/evidencias/{id}/ → Editar evidencia
    - DELETE /api/v1/work/evidencias/{id}/ → Eliminar evidencia
    
    Acciones personalizadas:
    - POST /api/v1/work/evidencias/presigned/ → Obtener URL presigned para subir archivo
    
    Permisos:
    - Usa WorkOrderPermission
    - Solo MECANICO, SUPERVISOR, ADMIN, GUARDIA pueden subir evidencias
    
    Filtros:
    - Por tipo (FOTO/PDF/OTRO)
    - Por OT
    - Ordenamiento por fecha de subida
    
    Flujo de subida:
    1. Frontend llama a /presigned/ para obtener URL
    2. Frontend sube archivo directamente a S3 usando URL presigned
    3. Frontend llama a POST /evidencias/ con la URL del archivo
    """
    queryset = Evidencia.objects.select_related("ot", "ot__vehiculo", "subido_por")
    serializer_class = EvidenciaSerializer
    permission_classes = [WorkOrderPermission]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["tipo", "ot"]
    ordering_fields = ["subido_en"]
    
    def get_queryset(self):
        """
        Filtra el queryset según el rol del usuario.
        
        - JEFE_TALLER: todas las evidencias de su Site
        - SUPERVISOR: solo evidencias de su Site
        - ADMIN: todas las evidencias
        - MECANICO: evidencias que él subió o de la OT en la que trabaja
        - GUARDIA: evidencias que él subió
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user or not user.is_authenticated:
            return queryset.none()
        
        rol = getattr(user, "rol", None)
        
        # Jefe de Taller: todas las evidencias de su Site
        if rol == "JEFE_TALLER":
            user_site = getattr(user, 'profile', None)
            if user_site and hasattr(user_site, 'site') and user_site.site:
                return queryset.filter(ot__vehiculo__site=user_site.site)
            # Si no tiene site configurado, mostrar todas (fallback)
            return queryset
        
        # Supervisor Zonal: solo evidencias de su Site
        if rol == "SUPERVISOR":
            user_site = getattr(user, 'profile', None)
            if user_site and hasattr(user_site, 'site') and user_site.site:
                return queryset.filter(ot__vehiculo__site=user_site.site)
            return queryset.none()
        
        # Administrador: todas las evidencias
        if rol == "ADMIN":
            return queryset
        
        # Mecánico: evidencias que él subió o de la OT en la que trabaja
        if rol == "MECANICO":
            # Evidencias que él subió
            queryset_user = queryset.filter(subido_por=user)
            # Evidencias de OTs asignadas a él
            queryset_ot = queryset.filter(ot__mecanico=user)
            # Combinar ambos querysets
            return queryset_user.union(queryset_ot)
        
        # Guardia: solo evidencias que él subió
        if rol == "GUARDIA":
            return queryset.filter(subido_por=user)
        
        # Otros roles: sin acceso
        return queryset.none()
    
    def create(self, request, *args, **kwargs):
        """
        Crea una nueva evidencia y envía notificaciones a usuarios relevantes.
        
        Sobrescribe el método create del ModelViewSet para agregar
        lógica de notificaciones cuando se sube una evidencia importante.
        También asigna automáticamente el usuario que sube la evidencia.
        """
        # Asignar automáticamente el usuario que sube la evidencia
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Asignar subido_por antes de guardar
        evidencia = serializer.save(subido_por=request.user)
        
        # Crear notificaciones para usuarios relevantes
        try:
            from apps.notifications.utils import crear_notificacion_evidencia
            crear_notificacion_evidencia(evidencia, request.user)
        except Exception as e:
            # Si falla la creación de notificaciones, no fallar la creación de evidencia
            # Solo registrar el error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al crear notificaciones para evidencia {evidencia.id}: {e}")
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(request=EmptySerializer, responses={200: None})
    @action(detail=False, methods=['post'], url_path='presigned')
    def presigned(self, request):
        """
        Genera una URL presigned para subir un archivo a S3.
        
        Endpoint: POST /api/v1/work/evidencias/presigned/
        
        Permisos:
        - Solo MECANICO, SUPERVISOR, ADMIN, GUARDIA
        
        Body JSON:
        {
            "ot": "uuid-de-ot",
            "filename": "foto.jpg",
            "content_type": "image/jpeg",  // Opcional, se detecta automáticamente
            "file_size": 1024000  // Tamaño en bytes
        }
        
        Validaciones:
        - Tamaño máximo: 10MB
        - Tipos permitidos: Imágenes, PDFs (validado por middleware)
        
        Retorna:
        - 200: {
            "upload": {
                "url": "https://s3...",
                "fields": {...}
            },
            "file_url": "https://s3.../evidencias/ot-id/uuid-filename"
          }
        - 403: Si no tiene permisos
        - 400: Si el archivo no es válido
        - 500: Si falta configuración de S3
        
        Uso:
        1. Frontend obtiene URL presigned
        2. Frontend sube archivo directamente a S3 usando la URL
        3. Frontend crea registro de Evidencia con la URL del archivo
        """
        # Verificar permisos
        if request.user.rol not in ("MECANICO", "SUPERVISOR", "ADMIN", "GUARDIA", "JEFE_TALLER"):
            return Response(
                {"detail": "No autorizado para subir evidencias."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Obtener configuración de S3
        bucket = os.getenv("AWS_STORAGE_BUCKET_NAME")
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        if not bucket:
            return Response(
                {"detail": "Falta configurar AWS_STORAGE_BUCKET_NAME."}, 
                status=500
            )

        # Obtener datos del archivo
        ot_id = request.data.get("ot")
        filename = request.data.get("filename", f"evidencia-{uuid.uuid4()}.bin")
        content_type = request.data.get("content_type") or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        file_size = request.data.get("file_size", 0)  # Tamaño en bytes

        # Validar archivo
        from .middleware import validate_file_upload
        
        # Crear objeto file simulado para validación
        class FileMock:
            def __init__(self, name, content_type, size):
                self.name = name
                self.content_type = content_type
                self.size = size
        
        file_mock = FileMock(filename, content_type, file_size)
        # Límite aumentado a 3GB (3072 MB) para soportar archivos grandes
        validation = validate_file_upload(file_mock, max_size_mb=3072)
        
        if not validation['valid']:
            return Response(
                {"detail": "; ".join(validation['errors'])},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generar key único para el archivo
        # Si no hay OT, usar carpeta "generales"
        if ot_id:
            key = f"evidencias/{ot_id}/{uuid.uuid4()}-{filename}"
        else:
            key = f"evidencias/generales/{uuid.uuid4()}-{filename}"

        # Determinar si usar LocalStack (desarrollo) o AWS real (producción)
        # Detectar automáticamente si estamos usando LocalStack
        endpoint_url_internal = os.getenv("AWS_ENDPOINT_URL") or os.getenv("AWS_S3_ENDPOINT_URL")
        use_local = endpoint_url_internal is not None and ("localstack" in endpoint_url_internal.lower() or "localhost:4566" in endpoint_url_internal.lower())
        
        # Para LocalStack, necesitamos dos URLs:
        # - endpoint_url_internal: Para que el backend se comunique con LocalStack (puede ser localstack:4566)
        # - endpoint_url_public: Para que el navegador se comunique con LocalStack (debe ser localhost:4566)
        endpoint_url_public = os.getenv("AWS_PUBLIC_URL_PREFIX", "http://localhost:4566") if use_local else None

        # Crear cliente S3 con endpoint interno (para comunicación backend -> LocalStack)
        s3 = boto3.client(
            "s3",
            region_name=region,
            endpoint_url=endpoint_url_internal,  # LocalStack interno en desarrollo
            config=Config(
                s3={
                    "addressing_style": "path",
                    "multipart_threshold": 64 * 1024 * 1024,  # 64MB - usar multipart para archivos grandes
                    "multipart_chunksize": 64 * 1024 * 1024,  # 64MB por chunk
                    "max_bandwidth": None,  # Sin límite de ancho de banda
                }
            )
        )

        # Límite aumentado a 3GB (3072 MB) para soportar archivos grandes
        max_size = 3072 * 1024 * 1024
        
        # Generar URL presigned para POST (subida directa)
        presigned = s3.generate_presigned_post(
            Bucket=bucket,
            Key=key,
            Fields={"Content-Type": content_type},
            Conditions=[
                {"Content-Type": content_type},
                ["content-length-range", 0, max_size]  # Validar tamaño
            ],
            ExpiresIn=60 * 60  # Expira en 1 hora (archivos grandes pueden tardar más en subir)
        )

        # Si estamos usando LocalStack, reemplazar la URL interna por la pública en la respuesta
        # para que el navegador pueda acceder
        if use_local and endpoint_url_public and presigned.get("url"):
            # Reemplazar la URL interna por la pública
            original_url = presigned["url"]
            new_url = original_url
            
            # Método 1: Reemplazar endpoint interno completo
            if endpoint_url_internal and endpoint_url_internal in original_url:
                new_url = original_url.replace(endpoint_url_internal, endpoint_url_public)
            
            # Método 2: Reemplazar hostname localstack por localhost
            elif "localstack" in original_url.lower():
                # Reemplazar cualquier variación de localstack por localhost
                new_url = re.sub(
                    r'http://localstack(?::\d+)?',
                    endpoint_url_public,
                    original_url,
                    flags=re.IGNORECASE
                )
                # Si el reemplazo no funcionó, hacer reemplazo simple
                if new_url == original_url:
                    new_url = original_url.replace("localstack:4566", "localhost:4566")
                    new_url = new_url.replace("localstack", "localhost")
            
            # Método 3: Usar urlparse para reemplazo más preciso
            if new_url == original_url and "http://" in original_url:
                parsed = urlparse(original_url)
                # Si el hostname contiene localstack, reemplazarlo
                if "localstack" in parsed.netloc.lower():
                    new_netloc = parsed.netloc.replace("localstack", "localhost")
                    new_parsed = parsed._replace(netloc=new_netloc)
                    new_url = urlunparse(new_parsed)
            
            presigned["url"] = new_url
            
            # Log para debugging (solo en desarrollo)
            if os.getenv("DEBUG", "False") == "True":
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"URL presigned reemplazada: {original_url} -> {new_url}")

        # Construir URL final del archivo
        if use_local:
            # LocalStack: usar URL pública para que el navegador pueda acceder
            if not endpoint_url_public:
                # Fallback si no está configurado
                endpoint_url_public = "http://localhost:4566"
            file_url = f"{endpoint_url_public.rstrip('/')}/{bucket}/{key}"
        else:
            # AWS real: https://bucket.s3.region.amazonaws.com/key
            file_url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

        # Validar que file_url es una URL válida
        try:
            from urllib.parse import urlparse
            parsed = urlparse(file_url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("URL inválida generada")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al generar file_url: {e}, file_url={file_url}, use_local={use_local}, endpoint_url_public={endpoint_url_public}")
            return Response(
                {"detail": f"Error al generar URL del archivo: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({"upload": presigned, "file_url": file_url})


# ============== COMENTARIOS EN OT =================
class ComentarioOTViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de comentarios en OT.
    
    Endpoints:
    - GET /api/v1/work/comentarios/ → Listar comentarios
    - POST /api/v1/work/comentarios/ → Crear comentario
    - GET /api/v1/work/comentarios/{id}/ → Ver comentario
    - PUT/PATCH /api/v1/work/comentarios/{id}/ → Editar comentario
    - DELETE /api/v1/work/comentarios/{id}/ → Eliminar comentario
    """
    queryset = ComentarioOT.objects.select_related("usuario", "ot").all().order_by("creado_en")
    serializer_class = ComentarioOTSerializer
    permission_classes = [WorkOrderPermission]
    
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["ot", "usuario"]
    ordering_fields = ["creado_en"]
    
    def perform_create(self, serializer):
        """Asignar usuario automáticamente al crear comentario."""
        serializer.save(usuario=self.request.user)
        
        # Notificar a usuarios mencionados
        comentario = serializer.instance
        menciones = comentario.menciones or []
        
        if menciones:
            try:
                from apps.notifications.utils import crear_notificacion_ot_comentario
                crear_notificacion_ot_comentario(comentario, menciones)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error al crear notificaciones de comentario {comentario.id}: {e}")
    
    def perform_update(self, serializer):
        """Marcar comentario como editado."""
        serializer.save(editado=True, editado_en=timezone.now())


# ============== TIMELINE DE OT =================
@extend_schema(
    description="Obtiene el timeline consolidado de una OT",
    responses={200: None}
)
@api_view(['GET'])
@permission_classes([WorkOrderPermission])
def timeline_ot(request, ot_id):
    """
    Endpoint para obtener el timeline consolidado de una OT.
    
    Retorna:
    - Cambios de estado (de Auditoria)
    - Comentarios
    - Evidencias
    - Pausas
    - Checklists
    - Actores (usuarios involucrados)
    
    Endpoint: GET /api/v1/work/ordenes/{ot_id}/timeline/
    """
    try:
        ot = OrdenTrabajo.objects.get(id=ot_id)
    except OrdenTrabajo.DoesNotExist:
        return Response(
            {"detail": "OT no encontrada."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Obtener cambios de estado desde Auditoria
    cambios_estado = Auditoria.objects.filter(
        objeto_tipo="OrdenTrabajo",
        objeto_id=str(ot_id),
        accion__in=["CAMBIO_ESTADO", "TRANSICION_ESTADO"]
    ).order_by("ts")
    
    # Obtener comentarios
    comentarios = ComentarioOT.objects.filter(ot=ot).order_by("creado_en")
    
    # Obtener evidencias
    evidencias = Evidencia.objects.filter(ot=ot).order_by("subido_en")
    
    # Obtener pausas
    pausas = Pausa.objects.filter(ot=ot).order_by("inicio")
    
    # Obtener checklists
    checklists = Checklist.objects.filter(ot=ot).order_by("fecha")
    
    # Construir timeline
    timeline = []
    
    # Agregar creación de OT
    timeline.append({
        "tipo": "creacion",
        "fecha": ot.apertura,
        "usuario": None,
        "accion": "OT creada",
        "detalle": {
            "estado": ot.estado,
            "motivo": ot.motivo
        }
    })
    
    # Agregar cambios de estado
    for cambio in cambios_estado:
        timeline.append({
            "tipo": "cambio_estado",
            "fecha": cambio.ts,
            "usuario": {
                "id": str(cambio.usuario.id) if cambio.usuario else None,
                "nombre": cambio.usuario.get_full_name() if cambio.usuario else "Sistema",
                "rol": cambio.usuario.rol if cambio.usuario else None
            },
            "accion": cambio.accion,
            "detalle": cambio.payload
        })
    
    # Agregar comentarios
    for comentario in comentarios:
        timeline.append({
            "tipo": "comentario",
            "fecha": comentario.creado_en,
            "usuario": {
                "id": str(comentario.usuario.id) if comentario.usuario else None,
                "nombre": comentario.usuario.get_full_name() if comentario.usuario else "Sistema",
                "rol": comentario.usuario.rol if comentario.usuario else None
            },
            "accion": "Comentario agregado",
            "detalle": {
                "contenido": comentario.contenido,
                "menciones": comentario.menciones,
                "editado": comentario.editado
            }
        })
    
    # Agregar evidencias
    for evidencia in evidencias:
        timeline.append({
            "tipo": "evidencia",
            "fecha": evidencia.subido_en,
            "usuario": None,  # Evidencia no tiene usuario directo
            "accion": "Evidencia subida",
            "detalle": {
                "tipo": evidencia.tipo,
                "descripcion": evidencia.descripcion,
                "url": evidencia.url,
                "invalidado": evidencia.invalidado
            }
        })
    
    # Agregar pausas
    for pausa in pausas:
        timeline.append({
            "tipo": "pausa",
            "fecha": pausa.inicio,
            "usuario": {
                "id": str(pausa.usuario.id) if pausa.usuario else None,
                "nombre": pausa.usuario.get_full_name() if pausa.usuario else "Sistema",
                "rol": pausa.usuario.rol if pausa.usuario else None
            },
            "accion": f"Pausa: {pausa.tipo}",
            "detalle": {
                "motivo": pausa.motivo,
                "duracion_minutos": pausa.duracion_minutos,
                "es_automatica": pausa.es_automatica
            }
        })
    
    # Agregar checklists
    for checklist in checklists:
        timeline.append({
            "tipo": "checklist",
            "fecha": checklist.fecha,
            "usuario": {
                "id": str(checklist.verificador.id) if checklist.verificador else None,
                "nombre": checklist.verificador.get_full_name() if checklist.verificador else "Sistema",
                "rol": checklist.verificador.rol if checklist.verificador else None
            },
            "accion": f"Checklist: {checklist.resultado}",
            "detalle": {
                "resultado": checklist.resultado,
                "observaciones": checklist.observaciones
            }
        })
    
    # Ordenar por fecha
    timeline.sort(key=lambda x: x["fecha"])
    
    # Obtener actores (usuarios involucrados)
    actores = set()
    if ot.supervisor:
        actores.add((str(ot.supervisor.id), ot.supervisor.get_full_name(), ot.supervisor.rol))
    if ot.jefe_taller:
        actores.add((str(ot.jefe_taller.id), ot.jefe_taller.get_full_name(), ot.jefe_taller.rol))
    if ot.mecanico:
        actores.add((str(ot.mecanico.id), ot.mecanico.get_full_name(), ot.mecanico.rol))
    
    return Response({
        "ot_id": str(ot.id),
        "timeline": timeline,
        "actores": [
            {"id": a[0], "nombre": a[1], "rol": a[2]} for a in actores
        ]
    })


# ============== INVALIDAR EVIDENCIA =================
@extend_schema(
    description="Invalida una evidencia y crea una versión en el historial",
    request=EmptySerializer,
    responses={200: None}
)
@api_view(['POST'])
@permission_classes([WorkOrderPermission])
@transaction.atomic
def invalidar_evidencia(request, evidencia_id):
    """
    Invalida una evidencia y crea un registro en el historial de versiones.
    
    Solo roles permitidos pueden invalidar evidencias:
    - JEFE_TALLER
    - ADMIN
    - SUPERVISOR
    
    Endpoint: POST /api/v1/work/evidencias/{evidencia_id}/invalidar/
    """
    # Verificar permisos
    if request.user.rol not in ["JEFE_TALLER", "ADMIN", "SUPERVISOR"]:
        return Response(
            {"detail": "No tiene permisos para invalidar evidencias."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        evidencia = Evidencia.objects.get(id=evidencia_id)
    except Evidencia.DoesNotExist:
        return Response(
            {"detail": "Evidencia no encontrada."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Validar que no esté ya invalidada
    if evidencia.invalidado:
        return Response(
            {"detail": "La evidencia ya está invalidada."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Obtener motivo de invalidación
    motivo = request.data.get("motivo", "")
    if not motivo:
        return Response(
            {"detail": "El motivo de invalidación es obligatorio."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Guardar URL anterior antes de invalidar
    url_anterior = evidencia.url
    
    # Invalidar evidencia
    evidencia.invalidado = True
    evidencia.invalidado_por = request.user
    evidencia.invalidado_en = timezone.now()
    evidencia.motivo_invalidacion = motivo
    evidencia.save()
    
    # Crear versión en el historial
    VersionEvidencia.objects.create(
        evidencia_original=evidencia,
        url_anterior=url_anterior,
        invalidado_por=request.user,
        motivo=motivo
    )
    
    # Registrar auditoría
    Auditoria.objects.create(
        usuario=request.user,
        accion="INVALIDAR_EVIDENCIA",
        objeto_tipo="Evidencia",
        objeto_id=str(evidencia.id),
        payload={
            "ot_id": str(evidencia.ot.id) if evidencia.ot else None,
            "motivo": motivo
        }
    )
    
    return Response({
        "detail": "Evidencia invalidada correctamente.",
        "evidencia": EvidenciaSerializer(evidencia).data
    })
