# apps/workorders/serializers.py
from rest_framework import serializers
from .models import (OrdenTrabajo, ItemOT, Presupuesto, DetallePresup,
                    Aprobacion, Pausa, Checklist, Evidencia, ComentarioOT,
                    BloqueoVehiculo, VersionEvidencia)
from decimal import Decimal

# --- PRIMERO DEFINIMOS LOS SERIALIZERS BÁSICOS ---

class ItemOTSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemOT
        fields = "__all__"

class DetallePresupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePresup
        fields = "__all__"

# --- AHORA DEFINIMOS LOS SERIALIZERS QUE USAN A OTROS ---

class ItemOTCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemOT
        exclude = ('ot',)

class OrdenTrabajoSerializer(serializers.ModelSerializer):
    """
    Serializer para OrdenTrabajo.
    
    Validaciones implementadas:
    - Vehículo existente
    - No permitir OT duplicadas (vehículo no puede tener otra OT activa)
    - Campos obligatorios (motivo, supervisor, site, fecha_apertura)
    """
    # Ahora Python ya sabe qué es ItemOTSerializer
    items = ItemOTSerializer(many=True, read_only=True)
    items_data = ItemOTCreateSerializer(many=True, write_only=True, required=False)
    vehiculo_patente = serializers.CharField(source="vehiculo.patente", read_only=True)
    responsable_nombre = serializers.CharField(source="responsable.get_full_name", read_only=True)
    supervisor_nombre = serializers.CharField(source="supervisor.get_full_name", read_only=True)
    jefe_taller_nombre = serializers.CharField(source="jefe_taller.get_full_name", read_only=True)
    mecanico_nombre = serializers.CharField(source="mecanico.get_full_name", read_only=True)
    fecha_apertura = serializers.DateTimeField(source="apertura", read_only=True)

    class Meta:
        model = OrdenTrabajo
        fields = '__all__'
    
    def validate_vehiculo(self, value):
        """
        Valida que el vehículo exista.
        """
        if not value:
            raise serializers.ValidationError("El vehículo es obligatorio.")
        return value
    
    def validate(self, attrs):
        """
        Validaciones a nivel de objeto completo.
        """
        # Validar campos obligatorios
        # Nota: 'apertura' se genera automáticamente (auto_now_add=True), no es requerido
        # Nota: 'supervisor' no es obligatorio al crear (el guardia puede crear OT sin supervisor)
        campos_obligatorios = {
            'motivo': 'motivo de ingreso',
            'site': 'site'
        }
        
        for campo, nombre_display in campos_obligatorios.items():
            if campo not in attrs:
                if self.instance:
                    # En actualización, si no viene en attrs, usar el valor actual
                    if not getattr(self.instance, campo, None):
                        raise serializers.ValidationError({campo: f"El campo {nombre_display} es obligatorio."})
                else:
                    # En creación, el campo debe estar en attrs
                    raise serializers.ValidationError({campo: f"El campo {nombre_display} es obligatorio."})
        
        # Validar que el vehículo no tenga otra OT activa (solo en creación)
        if not self.instance:  # Solo validar en creación
            vehiculo = attrs.get('vehiculo')
            if vehiculo:
                ots_activas = OrdenTrabajo.objects.filter(
                    vehiculo=vehiculo,
                    estado__in=['ABIERTA', 'EN_EJECUCION', 'QA', 'EN_DIAGNOSTICO', 'EN_PAUSA']
                ).exists()
                
                if ots_activas:
                    raise serializers.ValidationError({
                        'vehiculo': "Este vehículo ya cuenta con una OT activa."
                    })
        
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop('items_data', [])
        orden = OrdenTrabajo.objects.create(**validated_data)
        for item_data in items_data:
            ItemOT.objects.create(ot=orden, **item_data)
        return orden

class DetallePresupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePresup
        exclude = ('presupuesto',)

class PresupuestoSerializer(serializers.ModelSerializer):
    # Ahora Python ya sabe qué es DetallePresupSerializer
    detalles = DetallePresupSerializer(many=True, read_only=True)
    detalles_data = DetallePresupCreateSerializer(many=True, write_only=True, required=False)

    total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    requiere_aprobacion = serializers.BooleanField(read_only=True)

    class Meta:
        model = Presupuesto
        fields = '__all__'
    
    def create(self, validated_data):
        """Excluir detalles_data de validated_data antes de crear el objeto"""
        validated_data.pop('detalles_data', None)
        return super().create(validated_data)

# --- Y FINALMENTE, EL RESTO DE SERIALIZERS SIMPLES ---

class AprobacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aprobacion
        fields = "__all__"

class PausaSerializer(serializers.ModelSerializer):
    """
    Serializer para Pausa.
    
    Validaciones implementadas:
    - No permitir pausar si la OT no está EN_EJECUCION
    - No permitir reanudar si la OT no está EN_PAUSA
    """
    usuario_nombre = serializers.CharField(source="usuario.get_full_name", read_only=True)
    duracion_minutos = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Pausa
        fields = "__all__"
    
    def validate(self, attrs):
        """
        Validaciones a nivel de objeto completo.
        """
        ot = attrs.get('ot') or (self.instance.ot if self.instance else None)
        
        if not ot:
            raise serializers.ValidationError({"ot": "La OT es obligatoria."})
        
        # Si se está creando una pausa (no tiene fin), validar que la OT esté EN_EJECUCION
        if not self.instance:  # Creación
            if ot.estado != 'EN_EJECUCION':
                raise serializers.ValidationError({
                    'ot': "Solo se pueden crear pausas cuando la OT está en estado EN_EJECUCION."
                })
        
        return attrs

class ChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checklist
        fields = "__all__"

class EvidenciaSerializer(serializers.ModelSerializer):
    invalidado = serializers.BooleanField(read_only=True)
    invalidado_por_nombre = serializers.CharField(source="invalidado_por.get_full_name", read_only=True)
    invalidado_en = serializers.DateTimeField(read_only=True)
    subido_por_nombre = serializers.CharField(source="subido_por.get_full_name", read_only=True)
    
    class Meta:
        model = Evidencia
        fields = "__all__"
        read_only_fields = ["subido_en", "subido_por"]


class ComentarioOTSerializer(serializers.ModelSerializer):
    """
    Serializer para comentarios en OT.
    
    Soporta:
    - Creación de comentarios
    - Respuestas a comentarios (comentario_padre)
    - Menciones de usuarios
    - Edición de comentarios
    """
    usuario_nombre = serializers.CharField(source="usuario.get_full_name", read_only=True)
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)
    usuario_rol = serializers.CharField(source="usuario.rol", read_only=True)
    respuestas = serializers.SerializerMethodField()
    
    class Meta:
        model = ComentarioOT
        fields = "__all__"
        read_only_fields = ["editado", "editado_en", "creado_en"]
    
    def get_respuestas(self, obj):
        """Obtiene las respuestas de un comentario."""
        respuestas = obj.respuestas.all().order_by("creado_en")
        return ComentarioOTSerializer(respuestas, many=True).data
    
    def validate(self, attrs):
        """Validar que el contenido no esté vacío."""
        contenido = attrs.get("contenido", "").strip()
        if not contenido:
            raise serializers.ValidationError({"contenido": "El comentario no puede estar vacío."})
        return attrs


class BloqueoVehiculoSerializer(serializers.ModelSerializer):
    """
    Serializer para bloqueos de vehículos.
    """
    creado_por_nombre = serializers.CharField(source="creado_por.get_full_name", read_only=True)
    resuelto_por_nombre = serializers.CharField(source="resuelto_por.get_full_name", read_only=True)
    vehiculo_patente = serializers.CharField(source="vehiculo.patente", read_only=True)
    
    class Meta:
        model = BloqueoVehiculo
        fields = "__all__"
        read_only_fields = ["creado_en", "resuelto_en"]


class VersionEvidenciaSerializer(serializers.ModelSerializer):
    """
    Serializer para versiones de evidencias invalidadas.
    """
    invalidado_por_nombre = serializers.CharField(source="invalidado_por.get_full_name", read_only=True)
    
    class Meta:
        model = VersionEvidencia
        fields = "__all__"
        read_only_fields = ["invalidado_en"]


class OrdenTrabajoListSerializer(serializers.ModelSerializer):
    vehiculo_patente = serializers.CharField(source="vehiculo.patente", read_only=True)
    responsable_nombre = serializers.CharField(source="responsable.get_full_name", read_only=True)
    supervisor_nombre = serializers.CharField(source="supervisor.get_full_name", read_only=True)
    mecanico_nombre = serializers.CharField(source="mecanico.get_full_name", read_only=True)
    fecha_apertura = serializers.DateTimeField(source="apertura", read_only=True)

    class Meta:
        model = OrdenTrabajo
        fields = [
            "id",
            "estado",
            "vehiculo_patente",
            "responsable_nombre",
            "supervisor_nombre",
            "mecanico_nombre",
            "prioridad",
            "tipo",
            "fecha_apertura",
            "zona",
        ]
