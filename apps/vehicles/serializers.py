# apps/vehicles/serializers.py
from rest_framework import serializers
from .models import Vehiculo, IngresoVehiculo, EvidenciaIngreso


class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = "__all__"


class VehiculoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = [
            "id", "patente", "tipo", "categoria", "marca", "modelo", "anio",
            "estado", "zona", "sucursal", "km_mensual_promedio"
        ]


class EvidenciaIngresoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenciaIngreso
        fields = "__all__"


class IngresoVehiculoSerializer(serializers.ModelSerializer):
    evidencias = EvidenciaIngresoSerializer(many=True, read_only=True)
    vehiculo_patente = serializers.CharField(source="vehiculo.patente", read_only=True)
    guardia_nombre = serializers.CharField(source="guardia.get_full_name", read_only=True)
    
    class Meta:
        model = IngresoVehiculo
        fields = "__all__"

