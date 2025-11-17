# apps/vehicles/views.py

from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend

from .models import Vehiculo
from .serializers import VehiculoSerializer
from .permissions import VehiclePermission
from .serializers import VehiculoListSerializer


class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all().order_by("-created_at")
    serializer_class = VehiculoSerializer
    permission_classes = [permissions.IsAuthenticated, VehiclePermission]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ["estado", "marca", "anio"]
    search_fields = ["patente", "marca", "modelo", "vin"]
    ordering_fields = ["patente", "anio", "marca"]

serializer_class = VehiculoListSerializer