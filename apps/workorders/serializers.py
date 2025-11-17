# apps/workorders/serializers.py
from rest_framework import serializers
from .models import (OrdenTrabajo, ItemOT, Presupuesto, DetallePresup,
                    Aprobacion, Pausa, Checklist, Evidencia)
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
    # Ahora Python ya sabe qué es ItemOTSerializer
    items = ItemOTSerializer(many=True, read_only=True)
    items_data = ItemOTCreateSerializer(many=True, write_only=True, required=False)
    vehiculo_patente = serializers.CharField(source="vehiculo.patente", read_only=True)
    responsable_nombre = serializers.CharField(source="responsable.get_full_name", read_only=True)
    fecha_apertura = serializers.DateTimeField(source="apertura", read_only=True)

    class Meta:
        model = OrdenTrabajo
        fields = '__all__'

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

# --- Y FINALMENTE, EL RESTO DE SERIALIZERS SIMPLES ---

class AprobacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aprobacion
        fields = "__all__"

class PausaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pausa
        fields = "__all__"

class ChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checklist
        fields = "__all__"

class EvidenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidencia
        fields = "__all__"


class OrdenTrabajoListSerializer(serializers.ModelSerializer):
    vehiculo_patente = serializers.CharField(source="vehiculo.patente", read_only=True)
    responsable_nombre = serializers.CharField(source="responsable.get_full_name", read_only=True)
    fecha_apertura = serializers.DateTimeField(source="apertura", read_only=True)

    class Meta:
        model = OrdenTrabajo
        fields = [
            "id",
            "estado",
            "vehiculo_patente",
            "responsable_nombre",
            "fecha_apertura",
        ]
