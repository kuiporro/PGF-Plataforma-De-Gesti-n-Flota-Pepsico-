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
    @action(detail=True, methods=['post'], url_path='cerrar')
    def cerrar(self, request, pk=None):
        if request.user.rol not in ("SUPERVISOR", "ADMIN"):
            return Response({"detail": "Solo SUPERVISOR/ADMIN pueden cerrar la OT."},
                            status=status.HTTP_403_FORBIDDEN)
        ot = self.get_object()
        ok, err = transition(ot, "CERRADA")
        if not ok:
            return Response({"detail": err}, status=status.HTTP_400_BAD_REQUEST)

        from .tasks import generar_pdf_cierre
        generar_pdf_cierre.delay(str(ot.id), request.user.id)

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
    queryset = Pausa.objects.select_related("ot", "usuario")
    serializer_class = PausaSerializer
    permission_classes = [WorkOrderPermission]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["ot", "usuario"]
    ordering_fields = ["inicio", "fin"]


# ============== CHECKLIST =================
class ChecklistViewSet(viewsets.ModelViewSet):
    queryset = Checklist.objects.select_related("ot", "verificador")
    serializer_class = ChecklistSerializer
    permission_classes = [WorkOrderPermission]

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["resultado", "ot"]
    ordering_fields = ["fecha"]
    search_fields = ["observaciones"]


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
        if request.user.rol not in ("MECANICO", "SUPERVISOR", "ADMIN"):
            return Response({"detail": "No autorizado para subir evidencias."}, status=status.HTTP_403_FORBIDDEN)

        bucket = os.getenv("AWS_STORAGE_BUCKET_NAME")
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        if not bucket:
            return Response({"detail": "Falta configurar AWS_STORAGE_BUCKET_NAME."}, status=500)

        ot_id = request.data.get("ot")
        filename = request.data.get("filename", f"evidencia-{uuid.uuid4()}.bin")
        content_type = request.data.get("content_type") or mimetypes.guess_type(filename)[0] or "application/octet-stream"

        key = f"evidencias/{ot_id}/{uuid.uuid4()}-{filename}"

        use_local = os.getenv("USE_LOCALSTACK_S3", "0") == "1"
        endpoint_url = os.getenv("AWS_ENDPOINT_URL") if use_local else None

        s3 = boto3.client(
            "s3",
            region_name=region,
            endpoint_url=endpoint_url,
            config=Config(s3={"addressing_style": "path"})
        )

        presigned = s3.generate_presigned_post(
            Bucket=bucket,
            Key=key,
            Fields={"Content-Type": content_type},
            Conditions=[
                {"Content-Type": content_type},
                ["content-length-range", 0, 20 * 1024 * 1024]
            ],
            ExpiresIn=60 * 5
        )

        if use_local:
            file_url = f"{os.getenv('AWS_ENDPOINT_URL','http://localhost:4566')}/{bucket}/{key}"
        else:
            file_url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

        return Response({"upload": presigned, "file_url": file_url})


