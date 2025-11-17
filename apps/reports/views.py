# apps/reports/views.py
from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
from drf_spectacular.utils import extend_schema

from apps.workorders.models import OrdenTrabajo, Pausa
from apps.vehicles.models import Vehiculo
from apps.users.models import User
from apps.inventory.models import SolicitudRepuesto, MovimientoStock


class DashboardEjecutivoView(views.APIView):
    """Dashboard con KPIs para el ejecutivo (Alexis González)"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        description="Obtiene todos los KPIs del dashboard ejecutivo",
        responses={200: None}
    )
    def get(self, request):
        """Retorna todos los KPIs requeridos para el dashboard ejecutivo"""
        
        # Verificar que el usuario tenga rol EJECUTIVO, ADMIN o SPONSOR
        if request.user.rol not in ("EJECUTIVO", "ADMIN", "SPONSOR"):
            return Response(
                {"detail": "No autorizado para ver el dashboard ejecutivo."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Intentar obtener del cache (válido por 2 minutos)
        cache_key = "dashboard_ejecutivo_kpis"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        hoy = timezone.now().date()
        inicio_dia = timezone.make_aware(timezone.datetime.combine(hoy, timezone.datetime.min.time()))
        
        # KPIs de OT
        ot_abiertas = OrdenTrabajo.objects.filter(estado="ABIERTA").count()
        ot_en_diagnostico = OrdenTrabajo.objects.filter(estado="EN_DIAGNOSTICO").count()
        ot_en_ejecucion = OrdenTrabajo.objects.filter(estado="EN_EJECUCION").count()
        ot_en_pausa = OrdenTrabajo.objects.filter(estado="EN_PAUSA").count()
        ot_en_qa = OrdenTrabajo.objects.filter(estado="EN_QA").count()
        ot_retrabajo = OrdenTrabajo.objects.filter(estado="RETRABAJO").count()
        ot_cerradas_hoy = OrdenTrabajo.objects.filter(
            estado="CERRADA",
            cierre__date=hoy
        ).count()
        
        # Últimas 5 OT
        ultimas_5_ot = OrdenTrabajo.objects.select_related(
            'vehiculo', 'responsable'
        ).order_by('-apertura')[:5]
        ultimas_5_ot_data = [{
            "id": str(ot.id),
            "patente": ot.vehiculo.patente if ot.vehiculo else "N/A",
            "estado": ot.estado,
            "responsable": f"{ot.responsable.first_name} {ot.responsable.last_name}" if ot.responsable else "Sin responsable",
            "apertura": ot.apertura.isoformat(),
            "tipo": ot.tipo if hasattr(ot, 'tipo') else None,
        } for ot in ultimas_5_ot]
        
        # Total vehículos en taller (EN_ESPERA o EN_MANTENIMIENTO)
        vehiculos_en_taller = Vehiculo.objects.filter(
            estado__in=["EN_ESPERA", "EN_MANTENIMIENTO"]
        ).count()
        
        # Productividad del taller (OT cerradas en los últimos 7 días)
        hace_7_dias = hoy - timedelta(days=7)
        ot_cerradas_7_dias = OrdenTrabajo.objects.filter(
            estado="CERRADA",
            cierre__date__gte=hace_7_dias
        ).count()
        
        # Pausas más frecuentes
        pausas_frecuentes = Pausa.objects.values('motivo').annotate(
            cantidad=Count('id')
        ).order_by('-cantidad')[:5]
        
        # Mecánicos con más carga de trabajo
        mecanicos_carga = User.objects.filter(
            rol="MECANICO",
            ots_responsable__estado__in=["ABIERTA", "EN_EJECUCION", "EN_PAUSA"]
        ).annotate(
            total_ots=Count('ots_responsable')
        ).order_by('-total_ots')[:5]
        mecanicos_carga_data = [{
            "id": m.id,
            "nombre": f"{m.first_name} {m.last_name}",
            "total_ots": m.total_ots
        } for m in mecanicos_carga]
        
        # Tiempos promedio por estado
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
        
        # Guardar en cache por 2 minutos
        cache.set(cache_key, response_data, 120)
        
        return Response(response_data)


class ReporteProductividadView(views.APIView):
    """Reporte de productividad del taller"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        description="Genera reporte de productividad",
        responses={200: None}
    )
    def get(self, request):
        if request.user.rol not in ("EJECUTIVO", "ADMIN", "JEFE_TALLER", "SUPERVISOR"):
            return Response(
                {"detail": "No autorizado."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Parámetros de fecha
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        if fecha_inicio:
            fecha_inicio = timezone.datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
        else:
            fecha_inicio = timezone.now() - timedelta(days=30)
        
        if fecha_fin:
            fecha_fin = timezone.datetime.fromisoformat(fecha_fin.replace('Z', '+00:00'))
        else:
            fecha_fin = timezone.now()
        
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
    """Genera reportes en PDF (diario, semanal, mensual)"""
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
            fecha = None
            if fecha_inicio_str:
                fecha = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
            pdf_bytes = generar_reporte_diario_pdf(fecha)
            filename = f"reporte_diario_{fecha or timezone.now().date()}.pdf"
        
        elif tipo == "semanal":
            fecha_inicio = None
            fecha_fin = None
            if fecha_inicio_str:
                fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
            if fecha_fin_str:
                fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
            if not fecha_inicio:
                fecha_fin = timezone.now().date()
                fecha_inicio = fecha_fin - timedelta(days=7)
            pdf_bytes = generar_reporte_semanal_pdf(fecha_inicio, fecha_fin)
            filename = f"reporte_semanal_{fecha_inicio}_al_{fecha_fin}.pdf"
        
        elif tipo == "mensual":
            # Para mensual, usamos el generador semanal con rango de 30 días
            fecha_inicio = None
            fecha_fin = None
            if fecha_inicio_str:
                fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
            if fecha_fin_str:
                fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
            if not fecha_inicio:
                fecha_fin = timezone.now().date()
                fecha_inicio = fecha_fin - timedelta(days=30)
            pdf_bytes = generar_reporte_semanal_pdf(fecha_inicio, fecha_fin)
            filename = f"reporte_mensual_{fecha_inicio}_al_{fecha_fin}.pdf"
        
        else:
            return Response(
                {"detail": "Tipo de reporte inválido. Use: diario, semanal o mensual"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.http import HttpResponse
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class ReportePausasView(views.APIView):
    """Reporte de pausas por OT y mecánico"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        description="Genera reporte de pausas",
        responses={200: None}
    )
    def get(self, request):
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

