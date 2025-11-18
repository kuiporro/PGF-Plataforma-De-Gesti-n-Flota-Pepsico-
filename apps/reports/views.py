# apps/reports/views.py
"""
Vistas para generación de reportes y dashboards.

Este módulo define todos los endpoints de la API relacionados con:
- Dashboard Ejecutivo: KPIs y métricas para ejecutivos
- Reportes de Productividad: Estadísticas de productividad del taller
- Reportes PDF: Generación de reportes en formato PDF
- Reportes de Pausas: Análisis de pausas en las OT

Relaciones:
- Usa: apps/workorders/models.py (OrdenTrabajo, Pausa)
- Usa: apps/vehicles/models.py (Vehiculo)
- Usa: apps/users/models.py (User)
- Usa: apps/inventory/models.py (SolicitudRepuesto, MovimientoStock)
- Usa: apps/reports/pdf_generator.py (generación de PDFs)
- Conectado a: apps/reports/urls.py

Endpoints principales:
- /api/v1/reports/dashboard-ejecutivo/ → KPIs del dashboard ejecutivo
- /api/v1/reports/productividad/ → Reporte de productividad
- /api/v1/reports/pdf/ → Generar reporte PDF
- /api/v1/reports/pausas/ → Reporte de pausas

Características:
- Caché de KPIs (2 minutos) para optimizar rendimiento
- Generación de PDFs con ReportLab
- Agregaciones complejas con Django ORM
"""

from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum, Q, F  # Funciones de agregación
from django.utils import timezone
from django.core.cache import cache  # Sistema de caché
from datetime import timedelta
from drf_spectacular.utils import extend_schema

from apps.workorders.models import OrdenTrabajo, Pausa
from apps.vehicles.models import Vehiculo
from apps.users.models import User
from apps.inventory.models import SolicitudRepuesto, MovimientoStock


class DashboardEjecutivoView(views.APIView):
    """
    Dashboard con KPIs para el ejecutivo.
    
    Endpoint: GET /api/v1/reports/dashboard-ejecutivo/
    
    Permisos:
    - Solo EJECUTIVO, ADMIN o SPONSOR
    
    Características:
    - Caché de 2 minutos para optimizar rendimiento
    - KPIs en tiempo real
    - Últimas 5 OT
    - Pausas más frecuentes
    - Mecánicos con más carga
    - Tiempos promedio por estado
    
    Retorna:
    - 200: {
        "kpis": {
            "ot_abiertas": 10,
            "ot_en_diagnostico": 2,
            "ot_en_ejecucion": 5,
            "ot_en_pausa": 1,
            "ot_en_qa": 3,
            "ot_retrabajo": 0,
            "ot_cerradas_hoy": 8,
            "vehiculos_en_taller": 12,
            "productividad_7_dias": 45
        },
        "ultimas_5_ot": [...],
        "pausas_frecuentes": [...],
        "mecanicos_carga": [...],
        "tiempos_promedio": {...}
      }
    - 403: Si no tiene permisos
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        description="Obtiene todos los KPIs del dashboard ejecutivo",
        responses={200: None}
    )
    def get(self, request):
        """
        Retorna todos los KPIs requeridos para el dashboard ejecutivo.
        
        Proceso:
        1. Verifica permisos
        2. Intenta obtener del caché (válido 2 minutos)
        3. Si no está en caché, calcula todos los KPIs
        4. Guarda en caché
        5. Retorna datos
        
        Optimizaciones:
        - Caché de 2 minutos reduce carga en la base de datos
        - select_related para reducir queries
        - Agregaciones eficientes con Django ORM
        """
        # Verificar que el usuario tenga rol EJECUTIVO, ADMIN o SPONSOR
        if request.user.rol not in ("EJECUTIVO", "ADMIN", "SPONSOR"):
            return Response(
                {"detail": "No autorizado para ver el dashboard ejecutivo."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Intentar obtener del cache (válido por 2 minutos)
        # Esto reduce la carga en la base de datos para consultas frecuentes
        cache_key = "dashboard_ejecutivo_kpis"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # Fecha actual para cálculos
        hoy = timezone.now().date()
        inicio_dia = timezone.make_aware(timezone.datetime.combine(hoy, timezone.datetime.min.time()))
        
        # ==================== KPIs DE OT ====================
        # Contar OT por estado
        ot_abiertas = OrdenTrabajo.objects.filter(estado="ABIERTA").count()
        ot_en_diagnostico = OrdenTrabajo.objects.filter(estado="EN_DIAGNOSTICO").count()
        ot_en_ejecucion = OrdenTrabajo.objects.filter(estado="EN_EJECUCION").count()
        ot_en_pausa = OrdenTrabajo.objects.filter(estado="EN_PAUSA").count()
        ot_en_qa = OrdenTrabajo.objects.filter(estado="EN_QA").count()
        ot_retrabajo = OrdenTrabajo.objects.filter(estado="RETRABAJO").count()
        
        # OT cerradas hoy
        ot_cerradas_hoy = OrdenTrabajo.objects.filter(
            estado="CERRADA",
            cierre__date=hoy
        ).count()
        
        # ==================== ÚLTIMAS 5 OT ====================
        # Obtener las 5 OT más recientes con optimización
        ultimas_5_ot = OrdenTrabajo.objects.select_related(
            'vehiculo', 'responsable'
        ).order_by('-apertura')[:5]
        
        # Serializar datos de las últimas 5 OT
        ultimas_5_ot_data = [{
            "id": str(ot.id),
            "patente": ot.vehiculo.patente if ot.vehiculo else "N/A",
            "estado": ot.estado,
            "responsable": f"{ot.responsable.first_name} {ot.responsable.last_name}" if ot.responsable else "Sin responsable",
            "apertura": ot.apertura.isoformat(),
            "tipo": ot.tipo if hasattr(ot, 'tipo') else None,
        } for ot in ultimas_5_ot]
        
        # ==================== VEHÍCULOS EN TALLER ====================
        # Total vehículos en taller (EN_ESPERA o EN_MANTENIMIENTO)
        vehiculos_en_taller = Vehiculo.objects.filter(
            estado__in=["EN_ESPERA", "EN_MANTENIMIENTO"]
        ).count()
        
        # ==================== PRODUCTIVIDAD ====================
        # Productividad del taller (OT cerradas en los últimos 7 días)
        hace_7_dias = hoy - timedelta(days=7)
        ot_cerradas_7_dias = OrdenTrabajo.objects.filter(
            estado="CERRADA",
            cierre__date__gte=hace_7_dias
        ).count()
        
        # ==================== PAUSAS MÁS FRECUENTES ====================
        # Agrupar pausas por motivo y contar
        pausas_frecuentes = Pausa.objects.values('motivo').annotate(
            cantidad=Count('id')
        ).order_by('-cantidad')[:5]  # Top 5
        
        # ==================== MECÁNICOS CON MÁS CARGA ====================
        # Mecánicos con más carga de trabajo (OT activas)
        mecanicos_carga = User.objects.filter(
            rol="MECANICO",
            ots_responsable__estado__in=["ABIERTA", "EN_EJECUCION", "EN_PAUSA"]
        ).annotate(
            total_ots=Count('ots_responsable')
        ).order_by('-total_ots')[:5]  # Top 5
        
        # Serializar datos de mecánicos
        mecanicos_carga_data = [{
            "id": m.id,
            "nombre": f"{m.first_name} {m.last_name}",
            "total_ots": m.total_ots
        } for m in mecanicos_carga]
        
        # ==================== TIEMPOS PROMEDIO ====================
        # Calcular tiempos promedio por estado
        tiempos_promedio = {}
        estados = ["ABIERTA", "EN_EJECUCION", "EN_PAUSA", "EN_QA"]
        
        for estado in estados:
            ots = OrdenTrabajo.objects.filter(estado=estado)
            if estado == "CERRADA":
                # Para cerradas, calcular tiempo desde apertura hasta cierre
                tiempos = ots.filter(cierre__isnull=False).annotate(
                    tiempo_total=F('cierre') - F('apertura')
                ).aggregate(
                    promedio=Avg('tiempo_total')
                )
            else:
                # Para otros estados, calcular tiempo desde apertura hasta ahora
                tiempos = ots.annotate(
                    tiempo_actual=timezone.now() - F('apertura')
                ).aggregate(
                    promedio=Avg('tiempo_actual')
                )
            
            if tiempos['promedio']:
                tiempos_promedio[estado] = str(tiempos['promedio'])
            else:
                tiempos_promedio[estado] = None
        
        # ==================== CONSTRUIR RESPUESTA ====================
        response_data = {
            "kpis": {
                "ot_abiertas": ot_abiertas,
                "ot_en_diagnostico": ot_en_diagnostico,
                "ot_en_ejecucion": ot_en_ejecucion,
                "ot_en_pausa": ot_en_pausa,
                "ot_en_qa": ot_en_qa,
                "ot_retrabajo": ot_retrabajo,
                "ot_cerradas_hoy": ot_cerradas_hoy,
                "vehiculos_en_taller": vehiculos_en_taller,
                "productividad_7_dias": ot_cerradas_7_dias,
            },
            "ultimas_5_ot": ultimas_5_ot_data,
            "pausas_frecuentes": list(pausas_frecuentes),
            "mecanicos_carga": mecanicos_carga_data,
            "tiempos_promedio": tiempos_promedio,
        }
        
        # Guardar en cache por 2 minutos (120 segundos)
        # Esto evita recalcular KPIs en cada request
        cache.set(cache_key, response_data, 120)
        
        return Response(response_data)


class ReporteProductividadView(views.APIView):
    """
    Reporte de productividad del taller.
    
    Endpoint: GET /api/v1/reports/productividad/
    
    Permisos:
    - EJECUTIVO, ADMIN, JEFE_TALLER, SUPERVISOR
    
    Parámetros (query):
    - fecha_inicio: Fecha de inicio (ISO format, opcional, default: 30 días atrás)
    - fecha_fin: Fecha de fin (ISO format, opcional, default: ahora)
    
    Retorna:
    - 200: {
        "periodo": {
            "inicio": "...",
            "fin": "..."
        },
        "total_ot_cerradas": 45,
        "estadisticas_mecanicos": [...]
      }
    - 403: Si no tiene permisos
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        description="Genera reporte de productividad",
        responses={200: None}
    )
    def get(self, request):
        """
        Genera reporte de productividad del taller.
        
        Calcula:
        - Total de OT cerradas en el período
        - Estadísticas por mecánico (total de OT cerradas)
        
        Parámetros:
        - fecha_inicio: Fecha de inicio del período
        - fecha_fin: Fecha de fin del período
        """
        if request.user.rol not in ("EJECUTIVO", "ADMIN", "JEFE_TALLER", "SUPERVISOR"):
            return Response(
                {"detail": "No autorizado."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Obtener parámetros de fecha
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        # Parsear fechas o usar defaults
        if fecha_inicio:
            fecha_inicio = timezone.datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
        else:
            fecha_inicio = timezone.now() - timedelta(days=30)  # Default: 30 días atrás
        
        if fecha_fin:
            fecha_fin = timezone.datetime.fromisoformat(fecha_fin.replace('Z', '+00:00'))
        else:
            fecha_fin = timezone.now()  # Default: ahora
        
        # OT cerradas en el período
        ot_cerradas = OrdenTrabajo.objects.filter(
            estado="CERRADA",
            cierre__gte=fecha_inicio,
            cierre__lte=fecha_fin
        )
        
        # Estadísticas por mecánico
        from django.db.models import DurationField, ExpressionWrapper
        estadisticas_mecanicos = User.objects.filter(
            rol="MECANICO",
            ots_responsable__in=ot_cerradas
        ).annotate(
            total_cerradas=Count('ots_responsable', filter=Q(ots_responsable__estado="CERRADA"))
        )
        
        return Response({
            "periodo": {
                "inicio": fecha_inicio.isoformat(),
                "fin": fecha_fin.isoformat(),
            },
            "total_ot_cerradas": ot_cerradas.count(),
            "estadisticas_mecanicos": [{
                "mecanico": f"{m.first_name} {m.last_name}",
                "total_cerradas": m.total_cerradas,
            } for m in estadisticas_mecanicos],
        })


class ReportePDFView(views.APIView):
    """
    Genera reportes en PDF (diario, semanal, mensual).
    
    Endpoint: GET /api/v1/reports/pdf/
    
    Permisos:
    - EJECUTIVO, ADMIN, JEFE_TALLER, SUPERVISOR, COORDINADOR_ZONA
    
    Parámetros (query):
    - tipo: Tipo de reporte ("diario", "semanal", "mensual")
    - fecha_inicio: Fecha de inicio (YYYY-MM-DD, opcional)
    - fecha_fin: Fecha de fin (YYYY-MM-DD, opcional)
    
    Retorna:
    - 200: Archivo PDF descargable
    - 400: Si el tipo es inválido
    - 403: Si no tiene permisos
    
    Tipos de reporte:
    - diario: Reporte del día (usa fecha_inicio o hoy)
    - semanal: Reporte de 7 días (usa fecha_inicio/fin o últimos 7 días)
    - mensual: Reporte de 30 días (usa fecha_inicio/fin o últimos 30 días)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        description="Genera reporte PDF según tipo (diario, semanal, mensual)",
        parameters=[
            {
                "name": "tipo",
                "in": "query",
                "required": True,
                "schema": {"type": "string", "enum": ["diario", "semanal", "mensual"]}
            },
            {
                "name": "fecha_inicio",
                "in": "query",
                "required": False,
                "schema": {"type": "string", "format": "date"}
            },
            {
                "name": "fecha_fin",
                "in": "query",
                "required": False,
                "schema": {"type": "string", "format": "date"}
            }
        ],
        responses={200: {"content": {"application/pdf": {}}}}
    )
    def get(self, request):
        """
        Genera y retorna un reporte PDF.
        
        Proceso:
        1. Valida permisos
        2. Obtiene tipo de reporte y fechas
        3. Llama al generador de PDF apropiado
        4. Retorna PDF como descarga
        
        Tipos soportados:
        - diario: Reporte de un día
        - semanal: Reporte de 7 días
        - mensual: Reporte de 30 días
        """
        if request.user.rol not in ("EJECUTIVO", "ADMIN", "JEFE_TALLER", "SUPERVISOR", "COORDINADOR_ZONA"):
            return Response(
                {"detail": "No autorizado."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        tipo = request.query_params.get("tipo", "semanal")
        fecha_inicio_str = request.query_params.get("fecha_inicio")
        fecha_fin_str = request.query_params.get("fecha_fin")
        
        from .pdf_generator import generar_reporte_semanal_pdf, generar_reporte_diario_pdf
        from datetime import datetime, timedelta
        
        if tipo == "diario":
            # Reporte diario
            fecha = None
            if fecha_inicio_str:
                fecha = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
            pdf_bytes = generar_reporte_diario_pdf(fecha)
            filename = f"reporte_diario_{fecha or timezone.now().date()}.pdf"
        
        elif tipo == "semanal":
            # Reporte semanal (7 días)
            fecha_inicio = None
            fecha_fin = None
            if fecha_inicio_str:
                fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
            if fecha_fin_str:
                fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
            if not fecha_inicio:
                # Default: últimos 7 días
                fecha_fin = timezone.now().date()
                fecha_inicio = fecha_fin - timedelta(days=7)
            pdf_bytes = generar_reporte_semanal_pdf(fecha_inicio, fecha_fin)
            filename = f"reporte_semanal_{fecha_inicio}_al_{fecha_fin}.pdf"
        
        elif tipo == "mensual":
            # Reporte mensual (30 días)
            fecha_inicio = None
            fecha_fin = None
            if fecha_inicio_str:
                fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
            if fecha_fin_str:
                fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
            if not fecha_inicio:
                # Default: últimos 30 días
                fecha_fin = timezone.now().date()
                fecha_inicio = fecha_fin - timedelta(days=30)
            pdf_bytes = generar_reporte_semanal_pdf(fecha_inicio, fecha_fin)  # Usa generador semanal con 30 días
            filename = f"reporte_mensual_{fecha_inicio}_al_{fecha_fin}.pdf"
        
        else:
            return Response(
                {"detail": "Tipo de reporte inválido. Use: diario, semanal o mensual"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Retornar PDF como descarga
        from django.http import HttpResponse
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class ReportePausasView(views.APIView):
    """
    Reporte de pausas por OT y mecánico.
    
    Endpoint: GET /api/v1/reports/pausas/
    
    Permisos:
    - EJECUTIVO, ADMIN, JEFE_TALLER, SUPERVISOR
    
    Retorna:
    - 200: {
        "pausas_activas": [...],
        "pausas_por_motivo": [...],
        "total_pausas_activas": 5
      }
    - 403: Si no tiene permisos
    
    Incluye:
    - Pausas activas (sin fecha de fin)
    - Pausas completadas con duración
    - Agrupación por motivo con duración promedio
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        description="Genera reporte de pausas",
        responses={200: None}
    )
    def get(self, request):
        """
        Genera reporte de pausas.
        
        Calcula:
        - Pausas activas (sin fecha de fin)
        - Pausas completadas con duración
        - Agrupación por motivo con estadísticas
        
        Retorna:
        - Array de pausas activas
        - Estadísticas por motivo
        - Total de pausas activas
        """
        if request.user.rol not in ("EJECUTIVO", "ADMIN", "JEFE_TALLER", "SUPERVISOR"):
            return Response(
                {"detail": "No autorizado."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Pausas activas (sin fin)
        pausas_activas = Pausa.objects.filter(fin__isnull=True).select_related('ot', 'usuario')
        
        # Pausas completadas con duración
        pausas_completadas = Pausa.objects.filter(
            fin__isnull=False
        ).annotate(
            duracion=F('fin') - F('inicio')
        ).select_related('ot', 'usuario')
        
        # Agrupar por motivo
        pausas_por_motivo = Pausa.objects.values('motivo').annotate(
            total=Count('id'),
            duracion_promedio=Avg(F('fin') - F('inicio'), filter=Q(fin__isnull=False))
        )
        
        return Response({
            "pausas_activas": [{
                "id": str(p.id),
                "ot_id": str(p.ot.id),
                "usuario": f"{p.usuario.first_name} {p.usuario.last_name}",
                "motivo": p.motivo,
                "inicio": p.inicio.isoformat(),
            } for p in pausas_activas],
            "pausas_por_motivo": list(pausas_por_motivo),
            "total_pausas_activas": pausas_activas.count(),
        })
