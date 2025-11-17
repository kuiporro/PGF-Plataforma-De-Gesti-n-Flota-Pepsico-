# apps/vehicles/serializers.py
from rest_framework import serializers
from .models import (Vehiculo)
class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = "__all__"


class VehiculoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = ["id", "patente", "marca", "modelo", "anio"]

