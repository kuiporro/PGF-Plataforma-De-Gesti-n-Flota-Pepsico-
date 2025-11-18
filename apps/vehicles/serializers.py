# apps/vehicles/serializers.py
"""
Serializers para el módulo de vehículos.

Este módulo define:
- VehiculoSerializer: Serializer completo para Vehiculo
- VehiculoListSerializer: Serializer simplificado para listados
- IngresoVehiculoSerializer: Serializer para IngresoVehiculo
- EvidenciaIngresoSerializer: Serializer para EvidenciaIngreso
- HistorialVehiculoSerializer: Serializer para HistorialVehiculo
- BackupVehiculoSerializer: Serializer para BackupVehiculo
"""

from rest_framework import serializers
from .models import Vehiculo, IngresoVehiculo, EvidenciaIngreso, HistorialVehiculo, BackupVehiculo
from apps.core.validators import (
    validar_formato_patente,
    validar_ano
)
from apps.workorders.models import OrdenTrabajo


class VehiculoSerializer(serializers.ModelSerializer):
    """
    Serializer completo para el modelo Vehiculo.
    
    Incluye todos los campos del vehículo, incluyendo los nuevos campos
    agregados para reportes (site, supervisor, estado_operativo, etc.)
    
    Validaciones implementadas:
    - Patente única
    - Formato de patente válido
    - Datos obligatorios (patente, marca, modelo, año, tipo_vehiculo, tipo_motor, site, supervisor)
    - Año válido (2000 - año actual)
    - No cambiar Site si tiene OT activa
    """
    supervisor_nombre = serializers.CharField(source="supervisor.get_full_name", read_only=True)
    
    class Meta:
        model = Vehiculo
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
    
    def validate_patente(self, value):
        """
        Valida que la patente tenga formato válido y sea única.
        """
        # Validar formato de patente
        es_valido, patente_limpia = validar_formato_patente(value)
        if not es_valido:
            raise serializers.ValidationError(patente_limpia)  # patente_limpia contiene el mensaje de error
        
        # Validar que la patente no esté registrada (excepto si es el mismo vehículo)
        instance = self.instance
        if instance:
            # Actualización: verificar que no exista otro vehículo con la misma patente
            if Vehiculo.objects.filter(patente=patente_limpia).exclude(pk=instance.pk).exists():
                raise serializers.ValidationError("La patente ya está registrada.")
        else:
            # Creación: verificar que no exista
            if Vehiculo.objects.filter(patente=patente_limpia).exists():
                raise serializers.ValidationError("La patente ya está registrada.")
        
        return patente_limpia
    
    def validate_anio(self, value):
        """
        Valida que el año sea válido (entre 2000 y el año actual).
        """
        if value:
            es_valido, mensaje = validar_ano(value)
            if not es_valido:
                raise serializers.ValidationError(mensaje)
        return value
    
    def validate(self, attrs):
        """
        Validaciones a nivel de objeto completo.
        """
        # Validar campos obligatorios
        campos_obligatorios = {
            'patente': 'patente',
            'marca': 'marca',
            'modelo': 'modelo',
            'anio': 'año',
            'tipo': 'tipo de vehículo',
            'site': 'site',
            'supervisor': 'supervisor'
        }
        
        for campo, nombre_display in campos_obligatorios.items():
            # Si es actualización, usar el valor del atributo o el nuevo valor
            if campo not in attrs:
                if self.instance:
                    # En actualización, si no viene en attrs, usar el valor actual
                    if not getattr(self.instance, campo, None):
                        raise serializers.ValidationError({campo: f"El campo {nombre_display} es obligatorio."})
                else:
                    # En creación, el campo debe estar en attrs
                    raise serializers.ValidationError({campo: f"El campo {nombre_display} es obligatorio."})
        
        # Validar que no se pueda cambiar el Site si tiene OT activa
        instance = self.instance
        if instance and 'site' in attrs:
            nuevo_site = attrs['site']
            site_actual = instance.site
            
            # Si el site está cambiando
            if nuevo_site != site_actual:
                # Verificar si hay OT activa
                ots_activas = OrdenTrabajo.objects.filter(
                    vehiculo=instance,
                    estado__in=['ABIERTA', 'EN_EJECUCION', 'QA']
                ).exists()
                
                if ots_activas:
                    raise serializers.ValidationError({
                        'site': "No se puede mover el vehículo mientras tiene una OT activa."
                    })
        
        return attrs


class VehiculoListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listados de vehículos.
    
    Solo incluye campos esenciales para optimizar rendimiento
    en listados grandes.
    """
    class Meta:
        model = Vehiculo
        fields = [
            "id",
            "patente",
            "marca",
            "modelo",
            "anio",
            "estado",
            "estado_operativo",
            "site",
            "supervisor",
        ]


class IngresoVehiculoSerializer(serializers.ModelSerializer):
    """
    Serializer para IngresoVehiculo.
    
    Validaciones implementadas:
    - Datos mínimos (patente, nombre conductor, RUT conductor, hora ingreso, site)
    - RUT conductor válido
    - No permitir ingreso si el vehículo ya tiene OT activa
    """
    vehiculo_patente = serializers.CharField(source="vehiculo.patente", read_only=True)
    guardia_nombre = serializers.CharField(source="guardia.get_full_name", read_only=True)
    
    class Meta:
        model = IngresoVehiculo
        fields = "__all__"
        read_only_fields = ["id", "fecha_ingreso"]
    
    def validate(self, attrs):
        """
        Validaciones a nivel de objeto completo.
        """
        from apps.core.validators import validar_rut_chileno
        from apps.workorders.models import OrdenTrabajo
        
        # Validar campos obligatorios
        campos_obligatorios = {
            'vehiculo': 'patente',
            'nombre_conductor': 'nombre del conductor',
            'rut_conductor': 'RUT del conductor',
            'fecha_ingreso': 'hora de ingreso',
            'site': 'site'
        }
        
        for campo, nombre_display in campos_obligatorios.items():
            if campo not in attrs:
                if self.instance:
                    if not getattr(self.instance, campo, None):
                        raise serializers.ValidationError({campo: f"El campo {nombre_display} es obligatorio."})
                else:
                    raise serializers.ValidationError({campo: f"El campo {nombre_display} es obligatorio."})
        
        # Validar RUT del conductor
        rut_conductor = attrs.get('rut_conductor') or (getattr(self.instance, 'rut_conductor', None) if self.instance else None)
        if rut_conductor:
            es_valido, rut_formateado = validar_rut_chileno(rut_conductor)
            if not es_valido:
                raise serializers.ValidationError({'rut_conductor': rut_formateado})
            attrs['rut_conductor'] = rut_formateado
        
        # Validar que el vehículo no tenga OT activa (solo en creación)
        if not self.instance:
            vehiculo = attrs.get('vehiculo')
            if vehiculo:
                ots_activas = OrdenTrabajo.objects.filter(
                    vehiculo=vehiculo,
                    estado__in=['ABIERTA', 'EN_EJECUCION', 'QA', 'EN_DIAGNOSTICO', 'EN_PAUSA']
                ).exists()
                
                if ots_activas:
                    raise serializers.ValidationError({
                        'vehiculo': "El vehículo ya se encuentra ingresado en el taller."
                    })
        
        return attrs


class EvidenciaIngresoSerializer(serializers.ModelSerializer):
    """
    Serializer para EvidenciaIngreso.
    """
    class Meta:
        model = EvidenciaIngreso
        fields = "__all__"
        read_only_fields = ["id", "subido_en"]


class HistorialVehiculoSerializer(serializers.ModelSerializer):
    """
    Serializer para HistorialVehiculo.
    """
    vehiculo_patente = serializers.CharField(source="vehiculo.patente", read_only=True)
    ot_numero = serializers.CharField(source="ot.id", read_only=True)
    supervisor_nombre = serializers.CharField(source="supervisor.get_full_name", read_only=True)
    backup_patente = serializers.CharField(source="backup_utilizado.vehiculo_backup.patente", read_only=True, allow_null=True)
    
    class Meta:
        model = HistorialVehiculo
        fields = "__all__"
        read_only_fields = ["id", "creado_en"]


class BackupVehiculoSerializer(serializers.ModelSerializer):
    """
    Serializer para BackupVehiculo.
    
    Validaciones implementadas:
    - Backup operativo (estado_operativo = OPERATIVO)
    - Backup no utilizado por otro vehículo
    - Backup no puede ser el mismo que el vehículo principal
    - Campos obligatorios (vehiculo_principal, vehiculo_backup, fecha_inicio, motivo)
    """
    vehiculo_principal_patente = serializers.CharField(source="vehiculo_principal.patente", read_only=True)
    vehiculo_backup_patente = serializers.CharField(source="vehiculo_backup.patente", read_only=True)
    ot_numero = serializers.CharField(source="ot.id", read_only=True, allow_null=True)
    supervisor_nombre = serializers.CharField(source="supervisor.get_full_name", read_only=True)
    
    def validate(self, attrs):
        """
        Validaciones a nivel de objeto completo.
        """
        # Validar campos obligatorios
        campos_obligatorios = {
            'vehiculo_principal': 'vehículo principal',
            'vehiculo_backup': 'vehículo backup',
            'fecha_inicio': 'fecha de inicio',
            'motivo': 'motivo'
        }
        
        for campo, nombre_display in campos_obligatorios.items():
            if campo not in attrs:
                if self.instance:
                    if not getattr(self.instance, campo, None):
                        raise serializers.ValidationError({campo: f"El campo {nombre_display} es obligatorio."})
                else:
                    raise serializers.ValidationError({campo: f"El campo {nombre_display} es obligatorio."})
        
        # Validar que el backup no sea el mismo que el vehículo principal
        vehiculo_principal = attrs.get('vehiculo_principal') or (self.instance.vehiculo_principal if self.instance else None)
        vehiculo_backup = attrs.get('vehiculo_backup') or (self.instance.vehiculo_backup if self.instance else None)
        
        if vehiculo_principal and vehiculo_backup:
            if vehiculo_principal == vehiculo_backup:
                raise serializers.ValidationError({
                    'vehiculo_backup': "Un vehículo no puede ser su propio backup."
                })
            
            # Validar que el backup esté operativo
            if vehiculo_backup.estado_operativo != 'OPERATIVO':
                raise serializers.ValidationError({
                    'vehiculo_backup': "El vehículo backup debe estar operativo."
                })
            
            # Validar que el backup no esté siendo usado por otro vehículo (solo en creación)
            if not self.instance:
                backup_activo = BackupVehiculo.objects.filter(
                    vehiculo_backup=vehiculo_backup,
                    estado='ACTIVO',
                    fecha_devolucion__isnull=True
                ).exists()
                
                if backup_activo:
                    raise serializers.ValidationError({
                        'vehiculo_backup': "El vehículo seleccionado ya está siendo utilizado como backup."
                    })
        
        return attrs
    
    class Meta:
        model = BackupVehiculo
        fields = "__all__"
        read_only_fields = ["id", "creado_en", "actualizado_en", "duracion_dias"]
    
    def create(self, validated_data):
        """
        Crea un backup y calcula la duración automáticamente.
        """
        backup = BackupVehiculo.objects.create(**validated_data)
        backup.calcular_duracion()
        return backup
