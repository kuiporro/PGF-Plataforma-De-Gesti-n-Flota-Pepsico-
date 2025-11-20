# 🗑️ Guía de Limpieza de Datos - PGF

Este documento explica cómo usar el comando `clear_all_data` para limpiar todos los datos de la aplicación PGF.

## 📋 Descripción

El comando `clear_all_data` elimina todos los registros de las tablas principales de la aplicación, dejando la base de datos completamente limpia. Esto es útil para:

- **Desarrollo**: Limpiar datos de prueba antes de comenzar nuevas pruebas
- **Testing**: Resetear el entorno de pruebas
- **Demostraciones**: Preparar un entorno limpio para presentaciones
- **Migración**: Limpiar datos antes de migraciones importantes

## ⚠️ Advertencia Importante

**Este comando es DESTRUCTIVO**. Eliminará permanentemente todos los datos de:

- ✅ Órdenes de Trabajo y todos sus componentes (evidencias, comentarios, pausas, etc.)
- ✅ Vehículos e ingresos
- ✅ Usuarios y perfiles
- ✅ Choferes
- ✅ Emergencias
- ✅ Notificaciones
- ✅ Inventario (repuestos y stock)
- ✅ Agenda y programaciones
- ✅ Tokens de recuperación de contraseña

**NO se pueden recuperar los datos después de ejecutar este comando.**

## 🚀 Uso Básico

### Limpieza Completa (con confirmación)

```bash
docker compose exec api poetry run python manage.py clear_all_data
```

Este comando:
1. Muestra una advertencia detallada
2. Pide confirmación escribiendo "SI"
3. Procede a eliminar todos los datos

### Limpieza Completa (sin confirmación)

```bash
docker compose exec api poetry run python manage.py clear_all_data --confirm
```

Este comando elimina todos los datos sin pedir confirmación. **Úsalo con precaución.**

## 🔧 Opciones Avanzadas

### Mantener Todos los Usuarios

Si quieres limpiar todos los datos pero mantener los usuarios existentes:

```bash
docker compose exec api poetry run python manage.py clear_all_data --keep-users --confirm
```

**Qué se mantiene:**
- ✅ Todos los usuarios
- ✅ Todos los perfiles de usuario

**Qué se elimina:**
- ❌ Todas las relaciones de usuarios (OTs asignadas, etc.)
- ❌ Todos los demás datos

### Mantener un Usuario Específico

Si quieres mantener solo un usuario (por ejemplo, el administrador):

```bash
docker compose exec api poetry run python manage.py clear_all_data \
  --keep-current-user \
  --username admin \
  --confirm
```

**Qué se mantiene:**
- ✅ El usuario especificado (ej: `admin`)
- ✅ Su perfil asociado

**Qué se elimina:**
- ❌ Todos los demás usuarios
- ❌ Todos los demás datos

## 📊 Tablas que se Limpian

El comando elimina datos de las siguientes tablas (en orden):

### 1. Órdenes de Trabajo
- `Evidencia` - Evidencias fotográficas/documentales
- `ComentarioOT` - Comentarios en OTs
- `Checklist` - Checklists de calidad
- `Pausa` - Pausas durante ejecución
- `DetallePresup` - Detalles de presupuestos
- `Aprobacion` - Aprobaciones de presupuestos
- `Presupuesto` - Presupuestos
- `ItemOT` - Items de trabajo (repuestos/servicios)
- `OrdenTrabajo` - Órdenes de trabajo
- `Auditoria` - Registros de auditoría
- `VersionEvidencia` - Versiones de evidencias
- `BloqueoVehiculo` - Bloqueos de vehículos

### 2. Vehículos
- `EvidenciaIngreso` - Evidencias de ingresos
- `HistorialVehiculo` - Historial de vehículos
- `BackupVehiculo` - Backups de vehículos
- `IngresoVehiculo` - Ingresos de vehículos
- `Vehiculo` - Vehículos

### 3. Choferes
- `HistorialAsignacionVehiculo` - Historial de asignaciones
- `Chofer` - Choferes

### 4. Emergencias
- `EmergenciaRuta` - Emergencias en ruta

### 5. Notificaciones
- `Notification` - Notificaciones del sistema

### 6. Inventario
- `Stock` - Stock de repuestos
- `Repuesto` - Repuestos

### 7. Agenda (si existe)
- `CupoDiario` - Cupos diarios
- `Agenda` - Programaciones

### 8. Usuarios (opcional)
- `PasswordResetToken` - Tokens de recuperación
- `Profile` - Perfiles de usuario
- `User` - Usuarios (si no se usa `--keep-users`)

## 📝 Ejemplos de Uso

### Ejemplo 1: Limpiar todo antes de una demostración

```bash
# Limpiar completamente la base de datos
docker compose exec api poetry run python manage.py clear_all_data --confirm

# Luego crear datos de demostración (si tienes un script)
docker compose exec api poetry run python manage.py seed_demo
```

### Ejemplo 2: Resetear datos pero mantener usuarios

```bash
# Mantener usuarios pero limpiar todo lo demás
docker compose exec api poetry run python manage.py clear_all_data \
  --keep-users \
  --confirm
```

### Ejemplo 3: Limpiar todo excepto el usuario admin

```bash
# Mantener solo el usuario admin
docker compose exec api poetry run python manage.py clear_all_data \
  --keep-current-user \
  --username admin \
  --confirm
```

### Ejemplo 4: Limpieza interactiva (recomendado)

```bash
# El comando pedirá confirmación
docker compose exec api poetry run python manage.py clear_all_data
```

**Salida esperada:**
```
⚠️  ADVERTENCIA: Este comando borrará TODOS los datos de la aplicación.

Esto incluye:
  - Todas las Órdenes de Trabajo
  - Todos los Vehículos e Ingresos
  - Todos los Usuarios (a menos que uses --keep-users o --keep-current-user)
  - Todos los Choferes
  - Todas las Emergencias
  - Todas las Notificaciones
  - Todo el Inventario
  - Toda la Agenda

¿Estás seguro de que deseas continuar? (escribe "SI" para confirmar): 
```

## 🔍 Verificación

Después de ejecutar el comando, puedes verificar que los datos fueron eliminados:

```bash
# Acceder al shell de Django
docker compose exec api poetry run python manage.py shell

# En el shell, verificar que las tablas están vacías
>>> from apps.workorders.models import OrdenTrabajo
>>> OrdenTrabajo.objects.count()
0

>>> from apps.vehicles.models import Vehiculo
>>> Vehiculo.objects.count()
0

>>> from apps.users.models import User
>>> User.objects.count()
0  # O el número de usuarios mantenidos
```

## 🛡️ Seguridad

### Transacciones

El comando usa transacciones de base de datos (`transaction.atomic()`), lo que significa que:

- ✅ Si ocurre un error, **todos los cambios se revierten** (rollback)
- ✅ La operación es **atómica**: o se completa toda o no se hace nada
- ✅ No quedan datos parcialmente eliminados

### Orden de Eliminación

Los datos se eliminan en el orden correcto para respetar las relaciones de claves foráneas:

1. Primero se eliminan las tablas dependientes (evidencias, comentarios, etc.)
2. Luego las tablas principales (OTs, vehículos, etc.)
3. Finalmente los usuarios (si no se mantienen)

## ⚙️ Parámetros del Comando

| Parámetro | Descripción | Requerido |
|-----------|-------------|-----------|
| `--keep-users` | Mantiene todos los usuarios | No |
| `--keep-current-user` | Mantiene un usuario específico | No |
| `--username USERNAME` | Username del usuario a mantener (requerido con `--keep-current-user`) | Condicional |
| `--confirm` | Omite la confirmación interactiva | No |

## 🐛 Solución de Problemas

### Error: "Usuario no encontrado"

Si usas `--keep-current-user` con un username que no existe:

```bash
# Verificar usuarios existentes
docker compose exec api poetry run python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.values_list('username', flat=True)
```

### Error: "No se puede eliminar debido a restricciones de clave foránea"

Si encuentras este error, es probable que haya un problema con el orden de eliminación. Verifica que estás usando la versión más reciente del comando.

### Error: "Transaction rollback"

Si el comando falla y hace rollback, todos los datos se mantienen intactos. Revisa los logs para identificar el problema:

```bash
docker compose logs api | tail -50
```

## 📚 Comandos Relacionados

- **Crear datos de demostración**: `python manage.py seed_demo`
- **Hacer migraciones**: `python manage.py migrate`
- **Crear superusuario**: `python manage.py createsuperuser`

## 💡 Recomendaciones

1. **Haz backup antes de limpiar**: Si los datos son importantes, haz un backup de la base de datos antes de ejecutar el comando.

2. **Usa confirmación interactiva**: A menos que estés en un script automatizado, evita usar `--confirm` para tener una oportunidad de cancelar.

3. **Mantén usuarios importantes**: Si necesitas mantener usuarios específicos, usa `--keep-current-user` con el username correcto.

4. **Verifica después**: Después de limpiar, verifica que las tablas están vacías antes de continuar.

## 📞 Soporte

Si encuentras problemas o tienes preguntas sobre el uso de este comando, consulta:

- La documentación del proyecto: `README.md`
- Los logs de la aplicación: `docker compose logs api`
- El código del comando: `apps/workorders/management/commands/clear_all_data.py`

---

**Última actualización**: 2025-01-XX  
**Versión del comando**: 1.0.0

