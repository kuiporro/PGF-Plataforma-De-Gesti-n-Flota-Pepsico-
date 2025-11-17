from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Vehiculo

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("patente", "marca", "modelo", "anio", "estado", "created_at")
    list_filter = ("estado", "marca", "anio")
    search_fields = ("patente", "marca", "modelo", "vin")
    ordering = ("patente",)
