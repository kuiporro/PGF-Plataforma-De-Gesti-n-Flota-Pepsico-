# 🚛 PGF - Plataforma de Gestión de Flota PepsiCo

Sistema completo de gestión de flota vehicular desarrollado para PepsiCo, con gestión de órdenes de trabajo, programación de mantenimientos, emergencias en ruta, choferes, reportes ejecutivos y más.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura](#️-arquitectura)
- [Inicio Rápido](#-inicio-rápido)
- [Instalación Completa](#-instalación-completa)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Variables de Entorno](#-variables-de-entorno)
- [Documentación API](#-documentación-api)
- [Testing](#-testing)
- [Contribuir](#-contribuir)

## ✨ Características

### 🔐 Autenticación y Usuarios
- Sistema de autenticación JWT con refresh tokens
- 10 roles diferentes (Admin, Ejecutivo, Sponsor, Supervisor, Jefe de Taller, Coordinador de Zona, Mecánico, Guardia, Recepcionista, Chofer)
- Control de acceso basado en roles (RBAC)
- Recuperación de contraseña por email
- Cambio de contraseña (usuario y admin)
- **Validaciones robustas**:
  - Correo único y formato válido
  - RUT chileno válido con dígito verificador y único
  - Rol válido contra lista permitida
  - Usuario inactivo no puede iniciar sesión

### 🚗 Gestión de Vehículos
- CRUD completo de vehículos
- Estados: Activo, En Espera, En Mantenimiento, Baja
- Tipos: Eléctrico, Diésel, Utilitario, Reparto, Ventas, Respaldo
- Categorías: Reparto, Ventas, Respaldo
- Ingreso y salida de vehículos al taller
- Evidencias fotográficas (S3)
- Historial completo de mantenimientos y backups
- **Validaciones robustas**:
  - Patente única y formato válido (AA1234, AAAA12, AAAB12)
  - Datos obligatorios (patente, marca, modelo, año, tipo, site, supervisor)
  - Año válido (2000 - año actual)
  - No permite cambiar Site si tiene OT activa
  - Sistema de backups con validación de disponibilidad

### 🔧 Órdenes de Trabajo (OT)
- Flujo completo de OT con estados:
  - **ABIERTA** → **EN_DIAGNOSTICO** → **EN_EJECUCION** → **EN_PAUSA** → **EN_QA** → **CERRADA**
  - Soporte para **RETRABAJO** desde QA
- Asignación de roles:
  - Jefe de Taller: Realiza diagnóstico
  - Supervisor: Aprueba asignación y asigna mecánico
  - Mecánico: Ejecuta el trabajo
- Pausas automáticas (colación 12:30-13:15) y manuales
- Items de trabajo (repuestos y servicios)
- Presupuestos con aprobaciones
- Checklists de calidad
- Evidencias fotográficas (hasta 3GB por archivo)
- Auditoría completa de acciones
- **Validaciones robustas**:
  - Vehículo debe existir
  - No permite OT duplicadas (vehículo no puede tener otra OT activa)
  - Campos obligatorios (motivo, supervisor, site, fecha_apertura)
  - Solo permite pausar si está EN_EJECUCION
  - Requiere fecha_cierre y diagnostico_final al cerrar
  - Cálculo automático de SLA y tiempos en taller

### 📅 Programación y Agenda
- Programación de mantenimientos preventivos
- Gestión de cupos diarios por zona
- Validación de disponibilidad
- Vinculación automática con OT al ingreso
- Estados: Programada, Confirmada, En Proceso, Completada, Cancelada, Reprogramada

### 🚨 Emergencias en Ruta
- Solicitud de emergencias por Coordinadores/Supervisores
- Aprobación por Jefe de Taller/Subgerencia
- Asignación de mecánico por Supervisor
- Creación automática de OT asociada
- Seguimiento de estado: Solicitada → Aprobada → Asignada → En Camino → En Sitio → Resuelta → Cerrada

### 👥 Choferes
- Gestión completa de choferes
- Asignación de vehículos
- Historial de asignaciones
- Zonas y sucursales
- KM mensual promedio

### 📊 Reportes y Dashboards
- **Dashboard Ejecutivo**: KPIs en tiempo real
  - OT por estado
  - Productividad (7 días)
  - Vehículos en taller
  - Métricas de eficiencia
- **Reportes PDF completos** (7 tipos):
  - Estado de Flota (General)
  - Órdenes de Trabajo
  - Uso/Comportamiento Operativo de Vehículos
  - Mantenimientos Recurrentes
  - Por Site/Zona/Supervisor
  - Cumplimiento y Política
  - Inventario/Características de Vehículos
- **Reportes básicos**: Diario, Semanal, Mensual
- Generación con ReportLab y branding PepsiCo
- **Validaciones robustas**:
  - Rangos de fecha válidos (fecha_inicio <= fecha_fin)
  - Permisos por rol (supervisores solo ven su Site, guardias no acceden)
  - Manejo de historial vacío sin errores

### 🔄 Tareas Automáticas (Celery)
- Colación automática (12:30-13:15)
- Generación de PDFs de cierre
- Tareas programadas con Celery Beat

### 🔔 Sistema de Notificaciones
- Notificaciones en tiempo real vía WebSocket
- Notificaciones push del navegador (Service Worker)
- Notificaciones por email (opcional)
- Sonidos de alerta (opcional)
- Badge con contador de no leídas
- Preferencias de usuario configurables
- Notificaciones para: OT creada/asignada/cerrada/aprobada/rechazada, evidencias importantes

### ✅ Sistema de Validaciones
- **Validadores reutilizables** en `apps/core/validators.py`:
  - RUT chileno (formato y dígito verificador)
  - Formato de patente chilena
  - Formato de correo electrónico
  - Validación de año
  - Validación de rol
  - Validación de rangos de fecha
- **Validaciones integradas** en serializers y views:
  - Usuarios: correo único, RUT único, rol válido
  - Vehículos: patente única, formato válido, datos obligatorios, año válido
  - OT: vehículo existente, no duplicadas, campos obligatorios, reglas de pausa/cierre
  - Guardia: datos mínimos, RUT conductor válido, no OT activa
  - Backups: operativo, no utilizado, no mismo vehículo
  - Reportes: rangos de fecha, permisos por rol

## 🏗️ Arquitectura

### Backend
- **Framework**: Django 5.x + Django REST Framework
- **Base de Datos**: PostgreSQL
- **Cache/Queue**: Redis
- **Tareas Asíncronas**: Celery + Celery Beat
- **Storage**: AWS S3 (LocalStack para desarrollo)
- **Autenticación**: JWT (Simple JWT)
- **Documentación**: drf-spectacular (Swagger/OpenAPI)
- **Filtros**: django-filter

### Frontend
- **Framework**: Next.js 15.5.5 (App Router) con Turbopack
- **Lenguaje**: TypeScript
- **Estilos**: Tailwind CSS
- **Estado Global**: Zustand
- **HTTP Client**: Fetch API con proxy routes
- **Iconos**: Heroicons
- **Notificaciones**: 
  - Toast system personalizado
  - WebSocket para notificaciones en tiempo real
  - Service Worker para push notifications
  - Badge con contador de no leídas
  - Preferencias de usuario configurables

### DevOps
- **Contenedores**: Docker + Docker Compose
- **Gestión de Dependencias**: Poetry (Python) + npm (Node.js)
- **CI/CD**: Preparado para GitHub Actions
- **WebSockets**: Django Channels con Redis como channel layer
- **ASGI Server**: Daphne para soporte HTTP y WebSocket

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker y Docker Compose instalados
- Git instalado
- (Opcional) Python 3.13+ y Node.js 18+ para desarrollo local

### Con Docker Compose (Recomendado)

```bash
# 1. Clonar el repositorio
git clone <tu-repo-url>
cd pgf

# 2. Crear archivo .env
cp .env.example .env
# Editar .env con tus configuraciones

# 3. Iniciar todos los servicios
docker-compose up -d

# 4. Aplicar migraciones
docker-compose exec api poetry run python manage.py migrate

# 5. Crear superusuario
docker-compose exec api poetry run python manage.py createsuperuser

# 6. Acceder a la aplicación
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Swagger Docs: http://localhost:8000/api/docs/
# Admin: http://localhost:8000/admin/
```

Para más detalles, ver [SETUP.md](./SETUP.md)

## 📁 Estructura del Proyecto

```
pgf/
├── apps/                          # Aplicaciones Django
│   ├── users/                     # Usuarios y autenticación
│   │   ├── models.py              # Modelo User con roles
│   │   ├── views.py               # ViewSets y vistas de auth
│   │   ├── serializers.py         # Serializers para API
│   │   ├── permissions.py         # Permisos personalizados
│   │   └── auth_urls.py           # URLs de autenticación
│   ├── core/                      # Utilidades compartidas
│   │   ├── validators.py          # Validadores reutilizables
│   │   └── serializers.py         # Serializers base
│   ├── vehicles/                  # Gestión de vehículos
│   │   ├── models.py              # Vehiculo, HistorialVehiculo, BackupVehiculo
│   │   ├── serializers.py         # Serializers con validaciones
│   │   └── utils.py               # Funciones de historial y backups
│   ├── workorders/                # Órdenes de trabajo
│   │   ├── models.py              # OrdenTrabajo, ItemOT, Pausa, etc.
│   │   ├── views.py               # ViewSets con acciones personalizadas
│   │   ├── serializers.py         # Serializers con validaciones
│   │   ├── services.py            # Lógica de transiciones de estado
│   │   └── tasks_colacion.py     # Tareas Celery para colación
│   ├── drivers/                   # Gestión de choferes
│   ├── scheduling/                # Programación y agenda
│   ├── emergencies/               # Emergencias en ruta
│   ├── reports/                   # Reportes y dashboards
│   │   ├── views.py               # Vistas de reportes con validaciones
│   │   ├── pdf_generator.py      # Generación de PDFs básicos
│   │   └── pdf_generator_completo.py  # Generación de 7 reportes completos
│   ├── notifications/            # Sistema de notificaciones
│   │   ├── models.py              # Modelo Notification
│   │   ├── views.py               # API de notificaciones
│   │   ├── consumers.py          # WebSocket consumers
│   │   └── utils.py               # Utilidades de notificaciones
│   └── inventory/                 # Inventario (futuro)
├── pgf_core/                      # Configuración Django
│   ├── settings/                  # Settings por ambiente
│   │   ├── base.py               # Configuración base
│   │   ├── dev.py                # Desarrollo
│   │   └── prod.py               # Producción
│   ├── urls.py                    # URLs principales
│   ├── celery.py                  # Configuración Celery
│   └── wsgi.py                    # WSGI application
├── frontend/
│   └── pgf-frontend/              # Aplicación Next.js
│       ├── src/
│       │   ├── app/               # App Router de Next.js
│       │   │   ├── api/          # API routes (proxy)
│       │   │   ├── auth/         # Autenticación
│       │   │   ├── dashboard/    # Dashboards
│       │   │   ├── users/        # Gestión de usuarios
│       │   │   ├── vehicles/     # Gestión de vehículos
│       │   │   ├── workorders/   # Órdenes de trabajo
│       │   │   ├── drivers/      # Choferes
│       │   │   ├── scheduling/  # Agenda
│       │   │   ├── emergencies/  # Emergencias
│       │   │   └── reports/      # Reportes
│       │   ├── components/       # Componentes React reutilizables
│       │   ├── hooks/            # Custom hooks
│       │   ├── lib/              # Utilidades y constantes
│       │   ├── store/            # Estado global (Zustand)
│       │   └── middleware.ts     # Middleware de Next.js
│       └── package.json
├── docker-compose.yml             # Configuración Docker Compose
├── Dockerfile                     # Dockerfile del backend
├── pyproject.toml                 # Dependencias Python (Poetry)
└── README.md                      # Este archivo
```

## 🔐 Variables de Entorno

Ver `.env.example` para todas las variables requeridas.

### Backend (Django)
- `SECRET_KEY`: Clave secreta de Django
- `DEBUG`: Modo debug (True/False)
- `DATABASE_URL`: URL de conexión a PostgreSQL
- `CELERY_BROKER_URL`: URL de Redis para Celery (ej: `redis://redis:6379/0`)
- `CELERY_RESULT_BACKEND`: Backend de resultados de Celery
- `REDIS_URL`: URL de Redis para cache
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`: Credenciales S3
- `AWS_STORAGE_BUCKET_NAME`: Nombre del bucket S3
- `AWS_S3_ENDPOINT_URL`: Endpoint de S3 (LocalStack: `http://localstack:4566`)
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`: Configuración SMTP

### Frontend (Next.js)
- `NEXT_PUBLIC_API_BASE_URL`: URL del backend (ej: `http://localhost:8000/api/v1`)
- `NEXT_PUBLIC_S3_ENDPOINT`: Endpoint de S3
- `NEXT_PUBLIC_S3_BUCKET`: Nombre del bucket

## 📚 Documentación API

La documentación interactiva está disponible en:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

### Endpoints Principales

- `/api/v1/auth/` - Autenticación (login, refresh, password reset)
- `/api/v1/users/` - Gestión de usuarios
- `/api/v1/vehicles/` - Gestión de vehículos
- `/api/v1/work/ordenes/` - Órdenes de trabajo
- `/api/v1/drivers/` - Choferes
- `/api/v1/scheduling/` - Programación
- `/api/v1/emergencies/` - Emergencias
- `/api/v1/reports/` - Reportes y dashboards

## 🧪 Testing

### Ejecutar Tests

```bash
# Todas las pruebas
docker-compose exec api poetry run pytest

# Pruebas con cobertura
docker-compose exec api poetry run pytest --cov=apps --cov-report=html

# Pruebas específicas
docker-compose exec api poetry run pytest apps/core/tests/test_validators.py -v

# Generar reportes detallados por módulo
docker-compose exec api poetry run python scripts/run_tests_with_reports.py
```

### Estructura de Tests

El proyecto incluye un sistema completo de pruebas:

- **Validadores** (`apps/core/tests/`): Pruebas de validadores reutilizables
- **Modelos** (`apps/*/tests/test_models.py`): Pruebas de modelos
- **Serializers** (`apps/*/tests/test_serializers.py`): Pruebas de serializers con validaciones
- **Views** (`apps/*/tests/test_views.py`): Pruebas de API endpoints

### Reportes de Pruebas

El script `scripts/run_tests_with_reports.py` genera reportes detallados por módulo:

- **HTML**: Reportes visuales con resultados detallados
- **JSON**: Datos estructurados para análisis
- **TXT**: Logs completos de ejecución
- **JUnit XML**: Compatible con CI/CD
- **Cobertura**: Reportes de cobertura de código

Los reportes se guardan en `test-results/reports/` organizados por módulo.

Ver [scripts/README.md](./scripts/README.md) para más detalles.

## 📝 Migraciones

```bash
# Crear migraciones
docker-compose exec api poetry run python manage.py makemigrations

# Aplicar migraciones
docker-compose exec api poetry run python manage.py migrate

# Ver estado de migraciones
docker-compose exec api poetry run python manage.py showmigrations
```

## 🔧 Comandos Útiles

```bash
# Ver logs
docker-compose logs -f api          # Backend
docker-compose logs -f web          # Frontend
docker-compose logs -f worker       # Celery worker
docker-compose logs -f beat         # Celery beat

# Reiniciar servicios
docker-compose restart api web worker beat

# Acceder a shell del backend
docker-compose exec api poetry run python manage.py shell

# Crear datos demo
docker-compose exec api poetry run python manage.py seed_demo

# Ver estado de servicios
docker-compose ps
```

## 🎨 Identidad Visual

El sistema utiliza la identidad visual de PepsiCo:
- **Color Principal**: #003DA5 (PepsiCo Blue)
- Aplicado en botones principales, links activos y elementos destacados

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es privado y propiedad de PepsiCo.

## 👥 Autores

- **Diego Alvarez** - dr.alvarez@duocuc.cl
- **Luis Diaz** - lu.diaza@duocuc.cl

## 🙏 Agradecimientos

- Django REST Framework
- Next.js
- Tailwind CSS
- Celery
- ReportLab

---

**Versión**: 2.0.0  
**Última actualización**: Noviembre 2024

## 📝 Changelog

### v2.0.0 (Noviembre 2024)
- ✅ Sistema completo de validaciones implementado
- ✅ Sistema de notificaciones en tiempo real (WebSocket + Push)
- ✅ Historial completo de vehículos y backups
- ✅ 7 tipos de reportes PDF completos
- ✅ Cálculo automático de SLA y tiempos en taller
- ✅ Evidencias con soporte hasta 3GB
- ✅ Preferencias de usuario para notificaciones

### v1.0.0 (2024)
- 🎉 Versión inicial del sistema
