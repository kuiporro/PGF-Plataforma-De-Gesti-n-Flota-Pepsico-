# 📚 Referencia Completa de Endpoints - API PGF

Esta guía contiene todos los endpoints disponibles en la API de PGF (Plataforma de Gestión de Flota).

**Base URL:** `http://localhost:8000` (desarrollo)  
**Versión API:** `api/v1`

---

## 🔐 Autenticación

### POST `/api/v1/auth/login/`
Iniciar sesión y obtener tokens JWT.

**Body:**
```json
{
    "username": "admin",
    "password": "password123"
}
```

**Response 200:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
        "id": "...",
        "username": "admin",
        "email": "...",
        "rol": "ADMIN"
    }
}
```

**Cookies:** Se establecen `pgf_access` y `pgf_refresh` automáticamente.

---

### POST `/api/v1/auth/refresh/`
Refrescar token de acceso usando refresh token de las cookies.

**Response 200:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### GET `/api/v1/users/me/`
Obtener información del usuario autenticado.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response 200:**
```json
{
    "id": "...",
    "username": "admin",
    "email": "...",
    "first_name": "...",
    "last_name": "...",
    "rol": "ADMIN",
    "rut": "..."
}
```

---

### POST `/api/v1/auth/password-reset/`
Solicitar reset de contraseña por email.

**Body:**
```json
{
    "email": "usuario@example.com"
}
```

---

### POST `/api/v1/auth/password-reset/confirm/`
Confirmar reset de contraseña con token.

**Body:**
```json
{
    "token": "token-del-email",
    "new_password": "nuevaPassword123",
    "confirm_password": "nuevaPassword123"
}
```

---

### POST `/api/v1/auth/change-password/`
Cambiar contraseña del usuario autenticado.

**Body:**
```json
{
    "current_password": "passwordActual",
    "new_password": "nuevaPassword123",
    "confirm_password": "nuevaPassword123"
}
```

---

## 👥 Usuarios

### GET `/api/v1/users/`
Listar usuarios (paginado).

**Query Params:**
- `page`: Número de página (default: 1)
- `page_size`: Tamaño de página (default: 20)
- `rol`: Filtrar por rol
- `search`: Búsqueda por nombre, email, username

**Response 200:**
```json
{
    "count": 100,
    "next": "http://...?page=2",
    "previous": null,
    "results": [...]
}
```

---

### POST `/api/v1/users/`
Crear un nuevo usuario.

**Body:**
```json
{
    "username": "nuevo_usuario",
    "email": "usuario@example.com",
    "password": "password123",
    "first_name": "Nombre",
    "last_name": "Apellido",
    "rol": "MECANICO",
    "rut": "123456789"
}
```

**Roles disponibles:** `ADMIN`, `SUPERVISOR`, `MECANICO`, `JEFE_TALLER`, `GUARDIA`, `SPONSOR`, `EJECUTIVO`, `COORDINADOR_ZONA`

---

### GET `/api/v1/users/{id}/`
Obtener detalles de un usuario.

---

### PATCH `/api/v1/users/{id}/`
Actualizar información de un usuario.

**Body:**
```json
{
    "first_name": "Nombre Actualizado",
    "email": "nuevo@example.com"
}
```

---

### DELETE `/api/v1/users/{id}/`
Eliminar un usuario.

---

### POST `/api/v1/users/{user_id}/change-password/`
Admin cambia contraseña de otro usuario.

**Body:**
```json
{
    "new_password": "nuevaPassword123",
    "confirm_password": "nuevaPassword123"
}
```

---

## 🚗 Vehículos

### GET `/api/v1/vehicles/`
Listar vehículos.

**Query Params:**
- `page`, `page_size`: Paginación
- `estado`: Filtrar por estado (`ACTIVO`, `EN_ESPERA`, `EN_MANTENIMIENTO`, `BAJA`)
- `marca`, `anio`, `tipo`, `categoria`, `zona`, `sucursal`: Filtros
- `search`: Búsqueda por patente, marca, modelo, VIN
- `ordering`: Ordenar por `patente`, `anio`, `marca`, `created_at`, `estado`

---

### POST `/api/v1/vehicles/`
Crear un nuevo vehículo.

**Body:**
```json
{
    "patente": "ABC123",
    "marca": "Toyota",
    "modelo": "Hilux",
    "anio": 2020,
    "tipo": "DIESEL",
    "categoria": "REPARTO",
    "zona": "Zona Norte",
    "sucursal": "Sucursal 1",
    "km_mensual_promedio": 5000
}
```

**Tipos:** `ELECTRICO`, `DIESEL`, `UTILITARIO`, `REPARTO`, `VENTAS`, `RESPALDO`  
**Categorías:** `REPARTO`, `VENTAS`, `RESPALDO`

---

### GET `/api/v1/vehicles/{id}/`
Obtener detalles de un vehículo.

---

### PATCH `/api/v1/vehicles/{id}/`
Actualizar información de un vehículo.

---

### DELETE `/api/v1/vehicles/{id}/`
Eliminar un vehículo.

---

### POST `/api/v1/vehicles/ingreso/`
Registrar ingreso rápido de vehículo al taller (solo GUARDIA).

**Body:**
```json
{
    "patente": "ABC123",
    "observaciones": "Vehículo con daños",
    "kilometraje": 50000,
    "motivo": "Reparación urgente",
    "prioridad": "ALTA",
    "zona": "Zona Norte"
}
```

**Response 201:**
```json
{
    "id": "...",
    "vehiculo": {...},
    "guardia": {...},
    "fecha_ingreso": "...",
    "ot_generada": {
        "id": "...",
        "estado": "ABIERTA",
        "motivo": "..."
    }
}
```

**Nota:** Crea automáticamente una OT si no existe.

---

### POST `/api/v1/vehicles/{id}/ingreso/evidencias/`
Agregar evidencia fotográfica al último ingreso.

**Body:**
```json
{
    "url": "https://s3.amazonaws.com/bucket/evidencia.jpg",
    "tipo": "FOTO_INGRESO",
    "descripcion": "Foto del vehículo al ingreso"
}
```

**Tipos:** `FOTO_INGRESO`, `FOTO_DANOS`, `FOTO_DOCUMENTOS`, `OTRO`

---

### GET `/api/v1/vehicles/{id}/historial/`
Obtener historial completo del vehículo.

**Response 200:**
```json
{
    "vehiculo": {...},
    "ordenes_trabajo": [...],
    "historial_repuestos": [...],
    "ingresos": [...],
    "total_ordenes": 10,
    "total_repuestos": 25,
    "total_ingresos": 5
}
```

---

## 🔧 Órdenes de Trabajo

### GET `/api/v1/work/ordenes/`
Listar órdenes de trabajo.

**Query Params:**
- `page`, `page_size`: Paginación
- `estado`: Filtrar por estado
- `vehiculo`: Filtrar por vehículo
- `mecanico`, `supervisor`, `responsable`: Filtrar por usuario
- `tipo`, `prioridad`, `zona`: Filtros
- `search`: Búsqueda por patente, motivo, diagnóstico
- `ordering`: Ordenar por `id`, `apertura`, `cierre`, `estado`, `prioridad`, `tipo`, `zona`

**Estados:** `ABIERTA`, `EN_DIAGNOSTICO`, `EN_EJECUCION`, `EN_PAUSA`, `EN_QA`, `RETRABAJO`, `CERRADA`, `ANULADA`

---

### POST `/api/v1/work/ordenes/`
Crear una nueva orden de trabajo.

**Body:**
```json
{
    "vehiculo": "vehicle-uuid-here",
    "tipo": "MANTENCION",
    "prioridad": "MEDIA",
    "motivo": "Mantención preventiva",
    "zona": "Zona Norte"
}
```

**Tipos:** `MANTENCION`, `REPARACION`, `EMERGENCIA`, `DIAGNOSTICO`, `OTRO`  
**Prioridades:** `CRITICA`, `ALTA`, `MEDIA`, `BAJA`

---

### GET `/api/v1/work/ordenes/{id}/`
Obtener detalles de una OT.

---

### PATCH `/api/v1/work/ordenes/{id}/`
Actualizar una OT.

---

### DELETE `/api/v1/work/ordenes/{id}/`
Eliminar una OT.

---

### POST `/api/v1/work/ordenes/{id}/diagnostico/`
Realizar diagnóstico de la OT (solo JEFE_TALLER).

**Body:**
```json
{
    "diagnostico": "Se requiere cambio de aceite y filtros"
}
```

**Estado requerido:** `ABIERTA` o `EN_DIAGNOSTICO`  
**Cambia estado a:** `EN_DIAGNOSTICO`

---

### POST `/api/v1/work/ordenes/{id}/aprobar-asignacion/`
Aprobar asignación de mecánico (solo SUPERVISOR/ADMIN/COORDINADOR_ZONA).

**Body:**
```json
{
    "mecanico_id": "mecanico-uuid-here",
    "prioridad": "ALTA"
}
```

**Estado requerido:** `EN_DIAGNOSTICO`  
**Cambia estado a:** `EN_EJECUCION`

---

### POST `/api/v1/work/ordenes/{id}/en-ejecucion/`
Cambiar estado a `EN_EJECUCION`.

**Permisos:** `SUPERVISOR`, `ADMIN`, `MECANICO`

---

### POST `/api/v1/work/ordenes/{id}/en-pausa/`
Cambiar estado a `EN_PAUSA`.

**Permisos:** `MECANICO`, `SUPERVISOR`, `ADMIN`, `JEFE_TALLER`

---

### POST `/api/v1/work/ordenes/{id}/en-qa/`
Cambiar estado a `EN_QA` (Control de Calidad).

**Permisos:** `SUPERVISOR`, `ADMIN`

---

### POST `/api/v1/work/ordenes/{id}/cerrar/`
Cerrar la OT (genera PDF automático).

**Permisos:** `SUPERVISOR`, `ADMIN`, `JEFE_TALLER`  
**Estado requerido:** `EN_QA` o `CERRADA`

**Response 200:**
```json
{
    "estado": "CERRADA",
    "cierre": "2025-11-18T10:00:00Z"
}
```

---

### POST `/api/v1/work/ordenes/{id}/anular/`
Anular la OT.

**Permisos:** `SUPERVISOR`, `ADMIN`

---

### POST `/api/v1/work/ordenes/{id}/retrabajo/`
Marcar OT como retrabajo (desde QA).

**Body:**
```json
{
    "motivo": "Requiere corrección"
}
```

**Permisos:** `SUPERVISOR`, `ADMIN`, `JEFE_TALLER`  
**Estado requerido:** `EN_QA`  
**Cambia estado a:** `RETRABAJO`

---

## 📋 Items OT

### GET `/api/v1/work/items/`
Listar items de OT.

**Query Params:**
- `ot`: Filtrar por OT
- `tipo`: Filtrar por tipo (`REPUESTO`, `SERVICIO`)

---

### POST `/api/v1/work/items/`
Crear un item en una OT.

**Body:**
```json
{
    "ot": "ot-uuid-here",
    "tipo": "REPUESTO",
    "descripcion": "Filtro de aceite",
    "cantidad": 2,
    "costo_unitario": 15000
}
```

---

### PATCH `/api/v1/work/items/{id}/`
Actualizar un item.

---

### DELETE `/api/v1/work/items/{id}/`
Eliminar un item.

---

## 💰 Presupuestos

### GET `/api/v1/work/presupuestos/`
Listar presupuestos.

**Query Params:**
- `ot`: Filtrar por OT
- `requiere_aprobacion`: Filtrar si requiere aprobación

---

### POST `/api/v1/work/presupuestos/`
Crear presupuesto con detalles.

**Body:**
```json
{
    "ot": "ot-uuid-here",
    "detalles_data": [
        {
            "concepto": "Repuestos",
            "cantidad": 2,
            "precio": 50000
        },
        {
            "concepto": "Mano de obra",
            "cantidad": 4,
            "precio": 25000
        }
    ]
}
```

**Nota:** Si el total > $1,000, se requiere aprobación automáticamente.

---

### POST `/api/v1/work/aprobaciones/{id}/aprobar/`
Aprobar un presupuesto (solo SPONSOR/ADMIN).

---

### POST `/api/v1/work/aprobaciones/{id}/rechazar/`
Rechazar un presupuesto (solo SPONSOR/ADMIN).

---

## ⏸️ Pausas

### GET `/api/v1/work/pausas/`
Listar pausas.

**Query Params:**
- `ot`: Filtrar por OT
- `usuario`: Filtrar por usuario

---

### POST `/api/v1/work/pausas/`
Crear una pausa.

**Body:**
```json
{
    "ot": "ot-uuid-here",
    "tipo": "ESPERA_REPUESTO",
    "motivo": "Esperando repuesto del proveedor"
}
```

**Tipos:** `ESPERA_REPUESTO`, `APROBACION_PENDIENTE`, `COLACION`, `OTRO`, `ADMINISTRATIVA`

**Nota:** Si es horario de colación (12:30-13:15), se marca automáticamente como `COLACION` y `es_automatica: true`.

---

### POST `/api/v1/work/pausas/{id}/reanudar/`
Reanudar una pausa.

**Permisos:** `MECANICO`, `SUPERVISOR`, `ADMIN`, `JEFE_TALLER`  
**Cambia estado de OT a:** `EN_EJECUCION` (si estaba en `EN_PAUSA`)

---

## ✅ Checklists QA

### GET `/api/v1/work/checklists/`
Listar checklists.

**Query Params:**
- `ot`: Filtrar por OT
- `resultado`: Filtrar por resultado (`OK`, `NO_OK`)

---

### POST `/api/v1/work/checklists/`
Crear un checklist de QA.

**Body:**
```json
{
    "ot": "ot-uuid-here",
    "resultado": "OK",
    "observaciones": "Todo correcto"
}
```

---

### POST `/api/v1/work/checklists/{id}/aprobar-qa/`
Aprobar QA (cierra la OT).

**Permisos:** `SUPERVISOR`, `ADMIN`, `JEFE_TALLER`  
**Estado requerido:** `EN_QA`  
**Cambia estado a:** `CERRADA`

**Body:**
```json
{
    "observaciones": "QA aprobada"
}
```

---

### POST `/api/v1/work/checklists/{id}/rechazar-qa/`
Rechazar QA (devuelve OT a EN_EJECUCION).

**Permisos:** `SUPERVISOR`, `ADMIN`, `JEFE_TALLER`  
**Estado requerido:** `EN_QA`  
**Cambia estado a:** `EN_EJECUCION`

**Body:**
```json
{
    "observaciones": "Requiere corrección"
}
```

---

## 📸 Evidencias

### GET `/api/v1/work/evidencias/`
Listar evidencias.

**Query Params:**
- `ot`: Filtrar por OT
- `tipo`: Filtrar por tipo (`FOTO`, `PDF`, `OTRO`)

---

### POST `/api/v1/work/evidencias/presigned/`
Obtener URL pre-firmada para subir archivo a S3.

**Body:**
```json
{
    "ot": "ot-uuid-here",
    "filename": "evidencia.jpg",
    "content_type": "image/jpeg",
    "file_size": 1048576
}
```

**Response 200:**
```json
{
    "upload": {
        "url": "https://s3.amazonaws.com/...",
        "fields": {...}
    },
    "file_url": "https://s3.amazonaws.com/bucket/evidencias/..."
}
```

**Límite:** 10MB por archivo (configurable)

**Proceso:**
1. Llamar este endpoint para obtener URL pre-firmada
2. Subir archivo directamente a S3 usando la URL pre-firmada
3. Llamar `POST /api/v1/work/evidencias/` con la URL del archivo

---

### POST `/api/v1/work/evidencias/`
Registrar evidencia después de subir a S3.

**Body:**
```json
{
    "ot": "ot-uuid-here",
    "url": "https://s3.amazonaws.com/bucket/evidencia.jpg",
    "tipo": "FOTO",
    "descripcion": "Foto del trabajo realizado"
}
```

---

### DELETE `/api/v1/work/evidencias/{id}/`
Eliminar una evidencia.

---

## 👨‍✈️ Choferes

### GET `/api/v1/drivers/choferes/`
Listar choferes.

**Query Params:**
- `page`, `page_size`: Paginación
- `zona`: Filtrar por zona
- `search`: Búsqueda por nombre, RUT, email

---

### POST `/api/v1/drivers/choferes/`
Crear un nuevo chofer.

**Body:**
```json
{
    "nombre_completo": "Juan Pérez",
    "rut": "123456789",
    "telefono": "+56912345678",
    "email": "juan@example.com",
    "zona": "Zona Norte"
}
```

---

### GET `/api/v1/drivers/choferes/{id}/`
Obtener detalles de un chofer.

---

### PATCH `/api/v1/drivers/choferes/{id}/`
Actualizar información de un chofer.

---

### DELETE `/api/v1/drivers/choferes/{id}/`
Eliminar un chofer.

---

### POST `/api/v1/drivers/choferes/{id}/asignar-vehiculo/`
Asignar vehículo a un chofer.

**Body:**
```json
{
    "vehiculo_id": "vehicle-uuid-here"
}
```

---

### GET `/api/v1/drivers/choferes/{id}/historial/`
Obtener historial de asignaciones del chofer.

---

## 📅 Agenda

### GET `/api/v1/scheduling/agendas/`
Listar agendas programadas.

**Query Params:**
- `page`, `page_size`: Paginación
- `estado`: Filtrar por estado (`PROGRAMADA`, `CONFIRMADA`, `EN_PROCESO`, `COMPLETADA`, `CANCELADA`)
- `vehiculo`: Filtrar por vehículo
- `fecha_programada`: Filtrar por fecha

---

### POST `/api/v1/scheduling/agendas/`
Crear una nueva agenda.

**Body:**
```json
{
    "vehiculo": "vehicle-uuid-here",
    "coordinador": "coordinador-uuid-here",
    "fecha_programada": "2025-11-20T10:00:00Z",
    "motivo": "Mantención preventiva",
    "tipo_mantenimiento": "PREVENTIVO",
    "zona": "Zona Norte"
}
```

**Tipos:** `PREVENTIVO`, `CORRECTIVO`, `INSPECCION`

---

### GET `/api/v1/scheduling/agendas/{id}/`
Obtener detalles de una agenda.

---

### PATCH `/api/v1/scheduling/agendas/{id}/`
Actualizar una agenda.

---

### DELETE `/api/v1/scheduling/agendas/{id}/`
Eliminar una agenda.

---

### POST `/api/v1/scheduling/agendas/{id}/reprogramar/`
Reprogramar una agenda.

**Body:**
```json
{
    "fecha_programada": "2025-11-25T10:00:00Z",
    "motivo": "Reprogramado por urgencia"
}
```

---

### POST `/api/v1/scheduling/agendas/{id}/cancelar/`
Cancelar una agenda.

---

### GET `/api/v1/scheduling/agendas/disponibilidad/`
Ver disponibilidad de cupos para una fecha.

**Query Params:**
- `fecha`: Fecha en formato `YYYY-MM-DD`

**Response 200:**
```json
{
    "fecha": "2025-11-20",
    "cupos_disponibles": 5,
    "cupos_ocupados": 3,
    "cupos_totales": 8
}
```

---

## 🚨 Emergencias

### GET `/api/v1/emergencies/`
Listar emergencias.

**Query Params:**
- `page`, `page_size`: Paginación
- `estado`: Filtrar por estado (`PENDIENTE`, `APROBADA`, `EN_PROCESO`, `RESUELTA`, `CERRADA`, `RECHAZADA`)
- `vehiculo`: Filtrar por vehículo
- `zona`: Filtrar por zona
- `prioridad`: Filtrar por prioridad

---

### POST `/api/v1/emergencies/`
Crear una nueva emergencia.

**Body:**
```json
{
    "vehiculo": "vehicle-uuid-here",
    "descripcion": "Avería en ruta",
    "ubicacion": "Ruta 5, km 120",
    "zona": "Zona Norte",
    "prioridad": "CRITICA"
}
```

**Prioridades:** `CRITICA`, `ALTA`, `MEDIA`, `BAJA`

---

### GET `/api/v1/emergencies/{id}/`
Obtener detalles de una emergencia.

---

### PATCH `/api/v1/emergencies/{id}/`
Actualizar una emergencia.

---

### DELETE `/api/v1/emergencies/{id}/`
Eliminar una emergencia.

---

### POST `/api/v1/emergencies/{id}/aprobar/`
Aprobar una emergencia.

**Permisos:** `SUPERVISOR`, `ADMIN`, `COORDINADOR_ZONA`

---

### POST `/api/v1/emergencies/{id}/asignar-supervisor/`
Asignar supervisor a emergencia.

**Body:**
```json
{
    "supervisor_id": "supervisor-uuid-here"
}
```

---

### POST `/api/v1/emergencies/{id}/asignar-mecanico/`
Asignar mecánico a emergencia.

**Body:**
```json
{
    "mecanico_id": "mecanico-uuid-here"
}
```

---

### POST `/api/v1/emergencies/{id}/resolver/`
Marcar emergencia como resuelta.

---

### POST `/api/v1/emergencies/{id}/cerrar/`
Cerrar una emergencia.

---

### POST `/api/v1/emergencies/{id}/rechazar/`
Rechazar una emergencia.

**Body:**
```json
{
    "motivo": "No es una emergencia real"
}
```

---

## 📊 Reportes

### GET `/api/v1/reports/dashboard-ejecutivo/`
Obtener datos del dashboard ejecutivo (KPIs).

**Permisos:** `ADMIN`, `SPONSOR`, `EJECUTIVO`

**Response 200:**
```json
{
    "ots_abiertas": 15,
    "ots_en_ejecucion": 8,
    "ots_cerradas_hoy": 3,
    "tiempo_promedio_cierre": 2.5,
    "productividad_mecanicos": [...],
    "costos_mes_actual": 1500000,
    "vehiculos_en_taller": 5
}
```

---

### GET `/api/v1/reports/productividad/`
Reporte de productividad por período.

**Query Params:**
- `fecha_inicio`: Fecha inicio (YYYY-MM-DD)
- `fecha_fin`: Fecha fin (YYYY-MM-DD)
- `mecanico`: Filtrar por mecánico (opcional)
- `zona`: Filtrar por zona (opcional)

**Response 200:**
```json
{
    "periodo": {
        "inicio": "2025-11-01",
        "fin": "2025-11-30"
    },
    "ots_cerradas": 45,
    "tiempo_promedio": 2.3,
    "productividad_por_mecanico": [...],
    "ots_por_estado": {...}
}
```

---

### GET `/api/v1/reports/pausas/`
Reporte de pausas por período.

**Query Params:**
- `fecha_inicio`: Fecha inicio (YYYY-MM-DD)
- `fecha_fin`: Fecha fin (YYYY-MM-DD)
- `tipo`: Filtrar por tipo de pausa (opcional)
- `ot`: Filtrar por OT (opcional)

**Response 200:**
```json
{
    "periodo": {
        "inicio": "2025-11-01",
        "fin": "2025-11-30"
    },
    "total_pausas": 120,
    "pausas_por_tipo": {...},
    "duracion_promedio": 45,
    "pausas_por_ot": [...]
}
```

---

### POST `/api/v1/reports/pdf/`
Generar PDF de reporte.

**Body:**
```json
{
    "tipo": "cierre_ot",
    "ot_id": "ot-uuid-here"
}
```

**Tipos:** `cierre_ot`, `productividad`, `pausas`, `dashboard`

**Response 200:**
- Content-Type: `application/pdf`
- Headers: `Content-Disposition: attachment; filename="reporte.pdf"`

---

## 🔒 Autenticación en Requests

Para la mayoría de los endpoints (excepto login y password reset), se requiere autenticación:

**Opción 1: Bearer Token (Header)**
```
Authorization: Bearer {access_token}
```

**Opción 2: Cookies (si se usa desde el frontend)**
Las cookies `pgf_access` y `pgf_refresh` se establecen automáticamente después del login.

---

## 📝 Notas Importantes

1. **UUIDs:** Todos los IDs son UUIDs (formato: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

2. **Paginación:** La mayoría de listados usan paginación estándar de DRF:
   - `count`: Total de resultados
   - `next`: URL de siguiente página (null si no hay)
   - `previous`: URL de página anterior (null si no hay)
   - `results`: Array de resultados

3. **Filtros:** Muchos endpoints soportan filtros múltiples combinados con `&`

4. **Ordenamiento:** Usar `ordering` query param con `-` para descendente (ej: `ordering=-created_at`)

5. **Búsqueda:** Usar `search` query param para búsqueda de texto en múltiples campos

6. **Estados y Transiciones:** Los estados de OT tienen transiciones específicas. Ver documentación de cada endpoint.

7. **Permisos:** Cada endpoint tiene permisos específicos por rol. Ver descripción de cada endpoint.

---

## 🚀 Próximas Funcionalidades

- [ ] Subida de evidencias hasta 3GB
- [ ] Reportes semanales y mensuales automáticos
- [ ] Botón de reporte diario para ADMIN/SPONSOR/JEFE_TALLER
- [ ] Soporte para hojas de cálculo y más tipos de archivo

---

**Última actualización:** 2025-11-18

