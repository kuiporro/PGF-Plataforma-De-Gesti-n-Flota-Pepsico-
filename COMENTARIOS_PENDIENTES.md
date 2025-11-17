# 📝 Archivos Pendientes de Comentar

Este documento lista los archivos que aún necesitan comentarios detallados.

## ✅ Archivos Ya Comentados

### Backend
- ✅ `apps/users/models.py` - Modelos User, Profile, PasswordResetToken
- ✅ `apps/workorders/services.py` - Transiciones de estado
- ✅ `apps/users/views.py` - Todas las vistas de usuarios y autenticación

### Frontend
- ✅ `frontend/src/store/auth.ts` - Store de autenticación Zustand
- ✅ `frontend/src/app/api/proxy/utils.ts` - Utilidades de proxy
- ✅ `frontend/src/middleware.ts` - Middleware de protección de rutas
- ✅ `frontend/src/components/RoleGuard.tsx` - Componente de protección por roles

## ⏳ Archivos Pendientes (Prioridad Alta)

### Backend

#### Modelos
- [ ] `apps/workorders/models.py` - OrdenTrabajo, ItemOT, Pausa, Evidencia, etc.
- [ ] `apps/vehicles/models.py` - Vehiculo, IngresoVehiculo, EvidenciaIngreso
- [ ] `apps/drivers/models.py` - Chofer, HistorialAsignacionVehiculo
- [ ] `apps/scheduling/models.py` - Agenda, CupoDiario
- [ ] `apps/emergencies/models.py` - EmergenciaRuta

#### Vistas
- [ ] `apps/workorders/views.py` - OrdenTrabajoViewSet y acciones
- [ ] `apps/vehicles/views.py` - VehiculoViewSet
- [ ] `apps/drivers/views.py` - ChoferViewSet
- [ ] `apps/scheduling/views.py` - AgendaViewSet, CupoDiarioViewSet
- [ ] `apps/emergencies/views.py` - EmergenciaRutaViewSet
- [ ] `apps/reports/views.py` - DashboardEjecutivoView, ReportePDFView

#### Serializers
- [ ] `apps/users/serializers.py` - Todos los serializers
- [ ] `apps/workorders/serializers.py` - Serializers de OT
- [ ] `apps/vehicles/serializers.py` - Serializers de vehículos

#### Servicios y Tareas
- [ ] `apps/workorders/tasks_colacion.py` - Tareas Celery para colación
- [ ] `apps/workorders/tasks.py` - Otras tareas Celery
- [ ] `apps/reports/pdf_generator.py` - Generación de PDFs

### Frontend

#### Componentes Principales
- [ ] `frontend/src/components/Sidebar.tsx` - Menú lateral
- [ ] `frontend/src/components/Topbar.tsx` - Barra superior
- [ ] `frontend/src/components/Pagination.tsx` - Componente de paginación
- [ ] `frontend/src/components/ToastContainer.tsx` - Sistema de notificaciones

#### Páginas Críticas
- [ ] `frontend/src/app/auth/login/page.tsx` - Página de login
- [ ] `frontend/src/app/dashboard/ejecutivo/page.tsx` - Dashboard ejecutivo
- [ ] `frontend/src/app/workorders/page.tsx` - Listado de OT
- [ ] `frontend/src/app/workorders/[id]/page.tsx` - Detalle de OT
- [ ] `frontend/src/app/users/page.tsx` - Listado de usuarios
- [ ] `frontend/src/app/vehicles/page.tsx` - Listado de vehículos

#### Hooks
- [ ] `frontend/src/hooks/useWorkOrders.ts` - Hook para OT
- [ ] `frontend/src/hooks/useVehicles.ts` - Hook para vehículos
- [ ] `frontend/src/hooks/useUsers.ts` - Hook para usuarios

#### API Routes
- [ ] `frontend/src/app/api/auth/login/route.ts` - Login API route
- [ ] `frontend/src/app/api/auth/me/route.ts` - Obtener usuario actual
- [ ] `frontend/src/app/api/proxy/work/ordenes/route.ts` - Proxy de OT

## 📋 Prioridad de Comentarios

### Fase 1 (Crítico - Hacer primero)
1. `apps/workorders/models.py` - Modelo central del sistema
2. `apps/workorders/views.py` - Lógica de negocio de OT
3. `apps/vehicles/models.py` - Modelo de vehículos
4. `frontend/src/app/workorders/page.tsx` - Página principal de OT
5. `frontend/src/components/Sidebar.tsx` - Navegación principal

### Fase 2 (Importante)
6. `apps/vehicles/views.py` - Gestión de vehículos
7. `apps/drivers/views.py` - Gestión de choferes
8. `apps/scheduling/views.py` - Programación
9. `apps/emergencies/views.py` - Emergencias
10. `apps/reports/views.py` - Reportes

### Fase 3 (Completar)
11. Todos los serializers
12. Todas las páginas de frontend
13. Todos los hooks
14. Todas las API routes

## 🎯 Estrategia

1. **Comentar modelos primero** - Son la base de datos, todo depende de ellos
2. **Comentar vistas después** - Implementan la lógica de negocio
3. **Comentar frontend por último** - Depende del backend

## 📝 Formato de Comentarios

Cada archivo debe tener:
- **Docstring del módulo**: Qué hace el módulo, relaciones principales
- **Docstring de clases**: Qué hace la clase, relaciones
- **Docstring de funciones**: Qué hace, parámetros, retornos, ejemplos
- **Comentarios inline**: Explicar lógica compleja o no obvia

---

**Nota**: Este es un documento vivo. Se actualizará conforme se completen los comentarios.

