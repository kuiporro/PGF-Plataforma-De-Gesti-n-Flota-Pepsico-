#apps/workorders/models.py
from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from apps.vehicles.models import Vehiculo
import uuid

class OrdenTrabajo(models.Model):
    ESTADOS = (("ABIERTA","ABIERTA"),("EN_EJECUCION","EN_EJECUCION"),
               ("EN_QA","EN_QA"),("CERRADA","CERRADA"),("ANULADA","ANULADA"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT, related_name="ordenes")
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name="ots_responsable")
    estado = models.CharField(max_length=20, choices=ESTADOS, default="ABIERTA")
    motivo = models.TextField(blank=True)
    apertura = models.DateTimeField(auto_now_add=True)
    cierre = models.DateTimeField(null=True, blank=True)
    class Meta:
        indexes = [
            models.Index(fields=["estado"]),
            models.Index(fields=["apertura"])
        ]


class ItemOT(models.Model):
    class TipoItem(models.TextChoices):
        REPUESTO = "REPUESTO", "REPUESTO"
        SERVICIO = "SERVICIO", "SERVICIO"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ot = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name="items")
    tipo = models.CharField(max_length=20, choices=TipoItem.choices)
    descripcion = models.TextField()
    cantidad = models.PositiveIntegerField()
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(cantidad__gt=0), name="itemot_cantidad_gt_0"),
            models.CheckConstraint(check=models.Q(costo_unitario__gte=0), name="itemot_costo_gte_0"),
        ]
        indexes = [models.Index(fields=["ot"]), models.Index(fields=["tipo"])]

class Presupuesto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ot = models.OneToOneField(OrdenTrabajo, on_delete=models.CASCADE, related_name="presupuesto")
    total = models.DecimalField(max_digits=14, decimal_places=2)
    requiere_aprobacion = models.BooleanField(default=False)
    umbral = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

class DetallePresup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE, related_name="detalles")
    concepto = models.CharField(max_length=255)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=12, decimal_places=2)

class Aprobacion(models.Model):
    ESTADOS = (("PENDIENTE","PENDIENTE"),("APROBADO","APROBADO"),("RECHAZADO","RECHAZADO"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    presupuesto = models.OneToOneField(Presupuesto, on_delete=models.CASCADE, related_name="aprobacion")
    sponsor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="aprobaciones")
    estado = models.CharField(max_length=20, choices=ESTADOS, default="PENDIENTE")
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

class Pausa(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ot = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name="pausas")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="pausas")
    motivo = models.CharField(max_length=255)
    inicio = models.DateTimeField(auto_now_add=True)
    fin = models.DateTimeField(null=True, blank=True)

class Checklist(models.Model):
    RESULTADOS = (("OK","OK"),("NO_OK","NO_OK"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ot = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name="checklists")
    verificador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="checklists_realizados")
    resultado = models.CharField(max_length=10, choices=RESULTADOS)
    observaciones = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

class Evidencia(models.Model):
    class TipoEvidencia(models.TextChoices):
        FOTO = "FOTO", "FOTO"
        PDF  = "PDF", "PDF"
        OTRO = "OTRO", "OTRO"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ot = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name="evidencias")
    url = models.URLField()
    tipo = models.CharField(max_length=10, choices=TipoEvidencia.choices, default="FOTO")
    descripcion = models.TextField(blank=True, default="")
    subido_en = models.DateTimeField(auto_now_add=True)

class Auditoria(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    accion = models.CharField(max_length=64)  # ej: APROBAR_PRESUPUESTO, RECHAZAR_PRESUPUESTO, GENERAR_PDF_CIERRE
    objeto_tipo = models.CharField(max_length=64)  # ej: 'Aprobacion', 'OrdenTrabajo'
    objeto_id = models.CharField(max_length=64)
    payload = models.JSONField(default=dict, blank=True)
    ts = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["objeto_tipo", "objeto_id"]),
            models.Index(fields=["accion"]),
            models.Index(fields=["ts"]),
        ]

    def __str__(self):
        return f"{self.ts} {self.accion} {self.objeto_tipo}:{self.objeto_id}"