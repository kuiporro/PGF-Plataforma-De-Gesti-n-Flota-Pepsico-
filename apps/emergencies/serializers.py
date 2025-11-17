# apps/emergencies/serializers.py
from rest_framework import serializers
from .models import EmergenciaRuta
from apps.vehicles.serializers import VehiculoListSerializer


class EmergenciaRutaSerializer(serializers.ModelSerializer):
    vehiculo_info = VehiculoListSerializer(source="vehiculo", read_only=True)
    solicitante_nombre = serializers.CharField(source="solicitante.get_full_name", read_only=True)
    aprobador_nombre = serializers.CharField(source="aprobador.get_full_name", read_only=True)
    supervisor_nombre = serializers.CharField(source="supervisor_asignado.get_full_name", read_only=True)
    mecanico_nombre = serializers.CharField(source="mecanico_asignado.get_full_name", read_only=True)
    
    class Meta:
        model = EmergenciaRuta
        fields = [
            "id", "vehiculo", "vehiculo_info", "solicitante", "solicitante_nombre",
            "aprobador", "aprobador_nombre", "supervisor_asignado", "supervisor_nombre",
            "mecanico_asignado", "mecanico_nombre", "descripcion", "ubicacion",
            "zona", "prioridad", "estado", "fecha_solicitud", "fecha_aprobacion",
            "fecha_asignacion", "fecha_resolucion", "fecha_cierre", "ot_asociada",
            "observaciones"
        ]
        read_only_fields = [
            "id", "fecha_solicitud", "fecha_aprobacion", "fecha_asignacion",
            "fecha_resolucion", "fecha_cierre", "ot_asociada"
        ]


class EmergenciaRutaListSerializer(serializers.ModelSerializer):
    vehiculo_patente = serializers.CharField(source="vehiculo.patente", read_only=True)
    
    class Meta:
        model = EmergenciaRuta
        fields = [
            "id", "vehiculo_patente", "descripcion", "ubicacion", "prioridad",
            "estado", "fecha_solicitud", "zona"
        ]


class EmergenciaRutaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear emergencia (solo requiere datos básicos)"""
    class Meta:
        model = EmergenciaRuta
        fields = [
            "vehiculo", "descripcion", "ubicacion", "zona", "prioridad", "observaciones"
        ]

