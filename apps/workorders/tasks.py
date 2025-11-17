import io
from celery import shared_task
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.core.files.storage import default_storage
from django.utils import timezone


from .models import OrdenTrabajo, Evidencia, Auditoria
from django.contrib.auth import get_user_model



User = get_user_model()

@shared_task
def generar_pdf_cierre(ot_id: str, user_id: int | None):
    ot = (OrdenTrabajo.objects
        .select_related("vehiculo", "responsable")
        .get(id=ot_id))
    usuario = User.objects.filter(id=user_id).first()

    # Generar PDF simple
    buff = io.BytesIO()
    c = canvas.Canvas(buff, pagesize=A4)
    t = c.beginText(40, 800)
    t.textLine(f"Orden de Trabajo #{ot.id}")
    t.textLine(f"Estado: {ot.estado}")
    t.textLine(f"Vehículo: {getattr(ot.vehiculo, 'patente', '-')}")
    t.textLine(f"Responsable: {getattr(ot.responsable, 'username', '-')}")
    t.textLine(f"Cierre: {ot.cierre or timezone.now()}")
    t.textLine("")
    t.textLine("Resumen:")
    t.textLine(f"- Items: {ot.items.count()} (detalles en sistema)")
    c.drawText(t)
    c.showPage()
    c.save()
    buff.seek(0)

    # Guardar archivo en storage
    fname = f"cierres/ot-{ot.id}.pdf"
    saved_path = default_storage.save(fname, buff)
    url = default_storage.url(saved_path)

    # Registrar evidencia
    Evidencia.objects.create(ot=ot, tipo="PDF_CIERRE", url=url)

    # Auditoría
    Auditoria.objects.create(
        usuario=usuario,
        accion="GENERAR_PDF_CIERRE",
        objeto_tipo="OrdenTrabajo",
        objeto_id=str(ot.id),
        payload={"evidencia": url}
    )


# apps/workorders/tasks.py


@shared_task
def ping_task():
    return "pong"
