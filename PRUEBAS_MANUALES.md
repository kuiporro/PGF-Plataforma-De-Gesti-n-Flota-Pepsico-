# 🧪 Pruebas Manuales por Rol - PGF Plataforma

**Fecha de creación**: 2025-01-19  
**Versión del sistema**: 2.0.0

Este documento contiene el listado completo de pruebas funcionales manuales organizadas por rol de usuario. Utilízalo para verificar que todas las funcionalidades están operativas antes de desplegar a producción.

---

## 📋 Índice General

1. [👮‍♂️ Guardia de Portería](#-guardia-de-portería)
2. [🚛 Chofer / Conductor](#-chofer--conductor)
3. [🔧 Mecánico / Técnico](#-mecánico--técnico)
4. [🧰 Jefe de Taller](#-jefe-de-taller)
5. [🧭 Supervisor Zonal](#-supervisor-zonal)
6. [🗂️ Coordinador de Zona](#️-coordinador-de-zona)
7. [🧑‍💼 Subgerente de Flota Nacional](#-subgerente-de-flota-nacional)
8. [🛠️ Administrador del Sistema](#️-administrador-del-sistema)
9. [🔍 Auditor Interno](#-auditor-interno)

---

## 👮‍♂️ Guardia de Portería

### Autenticación
- [ ] **PM-GUARDIA-001**: Login exitoso con credenciales válidas
- [ ] **PM-GUARDIA-002**: Login fallido con credenciales inválidas muestra error apropiado
- [ ] **PM-GUARDIA-003**: Sesión se mantiene activa después de refresh
- [ ] **PM-GUARDIA-004**: Logout limpia la sesión correctamente

### Registrar Ingreso de Vehículo
- [ ] **PM-GUARDIA-005**: Registrar ingreso con patente válida
- [ ] **PM-GUARDIA-006**: Crear vehículo automáticamente si no existe (solo con patente)
- [ ] **PM-GUARDIA-007**: Validar que patente es obligatoria
- [ ] **PM-GUARDIA-008**: Validar formato de patente (AA1234, AAAA12, AAAB12)
- [ ] **PM-GUARDIA-009**: OT se crea automáticamente al registrar ingreso
- [ ] **PM-GUARDIA-010**: OT se vincula con agenda programada si existe
- [ ] **PM-GUARDIA-011**: Alertas se muestran si vehículo tiene bloqueos activos
- [ ] **PM-GUARDIA-012**: Alertas se muestran si vehículo tiene OT abierta previa
- [ ] **PM-GUARDIA-013**: **Descargar ticket de ingreso en PDF**
- [ ] **PM-GUARDIA-014**: PDF del ticket contiene información correcta (vehículo, fecha, OT generada)

### Registrar Salida de Vehículo
- [ ] **PM-GUARDIA-015**: Registrar salida de vehículo ingresado
- [ ] **PM-GUARDIA-016**: Validar que ingreso_id es obligatorio
- [ ] **PM-GUARDIA-017**: Validar que OT debe estar en estado apropiado (CERRADA o similar)
- [ ] **PM-GUARDIA-018**: Estado del vehículo cambia a ACTIVO al registrar salida
- [ ] **PM-GUARDIA-019**: Observaciones de salida se guardan correctamente
- [ ] **PM-GUARDIA-020**: Kilometraje de salida se registra correctamente

### Listado de Ingresos del Día
- [ ] **PM-GUARDIA-021**: Ver listado de ingresos del día actual
- [ ] **PM-GUARDIA-022**: Filtro por patente funciona correctamente
- [ ] **PM-GUARDIA-023**: Ver información de cada ingreso (patente, hora, guardia, estado)
- [ ] **PM-GUARDIA-024**: Descargar PDF de ticket desde el listado

### Navegación y UI
- [ ] **PM-GUARDIA-025**: Sidebar muestra solo opciones permitidas para Guardia
- [ ] **PM-GUARDIA-026**: Acceso denegado a páginas no permitidas (403)
- [ ] **PM-GUARDIA-027**: Notificaciones se muestran correctamente

---

## 🚛 Chofer / Conductor

### Autenticación
- [ ] **PM-CHOFER-001**: Login exitoso con credenciales válidas
- [ ] **PM-CHOFER-002**: Logout funciona correctamente

### Ver Estado de Vehículo Asignado
- [ ] **PM-CHOFER-003**: Ver información de vehículo asignado (patente, marca, modelo)
- [ ] **PM-CHOFER-004**: Ver estado actual del vehículo (ACTIVO, EN_TALLER, etc.)
- [ ] **PM-CHOFER-005**: Ver kilometraje actual
- [ ] **PM-CHOFER-006**: Ver última revisión y próxima revisión programada

### Ver Estado de OTs
- [ ] **PM-CHOFER-007**: Ver OTs asociadas a su vehículo asignado
- [ ] **PM-CHOFER-008**: Ver detalle de OT (estado, motivo, mecánico asignado)
- [ ] **PM-CHOFER-009**: Ver timeline completo de OT
- [ ] **PM-CHOFER-010**: Ver comentarios en OT
- [ ] **PM-CHOFER-011**: Ver tiempo estimado de reparación
- [ ] **PM-CHOFER-012**: Ver estado actual de la OT (EN_EJECUCION, EN_QA, CERRADA)

### Notificaciones
- [ ] **PM-CHOFER-013**: Recibir notificación cuando OT inicia
- [ ] **PM-CHOFER-014**: Recibir notificación cuando OT entra en pausa
- [ ] **PM-CHOFER-015**: Recibir notificación cuando OT pasa a QA
- [ ] **PM-CHOFER-016**: Recibir notificación cuando vehículo está listo (OT cerrada)
- [ ] **PM-CHOFER-017**: Badge muestra contador de notificaciones no leídas

### Historial y Comprobantes
- [ ] **PM-CHOFER-018**: Ver historial de ingresos al taller
- [ ] **PM-CHOFER-019**: Descargar comprobantes de ingreso/salida (PDF)

### Navegación
- [ ] **PM-CHOFER-020**: Acceso solo a funcionalidades permitidas para Chofer
- [ ] **PM-CHOFER-021**: No puede crear, editar o eliminar OTs
- [ ] **PM-CHOFER-022**: Solo lectura de información

---

## 🔧 Mecánico / Técnico

### Autenticación
- [ ] **PM-MECANICO-001**: Login exitoso con credenciales válidas
- [ ] **PM-MECANICO-002**: Logout funciona correctamente

### Ver OTs Asignadas
- [ ] **PM-MECANICO-003**: Ver lista de OTs asignadas a él
- [ ] **PM-MECANICO-004**: Filtrar OTs por estado (EN_EJECUCION, EN_PAUSA, EN_QA)
- [ ] **PM-MECANICO-005**: Ver ordenamiento por prioridad o fecha

### Tomar OT Disponible
- [ ] **PM-MECANICO-006**: Ver OTs disponibles (sin mecánico asignado)
- [ ] **PM-MECANICO-007**: Asignarse a una OT disponible
- [ ] **PM-MECANICO-008**: Validar que solo puede tomar OTs de su taller/zona

### Cambiar Estado de OT
- [ ] **PM-MECANICO-009**: Cambiar estado a EN_DIAGNOSTICO
- [ ] **PM-MECANICO-010**: Cambiar estado a EN_EJECUCION
- [ ] **PM-MECANICO-011**: Pausar OT (EN_PAUSA) con motivo
- [ ] **PM-MECANICO-012**: Reanudar OT pausada
- [ ] **PM-MECANICO-013**: Validar transiciones de estado permitidas
- [ ] **PM-MECANICO-014**: Cambiar a ESPERA_REPUESTO con motivo específico

### Completar Checklist Técnico
- [ ] **PM-MECANICO-015**: Ver checklist técnico de la OT
- [ ] **PM-MECANICO-016**: Completar items del checklist
- [ ] **PM-MECANICO-017**: Agregar observaciones técnicas
- [ ] **PM-MECANICO-018**: Marcar checklist como completado

### Subir Evidencias
- [ ] **PM-MECANICO-019**: Subir foto de falla encontrada
- [ ] **PM-MECANICO-020**: Subir foto de diagnóstico
- [ ] **PM-MECANICO-021**: Subir foto de reparación
- [ ] **PM-MECANICO-022**: Subir documento técnico (PDF, Excel)
- [ ] **PM-MECANICO-023**: Validar tamaño máximo de archivo (3GB)
- [ ] **PM-MECANICO-024**: Agregar descripción a evidencia
- [ ] **PM-MECANICO-025**: Ver evidencias subidas anteriormente

### Agregar Observaciones
- [ ] **PM-MECANICO-026**: Agregar observaciones técnicas en OT
- [ ] **PM-MECANICO-027**: Agregar diagnóstico inicial
- [ ] **PM-MECANICO-028**: Agregar diagnóstico final
- [ ] **PM-MECANICO-029**: Ver historial de observaciones

### Ver Historial del Vehículo
- [ ] **PM-MECANICO-030**: Ver historial completo de OTs del vehículo
- [ ] **PM-MECANICO-031**: Ver historial de repuestos utilizados
- [ ] **PM-MECANICO-032**: Ver historial de ingresos al taller

### Registrar Horas Trabajadas
- [ ] **PM-MECANICO-033**: Registrar horas hombre trabajadas (si implementado)

### Ver Inventario (Solo Lectura)
- [ ] **PM-MECANICO-034**: Ver inventario de repuestos disponibles
- [ ] **PM-MECANICO-035**: Buscar repuesto por nombre o código
- [ ] **PM-MECANICO-036**: Ver stock disponible

### Navegación
- [ ] **PM-MECANICO-037**: Acceso solo a funcionalidades permitidas
- [ ] **PM-MECANICO-038**: No puede crear OTs ni gestionar usuarios
- [ ] **PM-MECANICO-039**: Notificaciones funcionan correctamente

---

## 🧰 Jefe de Taller

### Autenticación
- [ ] **PM-JEFE-001**: Login exitoso con credenciales válidas

### Dashboard del Taller
- [ ] **PM-JEFE-002**: Ver KPIs del taller (OTs abiertas, en ejecución, cerradas hoy)
- [ ] **PM-JEFE-003**: Ver carga de trabajo de mecánicos
- [ ] **PM-JEFE-004**: Ver vehículos en taller
- [ ] **PM-JEFE-005**: Ver OTs pendientes de asignación

### Crear OTs
- [ ] **PM-JEFE-006**: Crear OT nueva manualmente
- [ ] **PM-JEFE-007**: Validar campos obligatorios (vehículo, motivo, tipo)
- [ ] **PM-JEFE-008**: Seleccionar prioridad (ALTA, MEDIA, BAJA)
- [ ] **PM-JEFE-009**: Seleccionar tipo (MANTENCION, REPARACION, EMERGENCIA)
- [ ] **PM-JEFE-010**: Asignar mecánico al crear OT

### Gestor de OTs
- [ ] **PM-JEFE-011**: Ver todas las OTs del taller con filtros avanzados
- [ ] **PM-JEFE-012**: Filtrar por estado, tipo, prioridad, mecánico
- [ ] **PM-JEFE-013**: Filtrar por rango de fechas
- [ ] **PM-JEFE-014**: Buscar OT por número o patente
- [ ] **PM-JEFE-015**: Editar cualquier OT del taller
- [ ] **PM-JEFE-016**: Cambiar prioridad de OT
- [ ] **PM-JEFE-017**: Cambiar tipo de OT

### Asignación de Mecánicos
- [ ] **PM-JEFE-018**: Ver lista de mecánicos disponibles
- [ ] **PM-JEFE-019**: Ver carga de trabajo de cada mecánico
- [ ] **PM-JEFE-020**: Asignar mecánico a OT pendiente
- [ ] **PM-JEFE-021**: Reasignar mecánico en OT en ejecución
- [ ] **PM-JEFE-022**: Validar que mecánico pertenece al taller/zona

### Control de Calidad (QA)
- [ ] **PM-JEFE-023**: Ver OTs en estado EN_QA
- [ ] **PM-JEFE-024**: Ver evidencias subidas por mecánico
- [ ] **PM-JEFE-025**: Ver checklist final completado
- [ ] **PM-JEFE-026**: Aprobar QA (cambiar a CERRADA)
- [ ] **PM-JEFE-027**: Rechazar QA (devolver a EN_EJECUCION o RETRABAJO)
- [ ] **PM-JEFE-028**: Agregar observaciones de QA
- [ ] **PM-JEFE-029**: Invalidar evidencia incorrecta con motivo

### Gestionar Pausas
- [ ] **PM-JEFE-030**: Ver pausas activas del taller
- [ ] **PM-JEFE-031**: Finalizar pausa manualmente
- [ ] **PM-JEFE-032**: Agregar observaciones a pausa

### Control de Tiempos y SLA
- [ ] **PM-JEFE-033**: Ver OTs con SLA vencido
- [ ] **PM-JEFE-034**: Ver tiempos promedio de reparación
- [ ] **PM-JEFE-035**: Ver cumplimiento de SLA del taller

### Subir Evidencia Adicional
- [ ] **PM-JEFE-036**: Subir evidencia adicional a cualquier OT
- [ ] **PM-JEFE-037**: Corregir documentación incorrecta
- [ ] **PM-JEFE-038**: Invalidar evidencia con versionado

### Reportes
- [ ] **PM-JEFE-039**: Ver reportes operacionales del taller
- [ ] **PM-JEFE-040**: Descargar reporte semanal en PDF
- [ ] **PM-JEFE-041**: Descargar reporte mensual en PDF

### Navegación
- [ ] **PM-JEFE-042**: Acceso completo a funcionalidades del taller
- [ ] **PM-JEFE-043**: No puede gestionar usuarios (solo Admin)
- [ ] **PM-JEFE-044**: Notificaciones de cambios importantes funcionan

---

## 🧭 Supervisor Zonal

### Autenticación
- [ ] **PM-SUPERVISOR-001**: Login exitoso con credenciales válidas

### Dashboard de Zona
- [ ] **PM-SUPERVISOR-002**: Ver KPIs de la zona (OTs abiertas, SLA cumplimiento)
- [ ] **PM-SUPERVISOR-003**: Ver ranking de productividad por taller
- [ ] **PM-SUPERVISOR-004**: Ver cumplimiento SLA por taller
- [ ] **PM-SUPERVISOR-005**: Ver vehículos fuera de servicio
- [ ] **PM-SUPERVISOR-006**: Ver mapa de talleres (si implementado)

### Analizador de OTs
- [ ] **PM-SUPERVISOR-007**: Ver todas las OTs de su zona
- [ ] **PM-SUPERVISOR-008**: Filtrar por taller, mecánico, fechas, tipo de OT
- [ ] **PM-SUPERVISOR-009**: Ver información detallada de cada OT
- [ ] **PM-SUPERVISOR-010**: Exportar datos de OTs (si implementado)

### Reportes Zonales
- [ ] **PM-SUPERVISOR-011**: Ver reportes operacionales de la zona
- [ ] **PM-SUPERVISOR-012**: Descargar reporte zonal en PDF
- [ ] **PM-SUPERVISOR-013**: Ver comparativa de desempeño entre talleres
- [ ] **PM-SUPERVISOR-014**: Ver tipos de OT más frecuentes

### Gestión de Vehículos
- [ ] **PM-SUPERVISOR-015**: Ver vehículos de la zona
- [ ] **PM-SUPERVISOR-016**: Ver histórico completo por vehículo
- [ ] **PM-SUPERVISOR-017**: Subir documentos administrativos (solo lectura técnica)

### Navegación
- [ ] **PM-SUPERVISOR-018**: Acceso solo a su zona
- [ ] **PM-SUPERVISOR-019**: No puede ver datos de otras zonas
- [ ] **PM-SUPERVISOR-020**: Notificaciones de zona funcionan correctamente

---

## 🗂️ Coordinador de Zona / Administrativo

### Autenticación
- [ ] **PM-COORDINADOR-001**: Login exitoso con credenciales válidas

### Gestión de Vehículos
- [ ] **PM-COORDINADOR-002**: Registrar vehículo nuevo
- [ ] **PM-COORDINADOR-003**: Editar información de vehículo existente
- [ ] **PM-COORDINADOR-004**: Validar campos obligatorios (patente, marca, modelo, año)
- [ ] **PM-COORDINADOR-005**: Validar formato de patente
- [ ] **PM-COORDINADOR-006**: Ver lista de vehículos de la zona
- [ ] **PM-COORDINADOR-007**: Buscar vehículo por patente, VIN, modelo

### Soporte de Documentos
- [ ] **PM-COORDINADOR-008**: Subir factura administrativa
- [ ] **PM-COORDINADOR-009**: Subir guía de despacho
- [ ] **PM-COORDINADOR-010**: Subir informe administrativo
- [ ] **PM-COORDINADOR-011**: Subir padrón
- [ ] **PM-COORDINADOR-012**: Subir seguro
- [ ] **PM-COORDINADOR-013**: Subir permiso de circulación
- [ ] **PM-COORDINADOR-014**: Ver documentos subidos por vehículo
- [ ] **PM-COORDINADOR-015**: Descargar documentos subidos

### Gestión de OTs (Solo Lectura Técnica)
- [ ] **PM-COORDINADOR-016**: Ver OTs abiertas y cerradas de la zona
- [ ] **PM-COORDINADOR-017**: Filtrar OTs por estado, tipo, fecha
- [ ] **PM-COORDINADOR-018**: Ver detalle de OT (solo lectura)
- [ ] **PM-COORDINADOR-019**: No puede editar OTs (solo lectura)

### Reportes Operacionales
- [ ] **PM-COORDINADOR-020**: Ver reportes operacionales de la zona
- [ ] **PM-COORDINADOR-021**: Descargar reportes en PDF
- [ ] **PM-COORDINADOR-022**: Ver tiempos de reparación
- [ ] **PM-COORDINADOR-023**: Ver estado de flota

### Gestión de Inventario Simple
- [ ] **PM-COORDINADOR-024**: Ver inventario de repuestos (si tiene permisos)
- [ ] **PM-COORDINADOR-025**: Gestionar stock simple (si tiene permisos)

### Navegación
- [ ] **PM-COORDINADOR-026**: Acceso a funcionalidades administrativas
- [ ] **PM-COORDINADOR-027**: No puede gestionar usuarios ni permisos
- [ ] **PM-COORDINADOR-028**: Puede apoyar al Jefe de Taller con carga administrativa

---

## 🧑‍💼 Subgerente de Flota Nacional

### Autenticación
- [ ] **PM-SUBGERENTE-001**: Login exitoso con credenciales válidas

### Dashboard Nacional
- [ ] **PM-SUBGERENTE-002**: Ver OTs por región
- [ ] **PM-SUBGERENTE-003**: Ver SLA nacional
- [ ] **PM-SUBGERENTE-004**: Ver ranking de talleres
- [ ] **PM-SUBGERENTE-005**: Ver tendencias históricas
- [ ] **PM-SUBGERENTE-006**: Ver flota operativa vs no operativa
- [ ] **PM-SUBGERENTE-007**: Ver métricas nacionales agregadas

### Análisis Estratégico
- [ ] **PM-SUBGERENTE-008**: Ver gráficos de líneas (evolución en el tiempo)
- [ ] **PM-SUBGERENTE-009**: Ver gráficos de barras (comparativa)
- [ ] **PM-SUBGERENTE-010**: Ver heatmap (distribución por zona/tipo)
- [ ] **PM-SUBGERENTE-011**: Filtrar análisis por año, zona, tipo de OT, taller
- [ ] **PM-SUBGERENTE-012**: Comparar desempeño entre zonas

### Auditoría de Vehículos
- [ ] **PM-SUBGERENTE-013**: Ver historial completo de mantenciones por vehículo
- [ ] **PM-SUBGERENTE-014**: Ver evidencias de todas las OTs (solo lectura)
- [ ] **PM-SUBGERENTE-015**: Ver OTs agrupadas por tipo
- [ ] **PM-SUBGERENTE-016**: Analizar patrones de mantenimiento

### Reportes de Alto Nivel
- [ ] **PM-SUBGERENTE-017**: Descargar reportes nacionales en PDF
- [ ] **PM-SUBGERENTE-018**: Ver métricas: disponibilidad flota
- [ ] **PM-SUBGERENTE-019**: Ver métricas: % vehículos operativos
- [ ] **PM-SUBGERENTE-020**: Ver costos por tipo de OT (si implementado)

### Navegación
- [ ] **PM-SUBGERENTE-021**: Acceso completo a datos nacionales
- [ ] **PM-SUBGERENTE-022**: Solo lectura (no puede editar OTs ni vehículos)
- [ ] **PM-SUBGERENTE-023**: Notificaciones de eventos nacionales importantes

---

## 🛠️ Administrador del Sistema

### Autenticación
- [ ] **PM-ADMIN-001**: Login exitoso con credenciales válidas

### Gestión de Usuarios
- [ ] **PM-ADMIN-002**: Crear usuario nuevo
- [ ] **PM-ADMIN-003**: Editar datos de usuario existente
- [ ] **PM-ADMIN-004**: Cambiar rol de usuario
- [ ] **PM-ADMIN-005**: Deshabilitar usuario (is_active = False)
- [ ] **PM-ADMIN-006**: Habilitar usuario deshabilitado
- [ ] **PM-ADMIN-007**: Resetear contraseña de usuario
- [ ] **PM-ADMIN-008**: Validar RUT único al crear usuario
- [ ] **PM-ADMIN-009**: Validar email único al crear usuario
- [ ] **PM-ADMIN-010**: Validar rol válido contra lista permitida
- [ ] **PM-ADMIN-011**: Listar usuarios con filtros (rol, estado, zona)

### Configuración del Sistema
- [ ] **PM-ADMIN-012**: Ver configuración de tipos de OT
- [ ] **PM-ADMIN-013**: Configurar checklists de calidad
- [ ] **PM-ADMIN-014**: Gestionar catálogo de talleres
- [ ] **PM-ADMIN-015**: Configurar zonas geográficas
- [ ] **PM-ADMIN-016**: Configurar políticas de seguridad
- [ ] **PM-ADMIN-017**: Ver duración de sesión configurada
- [ ] **PM-ADMIN-018**: Ver configuración de refresh token

### Integraciones
- [ ] **PM-ADMIN-019**: Ver configuración de S3 (bucket, región, estado)
- [ ] **PM-ADMIN-020**: Ver configuración de correos (SMTP)
- [ ] **PM-ADMIN-021**: Ver logs técnicos del sistema
- [ ] **PM-ADMIN-022**: Ver dashboard de errores
- [ ] **PM-ADMIN-023**: Gestionar integraciones con APIs externas (si implementado)

### Panel de Logs
- [ ] **PM-ADMIN-024**: Ver logs del sistema (Auditoria)
- [ ] **PM-ADMIN-025**: Filtrar logs por acción, usuario, fecha
- [ ] **PM-ADMIN-026**: Ver errores del sistema
- [ ] **PM-ADMIN-027**: Descargar logs en formato JSON/CSV

### Mantenimientos Técnicos
- [ ] **PM-ADMIN-028**: Realizar limpieza de datos (si implementado)
- [ ] **PM-ADMIN-029**: Optimizar base de datos (si implementado)
- [ ] **PM-ADMIN-030**: Ver estado de servicios (Celery, Redis, S3)

### Auditoría
- [ ] **PM-ADMIN-031**: Ver todos los cambios realizados en el sistema
- [ ] **PM-ADMIN-032**: Auditar acciones por usuario
- [ ] **PM-ADMIN-033**: Ver evidencias invalidadas
- [ ] **PM-ADMIN-034**: Descargar reportes de auditoría

### Navegación
- [ ] **PM-ADMIN-035**: Acceso completo a todas las funcionalidades
- [ ] **PM-ADMIN-036**: Sidebar muestra todas las opciones disponibles
- [ ] **PM-ADMIN-037**: Notificaciones de eventos críticos del sistema

---

## 🔍 Auditor Interno

### Autenticación
- [ ] **PM-AUDITOR-001**: Login exitoso con credenciales válidas
- [ ] **PM-AUDITOR-002**: Solo acceso de lectura (no puede editar nada)

### Dashboard de Auditoría
- [ ] **PM-AUDITOR-003**: Ver últimos cambios críticos del sistema
- [ ] **PM-AUDITOR-004**: Ver actividad por usuario
- [ ] **PM-AUDITOR-005**: Ver evidencias marcadas como inválidas
- [ ] **PM-AUDITOR-006**: Ver resumen de auditoría

### Ver Todas las OTs (Solo Lectura)
- [ ] **PM-AUDITOR-007**: Ver todas las OTs del sistema
- [ ] **PM-AUDITOR-008**: Filtrar OTs por estado, tipo, fecha, taller
- [ ] **PM-AUDITOR-009**: Ver detalle completo de OT
- [ ] **PM-AUDITOR-010**: Ver timeline completo de OT
- [ ] **PM-AUDITOR-011**: Ver comentarios en OT
- [ ] **PM-AUDITOR-012**: No puede editar ni crear OTs

### Ver Evidencias (Solo Lectura)
- [ ] **PM-AUDITOR-013**: Ver todas las evidencias del sistema
- [ ] **PM-AUDITOR-014**: Ver evidencias invalidadas con motivo
- [ ] **PM-AUDITOR-015**: Ver historial de versiones de evidencia
- [ ] **PM-AUDITOR-016**: Descargar evidencias (según permisos)

### Logs del Sistema
- [ ] **PM-AUDITOR-017**: Ver CRUD de usuarios (quién creó, editó, eliminó)
- [ ] **PM-AUDITOR-018**: Ver cambios de estado de OT
- [ ] **PM-AUDITOR-019**: Ver ediciones en OT
- [ ] **PM-AUDITOR-020**: Ver historial completo de acciones
- [ ] **PM-AUDITOR-021**: Filtrar logs por acción (LOGIN_EXITOSO, CERRAR_OT, etc.)
- [ ] **PM-AUDITOR-022**: Filtrar logs por usuario
- [ ] **PM-AUDITOR-023**: Filtrar logs por rango de fechas
- [ ] **PM-AUDITOR-024**: Exportar logs

### Auditoría por OT
- [ ] **PM-AUDITOR-025**: Ver línea de tiempo completa de OT
- [ ] **PM-AUDITOR-026**: Ver evidencias con estado original
- [ ] **PM-AUDITOR-027**: Comparar entre versiones de evidencia
- [ ] **PM-AUDITOR-028**: Ver historial de cambios en OT
- [ ] **PM-AUDITOR-029**: Ver actores involucrados en OT

### Reportes de Auditoría
- [ ] **PM-AUDITOR-030**: Descargar reportes de auditoría en PDF
- [ ] **PM-AUDITOR-031**: Generar reporte de cambios críticos
- [ ] **PM-AUDITOR-032**: Generar reporte de actividad por usuario

### Navegación
- [ ] **PM-AUDITOR-033**: Acceso solo de lectura
- [ ] **PM-AUDITOR-034**: No puede editar, crear ni eliminar nada
- [ ] **PM-AUDITOR-035**: Sidebar muestra solo opciones de auditoría

---

## 🧪 Pruebas Transversales (Todos los Roles)

### Sistema de Comentarios
- [ ] **PM-TRANS-001**: Agregar comentario en OT
- [ ] **PM-TRANS-002**: Mencionar usuarios con @username
- [ ] **PM-TRANS-003**: Responder a comentario
- [ ] **PM-TRANS-004**: Ver notificación al ser mencionado
- [ ] **PM-TRANS-005**: Ver hilo de conversación completo

### Timeline de OT
- [ ] **PM-TRANS-006**: Ver timeline consolidado de OT
- [ ] **PM-TRANS-007**: Ver cambios de estado en timeline
- [ ] **PM-TRANS-008**: Ver comentarios en timeline
- [ ] **PM-TRANS-009**: Ver evidencias en timeline
- [ ] **PM-TRANS-010**: Ver pausas en timeline
- [ ] **PM-TRANS-011**: Ver actores involucrados

### Notificaciones
- [ ] **PM-TRANS-012**: Recibir notificaciones en tiempo real (WebSocket)
- [ ] **PM-TRANS-013**: Ver badge con contador de no leídas
- [ ] **PM-TRANS-014**: Marcar notificación como leída
- [ ] **PM-TRANS-015**: Recibir notificaciones push del navegador (si configurado)
- [ ] **PM-TRANS-016**: Configurar preferencias de notificaciones

### Descarga de Documentos
- [ ] **PM-TRANS-017**: Descargar PDF de reportes
- [ ] **PM-TRANS-018**: Descargar PDF de ticket de ingreso
- [ ] **PM-TRANS-019**: Descargar evidencias según permisos
- [ ] **PM-TRANS-020**: Validar que solo se descarga lo permitido por rol

### Navegación y UI
- [ ] **PM-TRANS-021**: Sidebar se adapta según rol
- [ ] **PM-TRANS-022**: Dark mode funciona correctamente
- [ ] **PM-TRANS-023**: Responsive design funciona en móvil/tablet
- [ ] **PM-TRANS-024**: Links de navegación funcionan correctamente
- [ ] **PM-TRANS-025**: Mensajes de error son claros y útiles

---

## 📊 Resumen de Pruebas

| Rol | Total de Pruebas | Críticas | Importantes | Opcionales |
|-----|------------------|----------|-------------|------------|
| Guardia | 27 | 15 | 10 | 2 |
| Chofer | 22 | 10 | 10 | 2 |
| Mecánico | 39 | 25 | 12 | 2 |
| Jefe de Taller | 44 | 30 | 12 | 2 |
| Supervisor | 20 | 12 | 6 | 2 |
| Coordinador | 28 | 18 | 8 | 2 |
| Subgerente | 23 | 15 | 6 | 2 |
| Administrador | 37 | 25 | 10 | 2 |
| Auditor | 35 | 25 | 8 | 2 |
| **Transversales** | **25** | **15** | **8** | **2** |
| **TOTAL** | **300** | **190** | **90** | **20** |

---

## ✅ Criterios de Aceptación

Para considerar que las pruebas están completas:

- **100% de pruebas críticas** deben pasar
- **80% de pruebas importantes** deben pasar
- **60% de pruebas opcionales** pueden pasar

### Priorización

1. **Alta**: Funcionalidades críticas de negocio (crear OT, registrar ingreso, subir evidencia)
2. **Media**: Funcionalidades importantes (reportes, filtros, notificaciones)
3. **Baja**: Funcionalidades opcionales (NFC, gráficos avanzados)

---

## 📝 Notas para Ejecución

1. **Orden sugerido**: Ejecutar pruebas por rol, comenzando con Guardia y terminando con Auditor
2. **Datos de prueba**: Preparar datos de prueba antes de comenzar (vehículos, usuarios, OTs)
3. **Ambiente**: Usar ambiente de testing, no producción
4. **Documentación**: Documentar cualquier bug o comportamiento inesperado
5. **Regresión**: Ejecutar pruebas transversales al final para verificar integración

---

**Última actualización**: 2025-01-19  
**Versión del documento**: 1.0.0

