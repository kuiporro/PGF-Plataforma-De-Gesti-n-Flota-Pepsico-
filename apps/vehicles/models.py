# apps/vehicles/models.py
from django.db import models
from django.conf import settings
import uuid

class Vehiculo(models.Model):
    ESTADOS = (
        ("ACTIVO","ACTIVO"),
        ("EN_MANTENIMIENTO","EN_MANTENIMIENTO"),
        ("BAJA","BAJA"),
    )

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    patente = models.CharField(max_length=32, unique=True, db_index=True)
    marca = models.CharField(max_length=64, blank=True)
    modelo = models.CharField(max_length=64, blank=True)
    anio = models.PositiveIntegerField(null=True, blank=True)
    vin = models.CharField(max_length=64, blank=True)
    estado = models.CharField(max_length=32, choices=ESTADOS, default="ACTIVO")

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
