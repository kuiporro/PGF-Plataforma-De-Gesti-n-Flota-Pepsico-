# 🧪 Plan de Pruebas Robusto - PGF PepsiCo

Este documento describe el plan completo de pruebas para el sistema PGF, incluyendo pruebas unitarias, de integración, end-to-end y de rendimiento.

## 📋 Índice

1. [Estrategia de Pruebas](#estrategia-de-pruebas)
2. [Pruebas Unitarias](#pruebas-unitarias)
3. [Pruebas de Integración](#pruebas-de-integración)
4. [Pruebas End-to-End](#pruebas-end-to-end)
5. [Pruebas de Rendimiento](#pruebas-de-rendimiento)
6. [Pruebas de Seguridad](#pruebas-de-seguridad)
7. [Pruebas de Usabilidad](#pruebas-de-usabilidad)
8. [Checklist de Pruebas Manuales](#checklist-de-pruebas-manuales)

## 🎯 Estrategia de Pruebas

### Objetivos

- **Cobertura**: Al menos 80% de código cubierto
- **Calidad**: Todas las funcionalidades críticas probadas
- **Rendimiento**: Sistema capaz de manejar 100+ usuarios concurrentes
- **Seguridad**: Todas las vulnerabilidades conocidas mitigadas

### Tipos de Pruebas

1. **Unitarias**: Funciones y métodos individuales
2. **Integración**: Interacción entre componentes
3. **E2E**: Flujos completos de usuario
4. **Rendimiento**: Carga y estrés
5. **Seguridad**: Autenticación, autorización, validación
6. **Usabilidad**: UX/UI

## 🔬 Pruebas Unitarias

### Backend (Django)

#### 1. Modelos

```python
# apps/users/tests/test_models.py
- test_user_creation()
- test_user_rut_validation()
- test_user_email_unique()
- test_user_rol_choices()
- test_user_str_representation()

# apps/vehicles/tests/test_models.py
- test_vehiculo_creation()
- test_vehiculo_patente_unique()
- test_vehiculo_estado_transitions()
- test_ingreso_vehiculo_creation()

# apps/workorders/tests/test_models.py
- test_orden_trabajo_creation()
- test_orden_trabajo_estado_transitions()
- test_itemot_creation()
- test_pausa_creation()
- test_pausa_duracion_calculation()
```

#### 2. Serializers

```python
# apps/users/tests/test_serializers.py
- test_user_serializer_creation()
- test_user_serializer_validation()
- test_login_serializer_valid_credentials()
- test_login_serializer_invalid_credentials()
- test_login_serializer_inactive_user()

# apps/workorders/tests/test_serializers.py
- test_orden_trabajo_serializer()
- test_itemot_serializer()
- test_pausa_serializer()
```

#### 3. Views y ViewSets

```python
# apps/users/tests/test_views.py
- test_user_list_requires_authentication()
- test_user_list_admin_access()
- test_user_create()
- test_user_update()
- test_user_delete()
- test_login_view()
- test_password_reset_request()
- test_password_reset_confirm()
- test_change_password()
- test_admin_change_password()

# apps/workorders/tests/test_views.py
- test_orden_trabajo_list()
- test_orden_trabajo_create()
- test_orden_trabajo_diagnostico()
- test_orden_trabajo_aprobar_asignacion()
- test_orden_trabajo_retrabajo()
- test_orden_trabajo_transitions()
```

#### 4. Servicios

```python
# apps/workorders/tests/test_services.py
- test_can_transition_valid()
- test_can_transition_invalid()
- test_do_transition_success()
- test_do_transition_failure()
- test_transition_updates_dates()
```

#### 5. Permisos

```python
# apps/users/tests/test_permissions.py
- test_user_permission_admin()
- test_user_permission_supervisor()
- test_user_permission_regular_user()
- test_user_permission_own_object()
```

### Frontend (Next.js/React)

#### 1. Componentes

```typescript
// src/components/__tests__/Sidebar.test.tsx
- test_renders_correctly()
- test_shows_menu_items_based_on_role()
- test_active_link_highlighting()
- test_mobile_menu_toggle()

// src/components/__tests__/Topbar.test.tsx
- test_renders_user_info()
- test_logout_functionality()
- test_change_password_link()

// src/components/__tests__/RoleGuard.test.tsx
- test_allows_access_with_correct_role()
- test_denies_access_with_incorrect_role()
- test_redirects_to_login_when_not_authenticated()
```

#### 2. Hooks

```typescript
// src/hooks/__tests__/useAuth.test.ts
- test_login_success()
- test_login_failure()
- test_logout()
- test_refresh_token()
- test_hasRole()

// src/hooks/__tests__/useWorkOrders.test.ts
- test_fetch_work_orders()
- test_create_work_order()
- test_update_work_order()
- test_delete_work_order()
```

#### 3. Utilidades

```typescript
// src/lib/__tests__/utils.test.ts
- test_formatDate()
- test_formatCurrency()
- test_validateRUT()
- test_validateEmail()
```

## 🔗 Pruebas de Integración

### Backend

#### 1. API Endpoints

```python
# tests/integration/test_api_endpoints.py
- test_user_crud_flow()
- test_vehicle_crud_flow()
- test_work_order_complete_flow()
- test_emergency_complete_flow()
- test_scheduling_complete_flow()
- test_report_generation()
```

#### 2. Autenticación

```python
# tests/integration/test_authentication.py
- test_jwt_token_flow()
- test_refresh_token_flow()
- test_password_reset_flow()
- test_role_based_access()
```

#### 3. Celery Tasks

```python
# tests/integration/test_celery_tasks.py
- test_colacion_automatica_task()
- test_pdf_generation_task()
- test_email_sending_task()
```

### Frontend

#### 1. API Integration

```typescript
// tests/integration/api.test.ts
- test_proxy_routes()
- test_authentication_flow()
- test_error_handling()
- test_pagination()
```

#### 2. Form Submissions

```typescript
// tests/integration/forms.test.ts
- test_user_creation_form()
- test_vehicle_creation_form()
- test_work_order_creation_form()
- test_form_validation()
- test_form_error_handling()
```

## 🎭 Pruebas End-to-End

### Flujos Críticos

#### 1. Flujo Completo de OT

```
1. Login como Admin
2. Crear vehículo
3. Crear OT para el vehículo
4. Login como Jefe de Taller
5. Realizar diagnóstico
6. Login como Supervisor
7. Aprobar asignación y asignar mecánico
8. Login como Mecánico
9. Iniciar ejecución
10. Crear pausa
11. Finalizar pausa
12. Enviar a QA
13. Login como Supervisor
14. Cerrar OT
15. Verificar OT cerrada
```

#### 2. Flujo de Emergencia

```
1. Login como Coordinador
2. Crear emergencia
3. Login como Jefe de Taller
4. Aprobar emergencia
5. Login como Supervisor
6. Asignar mecánico
7. Login como Mecánico
8. Marcar como resuelta
9. Login como Supervisor
10. Cerrar emergencia
11. Verificar OT asociada cerrada
```

#### 3. Flujo de Programación

```
1. Login como Coordinador
2. Crear programación
3. Verificar cupos disponibles
4. Confirmar programación
5. Simular ingreso de vehículo
6. Verificar OT creada automáticamente
7. Verificar vinculación con agenda
```

#### 4. Flujo de Reportes

```
1. Login como Ejecutivo
2. Acceder a dashboard ejecutivo
3. Verificar KPIs
4. Generar reporte diario
5. Descargar PDF
6. Generar reporte semanal
7. Descargar PDF
8. Generar reporte mensual
9. Descargar PDF
```

## ⚡ Pruebas de Rendimiento

### Backend

#### 1. Carga de API

```python
# tests/performance/test_api_load.py
- test_user_list_with_1000_users()
- test_work_order_list_with_500_ots()
- test_dashboard_ejecutivo_response_time()
- test_pdf_generation_performance()
```

#### 2. Base de Datos

```python
# tests/performance/test_database.py
- test_query_optimization()
- test_index_usage()
- test_bulk_operations()
```

#### 3. Celery

```python
# tests/performance/test_celery.py
- test_concurrent_task_execution()
- test_task_queue_handling()
```

### Frontend

#### 1. Carga de Páginas

```typescript
// tests/performance/pages.test.ts
- test_dashboard_load_time()
- test_work_orders_list_load_time()
- test_large_data_rendering()
```

#### 2. Optimización

```typescript
// tests/performance/optimization.test.ts
- test_code_splitting()
- test_lazy_loading()
- test_image_optimization()
```

## 🔒 Pruebas de Seguridad

### Autenticación

- [ ] Login con credenciales válidas
- [ ] Login con credenciales inválidas
- [ ] Login con usuario inactivo
- [ ] Token JWT expira correctamente
- [ ] Refresh token funciona
- [ ] Logout invalida tokens

### Autorización

- [ ] Usuario no puede acceder a rutas protegidas sin autenticación
- [ ] Usuario solo ve datos según su rol
- [ ] Admin puede acceder a todo
- [ ] Supervisor tiene permisos correctos
- [ ] Mecánico solo ve sus OTs asignadas

### Validación

- [ ] RUT válido e inválido
- [ ] Email válido e inválido
- [ ] Contraseña cumple requisitos
- [ ] SQL Injection prevenido
- [ ] XSS prevenido
- [ ] CSRF protegido

### Datos Sensibles

- [ ] Contraseñas no se exponen en logs
- [ ] Tokens no se exponen en URLs
- [ ] Datos personales encriptados

## 🎨 Pruebas de Usabilidad

### Navegación

- [ ] Menú lateral funciona correctamente
- [ ] Breadcrumbs son claros
- [ ] Botones de acción son visibles
- [ ] Links funcionan correctamente

### Formularios

- [ ] Validación en tiempo real
- [ ] Mensajes de error claros
- [ ] Campos requeridos marcados
- [ ] Autocompletado funciona

### Responsive

- [ ] Funciona en desktop (1920x1080)
- [ ] Funciona en tablet (768x1024)
- [ ] Funciona en móvil (375x667)
- [ ] Menú móvil funciona

### Accesibilidad

- [ ] Contraste de colores adecuado
- [ ] Navegación por teclado funciona
- [ ] Screen readers compatibles
- [ ] ARIA labels presentes

## ✅ Checklist de Pruebas Manuales

### Autenticación

- [ ] Login con usuario válido
- [ ] Login con usuario inválido
- [ ] Logout funciona
- [ ] Recuperación de contraseña
- [ ] Cambio de contraseña
- [ ] Admin cambia contraseña de otro usuario

### Usuarios

- [ ] Listar usuarios
- [ ] Crear usuario
- [ ] Editar usuario
- [ ] Eliminar usuario
- [ ] Validación de RUT
- [ ] Validación de email
- [ ] Filtros y búsqueda

### Vehículos

- [ ] Listar vehículos
- [ ] Crear vehículo
- [ ] Editar vehículo
- [ ] Eliminar vehículo
- [ ] Ingreso al taller
- [ ] Salida del taller
- [ ] Cargar evidencias

### Órdenes de Trabajo

- [ ] Crear OT
- [ ] Realizar diagnóstico
- [ ] Aprobar asignación
- [ ] Asignar mecánico
- [ ] Iniciar ejecución
- [ ] Crear pausa
- [ ] Finalizar pausa
- [ ] Enviar a QA
- [ ] Marcar retrabajo
- [ ] Cerrar OT
- [ ] Ver historial

### Choferes

- [ ] Listar choferes
- [ ] Crear chofer
- [ ] Editar chofer
- [ ] Asignar vehículo
- [ ] Ver historial de asignaciones

### Programación

- [ ] Crear programación
- [ ] Editar programación
- [ ] Verificar cupos
- [ ] Confirmar programación
- [ ] Cancelar programación

### Emergencias

- [ ] Crear emergencia
- [ ] Aprobar emergencia
- [ ] Asignar mecánico
- [ ] Resolver emergencia
- [ ] Cerrar emergencia

### Reportes

- [ ] Dashboard ejecutivo carga
- [ ] KPIs se muestran correctamente
- [ ] Generar reporte diario
- [ ] Generar reporte semanal
- [ ] Generar reporte mensual
- [ ] PDFs se descargan correctamente

## 📊 Métricas de Éxito

### Cobertura de Código

- **Objetivo**: 80%+
- **Backend**: pytest-cov
- **Frontend**: Jest coverage

### Tiempo de Respuesta

- **API**: < 200ms (p95)
- **Páginas**: < 2s (carga inicial)
- **PDFs**: < 5s (generación)

### Errores

- **Tasa de error**: < 0.1%
- **Errores críticos**: 0

## 🛠️ Herramientas de Pruebas

### Backend

- **pytest**: Framework de pruebas
- **pytest-django**: Plugin para Django
- **pytest-cov**: Cobertura de código
- **factory-boy**: Fixtures de datos
- **faker**: Datos de prueba

### Frontend

- **Jest**: Framework de pruebas
- **React Testing Library**: Pruebas de componentes
- **Playwright**: Pruebas E2E
- **Lighthouse**: Rendimiento

### Integración

- **Postman/Insomnia**: Pruebas de API
- **Selenium**: Pruebas E2E (alternativa)

## 📝 Ejecutar Pruebas

### Backend

```bash
# Todas las pruebas
docker-compose exec api poetry run pytest

# Con cobertura
docker-compose exec api poetry run pytest --cov=apps --cov-report=html

# Pruebas específicas
docker-compose exec api poetry run pytest apps/users/tests/

# Con verbose
docker-compose exec api poetry run pytest -v
```

### Frontend

```bash
# Todas las pruebas
cd frontend/pgf-frontend
npm test

# Con cobertura
npm test -- --coverage

# Watch mode
npm test -- --watch

# Pruebas E2E
npm run test:e2e
```

## 🎯 Próximos Pasos

1. **Implementar pruebas unitarias** para modelos críticos
2. **Implementar pruebas de integración** para flujos principales
3. **Configurar CI/CD** para ejecutar pruebas automáticamente
4. **Implementar pruebas E2E** con Playwright
5. **Configurar monitoreo** de rendimiento en producción

---

**Nota**: Este plan es un documento vivo y debe actualizarse conforme se implementen las pruebas y se descubran nuevos casos de prueba.

