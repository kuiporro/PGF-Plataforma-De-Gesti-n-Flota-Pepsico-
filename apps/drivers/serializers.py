# apps/drivers/serializers.py
from rest_framework import serializers
from .models import Chofer, HistorialAsignacionVehiculo
from apps.vehicles.serializers import VehiculoListSerializer


class ChoferSerializer(serializers.ModelSerializer):
    vehiculo_asignado_info = VehiculoListSerializer(source="vehiculo_asignado", read_only=True)
    
    class Meta:
        model = Chofer
        fields = [
            "id", "nombre_completo", "rut", "telefono", "email",
            "zona", "sucursal", "vehiculo_asignado", "vehiculo_asignado_info",
            "km_mensual_promedio", "activo", "fecha_ingreso", "observaciones",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ChoferListSerializer(serializers.ModelSerializer):
    vehiculo_patente = serializers.CharField(source="vehiculo_asignado.patente", read_only=True)
    
    class Meta:
        model = Chofer
        fields = [
            "id", "nombre_completo", "rut", "telefono", "zona",
            "vehiculo_patente", "activo"
        ]


class HistorialAsignacionVehiculoSerializer(serializers.ModelSerializer):
    chofer_nombre = serializers.CharField(source="chofer.nombre_completo", read_only=True)
    vehiculo_patente = serializers.CharField(source="vehiculo.patente", read_only=True)
    
    class Meta:
        model = HistorialAsignacionVehiculo
        fields = [
            "id", "chofer", "chofer_nombre", "vehiculo", "vehiculo_patente",
            "fecha_asignacion", "fecha_fin", "motivo_fin", "activa"
        ]
        read_only_fields = ["id", "fecha_asignacion"]

