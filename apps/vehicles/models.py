# apps/vehicles/models.py
from django.db import models
from django.conf import settings
import uuid

class Vehiculo(models.Model):
    ESTADOS = (
        ("ACTIVO","ACTIVO"),
        ("EN_ESPERA","EN_ESPERA"),  # Vehículo ingresado al taller, esperando atención
        ("EN_MANTENIMIENTO","EN_MANTENIMIENTO"),
        ("BAJA","BAJA"),
    )
    
    TIPOS = (
        ("ELECTRICO", "Eléctrico"),
        ("DIESEL", "Diésel"),
        ("UTILITARIO", "Utilitario"),
        ("REPARTO", "Reparto"),
        ("VENTAS", "Ventas"),
        ("RESPALDO", "Respaldo"),
    )
    
    CATEGORIAS = (
        ("REPARTO", "Reparto"),
        ("VENTAS", "Ventas"),
        ("RESPALDO", "Respaldo"),
    )

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    patente = models.CharField(max_length=32, unique=True, db_index=True)
    tipo = models.CharField(max_length=20, choices=TIPOS, blank=True, help_text="Tipo de vehículo (eléctrico/diésel/utilitario)")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, blank=True, help_text="Categoría operativa")
    marca = models.CharField(max_length=64, blank=True)
    modelo = models.CharField(max_length=64, blank=True)
    anio = models.PositiveIntegerField(null=True, blank=True)
    vin = models.CharField(max_length=64, blank=True)
    estado = models.CharField(max_length=32, choices=ESTADOS, default="ACTIVO")
    zona = models.CharField(max_length=100, blank=True, help_text="Zona o sucursal asignada")
    sucursal = models.CharField(max_length=100, blank=True, help_text="Sucursal específica")
    km_mensual_promedio = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Kilometraje promedio mensual"
    )

    # (Opcional) Dueño/creador del vehículo, si quieres mostrar "vehiculos" en UserSerializer
    # owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
    #                           on_delete=models.SET_NULL, related_name="vehiculos")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["estado"]),
            models.Index(fields=["marca", "modelo"]),
        ]
        constraints = [
            models.CheckConstraint(
                name="vehiculo_anio_valid",
                check=(
                    models.Q(anio__isnull=True) |
                    (models.Q(anio__gte=1900) & models.Q(anio__lte=2100))
                ),
            ),
        ]

    def __str__(self):
        return self.patente


class IngresoVehiculo(models.Model):
    """Registro de ingreso de vehículo al taller por el guardia"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT, related_name="ingresos")
    guardia = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="ingresos_registrados")
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)
    kilometraje = models.PositiveIntegerField(null=True, blank=True)
    qr_code = models.CharField(max_length=255, blank=True)  # Para escaneo QR opcional
    
    class Meta:
        indexes = [
            models.Index(fields=["fecha_ingreso"]),
            models.Index(fields=["vehiculo", "fecha_ingreso"]),
        ]
        ordering = ["-fecha_ingreso"]
    
    def __str__(self):
        return f"Ingreso {self.vehiculo.patente} - {self.fecha_ingreso}"


class EvidenciaIngreso(models.Model):
    """Evidencias fotográficas del ingreso del vehículo"""
    class TipoEvidencia(models.TextChoices):
        FOTO_INGRESO = "FOTO_INGRESO", "Foto de Ingreso"
        FOTO_DANOS = "FOTO_DANOS", "Foto de Daños"
        FOTO_DOCUMENTOS = "FOTO_DOCUMENTOS", "Foto de Documentos"
        OTRO = "OTRO", "Otro"
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ingreso = models.ForeignKey(IngresoVehiculo, on_delete=models.CASCADE, related_name="evidencias")
    url = models.URLField()
    tipo = models.CharField(max_length=20, choices=TipoEvidencia.choices, default=TipoEvidencia.FOTO_INGRESO)
    descripcion = models.TextField(blank=True)
    subido_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["ingreso", "tipo"]),
        ]
    
    def __str__(self):
        return f"Evidencia {self.tipo} - {self.ingreso.vehiculo.patente}"
