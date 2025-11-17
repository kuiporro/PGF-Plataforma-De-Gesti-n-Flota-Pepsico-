# apps/inventory/serializers.py
from rest_framework import serializers
from .models import Repuesto, Stock, MovimientoStock, SolicitudRepuesto, HistorialRepuestoVehiculo


class RepuestoSerializer(serializers.ModelSerializer):
    stock_actual = serializers.SerializerMethodField()
    necesita_reorden = serializers.SerializerMethodField()
    
    class Meta:
        model = Repuesto
        fields = "__all__"
    
    def get_stock_actual(self, obj):
        if hasattr(obj, 'stock'):
            return obj.stock.cantidad_actual
        return 0
    
    def get_necesita_reorden(self, obj):
        if hasattr(obj, 'stock'):
            return obj.stock.necesita_reorden
        return False


class StockSerializer(serializers.ModelSerializer):
    repuesto_nombre = serializers.CharField(source="repuesto.nombre", read_only=True)
    repuesto_codigo = serializers.CharField(source="repuesto.codigo", read_only=True)
    
    class Meta:
        model = Stock
        fields = "__all__"


class MovimientoStockSerializer(serializers.ModelSerializer):
    repuesto_codigo = serializers.CharField(source="repuesto.codigo", read_only=True)
    repuesto_nombre = serializers.CharField(source="repuesto.nombre", read_only=True)
    usuario_nombre = serializers.CharField(source="usuario.get_full_name", read_only=True)
    ot_id = serializers.UUIDField(source="ot.id", read_only=True)
    vehiculo_patente = serializers.CharField(source="vehiculo.patente", read_only=True)
    
    class Meta:
        model = MovimientoStock
        fields = "__all__"


class SolicitudRepuestoSerializer(serializers.ModelSerializer):
    repuesto_codigo = serializers.CharField(source="repuesto.codigo", read_only=True)
    repuesto_nombre = serializers.CharField(source="repuesto.nombre", read_only=True)
    ot_id = serializers.UUIDField(source="ot.id", read_only=True)
    solicitante_nombre = serializers.CharField(source="solicitante.get_full_name", read_only=True)
    aprobador_nombre = serializers.CharField(source="aprobador.get_full_name", read_only=True, allow_null=True)
    entregador_nombre = serializers.CharField(source="entregador.get_full_name", read_only=True, allow_null=True)
    
    class Meta:
        model = SolicitudRepuesto
        fields = "__all__"


class HistorialRepuestoVehiculoSerializer(serializers.ModelSerializer):
    repuesto_codigo = serializers.CharField(source="repuesto.codigo", read_only=True)
    repuesto_nombre = serializers.CharField(source="repuesto.nombre", read_only=True)
    vehiculo_patente = serializers.CharField(source="vehiculo.patente", read_only=True)
    ot_id = serializers.UUIDField(source="ot.id", read_only=True, allow_null=True)
    
    class Meta:
        model = HistorialRepuestoVehiculo
        fields = "__all__"

