# 🚀 Guía de Instalación y Configuración - PGF

Esta guía te ayudará a instalar y configurar el proyecto PGF (Plataforma de Gestión de Flota) desde cero en un nuevo equipo.

## 📋 Requisitos Previos

### Software Necesario

1. **Git** (versión 2.0+)
   - Windows: Descargar desde [git-scm.com](https://git-scm.com/download/win)
   - Verificar instalación: `git --version`

2. **Docker Desktop** (versión 20.10+)
   - Windows: Descargar desde [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
   - Verificar instalación: `docker --version` y `docker-compose --version`

3. **Node.js** (versión 18.0+)
   - Descargar desde [nodejs.org](https://nodejs.org/)
   - Verificar instalación: `node --version` y `npm --version`

4. **Python** (versión 3.11+)
   - Descargar desde [python.org](https://www.python.org/downloads/)
   - Verificar instalación: `python --version`

5. **Poetry** (gestor de dependencias Python)
   - Instalar: `pip install poetry`
   - Verificar instalación: `poetry --version`

## 📥 Paso 1: Clonar el Repositorio

```bash
# Clonar el repositorio desde GitHub
git clone https://github.com/kuiporro/PGF-Plataforma-De-Gesti-n-Flota-Pepsico-.git

# Entrar al directorio del proyecto
cd PGF-Plataforma-De-Gesti-n-Flota-Pepsico-
```

## 🔧 Paso 2: Configurar Variables de Entorno

### Backend (.env)

Crear archivo `.env` en la raíz del proyecto:

```bash
# Copiar el archivo de ejemplo (si existe)
cp .env.example .env

# O crear manualmente
```

Contenido mínimo del `.env`:

```env
# Django
DEBUG=True
SECRET_KEY=tu-secret-key-super-segura-aqui
ALLOWED_HOSTS=localhost,127.0.0.1,pgf-api

# Base de datos
DATABASE_URL=postgresql://pgf_user:pgf_password@postgres:5432/pgf_db

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# AWS S3 (LocalStack para desarrollo)
USE_LOCALSTACK_S3=1
AWS_STORAGE_BUCKET_NAME=pgf-evidencias
AWS_DEFAULT_REGION=us-east-1
AWS_ENDPOINT_URL=http://localstack:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test

# Frontend URL (para emails de reset de contraseña)
FRONTEND_URL=http://localhost:3000

# Email (Gmail App Password)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=tu-email@gmail.com

# API Base URL (para el frontend)
API_BASE=http://pgf-api:8000/api/v1
```

### Frontend (.env.local)

Crear archivo `.env.local` en `frontend/pgf-frontend/`:

```env
# URL del backend API
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1

# API Base (para proxy routes)
API_BASE=http://pgf-api:8000/api/v1
```

## 🐳 Paso 3: Iniciar Servicios con Docker

### Verificar Docker

```bash
# Verificar que Docker está corriendo
docker ps

# Si no está corriendo, iniciar Docker Desktop
```

### Construir e Iniciar Contenedores

```bash
# Construir imágenes (primera vez)
docker-compose build

# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### Servicios que se Inician

- **postgres**: Base de datos PostgreSQL (puerto 5432)
- **redis**: Cache y broker de Celery (puerto 6379)
- **localstack**: S3 local para desarrollo (puerto 4566)
- **api**: Backend Django (puerto 8000)
- **frontend**: Frontend Next.js (puerto 3000)
- **worker**: Celery worker (tareas asíncronas)
- **beat**: Celery beat (tareas programadas)

## 🗄️ Paso 4: Configurar Base de Datos

### Crear Base de Datos

```bash
# Entrar al contenedor de la API
docker-compose exec api bash

# Dentro del contenedor, ejecutar migraciones
poetry run python manage.py migrate

# Crear superusuario (opcional)
poetry run python manage.py createsuperuser
```

### Salir del Contenedor

```bash
exit
```

## 📦 Paso 5: Instalar Dependencias del Frontend

```bash
# Entrar al directorio del frontend
cd frontend/pgf-frontend

# Instalar dependencias
npm install

# O si usas yarn
yarn install
```

## 🚀 Paso 6: Iniciar el Proyecto

### Opción A: Todo con Docker (Recomendado)

```bash
# Desde la raíz del proyecto
docker-compose up -d

# Verificar que todos los servicios están corriendo
docker-compose ps
```

### Opción B: Desarrollo Local (Sin Docker)

#### Backend

```bash
# Desde la raíz del proyecto
cd backend  # O donde esté el manage.py

# Activar entorno virtual de Poetry
poetry shell

# Instalar dependencias
poetry install

# Ejecutar migraciones
poetry run python manage.py migrate

# Crear superusuario
poetry run python manage.py createsuperuser

# Iniciar servidor
poetry run python manage.py runserver
```

#### Frontend

```bash
# Desde frontend/pgf-frontend
cd frontend/pgf-frontend

# Instalar dependencias (si no lo hiciste)
npm install

# Iniciar servidor de desarrollo
npm run dev
```

## ✅ Paso 7: Verificar Instalación

### Verificar Backend

1. Abrir navegador: `http://localhost:8000/api/v1/`
2. Deberías ver la documentación de la API (Swagger/OpenAPI)

### Verificar Frontend

1. Abrir navegador: `http://localhost:3000`
2. Deberías ver la página de login

### Verificar Base de Datos

```bash
# Conectar a PostgreSQL
docker-compose exec postgres psql -U pgf_user -d pgf_db

# Listar tablas
\dt

# Salir
\q
```

## 🔐 Paso 8: Crear Usuario Administrador

### Opción A: Desde Django Admin

1. Acceder a: `http://localhost:8000/admin/`
2. Login con superusuario creado
3. Crear usuarios desde el panel

### Opción B: Desde la API

```bash
# Hacer POST a /api/v1/users/
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "password123",
    "rol": "ADMIN"
  }'
```

### Opción C: Desde el Frontend

1. Acceder a: `http://localhost:3000/auth/login`
2. Si no hay usuarios, el sistema permite crear el primer usuario como ADMIN

## 🧪 Paso 9: Ejecutar Tests (Opcional)

```bash
# Tests del backend
docker-compose exec api poetry run pytest

# Tests del frontend
cd frontend/pgf-frontend
npm test
```

## 🔍 Solución de Problemas Comunes

### Error: Puerto ya en uso

```bash
# Ver qué está usando el puerto
# Windows PowerShell
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Detener el proceso o cambiar el puerto en docker-compose.yml
```

### Error: Base de datos no existe

```bash
# Crear base de datos manualmente
docker-compose exec postgres psql -U postgres
CREATE DATABASE pgf_db;
CREATE USER pgf_user WITH PASSWORD 'pgf_password';
GRANT ALL PRIVILEGES ON DATABASE pgf_db TO pgf_user;
\q
```

### Error: Migraciones pendientes

```bash
# Ejecutar migraciones
docker-compose exec api poetry run python manage.py migrate

# Si hay conflictos, hacer makemigrations primero
docker-compose exec api poetry run python manage.py makemigrations
```

### Error: Docker no inicia

1. Verificar que Docker Desktop está corriendo
2. Reiniciar Docker Desktop
3. Verificar recursos del sistema (RAM, CPU)

### Error: Frontend no se conecta al backend

1. Verificar que `NEXT_PUBLIC_API_BASE_URL` en `.env.local` apunta al backend correcto
2. Verificar que el backend está corriendo: `http://localhost:8000/api/v1/`
3. Verificar CORS en `pgf_core/settings/base.py`

## 📝 Comandos Útiles

### Docker

```bash
# Ver logs de un servicio específico
docker-compose logs -f api
docker-compose logs -f frontend

# Reiniciar un servicio
docker-compose restart api

# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (⚠️ elimina datos)
docker-compose down -v

# Reconstruir un servicio
docker-compose build api
docker-compose up -d api
```

### Backend

```bash
# Ejecutar migraciones
docker-compose exec api poetry run python manage.py migrate

# Crear migraciones
docker-compose exec api poetry run python manage.py makemigrations

# Shell de Django
docker-compose exec api poetry run python manage.py shell

# Crear superusuario
docker-compose exec api poetry run python manage.py createsuperuser

# Recolectar archivos estáticos
docker-compose exec api poetry run python manage.py collectstatic --noinput
```

### Frontend

```bash
# Instalar dependencias
cd frontend/pgf-frontend
npm install

# Iniciar desarrollo
npm run dev

# Construir para producción
npm run build

# Iniciar producción
npm start
```

## 🎯 Próximos Pasos

1. **Configurar Email**: Actualizar credenciales de Gmail en `.env`
2. **Configurar S3**: Para producción, cambiar a AWS S3 real
3. **Crear Usuarios**: Crear usuarios de prueba con diferentes roles
4. **Configurar Celery Beat**: Verificar que las tareas programadas funcionan
5. **Revisar Logs**: Monitorear logs para detectar errores

## 📚 Recursos Adicionales

- **Documentación Django**: https://docs.djangoproject.com/
- **Documentación Next.js**: https://nextjs.org/docs
- **Documentación Docker**: https://docs.docker.com/
- **Documentación Poetry**: https://python-poetry.org/docs/

## ⚠️ Notas Importantes

1. **Desarrollo vs Producción**: Esta guía es para desarrollo local. Para producción, configurar:
   - HTTPS
   - Variables de entorno seguras
   - Base de datos en servidor dedicado
   - S3 real (no LocalStack)

2. **Seguridad**: Nunca subir `.env` a Git. Está en `.gitignore`

3. **Backups**: Configurar backups regulares de la base de datos

4. **Performance**: En producción, usar:
   - Nginx como reverse proxy
   - Gunicorn/uWSGI para Django
   - CDN para archivos estáticos

---

**¿Problemas?** Revisa los logs con `docker-compose logs` o consulta la documentación del proyecto.

