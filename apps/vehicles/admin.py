from django.contrib import admin
from .models import Vehiculo, IngresoVehiculo, EvidenciaIngreso


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("patente", "marca", "modelo", "anio", "estado", "created_at")
    list_filter = ("estado", "marca", "anio")
    search_fields = ("patente", "marca", "modelo", "vin")
    ordering = ("patente",)


@admin.register(IngresoVehiculo)
class IngresoVehiculoAdmin(admin.ModelAdmin):
    list_display = ("vehiculo", "guardia", "fecha_ingreso", "kilometraje")
    list_filter = ("fecha_ingreso", "guardia")
    search_fields = ("vehiculo__patente", "guardia__username")
    ordering = ("-fecha_ingreso",)
    readonly_fields = ("fecha_ingreso",)


@admin.register(EvidenciaIngreso)
class EvidenciaIngresoAdmin(admin.ModelAdmin):
    list_display = ("ingreso", "tipo", "subido_en")
    list_filter = ("tipo", "subido_en")
    search_fields = ("ingreso__vehiculo__patente", "descripcion")
    ordering = ("-subido_en",)
    readonly_fields = ("subido_en",)
