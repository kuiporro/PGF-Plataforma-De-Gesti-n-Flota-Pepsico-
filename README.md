# PGF - Plataforma de Gestión de Flota

Sistema completo de gestión de flota vehicular con órdenes de trabajo, presupuestos, evidencias y más.

## 🏗️ Arquitectura

- **Backend**: Django REST Framework + PostgreSQL + Celery + Redis
- **Frontend**: Next.js 15 (App Router) + TypeScript + Tailwind CSS
- **Storage**: AWS S3 (LocalStack para desarrollo)
- **Autenticación**: JWT (Simple JWT)

## 📋 Características

### Backend (Django)
- ✅ Gestión de usuarios con roles (Admin, Supervisor, Mecánico, Guardia, Sponsor)
- ✅ Gestión de vehículos
- ✅ Órdenes de trabajo con estados (Abierta, En Ejecución, En QA, Cerrada, Anulada)
- ✅ Items de orden de trabajo (Repuestos y Servicios)
- ✅ Presupuestos con aprobaciones
- ✅ Evidencias (Fotos, PDFs) almacenadas en S3
- ✅ Checklists de calidad
- ✅ Pausas en órdenes de trabajo
- ✅ Auditoría de acciones
- ✅ Generación de PDFs de cierre (Celery)
- ✅ API REST completa con documentación Swagger

### Frontend (Next.js)
- ✅ Dashboard con KPIs
- ✅ Gestión de usuarios
- ✅ Gestión de vehículos
- ✅ Gestión de órdenes de trabajo
- ✅ Carga de evidencias con presigned URLs
- ✅ Sistema de autenticación con refresh tokens
- ✅ Control de acceso basado en roles
- ✅ Manejo robusto de errores y validación de JSON

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker y Docker Compose
- Python 3.13+ (para desarrollo local)
- Node.js 18+ (para desarrollo local)

### Con Docker Compose (Recomendado)

1. Clonar el repositorio:
```bash
git clone <tu-repo-url>
cd pgf
```

2. Crear archivo `.env` en la raíz:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. Iniciar servicios:
```bash
docker-compose up -d
```

4. Crear superusuario:
```bash
docker-compose exec api poetry run python manage.py createsuperuser
```

5. Acceder a:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/api/docs/
   - Admin: http://localhost:8000/admin/

### Desarrollo Local

#### Backend

```bash
# Instalar dependencias
poetry install

# Configurar base de datos
poetry run python manage.py migrate

# Crear superusuario
poetry run python manage.py createsuperuser

# Ejecutar servidor
poetry run python manage.py runserver

# Ejecutar Celery worker (en otra terminal)
poetry run celery -A pgf_core worker -l info
```

#### Frontend

```bash
cd frontend/pgf-frontend

# Instalar dependencias
npm install

# Ejecutar servidor de desarrollo
npm run dev
```

## 📁 Estructura del Proyecto

```
pgf/
├── apps/                    # Aplicaciones Django
│   ├── users/              # Usuarios y autenticación
│   ├── vehicles/           # Gestión de vehículos
│   └── workorders/         # Órdenes de trabajo
├── pgf_core/               # Configuración Django
│   ├── settings/          # Settings por ambiente
│   └── urls.py            # URLs principales
├── frontend/
│   └── pgf-frontend/      # Aplicación Next.js
│       ├── src/
│       │   ├── app/       # App Router de Next.js
│       │   ├── components/# Componentes React
│       │   ├── hooks/     # Custom hooks
│       │   └── lib/       # Utilidades
├── docker-compose.yml      # Configuración Docker
├── Dockerfile             # Dockerfile del backend
└── pyproject.toml        # Dependencias Python
```

## 🔐 Variables de Entorno

Ver `.env.example` para todas las variables requeridas.

### Backend (Django)
- `SECRET_KEY`: Clave secreta de Django
- `DEBUG`: Modo debug (True/False)
- `DATABASE_URL`: URL de conexión a PostgreSQL
- `CELERY_BROKER_URL`: URL de Redis para Celery
- `AWS_*`: Configuración de S3

### Frontend (Next.js)
- `NEXT_PUBLIC_API_BASE_URL`: URL del backend
- `NEXT_PUBLIC_S3_ENDPOINT`: Endpoint de S3
- `NEXT_PUBLIC_S3_BUCKET`: Nombre del bucket

## 🧪 Testing

```bash
# Backend
poetry run pytest

# Frontend
cd frontend/pgf-frontend
npm test
```

## 📝 Migraciones

```bash
# Crear migraciones
poetry run python manage.py makemigrations

# Aplicar migraciones
poetry run python manage.py migrate
```

## 🔧 Comandos Útiles

```bash
# Seed de datos demo
docker-compose exec api poetry run python manage.py seed_demo

# Ver logs
docker-compose logs -f api
docker-compose logs -f web

# Reiniciar servicios
docker-compose restart api web
```

## 📚 Documentación API

La documentación interactiva está disponible en:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## 🐛 Troubleshooting

### Error de conexión a base de datos
- Verificar que PostgreSQL esté corriendo: `docker-compose ps db`
- Verificar variables de entorno en `.env`

### Error "Unexpected end of JSON input"
- ✅ **Corregido**: Se implementó manejo robusto de errores en todas las llamadas fetch

### Error "Failed to fetch"
- ✅ **Corregido**: Se agregó manejo de errores en DashboardLayout y todas las rutas API

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es privado.

## 👥 Autores

- Kuiper - diaz526.ld@gmail.com

## 🙏 Agradecimientos

- Django REST Framework
- Next.js
- Tailwind CSS

