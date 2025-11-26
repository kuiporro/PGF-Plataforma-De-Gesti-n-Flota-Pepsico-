# 🌱 Guía de Seed de Datos - PGF

Esta guía explica cómo usar el comando `seed_completo` para generar datos de prueba completos para todos los módulos de la aplicación.

## 📋 Descripción

El comando `seed_completo` genera datos de prueba realistas y completos para:

- ✅ **Usuarios** con todos los roles y campos completos (RUT, email, teléfono, perfil)
- ✅ **Vehículos** con todos los campos (patente, marca, modelo, año, tipo, categoría, estado, etc.)
- ✅ **Choferes** completos con asignaciones
- ✅ **Órdenes de Trabajo** en diferentes estados con items, presupuestos, evidencias, pausas, checklists y comentarios
- ✅ **Emergencias** en diferentes estados
- ✅ **Agenda** y cupos diarios
- ✅ **Repuestos e Inventario** con stock y movimientos
- ✅ **Solicitudes de repuestos**
- ✅ **Historial de repuestos por vehículo**
- ✅ **Ingresos de vehículos** con evidencias
- ✅ **Asignaciones de vehículos a choferes**

## 🚀 Uso Básico

### Generar Datos con Valores por Defecto

```bash
docker compose exec api poetry run python manage.py seed_completo
```

**Valores por defecto:**
- 30 usuarios
- 50 vehículos
- 80 órdenes de trabajo
- 25 choferes
- 15 emergencias
- 20 agendas
- 100 repuestos

### Personalizar Cantidad de Datos

```bash
# Generar más datos
docker compose exec api poetry run python manage.py seed_completo \
  --users 50 \
  --vehicles 100 \
  --workorders 150 \
  --drivers 40 \
  --emergencies 30 \
  --agendas 50 \
  --repuestos 200
```

### Generar Datos Mínimos (Rápido)

```bash
# Para pruebas rápidas
docker compose exec api poetry run python manage.py seed_completo \
  --users 10 \
  --vehicles 15 \
  --workorders 20 \
  --drivers 8 \
  --emergencies 5 \
  --agendas 10 \
  --repuestos 30
```

## 📊 Datos Generados

### Usuarios

Se crean usuarios con todos los roles:
- **ADMIN**: Administradores del sistema
- **SUPERVISOR**: Supervisores zonales
- **JEFE_TALLER**: Jefes de taller
- **MECANICO**: Mecánicos
- **GUARDIA**: Guardias de portería
- **COORDINADOR_ZONA**: Coordinadores de zona
- **RECEPCIONISTA**: Recepcionistas
- **EJECUTIVO**: Ejecutivos
- **SPONSOR**: Sponsors
- **CHOFER**: Choferes

**Campos completados:**
- ✅ Username único
- ✅ Email único (@pepsico.cl)
- ✅ RUT chileno válido con dígito verificador
- ✅ Nombre y apellido
- ✅ Contraseña: `password123` (para todos)
- ✅ Perfil completo:
  - Teléfono
  - Zona, Site, Sucursal
  - Preferencias de notificaciones

### Vehículos

**Campos completados:**
- ✅ Patente única (formato chileno válido)
- ✅ Marca y modelo (Toyota, Ford, Chevrolet, etc.)
- ✅ Año (2018-2024)
- ✅ Tipo (Eléctrico, Diésel, Utilitario, Reparto, Ventas, Respaldo)
- ✅ Categoría (Reparto, Ventas, Respaldo)
- ✅ Estado (Activo, En Espera, En Mantenimiento, Baja)
- ✅ Estado operativo
- ✅ VIN único
- ✅ Zona, Site, Sucursal
- ✅ Supervisor asignado
- ✅ Kilometraje mensual promedio
- ✅ CECO
- ✅ Cumplimiento

### Choferes

**Campos completados:**
- ✅ Nombre completo
- ✅ RUT único válido
- ✅ Teléfono
- ✅ Email
- ✅ Zona y sucursal
- ✅ Vehículo asignado (algunos)
- ✅ Kilometraje mensual promedio
- ✅ Fecha de ingreso
- ✅ Observaciones (algunos)
- ✅ Historial de asignaciones

### Órdenes de Trabajo

**Campos completados:**
- ✅ Vehículo asignado
- ✅ Supervisor, Jefe de Taller, Mecánico (según estado)
- ✅ Estado (ABIERTA, EN_DIAGNOSTICO, EN_EJECUCION, EN_PAUSA, EN_QA, RETRABAJO, CERRADA, ANULADA)
- ✅ Tipo (MANTENCION, REPARACION, EMERGENCIA, DIAGNOSTICO, OTRO)
- ✅ Prioridad (CRITICA, ALTA, MEDIA, BAJA)
- ✅ Motivo completo
- ✅ Diagnóstico (si aplica)
- ✅ Zona y Site
- ✅ Fechas (apertura, cierre si está cerrada)
- ✅ Kilometraje ingreso/salida
- ✅ Tiempo en taller (si está cerrada)
- ✅ Costo total (si está cerrada)

**Relaciones creadas:**
- ✅ Items de OT (1-5 items por OT)
- ✅ Presupuestos (algunas OTs)
- ✅ Detalles de presupuesto
- ✅ Aprobaciones (si el presupuesto está aprobado)
- ✅ Pausas (para OTs en ejecución)
- ✅ Evidencias (2-8 por OT)
- ✅ Checklists (para OTs en QA o cerradas)
- ✅ Comentarios (1-5 por OT, con menciones)

### Emergencias

**Campos completados:**
- ✅ Vehículo
- ✅ Solicitante (Coordinador o Supervisor)
- ✅ Aprobador (Jefe de Taller, si está aprobada)
- ✅ Supervisor asignado
- ✅ Mecánico asignado (si está en reparación)
- ✅ Descripción completa
- ✅ Ubicación (ciudad y dirección)
- ✅ Zona
- ✅ Prioridad (CRITICA, ALTA, MEDIA)
- ✅ Estado (SOLICITADA, APROBADA, ASIGNADA, EN_CAMINO, EN_REPARACION, RESUELTA, CERRADA, RECHAZADA)
- ✅ Fechas (solicitud, aprobación, asignación, resolución, cierre según estado)
- ✅ Observaciones
- ✅ OT asociada (algunas)

### Agenda

**Campos completados:**
- ✅ Vehículo
- ✅ Coordinador
- ✅ Fecha programada
- ✅ Motivo
- ✅ Tipo de mantenimiento (PREVENTIVO, CORRECTIVO, EMERGENCIA)
- ✅ Zona
- ✅ Estado (PROGRAMADA, CONFIRMADA, EN_PROCESO, COMPLETADA, CANCELADA, REPROGRAMADA)
- ✅ Observaciones
- ✅ OT asociada (si está en proceso o completada)

**Cupos diarios:**
- ✅ Cupos para los próximos 30 días
- ✅ Por zona
- ✅ Cupos totales y ocupados

### Repuestos e Inventario

**Repuestos:**
- ✅ Código único
- ✅ Nombre descriptivo
- ✅ Descripción completa
- ✅ Marca
- ✅ Categoría (Frenos, Motor, Transmisión, etc.)
- ✅ Precio de referencia
- ✅ Unidad de medida
- ✅ Estado activo/inactivo

**Stock:**
- ✅ Cantidad actual
- ✅ Cantidad mínima (nivel de reorden)
- ✅ Ubicación en bodega

**Movimientos de stock:**
- ✅ Entradas, salidas, ajustes, devoluciones
- ✅ Cantidades anteriores y nuevas
- ✅ Motivo
- ✅ Usuario responsable
- ✅ Relación con OT y vehículo (algunos)

**Solicitudes de repuestos:**
- ✅ Desde OTs
- ✅ Estados: PENDIENTE, APROBADA, RECHAZADA, ENTREGADA, CANCELADA
- ✅ Solicitante, aprobador, entregador
- ✅ Fechas según estado

**Historial de repuestos por vehículo:**
- ✅ Repuestos utilizados por vehículo
- ✅ Relación con OT e items
- ✅ Costo unitario

### Ingresos de Vehículos

**Campos completados:**
- ✅ Vehículo
- ✅ Chofer
- ✅ Guardia
- ✅ Kilometraje de ingreso
- ✅ Motivo de ingreso
- ✅ Observaciones
- ✅ Fecha de ingreso
- ✅ Fecha de salida (algunos)
- ✅ Kilometraje de salida (si hay salida)
- ✅ Observaciones de salida

**Evidencias de ingreso:**
- ✅ 1-3 evidencias por ingreso
- ✅ Tipos: FOTO_FRONTAL, FOTO_LATERAL, FOTO_TRASERA, FOTO_INTERIOR, OTRO
- ✅ Descripción

## 🔐 Credenciales de Acceso

Todos los usuarios generados tienen la misma contraseña por defecto:

**Contraseña:** `password123`

**Ejemplos de usuarios:**
- `admin1` / `password123` (Administrador)
- `supervisor1` / `password123` (Supervisor)
- `mecanico1` / `password123` (Mecánico)
- `guardia1` / `password123` (Guardia)
- `jefe_taller1` / `password123` (Jefe de Taller)
- etc.

## 📝 Ejemplos de Uso

### Preparar Entorno para Demostración

```bash
# Limpiar datos existentes
docker compose exec api poetry run python manage.py clear_all_data --confirm

# Generar datos completos
docker compose exec api poetry run python manage.py seed_completo \
  --users 40 \
  --vehicles 60 \
  --workorders 100 \
  --drivers 30 \
  --emergencies 20 \
  --agendas 30 \
  --repuestos 150
```

### Generar Datos para Testing

```bash
# Datos mínimos para pruebas rápidas
docker compose exec api poetry run python manage.py seed_completo \
  --users 15 \
  --vehicles 20 \
  --workorders 30 \
  --drivers 10 \
  --emergencies 8 \
  --agendas 15 \
  --repuestos 50
```

### Generar Datos Masivos

```bash
# Para pruebas de rendimiento
docker compose exec api poetry run python manage.py seed_completo \
  --users 100 \
  --vehicles 200 \
  --workorders 500 \
  --drivers 80 \
  --emergencies 50 \
  --agendas 100 \
  --repuestos 500
```

## ⚙️ Parámetros del Comando

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `--users` | Número de usuarios a crear | 30 |
| `--vehicles` | Número de vehículos a crear | 50 |
| `--workorders` | Número de órdenes de trabajo a crear | 80 |
| `--drivers` | Número de choferes a crear | 25 |
| `--emergencies` | Número de emergencias a crear | 15 |
| `--agendas` | Número de agendas a crear | 20 |
| `--repuestos` | Número de repuestos a crear | 100 |

## 🔍 Verificar Datos Generados

### Contar Registros

```bash
# Acceder al shell de Django
docker compose exec api poetry run python manage.py shell

# Contar usuarios
>>> from apps.users.models import User
>>> User.objects.count()

# Contar vehículos
>>> from apps.vehicles.models import Vehiculo
>>> Vehiculo.objects.count()

# Contar OTs
>>> from apps.workorders.models import OrdenTrabajo
>>> OrdenTrabajo.objects.count()

# Ver usuarios por rol
>>> from django.db.models import Count
>>> User.objects.values('rol').annotate(total=Count('id')).order_by('rol')
```

### Ver Datos Específicos

```bash
# Ver un usuario
>>> user = User.objects.filter(rol='ADMIN').first()
>>> print(f"{user.username} - {user.email} - {user.rut}")

# Ver un vehículo
>>> vehiculo = Vehiculo.objects.first()
>>> print(f"{vehiculo.patente} - {vehiculo.marca} {vehiculo.modelo} - {vehiculo.estado}")

# Ver una OT
>>> ot = OrdenTrabajo.objects.first()
>>> print(f"OT {ot.id} - {ot.vehiculo.patente} - {ot.estado} - Items: {ot.items.count()}")
```

## 🐛 Solución de Problemas

### Error: "Faker no está instalado"

**Solución:**
```bash
docker compose exec api poetry add --group dev faker
```

### Error: "RUT duplicado" o "Patente duplicada"

El comando maneja esto automáticamente, pero si ocurre:
- El comando regenera RUTs/patentes hasta encontrar uno único
- Si persiste, limpia los datos y vuelve a ejecutar

### Error: "No hay suficientes usuarios de un rol"

**Solución:**
Aumenta el número de usuarios:
```bash
docker compose exec api poetry run python manage.py seed_completo --users 50
```

### Datos Incompletos

Si algunos datos no se generan correctamente:
1. Verifica que no haya errores en la consola
2. Revisa los logs del comando
3. Limpia los datos y vuelve a ejecutar

## 💡 Recomendaciones

1. **Antes de generar datos:**
   - Limpia los datos existentes si es necesario
   - Asegúrate de tener espacio suficiente en la base de datos

2. **Para demostraciones:**
   - Usa cantidades moderadas (30-50 usuarios, 50-100 vehículos)
   - Los datos se generan más rápido y son más fáciles de navegar

3. **Para pruebas de rendimiento:**
   - Genera datos masivos (100+ usuarios, 200+ vehículos)
   - Mide el tiempo de generación y consultas

4. **Para desarrollo:**
   - Usa cantidades mínimas para pruebas rápidas
   - Regenera datos cuando cambies modelos

## 📊 Tiempos Estimados

| Cantidad | Tiempo Estimado |
|----------|----------------|
| Datos mínimos (10-20) | 10-30 segundos |
| Datos por defecto (30-100) | 1-3 minutos |
| Datos masivos (100-500) | 5-15 minutos |

## 🔄 Regenerar Datos

Para regenerar datos desde cero:

```bash
# 1. Limpiar datos existentes
docker compose exec api poetry run python manage.py clear_all_data --confirm

# 2. Generar nuevos datos
docker compose exec api poetry run python manage.py seed_completo
```

## 📚 Comandos Relacionados

- **Limpiar datos**: `python manage.py clear_all_data --confirm`
- **Crear superusuario**: `python manage.py createsuperuser`
- **Migraciones**: `python manage.py migrate`

---

**Última actualización**: 2025-01-XX  
**Versión**: 1.0.0

