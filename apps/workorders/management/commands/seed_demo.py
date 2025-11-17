from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.vehicles.models import Vehiculo
from apps.workorders.models import (
    OrdenTrabajo, ItemOT, Presupuesto, DetallePresup,
    Aprobacion, Pausa, Checklist, Evidencia
)
from decimal import Decimal

class Command(BaseCommand):
    help = "Crea datos de demostración completos para PGF"

    def handle(self, *args, **options):
        User = get_user_model()
        users = [
            ("admin","admin@example.com","ADMIN","admin123", True),
            ("guardia","guardia@example.com","GUARDIA","guardia123", False),
            ("mecanico","mecanico@example.com","MECANICO","mecanico123", False),
            ("supervisor","supervisor@example.com","SUPERVISOR","supervisor123", True),
            ("sponsor","sponsor@example.com","SPONSOR","sponsor123", False),
        ]
        created = {}
        for username,email,rol,pwd,is_staff in users:
            u, _ = User.objects.get_or_create(username=username, defaults={"email": email, "rol": rol, "is_staff": is_staff})
            u.set_password(pwd); u.save()
            created[rol] = u

        v1, _ = Vehiculo.objects.get_or_create(patente="ABCJ12", defaults=dict(marca="Scania", modelo="R500", anio=2021, vin="VIN1234567890", estado="ACTIVO"))
        v2, _ = Vehiculo.objects.get_or_create(patente="KLMN34", defaults=dict(marca="Volvo", modelo="FH 460", anio=2022, vin="VIN0987654321", estado="ACTIVO"))

        ot1, _ = OrdenTrabajo.objects.get_or_create(vehiculo=v1, estado="ABIERTA", defaults=dict(responsable=created["SUPERVISOR"], motivo="Ruidos en frenos y vibración al frenar."))
        ItemOT.objects.get_or_create(ot=ot1, tipo="SERVICIO", descripcion="Diagnóstico de frenos", cantidad=1, costo_unitario=Decimal("0.00"))
        ItemOT.objects.get_or_create(ot=ot1, tipo="REPUESTO", descripcion="Pastillas de freno delanteras", cantidad=1, costo_unitario=Decimal("180.00"))
        ItemOT.objects.get_or_create(ot=ot1, tipo="REPUESTO", descripcion="Discos de freno delanteros (par)", cantidad=1, costo_unitario=Decimal("320.00"))
        ItemOT.objects.get_or_create(ot=ot1, tipo="SERVICIO", descripcion="Mano de obra", cantidad=4, costo_unitario=Decimal("25.00"))
        total = sum([i.cantidad * i.costo_unitario for i in ot1.items.all()])
        pres, _ = Presupuesto.objects.get_or_create(ot=ot1, defaults=dict(total=total, requiere_aprobacion=True, umbral=Decimal("300.00")))
        for it in ot1.items.all():
            DetallePresup.objects.get_or_create(presupuesto=pres, concepto=it.descripcion, cantidad=it.cantidad, precio=it.costo_unitario)
        Aprobacion.objects.get_or_create(presupuesto=pres, defaults=dict(sponsor=created["SPONSOR"], estado="PENDIENTE", comentario="A la espera de confirmación"))
        Evidencia.objects.get_or_create(ot=ot1, url="https://example.com/fotos/freno_antes.jpg", tipo="FOTO")
        Pausa.objects.get_or_create(ot=ot1, usuario=created["MECANICO"], motivo="Esperando repuestos", fin=None)
        Checklist.objects.get_or_create(ot=ot1, resultado="NO_OK", observaciones="Desbalance leve detectado en rueda delantera izquierda.")

        ot2, _ = OrdenTrabajo.objects.get_or_create(vehiculo=v2, estado="EN_QA", defaults=dict(responsable=created["SUPERVISOR"], motivo="Mantención programada 20.000 km"))
        ItemOT.objects.get_or_create(ot=ot2, tipo="SERVICIO", descripcion="Cambio de aceite y filtros", cantidad=1, costo_unitario=Decimal("120.00"))
        ItemOT.objects.get_or_create(ot=ot2, tipo="SERVICIO", descripcion="Revisión general", cantidad=1, costo_unitario=Decimal("60.00"))
        Checklist.objects.get_or_create(ot=ot2, resultado="OK", observaciones="Todo conforme.")

        self.stdout.write(self.style.SUCCESS("Seed creada. Credenciales:"))
        self.stdout.write(" admin / admin123 | guardia / guardia123 | mecanico / mecanico123 | supervisor / supervisor123 | sponsor / sponsor123")
