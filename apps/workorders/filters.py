# apps/workorders/filters.py
import django_filters as filters
from django.db.models import Q
from .models import OrdenTrabajo

class OrdenTrabajoFilter(filters.FilterSet):
    estado = filters.CharFilter(field_name="estado", lookup_expr="iexact")
    apertura_from = filters.DateFilter(field_name="apertura", lookup_expr="date__gte")
    apertura_to   = filters.DateFilter(field_name="apertura", lookup_expr="date__lte")
    patente = filters.CharFilter(label="Patente", method="filter_patente")

    def filter_patente(self, queryset, name, value):
        return queryset.filter(Q(vehiculo__patente__icontains=value))

    class Meta:
        model = OrdenTrabajo
        fields = ["id", "estado", "vehiculo"]
        order_by = filters.OrderingFilter(
            fields=(
                ('apertura', 'apertura'),
                ('estado', 'estado'),
            )
        )