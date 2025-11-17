# apps/workorders/views.py
import os
import uuid
import mimetypes
from decimal import Decimal

import boto3
from botocore.config import Config

from django.db import transaction

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.views import APIView  # ✅ IMPORT CRÍTICO PARA PingView

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from drf_spectacular.utils import extend_schema


from apps.core.serializers import EmptySerializer
from .filters import OrdenTrabajoFilter
from .permissions import WorkOrderPermission
from .services import transition, do_transition
from .serializers import OrdenTrabajoListSerializer

from .models import (
    OrdenTrabajo, ItemOT, Presupuesto, DetallePresup,
    Aprobacion, Pausa, Checklist, Evidencia, Auditoria
)
from .serializers import (
    OrdenTrabajoSerializer, ItemOTSerializer,
    PresupuestoSerializer, DetallePresupSerializer,
    AprobacionSerializer, PausaSerializer,
    ChecklistSerializer, EvidenciaSerializer

)


class PingView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmptySerializer
    http_method_names = ["post"]  # explícito y claro

    @extend_schema(
        request=EmptySerializer,
        responses={200: None},
        description="Ping de salud autenticado"
    )
    def post(self, request, *args, **kwargs):
        return Response({"ok": True})

# ============== ORDENES DE TRABAJO =================
class OrdenTrabajoViewSet(viewsets.ModelViewSet):
    queryset = OrdenTrabajo.objects.select_related("vehiculo", "responsable").all().order_by("-apertura")
    serializer_class = OrdenTrabajoSerializer

    # filtros
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["id", "apertura", "cierre", "estado"]  
    search_fields = ["vehiculo__patente"]

    def perform_destroy(self, instance):
        """Eliminar OT sin intentar eliminar relaciones de inventory que pueden no existir"""
        try:
            # Intentar eliminar solicitudes de repuestos relacionadas
            from apps.inventory.models import SolicitudRepuesto
            SolicitudRepuesto.objects.filter(ot=instance).delete()
        except Exception:
            # Si la tabla no existe o hay error, continuar
            pass
        
        try:
            # Intentar eliminar movimientos de stock relacionados
            from apps.inventory.models import MovimientoStock
            MovimientoStock.objects.filter(ot=instance).update(ot=None)
        except Exception:
            # Si la tabla no existe o hay error, continuar
            pass
        
        # Eliminar la OT
        instance.delete() 

    @extend_schema(request=EmptySerializer, responses={200: None})
    @action(detail=True, methods=['post'], url_path='en-ejecucion')
    def en_ejecucion(self, request, pk=None):
        if request.user.rol not in ("SUPERVISOR", "ADMIN", "MECANICO"):
            return Response({"detail": "Solo SUPERVISOR/ADMIN/MECANICO pueden iniciar la ejecución."},
                            status=status.HTTP_403_FORBIDDEN)
        ot = self.get_object()
        do_transition(ot, "EN_EJECUCION")
        return Response({"estado": ot.estado})

    @extend_schema(request=EmptySerializer, responses={200: None})
    @action(detail=True, methods=['post'], url_path='en-qa')
    def en_qa(self, request, pk=None):
        if request.user.rol not in ("SUPERVISOR", "ADMIN"):
            return Response({"detail": "Solo SUPERVISOR/ADMIN pueden mover a QA."},
                            status=status.HTTP_403_FORBIDDEN)
        ot = self.get_object()
        do_transition(ot, "EN_QA")
        return Response({"estado": ot.estado})

    @extend_schema(request=EmptySerializer, responses={200: None})
    @action(detail=True, methods=['post'], url_path='en-pausa')
    @transaction.atomic
    def en_pausa(self, request, pk=None):
        """Transición directa a EN_PAUSA (alternativa a crear pausa)"""
        if request.user.rol not in ("MECANICO", "SUPERVISOR", "ADMIN", "JEFE_TALLER"):
            return Response({"detail": "No autorizado para pausar OT."},
                            status=status.HTTP_403_FORBIDDEN)
        ot = self.get_object()
        do_transition(ot, "EN_PAUSA")
        return Response({"estado": ot.estado})

    @extend_schema(request=EmptySerializer, responses={200: None})
    @action(detail=True, methods=['post'], url_path='cerrar')
    @transaction.atomic
    def cerrar(self, request, pk=None):
        """Cierra la OT directamente (solo si está en EN_QA o CERRADA)"""
        if request.user.rol not in ("SUPERVISOR", "ADMIN", "JEFE_TALLER"):
            return Response({"detail": "Solo SUPERVISOR/ADMIN/JEFE_TALLER pueden cerrar la OT."},
                            status=status.HTTP_403_FORBIDDEN)
        ot = self.get_object()
        
        if ot.estado not in ("EN_QA", "CERRADA"):
            return Response(
                {"detail": f"No se puede cerrar una OT en estado {ot.estado}. Debe estar en EN_QA."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        do_transition(ot, "CERRADA")
        
        # Generar PDF de cierre automáticamente
        from .tasks import generar_pdf_cierre
        generar_pdf_cierre.delay(str(ot.id), request.user.id)
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=request.user,
            accion="CERRAR_OT",
            objeto_tipo="OrdenTrabajo",
            objeto_id=str(ot.id),
            payload={}
        )
        
        return Response({"estado": ot.estado, "cierre": ot.cierre})

    @extend_schema(request=EmptySerializer, responses={200: None})
    @action(detail=True, methods=['post'], url_path='anular')
    def anular(self, request, pk=None):
        if request.user.rol not in ("SUPERVISOR", "ADMIN"):
            return Response({"detail": "Solo SUPERVISOR/ADMIN pueden anular la OT."},
                            status=status.HTTP_403_FORBIDDEN)
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
        """Jefe de Taller realiza diagnóstico"""
        if request.user.rol not in ("JEFE_TALLER", "ADMIN"):
            return Response(
                {"detail": "Solo JEFE_TALLER puede realizar diagnóstico."},
                status=status.HTTP_403_FORBIDDEN
            )
        ot = self.get_object()
        
        if ot.estado not in ("ABIERTA", "EN_DIAGNOSTICO"):
            return Response(
                {"detail": f"La OT debe estar en ABIERTA o EN_DIAGNOSTICO para realizar diagnóstico."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        diagnostico_texto = request.data.get("diagnostico", "")
        if not diagnostico_texto:
            return Response(
                {"detail": "El diagnóstico es requerido."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ot.diagnostico = diagnostico_texto
        ot.jefe_taller = request.user
        ot.fecha_diagnostico = timezone.now()
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
        """Supervisor aprueba asignación de mecánico"""
        if request.user.rol not in ("SUPERVISOR", "ADMIN", "COORDINADOR_ZONA"):
            return Response(
                {"detail": "Solo SUPERVISOR/COORDINADOR puede aprobar asignación."},
                status=status.HTTP_403_FORBIDDEN
            )
        ot = self.get_object()
        
        if ot.estado != "EN_DIAGNOSTICO":
            return Response(
                {"detail": "La OT debe estar en EN_DIAGNOSTICO para aprobar asignación."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        mecanico_id = request.data.get("mecanico_id")
        if not mecanico_id:
            return Response(
                {"detail": "Se requiere mecanico_id."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.users.models import User
        try:
            mecanico = User.objects.get(id=mecanico_id, rol="MECANICO")
        except User.DoesNotExist:
            return Response(
                {"detail": "Mecánico no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        ot.mecanico = mecanico
        ot.supervisor = request.user
        ot.fecha_aprobacion_supervisor = timezone.now()
        ot.fecha_asignacion_mecanico = timezone.now()
        
        # Ajustar prioridad si se proporciona
        nueva_prioridad = request.data.get("prioridad")
        if nueva_prioridad:
            ot.prioridad = nueva_prioridad
        
        do_transition(ot, "EN_EJECUCION")
        
        # Registrar auditoría
        Auditoria.objects.create(
            usuario=request.user,
            accion="APROBAR_ASIGNACION_OT",
            objeto_tipo="OrdenTrabajo",
            objeto_id=str(ot.id),
            payload={"mecanico_id": str(mecanico.id), "mecanico": mecanico.username}
        )
        
        return Response({
            "estado": ot.estado,
            "mecanico": mecanico.username,
            "supervisor": request.user.username
        })
    
    @action(detail=True, methods=['post'], url_path='retrabajo')
    @transaction.atomic
    def retrabajo(self, request, pk=None):
        """Marca OT como retrabajo (desde QA)"""
        if request.user.rol not in ("SUPERVISOR", "ADMIN", "JEFE_TALLER"):
            return Response(
                {"detail": "Solo SUPERVISOR/JEFE_TALLER puede marcar como retrabajo."},
                status=status.HTTP_403_FORBIDDEN
            )
        ot = self.get_object()
        
        if ot.estado != "EN_QA":
            return Response(
                {"detail": "Solo se puede marcar como retrabajo desde EN_QA."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        motivo = request.data.get("motivo", "Retrabajo por calidad")
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
    queryset = ItemOT.objects.select_related("ot")
    serializer_class = ItemOTSerializer
    permission_classes = [WorkOrderPermission]

    # solo campos que EXISTEN en ItemOT
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["tipo", "ot"]
    search_fields = ["descripcion"]
    ordering_fields = ["costo_unitario", "cantidad"]
    ordering = ["-id"]


# ============== PRESUPUESTO =================
class PresupuestoViewSet(viewsets.ModelViewSet):
    queryset = Presupuesto.objects.select_related("ot")
    serializer_class = PresupuestoSerializer
    permission_classes = [WorkOrderPermission]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["requiere_aprobacion", "ot"]
    ordering_fields = ["total", "creado_en"]

    @transaction.atomic
    def perform_create(self, serializer):
        detalles_data = self.request.data.get('detalles_data', [])
        total = Decimal('0')
        normalizados = []
        for d in detalles_data:
            cantidad = Decimal(str(d.get('cantidad', '0')))
            precio = Decimal(str(d.get('precio', '0')))
            total += cantidad * precio
            normalizados.append({
                "concepto": d.get("concepto", ""),
                "cantidad": int(cantidad),
                "precio": precio
            })

        UMBRAL = Decimal('1000.00')
        presupuesto = serializer.save(
            total=total,
            requiere_aprobacion=(total > UMBRAL),
            umbral=UMBRAL
        )
        for nd in normalizados:
            DetallePresup.objects.create(presupuesto=presupuesto, **nd)


# ============== DETALLES PRESUP =================
class DetallePresupViewSet(viewsets.ModelViewSet):
    queryset = DetallePresup.objects.select_related("presupuesto").all()
    serializer_class = DetallePresupSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["presupuesto"]
    search_fields = ["concepto"]        # <- existe en el modelo
    ordering_fields = ["precio", "cantidad", "id"]
    ordering = ["-id"]


# ============== APROBACIONES (SPONSOR) =================
class AprobacionViewSet(viewsets.ModelViewSet):
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
        if request.user.rol not in ("SPONSOR", "ADMIN"):
            return Response({"detail": "Solo SPONSOR/ADMIN pueden aprobar."}, status=status.HTTP_403_FORBIDDEN)
        ap = self.get_object()
        ap.estado = "APROBADO"   # <- coincide con choices
        ap.save(update_fields=["estado"])
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
        if request.user.rol not in ("SPONSOR", "ADMIN"):
            return Response({"detail": "Solo SPONSOR/ADMIN pueden rechazar."}, status=status.HTTP_403_FORBIDDEN)
        ap = self.get_object()
        ap.estado = "RECHAZADO"  # <- coincide con choices
        ap.save(update_fields=["estado"])
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
    """ViewSet para gestión de pausas, incluyendo colación automática"""
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
        """Reanuda una pausa y cambia el estado de la OT a EN_EJECUCION"""
        if request.user.rol not in ("MECANICO", "SUPERVISOR", "ADMIN", "JEFE_TALLER"):
            return Response({"detail": "No autorizado para reanudar pausas."},
                            status=status.HTTP_403_FORBIDDEN)
        
        pausa = self.get_object()
        
        if pausa.fin is not None:
            return Response({"detail": "Esta pausa ya fue reanudada."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        from django.utils import timezone
        pausa.fin = timezone.now()
        pausa.save(update_fields=["fin"])
        
        # Cambiar estado de OT a EN_EJECUCION si estaba en EN_PAUSA
        ot = pausa.ot
        if ot.estado == "EN_PAUSA":
            do_transition(ot, "EN_EJECUCION")
        
        # Registrar auditoría
        from .models import Auditoria
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
        """Al crear una pausa, cambia el estado de la OT a EN_PAUSA si está en EN_EJECUCION"""
        # Detectar si es colación automática (12:30-13:15)
        ahora = timezone.now()
        hora_actual = ahora.hour * 60 + ahora.minute
        hora_colacion_inicio = 12 * 60 + 30  # 12:30
        hora_colacion_fin = 13 * 60 + 15     # 13:15
        
        es_colacion = hora_actual >= hora_colacion_inicio and hora_actual <= hora_colacion_fin
        
        # Si no se especifica tipo y es horario de colación, asignar automáticamente
        tipo_pausa = serializer.validated_data.get("tipo", "OTRO")
        if es_colacion and tipo_pausa == "OTRO":
            tipo_pausa = "COLACION"
            serializer.validated_data["tipo"] = "COLACION"
            serializer.validated_data["es_automatica"] = True
        
        pausa = serializer.save(usuario=self.request.user)
        ot = pausa.ot
        
        # Solo cambiar a EN_PAUSA si está en EN_EJECUCION
        if ot.estado == "EN_EJECUCION":
            do_transition(ot, "EN_PAUSA")
        
        # Registrar auditoría
        from .models import Auditoria
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
    queryset = Checklist.objects.select_related("ot", "verificador")
    serializer_class = ChecklistSerializer
    permission_classes = [WorkOrderPermission]

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["resultado", "ot"]
    ordering_fields = ["fecha"]
    search_fields = ["observaciones"]
    
    def perform_create(self, serializer):
        """Al crear checklist, se asigna el verificador automáticamente"""
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
        """Aprueba QA y cierra la OT"""
        if request.user.rol not in ("SUPERVISOR", "ADMIN", "JEFE_TALLER"):
            return Response(
                {"detail": "Solo SUPERVISOR/ADMIN/JEFE_TALLER pueden aprobar QA."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        checklist = self.get_object()
        ot = checklist.ot
        
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
        
        return Response({
            "checklist": ChecklistSerializer(checklist).data,
            "ot_estado": ot.estado,
            "mensaje": "QA aprobada y OT cerrada"
        })
    
    @extend_schema(request=EmptySerializer, responses={200: None})
    @action(detail=True, methods=['post'], url_path='rechazar-qa')
    @transaction.atomic
    def rechazar_qa(self, request, pk=None):
        """Rechaza QA y devuelve la OT a EN_EJECUCION para corrección"""
        if request.user.rol not in ("SUPERVISOR", "ADMIN", "JEFE_TALLER"):
            return Response(
                {"detail": "Solo SUPERVISOR/ADMIN/JEFE_TALLER pueden rechazar QA."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        checklist = self.get_object()
        ot = checklist.ot
        
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
        
        return Response({
            "checklist": ChecklistSerializer(checklist).data,
            "ot_estado": ot.estado,
            "mensaje": "QA rechazada. OT devuelta a EN_EJECUCION para corrección"
        })


# ============== EVIDENCIAS (incluye presigned S3) =================
class EvidenciaViewSet(viewsets.ModelViewSet):
    queryset = Evidencia.objects.select_related("ot")
    serializer_class = EvidenciaSerializer
    permission_classes = [WorkOrderPermission]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["tipo", "ot"]
    ordering_fields = ["subido_en"]

    @extend_schema(request=EmptySerializer, responses={200: None})
    @action(detail=False, methods=['post'], url_path='presigned')
    def presigned(self, request):
        if request.user.rol not in ("MECANICO", "SUPERVISOR", "ADMIN", "GUARDIA"):
            return Response({"detail": "No autorizado para subir evidencias."}, status=status.HTTP_403_FORBIDDEN)

        bucket = os.getenv("AWS_STORAGE_BUCKET_NAME")
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        if not bucket:
            return Response({"detail": "Falta configurar AWS_STORAGE_BUCKET_NAME."}, status=500)

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
        validation = validate_file_upload(file_mock, max_size_mb=10)
        
        if not validation['valid']:
            return Response(
                {"detail": "; ".join(validation['errors'])},
                status=status.HTTP_400_BAD_REQUEST
            )

        key = f"evidencias/{ot_id}/{uuid.uuid4()}-{filename}"

        use_local = os.getenv("USE_LOCALSTACK_S3", "0") == "1"
        endpoint_url = os.getenv("AWS_ENDPOINT_URL") if use_local else None

        s3 = boto3.client(
            "s3",
            region_name=region,
            endpoint_url=endpoint_url,
            config=Config(s3={"addressing_style": "path"})
        )

        # Límite de 10MB
        max_size = 10 * 1024 * 1024
        presigned = s3.generate_presigned_post(
            Bucket=bucket,
            Key=key,
            Fields={"Content-Type": content_type},
            Conditions=[
                {"Content-Type": content_type},
                ["content-length-range", 0, max_size]
            ],
            ExpiresIn=60 * 5
        )

        if use_local:
            file_url = f"{os.getenv('AWS_ENDPOINT_URL','http://localhost:4566')}/{bucket}/{key}"
        else:
            file_url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

        return Response({"upload": presigned, "file_url": file_url})


