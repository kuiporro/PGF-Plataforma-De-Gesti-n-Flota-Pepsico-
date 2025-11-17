# apps/vehicles/models.py
"""
Modelos para gestión de vehículos.

Este módulo define:
- Vehiculo: Modelo principal de vehículo
- IngresoVehiculo: Registro de ingreso al taller
- EvidenciaIngreso: Evidencias fotográficas del ingreso

Relaciones:
- Vehiculo -> OrdenTrabajo (OneToMany, related_name="ordenes")
- Vehiculo -> IngresoVehiculo (OneToMany, related_name="ingresos")
- IngresoVehiculo -> EvidenciaIngreso (OneToMany, related_name="evidencias")
- Vehiculo -> Chofer (OneToMany, related_name="choferes" en apps/drivers/models.py)

Estados del vehículo:
- ACTIVO: En operación normal
- EN_ESPERA: Ingresado al taller, esperando atención
- EN_MANTENIMIENTO: Actualmente en mantenimiento/reparación
- BAJA: Dado de baja del sistema
"""

from django.db import models
from django.conf import settings  # Para acceder a AUTH_USER_MODEL
import uuid  # Para generar IDs únicos


class Vehiculo(models.Model):
    """
    Modelo principal que representa un vehículo de la flota.
    
    Almacena toda la información de un vehículo, incluyendo:
    - Identificación (patente, VIN)
    - Características (marca, modelo, año, tipo)
    - Estado operativo
    - Ubicación (zona, sucursal)
    - Métricas (km mensual promedio)
    
    Relaciones:
    - OneToMany con OrdenTrabajo (vehiculo.ordenes.all())
    - OneToMany con IngresoVehiculo (vehiculo.ingresos.all())
    - OneToMany con Chofer (vehiculo.choferes.all() en drivers app)
    
    Validaciones:
    - Patente única (no puede haber dos vehículos con la misma patente)
    - Año entre 1900 y 2100 (CheckConstraint)
    """
    
    # ==================== ESTADOS ====================
    ESTADOS = (
        ("ACTIVO", "ACTIVO"),  # En operación normal
        ("EN_ESPERA", "EN_ESPERA"),  # Ingresado al taller, esperando atención
        ("EN_MANTENIMIENTO", "EN_MANTENIMIENTO"),  # Actualmente en mantenimiento
        ("BAJA", "BAJA"),  # Dado de baja del sistema
    )
    
    # ==================== TIPOS ====================
    TIPOS = (
        ("ELECTRICO", "Eléctrico"),  # Vehículo eléctrico
        ("DIESEL", "Diésel"),  # Vehículo diésel
        ("UTILITARIO", "Utilitario"),  # Vehículo utilitario
        ("REPARTO", "Reparto"),  # Vehículo de reparto
        ("VENTAS", "Ventas"),  # Vehículo de ventas
        ("RESPALDO", "Respaldo"),  # Vehículo de respaldo
    )
    
    # ==================== CATEGORÍAS ====================
    CATEGORIAS = (
        ("REPARTO", "Reparto"),  # Categoría de reparto
        ("VENTAS", "Ventas"),  # Categoría de ventas
        ("RESPALDO", "Respaldo"),  # Categoría de respaldo
    )

    # ==================== CAMPOS PRINCIPALES ====================
    
    # ID único: UUID4
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    
    # Patente: identificador único del vehículo
    # unique=True: no puede haber dos vehículos con la misma patente
    # db_index=True: índice para búsquedas rápidas
    patente = models.CharField(max_length=32, unique=True, db_index=True)
    
    # Tipo de vehículo: clasificación técnica
    tipo = models.CharField(
        max_length=20, 
        choices=TIPOS, 
        blank=True, 
        help_text="Tipo de vehículo (eléctrico/diésel/utilitario)"
    )
    
    # Categoría operativa: clasificación funcional
    categoria = models.CharField(
        max_length=20, 
        choices=CATEGORIAS, 
        blank=True, 
        help_text="Categoría operativa"
    )
    
    # Información del vehículo
    marca = models.CharField(max_length=64, blank=True)  # Ej: "Toyota", "Ford"
    modelo = models.CharField(max_length=64, blank=True)  # Ej: "Hilux", "Ranger"
    anio = models.PositiveIntegerField(null=True, blank=True)  # Año de fabricación
    
    # VIN: Número de identificación del vehículo (Vehicle Identification Number)
    vin = models.CharField(max_length=64, blank=True)
    
    # Estado operativo del vehículo
    estado = models.CharField(max_length=32, choices=ESTADOS, default="ACTIVO")
    
    # ==================== UBICACIÓN Y MÉTRICAS ====================
    
    # Zona: zona geográfica o sucursal asignada
    zona = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Zona o sucursal asignada"
    )
    
    # Sucursal: sucursal específica
    sucursal = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Sucursal específica"
    )
    
    # Kilometraje promedio mensual
    # Se usa para planificación de mantenimientos preventivos
    km_mensual_promedio = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Kilometraje promedio mensual"
    )

    # ==================== TIMESTAMPS ====================
    
    # Fecha de creación en el sistema
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Fecha de última actualización
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Configuración del modelo.
        
        - indexes: índices para optimizar búsquedas frecuentes
        - constraints: validaciones a nivel de base de datos
        """
        indexes = [
            models.Index(fields=["estado"]),  # Filtros por estado (muy frecuente)
            models.Index(fields=["marca", "modelo"]),  # Búsquedas por marca/modelo
        ]
        constraints = [
            # Validar que el año esté en un rango razonable
            models.CheckConstraint(
                name="vehiculo_anio_valid",
                check=(
                    models.Q(anio__isnull=True) |  # Puede ser null
                    (models.Q(anio__gte=1900) & models.Q(anio__lte=2100))  # O entre 1900 y 2100
                ),
            ),
        ]

    def __str__(self):
        """
        Representación en string del vehículo.
        
        Retorna la patente, que es el identificador principal.
        """
        return self.patente


class IngresoVehiculo(models.Model):
    """
    Registro de ingreso de un vehículo al taller.
    
    Se crea cuando un Guardia o Recepcionista registra el ingreso
    de un vehículo al taller. Esto puede generar automáticamente
    una Orden de Trabajo si hay una Agenda programada.
    
    Relaciones:
    - ForeignKey a Vehiculo (vehiculo.ingresos.all())
    - ForeignKey a User (guardia que registra el ingreso)
    - OneToMany con EvidenciaIngreso (ingreso.evidencias.all())
    
    Uso:
    - Registrado desde apps/vehicles/views.py en acción 'ingreso'
    - Puede vincularse con Agenda para crear OT automáticamente
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Vehículo que ingresa
    vehiculo = models.ForeignKey(
        Vehiculo, 
        on_delete=models.PROTECT,  # No permitir eliminar vehículo con ingresos
        related_name="ingresos"
    )
    
    # Guardia o Recepcionista que registra el ingreso
    guardia = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        related_name="ingresos_registrados"
    )
    
    # Fecha/hora de ingreso (automática al crear)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    
    # Observaciones del ingreso
    observaciones = models.TextField(blank=True)
    
    # Kilometraje al momento del ingreso
    kilometraje = models.PositiveIntegerField(null=True, blank=True)
    
    # Código QR opcional para escaneo
    qr_code = models.CharField(max_length=255, blank=True)
    
    class Meta:
        """
        Configuración del modelo.
        
        - indexes: índices para búsquedas frecuentes
        - ordering: orden por defecto (más recientes primero)
        """
        indexes = [
            models.Index(fields=["fecha_ingreso"]),  # Filtros por fecha
            models.Index(fields=["vehiculo", "fecha_ingreso"]),  # Búsquedas por vehículo y fecha
        ]
        ordering = ["-fecha_ingreso"]  # Más recientes primero
    
    def __str__(self):
        """
        Representación en string del ingreso.
        
        Formato: "Ingreso {patente} - {fecha}"
        """
        return f"Ingreso {self.vehiculo.patente} - {self.fecha_ingreso}"


class EvidenciaIngreso(models.Model):
    """
    Evidencias fotográficas del ingreso de un vehículo.
    
    Se almacenan fotos y documentos relacionados con el ingreso,
    como fotos del estado del vehículo, daños, documentos, etc.
    
    Las evidencias se almacenan en S3 (AWS o LocalStack) y se
    referencia mediante URL.
    
    Relaciones:
    - ForeignKey a IngresoVehiculo (ingreso.evidencias.all())
    
    Tipos:
    - FOTO_INGRESO: Foto general del ingreso
    - FOTO_DANOS: Foto de daños detectados
    - FOTO_DOCUMENTOS: Foto de documentos
    - OTRO: Otro tipo de evidencia
    """
    
    class TipoEvidencia(models.TextChoices):
        """
        Tipos de evidencias de ingreso.
        """
        FOTO_INGRESO = "FOTO_INGRESO", "Foto de Ingreso"  # Foto general
        FOTO_DANOS = "FOTO_DANOS", "Foto de Daños"  # Foto de daños
        FOTO_DOCUMENTOS = "FOTO_DOCUMENTOS", "Foto de Documentos"  # Foto de documentos
        OTRO = "OTRO", "Otro"  # Otro tipo
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Ingreso al que pertenece la evidencia
    ingreso = models.ForeignKey(
        IngresoVehiculo, 
        on_delete=models.CASCADE,  # Si se elimina el ingreso, se eliminan las evidencias
        related_name="evidencias"
    )
    
    # URL de la evidencia en S3
    # Se genera mediante presigned URL
    url = models.URLField()
    
    # Tipo de evidencia
    tipo = models.CharField(
        max_length=20, 
        choices=TipoEvidencia.choices, 
        default=TipoEvidencia.FOTO_INGRESO
    )
    
    # Descripción opcional
    descripcion = models.TextField(blank=True)
    
    # Fecha de subida
    subido_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """
        Configuración del modelo.
        
        - indexes: índices para búsquedas frecuentes
        """
        indexes = [
            models.Index(fields=["ingreso", "tipo"]),  # Filtros por ingreso y tipo
        ]
    
    def __str__(self):
        """
        Representación en string de la evidencia.
        
        Formato: "Evidencia {tipo} - {patente}"
        """
        return f"Evidencia {self.tipo} - {self.ingreso.vehiculo.patente}"
