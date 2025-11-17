# apps/reports/urls.py
from django.urls import path
from .views import (
    DashboardEjecutivoView,
    ReporteProductividadView,
    ReportePausasView,
    ReportePDFView
)

urlpatterns = [
    path('dashboard-ejecutivo/', DashboardEjecutivoView.as_view(), name='dashboard-ejecutivo'),
    path('productividad/', ReporteProductividadView.as_view(), name='reporte-productividad'),
    path('pausas/', ReportePausasView.as_view(), name='reporte-pausas'),
    path('pdf/', ReportePDFView.as_view(), name='reporte-pdf'),
]

