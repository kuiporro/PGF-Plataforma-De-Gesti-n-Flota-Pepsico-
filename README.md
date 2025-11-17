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
- Validación de RUT chileno

### 🚗 Gestión de Vehículos
- CRUD completo de vehículos
- Estados: Activo, En Espera, En Mantenimiento, Baja
- Tipos: Eléctrico, Diésel, Utilitario, Reparto, Ventas, Respaldo
- Categorías: Reparto, Ventas, Respaldo
- Ingreso y salida de vehículos al taller
- Evidencias fotográficas (S3)
- Historial de mantenimientos

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
- Evidencias fotográficas
- Auditoría completa de acciones

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
- **Reportes PDF**:
  - Diario
  - Semanal
  - Mensual
- Generación con ReportLab y branding PepsiCo

### 🔄 Tareas Automáticas (Celery)
- Colación automática (12:30-13:15)
- Generación de PDFs de cierre
- Tareas programadas con Celery Beat

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
- **Notificaciones**: Toast system personalizado

### DevOps
- **Contenedores**: Docker + Docker Compose
- **Gestión de Dependencias**: Poetry (Python) + npm (Node.js)
- **CI/CD**: Preparado para GitHub Actions

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
│   ├── vehicles/                  # Gestión de vehículos
│   ├── workorders/                # Órdenes de trabajo
│   │   ├── models.py              # OrdenTrabajo, ItemOT, Pausa, etc.
│   │   ├── views.py               # ViewSets con acciones personalizadas
│   │   ├── services.py            # Lógica de transiciones de estado
│   │   └── tasks_colacion.py     # Tareas Celery para colación
│   ├── drivers/                   # Gestión de choferes
│   ├── scheduling/                # Programación y agenda
│   ├── emergencies/               # Emergencias en ruta
│   ├── reports/                   # Reportes y dashboards
│   │   ├── views.py               # Vistas de reportes
│   │   └── pdf_generator.py      # Generación de PDFs
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

Ver [PLAN_PRUEBAS.md](./PLAN_PRUEBAS.md) para el plan completo de pruebas.

### Ejecutar Tests

```bash
# Backend
docker-compose exec api poetry run pytest

# Frontend
cd frontend/pgf-frontend
npm test
```

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

## 🐛 Troubleshooting

### Error de conexión a base de datos
- Verificar que PostgreSQL esté corriendo: `docker-compose ps db`
- Verificar variables de entorno en `.env`
- Verificar logs: `docker-compose logs db`

### Error "Unexpected end of JSON input"
- ✅ **Corregido**: Se implementó manejo robusto de errores en todas las llamadas fetch

### Error "Failed to fetch"
- ✅ **Corregido**: Se agregó manejo de errores en DashboardLayout y todas las rutas API

### Error de migraciones
- Verificar que la base de datos esté inicializada
- Ejecutar: `docker-compose exec api poetry run python manage.py migrate`

### Celery no ejecuta tareas
- Verificar que Redis esté corriendo: `docker-compose ps redis`
- Verificar logs del worker: `docker-compose logs worker`

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

- **Kuiper** - diaz526.ld@gmail.com

## 🙏 Agradecimientos

- Django REST Framework
- Next.js
- Tailwind CSS
- Celery
- ReportLab

---

**Versión**: 1.0.0  
**Última actualización**: 2024
