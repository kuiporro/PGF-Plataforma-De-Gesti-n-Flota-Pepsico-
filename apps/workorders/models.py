#apps/workorders/models.py
from django.db import models
from django.conf import settings
from apps.vehicles.models import Vehiculo
import uuid

class OrdenTrabajo(models.Model):
    ESTADOS = (
        ("ABIERTA","ABIERTA"),
        ("EN_DIAGNOSTICO","EN_DIAGNOSTICO"),  # Nuevo estado para diagnóstico
        ("EN_EJECUCION","EN_EJECUCION"),
        ("EN_PAUSA","EN_PAUSA"),
        ("EN_QA","EN_QA"),
        ("RETRABAJO","RETRABAJO"),  # Nuevo estado para retrabajo
        ("CERRADA","CERRADA"),
        ("ANULADA","ANULADA")
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT, related_name="ordenes")
    
    # Asignaciones
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ots_supervisadas",
        limit_choices_to={"rol__in": ["SUPERVISOR", "COORDINADOR_ZONA"]},
        help_text="Supervisor asignado"
    )
    jefe_taller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ots_jefe_taller",
        limit_choices_to={"rol": "JEFE_TALLER"},
        help_text="Jefe de Taller que valida"
    )
    mecanico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ots_asignadas",
        limit_choices_to={"rol": "MECANICO"},
        help_text="Mecánico asignado para ejecución"
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ots_responsable",
        help_text="Responsable general (puede ser supervisor o mecánico)"
    )
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default="ABIERTA")
    tipo = models.CharField(
        max_length=50,
        blank=True,
        default="MANTENCION",
        choices=[
            ("MANTENCION", "Mantención"),
            ("REPARACION", "Reparación"),
            ("EMERGENCIA", "Emergencia"),
            ("DIAGNOSTICO", "Diagnóstico"),
            ("OTRO", "Otro"),
        ]
    )
    prioridad = models.CharField(
        max_length=20,
        blank=True,
        default="MEDIA",
        choices=[
            ("CRITICA", "Crítica"),
            ("ALTA", "Alta"),
            ("MEDIA", "Media"),
            ("BAJA", "Baja"),
        ]
    )
    motivo = models.TextField(blank=True)
    diagnostico = models.TextField(blank=True, help_text="Diagnóstico realizado por Jefe de Taller")
    zona = models.CharField(max_length=100, blank=True, help_text="Zona o sucursal")
    
    # Fechas
    apertura = models.DateTimeField(auto_now_add=True)
    fecha_diagnostico = models.DateTimeField(null=True, blank=True)
    fecha_aprobacion_supervisor = models.DateTimeField(null=True, blank=True)
    fecha_asignacion_mecanico = models.DateTimeField(null=True, blank=True)
    fecha_inicio_ejecucion = models.DateTimeField(null=True, blank=True)
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
    TIPOS = (
        ("ESPERA_REPUESTO", "Espera de Repuesto"),
        ("APROBACION_PENDIENTE", "Aprobación Pendiente"),
        ("COLACION", "Colación (12:30-13:15)"),
        ("OTRO", "Otro Motivo Operativo"),
        ("ADMINISTRATIVA", "Pausa Administrativa"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ot = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name="pausas")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="pausas")
    tipo = models.CharField(max_length=30, choices=TIPOS, default="OTRO", help_text="Tipo de pausa")
    motivo = models.CharField(max_length=255, help_text="Motivo detallado de la pausa")
    es_automatica = models.BooleanField(default=False, help_text="Indica si es una pausa automática (ej: colación)")
    inicio = models.DateTimeField(auto_now_add=True)
    fin = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["ot", "inicio"]),
            models.Index(fields=["tipo", "inicio"]),
            models.Index(fields=["es_automatica"]),
        ]
        ordering = ["-inicio"]
    
    @property
    def duracion_minutos(self):
        """Calcula la duración en minutos si la pausa está cerrada"""
        if self.fin and self.inicio:
            delta = self.fin - self.inicio
            return int(delta.total_seconds() / 60)
        return None

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