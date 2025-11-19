# apps/reports/pdf_generator.py
"""
Generador de reportes PDF usando ReportLab
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from django.utils import timezone
from datetime import timedelta
# No importar views aquí para evitar circular imports


def generar_ticket_ingreso_pdf(ingreso_id: str):
    """
    Genera un PDF del ticket de ingreso de vehículo al taller.
    
    Args:
        ingreso_id: UUID del IngresoVehiculo
        
    Returns:
        BytesIO: Buffer con el PDF generado
    """
    from apps.vehicles.models import IngresoVehiculo
    
    # Obtener el ingreso con relaciones
    try:
        ingreso = IngresoVehiculo.objects.select_related(
            'vehiculo', 'guardia', 'guardia_salida'
        ).prefetch_related('evidencias').get(id=ingreso_id)
    except IngresoVehiculo.DoesNotExist:
        raise ValueError(f"Ingreso con ID {ingreso_id} no encontrado")
    
    # Crear buffer para el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=30, 
        leftMargin=30, 
        topMargin=30, 
        bottomMargin=30
    )
    
    # Contenedor para elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#003DA5'),  # Azul PepsiCo
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#003DA5'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Título
    elements.append(Paragraph("TICKET DE INGRESO AL TALLER", title_style))
    elements.append(Paragraph("PepsiCo Chile - Sistema PGF", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Información del vehículo
    vehiculo = ingreso.vehiculo
    elements.append(Paragraph("INFORMACIÓN DEL VEHÍCULO", heading_style))
    
    vehiculo_data = [
        ["Patente:", vehiculo.patente],
        ["Marca:", vehiculo.marca or "N/A"],
        ["Modelo:", vehiculo.modelo or "N/A"],
        ["Año:", str(vehiculo.anio) if vehiculo.anio else "N/A"],
        ["VIN:", vehiculo.vin or "N/A"],
        ["Tipo:", vehiculo.tipo or "N/A"],
        ["Kilometraje al ingreso:", f"{ingreso.kilometraje:,} km" if ingreso.kilometraje else "N/A"],
    ]
    
    vehiculo_table = Table(vehiculo_data, colWidths=[2*inch, 4*inch])
    vehiculo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(vehiculo_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Información del ingreso
    elements.append(Paragraph("INFORMACIÓN DEL INGRESO", heading_style))
    
    ingreso_data = [
        ["Número de Ticket:", str(ingreso.id)[:8].upper()],
        ["Fecha y Hora:", ingreso.fecha_ingreso.strftime("%d/%m/%Y %H:%M:%S")],
        ["Registrado por:", ingreso.guardia.get_full_name() or ingreso.guardia.username],
        ["QR Code:", ingreso.qr_code or "N/A"],
    ]
    
    if ingreso.observaciones:
        ingreso_data.append(["Observaciones:", ingreso.observaciones])
    
    ingreso_table = Table(ingreso_data, colWidths=[2*inch, 4*inch])
    ingreso_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(ingreso_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Información de OT generada (si existe)
    from apps.workorders.models import OrdenTrabajo
    ot = OrdenTrabajo.objects.filter(
        vehiculo=vehiculo,
        apertura__gte=ingreso.fecha_ingreso - timedelta(minutes=5)
    ).first()
    
    if ot:
        elements.append(Paragraph("ORDEN DE TRABAJO GENERADA", heading_style))
        ot_data = [
            ["Número OT:", str(ot.id)[:8].upper()],
            ["Estado:", ot.estado],
            ["Tipo:", ot.tipo or "N/A"],
            ["Motivo:", ot.motivo or "N/A"],
            ["Prioridad:", ot.prioridad or "MEDIA"],
        ]
        
        ot_table = Table(ot_data, colWidths=[2*inch, 4*inch])
        ot_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(ot_table)
        elements.append(Spacer(1, 0.2*inch))
    
    # Pie de página
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(
        f"Generado el {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}",
        ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
    ))
    
    # Construir PDF
    doc.build(elements)
    
    # Retornar buffer
    buffer.seek(0)
    return buffer


def generar_reporte_semanal_pdf(fecha_inicio=None, fecha_fin=None):
    """
    Genera un reporte semanal en PDF con productividad del taller
    """
    if not fecha_inicio:
        fecha_fin = timezone.now().date()
        fecha_inicio = fecha_fin - timedelta(days=7)
    
    # Crear buffer para el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    
    # Contenedor para elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#003DA5'),  # Azul PepsiCo
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#003DA5'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Título
    elements.append(Paragraph("REPORTE SEMANAL DE PRODUCTIVIDAD", title_style))
    elements.append(Paragraph(f"PepsiCo Chile - Sistema PGF", styles['Normal']))
    elements.append(Paragraph(f"Período: {fecha_inicio} al {fecha_fin}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Importar datos
    from apps.workorders.models import OrdenTrabajo, Pausa
    from apps.vehicles.models import Vehiculo
    from apps.users.models import User
    from django.db.models import Count, Avg, Sum, Q, F
    from django.db.models.functions import Extract
    
    # KPIs principales
    ot_cerradas = OrdenTrabajo.objects.filter(
        estado="CERRADA",
        cierre__date__gte=fecha_inicio,
        cierre__date__lte=fecha_fin
    )
    
    total_cerradas = ot_cerradas.count()
    
    # Tiempo promedio de reparación
    tiempos = ot_cerradas.annotate(
        duracion=F('cierre') - F('apertura')
    ).aggregate(
        promedio=Avg('duracion')
    )
    
    tiempo_promedio = tiempos['promedio']
    if tiempo_promedio:
        horas = tiempo_promedio.total_seconds() / 3600
        tiempo_promedio_str = f"{horas:.2f} horas"
    else:
        tiempo_promedio_str = "N/A"
    
    # Productividad por mecánico
    mecanicos_stats = User.objects.filter(
        rol="MECANICO"
    ).annotate(
        total_cerradas=Count('ots_asignadas', filter=Q(ots_asignadas__estado="CERRADA", ots_asignadas__cierre__date__gte=fecha_inicio, ots_asignadas__cierre__date__lte=fecha_fin))
    ).filter(total_cerradas__gt=0).order_by('-total_cerradas')
    
    # Retrabajos
    retrabajos = OrdenTrabajo.objects.filter(
        estado="RETRABAJO",
        apertura__date__gte=fecha_inicio,
        apertura__date__lte=fecha_fin
    ).count()
    
    # Mantenciones vs Emergencias
    mantenciones = OrdenTrabajo.objects.filter(
        tipo="MANTENCION",
        cierre__date__gte=fecha_inicio,
        cierre__date__lte=fecha_fin
    ).count()
    
    emergencias = OrdenTrabajo.objects.filter(
        tipo="EMERGENCIA",
        cierre__date__gte=fecha_inicio,
        cierre__date__lte=fecha_fin
    ).count()
    
    # Pausas más frecuentes
    pausas_frecuentes = Pausa.objects.filter(
        inicio__date__gte=fecha_inicio,
        inicio__date__lte=fecha_fin
    ).values('tipo').annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    # Tabla de KPIs principales
    kpi_data = [
        ['KPI', 'Valor'],
        ['OT Cerradas', str(total_cerradas)],
        ['Tiempo Promedio de Reparación', tiempo_promedio_str],
        ['Retrabajos', str(retrabajos)],
        ['Mantenciones', str(mantenciones)],
        ['Emergencias', str(emergencias)],
    ]
    
    kpi_table = Table(kpi_data, colWidths=[4*inch, 2*inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003DA5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(Paragraph("KPIs Principales", heading_style))
    elements.append(kpi_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de productividad por mecánico
    if mecanicos_stats:
        elements.append(Paragraph("Productividad por Mecánico", heading_style))
        
        mecanicos_data = [['Mecánico', 'OT Cerradas']]
        for m in mecanicos_stats:
            nombre = f"{m.first_name} {m.last_name}".strip() or m.username
            mecanicos_data.append([nombre, str(m.total_cerradas)])
        
        mecanicos_table = Table(mecanicos_data, colWidths=[4*inch, 2*inch])
        mecanicos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003DA5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(mecanicos_table)
        elements.append(Spacer(1, 0.3*inch))
    
    # Pausas más frecuentes
    if pausas_frecuentes:
        elements.append(Paragraph("Pausas Más Frecuentes", heading_style))
        
        pausas_data = [['Tipo de Pausa', 'Cantidad']]
        for p in pausas_frecuentes:
            # Obtener display del tipo de pausa
            tipo_display = p['tipo']
            if p['tipo'] == "ESPERA_REPUESTO":
                tipo_display = "Espera de Repuesto"
            elif p['tipo'] == "APROBACION_PENDIENTE":
                tipo_display = "Aprobación Pendiente"
            elif p['tipo'] == "COLACION":
                tipo_display = "Colación (12:30-13:15)"
            elif p['tipo'] == "OTRO":
                tipo_display = "Otro Motivo Operativo"
            elif p['tipo'] == "ADMINISTRATIVA":
                tipo_display = "Pausa Administrativa"
            pausas_data.append([tipo_display, str(p['total'])])
        
        pausas_table = Table(pausas_data, colWidths=[4*inch, 2*inch])
        pausas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003DA5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(pausas_table)
        elements.append(Spacer(1, 0.3*inch))
    
    # Pie de página
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(f"Generado el {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Paragraph("Sistema PGF - PepsiCo Chile", styles['Normal']))
    
    # Construir PDF
    doc.build(elements)
    
    # Obtener bytes del PDF
    buffer.seek(0)
    return buffer.getvalue()


def generar_reporte_diario_pdf(fecha=None):
    """
    Genera un reporte diario en PDF con operación del día
    """
    if not fecha:
        fecha = timezone.now().date()
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#003DA5'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Título
    elements.append(Paragraph("REPORTE DIARIO DE OPERACIÓN", title_style))
    elements.append(Paragraph(f"PepsiCo Chile - Sistema PGF", styles['Normal']))
    elements.append(Paragraph(f"Fecha: {fecha}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Importar datos
    from apps.workorders.models import OrdenTrabajo, Pausa
    from apps.vehicles.models import Vehiculo
    
    # Vehículos activos
    vehiculos_activos = Vehiculo.objects.filter(estado="ACTIVO").count()
    vehiculos_en_taller = Vehiculo.objects.filter(estado__in=["EN_ESPERA", "EN_MANTENIMIENTO"]).count()
    
    # OT por estado
    ot_abiertas = OrdenTrabajo.objects.filter(estado="ABIERTA").count()
    ot_en_ejecucion = OrdenTrabajo.objects.filter(estado="EN_EJECUCION").count()
    ot_en_pausa = OrdenTrabajo.objects.filter(estado="EN_PAUSA").count()
    ot_en_qa = OrdenTrabajo.objects.filter(estado="EN_QA").count()
    ot_cerradas_hoy = OrdenTrabajo.objects.filter(
        estado="CERRADA",
        cierre__date=fecha
    ).count()
    
    # Pausas activas
    pausas_activas = Pausa.objects.filter(fin__isnull=True).count()
    
    # Tabla de resumen
    resumen_data = [
        ['Indicador', 'Valor'],
        ['Vehículos Activos', str(vehiculos_activos)],
        ['Vehículos en Taller', str(vehiculos_en_taller)],
        ['OT Abiertas', str(ot_abiertas)],
        ['OT en Ejecución', str(ot_en_ejecucion)],
        ['OT en Pausa', str(ot_en_pausa)],
        ['OT en QA', str(ot_en_qa)],
        ['OT Cerradas Hoy', str(ot_cerradas_hoy)],
        ['Pausas Activas', str(pausas_activas)],
    ]
    
    resumen_table = Table(resumen_data, colWidths=[4*inch, 2*inch])
    resumen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003DA5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(resumen_table)
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(f"Generado el {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

