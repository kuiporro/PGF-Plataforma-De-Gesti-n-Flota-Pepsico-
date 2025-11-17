# 🚀 Guía de Instalación Completa - PGF PepsiCo

Esta guía te llevará paso a paso desde clonar el repositorio hasta tener el sistema funcionando completamente.

## 📋 Prerrequisitos

### Software Requerido

1. **Git** (versión 2.30+)
   - Windows: Descargar de [git-scm.com](https://git-scm.com/download/win)
   - Mac: `brew install git`
   - Linux: `sudo apt-get install git`

2. **Docker Desktop** (versión 20.10+)
   - Windows/Mac: Descargar de [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
   - Linux: Seguir [guía oficial](https://docs.docker.com/engine/install/)

3. **Docker Compose** (incluido en Docker Desktop)
   - Verificar: `docker-compose --version`

### Verificar Instalaciones

```bash
# Verificar Git
git --version

# Verificar Docker
docker --version

# Verificar Docker Compose
docker-compose --version
```

## 📥 Paso 1: Clonar el Repositorio

```bash
# Clonar el repositorio
git clone <URL_DEL_REPOSITORIO>
cd pgf

# Verificar que estás en la rama correcta
git branch
```

## ⚙️ Paso 2: Configurar Variables de Entorno

### 2.1 Crear archivo .env

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar el archivo .env con tu editor preferido
# Windows: notepad .env
# Mac/Linux: nano .env o vim .env
```

### 2.2 Configurar Variables Mínimas

Abre `.env` y configura al menos estas variables:

```env
# Django
SECRET_KEY=tu-clave-secreta-generada-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de Datos
DATABASE_URL=postgresql://pgf_user:pgf_password@db:5432/pgf_db

# Redis
REDIS_URL=redis://redis:6379/2
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# S3 (LocalStack para desarrollo)
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_STORAGE_BUCKET_NAME=pgf-evidencias
AWS_S3_ENDPOINT_URL=http://localstack:4566
AWS_S3_REGION_NAME=us-east-1

# Email (opcional para desarrollo)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
EMAIL_USE_TLS=True

# Frontend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_S3_ENDPOINT=http://localhost:4566
NEXT_PUBLIC_S3_BUCKET=pgf-evidencias
```

### 2.3 Generar SECRET_KEY

```bash
# En Windows (PowerShell)
python -c "import secrets; print(secrets.token_urlsafe(50))"

# En Mac/Linux
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Copia el resultado y pégalo en `SECRET_KEY` del archivo `.env`.

## 🐳 Paso 3: Construir e Iniciar Contenedores

### 3.1 Construir Imágenes

```bash
# Construir todas las imágenes
docker-compose build

# Esto puede tardar varios minutos la primera vez
```

### 3.2 Iniciar Servicios

```bash
# Iniciar todos los servicios en segundo plano
docker-compose up -d

# Verificar que todos los servicios estén corriendo
docker-compose ps
```

Deberías ver algo como:
```
NAME                STATUS              PORTS
pgf-api             Up                 0.0.0.0:8000->8000/tcp
pgf-web             Up                 0.0.0.0:3000->3000/tcp
pgf-db              Up                 5432/tcp
pgf-redis           Up                 6379/tcp
pgf-localstack      Up                 4566/tcp
pgf-worker          Up
pgf-beat            Up
```

## 🗄️ Paso 4: Configurar Base de Datos

### 4.1 Aplicar Migraciones

```bash
# Aplicar todas las migraciones
docker-compose exec api poetry run python manage.py migrate

# Verificar estado de migraciones
docker-compose exec api poetry run python manage.py showmigrations
```

### 4.2 Crear Superusuario

```bash
# Crear usuario administrador
docker-compose exec api poetry run python manage.py createsuperuser

# Seguir las instrucciones:
# - Username: admin (o el que prefieras)
# - Email: admin@example.com
# - Password: (ingresar una contraseña segura)
```

## 🪣 Paso 5: Configurar S3 (LocalStack)

### 5.1 Crear Bucket

```bash
# Crear bucket en LocalStack
docker-compose exec localstack aws --endpoint-url=http://localhost:4566 s3 mb s3://pgf-evidencias

# Verificar que se creó
docker-compose exec localstack aws --endpoint-url=http://localhost:4566 s3 ls
```

### 5.2 Configurar CORS (Opcional)

```bash
# Si tienes un archivo cors.json, aplicarlo
docker-compose exec localstack aws --endpoint-url=http://localhost:4566 s3api put-bucket-cors --bucket pgf-evidencias --cors-configuration file://cors.json
```

## ✅ Paso 6: Verificar Instalación

### 6.1 Verificar Backend

```bash
# Ver logs del backend
docker-compose logs api

# Probar endpoint de salud (si existe)
curl http://localhost:8000/api/health/
```

### 6.2 Verificar Frontend

Abre tu navegador y visita:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/api/docs/
- **Admin Django**: http://localhost:8000/admin/

### 6.3 Verificar Celery

```bash
# Ver logs del worker
docker-compose logs worker

# Ver logs de beat
docker-compose logs beat
```

## 🧪 Paso 7: Crear Datos de Prueba (Opcional)

```bash
# Si existe un comando de seed
docker-compose exec api poetry run python manage.py seed_demo
```

## 🔧 Paso 8: Solución de Problemas Comunes

### Problema: Contenedores no inician

```bash
# Ver logs detallados
docker-compose logs

# Reiniciar servicios
docker-compose down
docker-compose up -d
```

### Problema: Error de conexión a base de datos

```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps db

# Ver logs de PostgreSQL
docker-compose logs db

# Reiniciar base de datos
docker-compose restart db
```

### Problema: Migraciones fallan

```bash
# Verificar estado de migraciones
docker-compose exec api poetry run python manage.py showmigrations

# Si hay migraciones pendientes, aplicarlas
docker-compose exec api poetry run python manage.py migrate

# Si hay conflictos, verificar logs
docker-compose logs api
```

### Problema: Frontend no carga

```bash
# Ver logs del frontend
docker-compose logs web

# Reconstruir frontend
docker-compose build web
docker-compose up -d web
```

### Problema: Celery no ejecuta tareas

```bash
# Verificar que Redis esté corriendo
docker-compose ps redis

# Reiniciar worker y beat
docker-compose restart worker beat

# Ver logs
docker-compose logs worker
```

## 📊 Paso 9: Verificar Funcionalidades

### 9.1 Login

1. Ir a http://localhost:3000
2. Hacer clic en "Login"
3. Ingresar credenciales del superusuario creado
4. Verificar que redirige al dashboard correcto

### 9.2 Crear Usuario

1. Ir a "Usuarios" en el menú
2. Hacer clic en "Nuevo Usuario"
3. Completar formulario
4. Verificar que se crea correctamente

### 9.3 Crear Vehículo

1. Ir a "Vehículos"
2. Hacer clic en "Nuevo Vehículo"
3. Completar formulario
4. Verificar que se crea correctamente

### 9.4 Crear OT

1. Ir a "Órdenes de Trabajo"
2. Hacer clic en "Nueva OT"
3. Seleccionar vehículo y completar formulario
4. Verificar que se crea correctamente

## 🎉 ¡Listo!

Si todos los pasos anteriores se completaron exitosamente, tu sistema PGF está funcionando completamente.

## 📝 Notas Adicionales

### Desarrollo Local (Sin Docker)

Si prefieres desarrollar sin Docker:

#### Backend

```bash
# Instalar Poetry
pip install poetry

# Instalar dependencias
poetry install

# Activar entorno virtual
poetry shell

# Configurar base de datos local
# Editar .env con DATABASE_URL local

# Aplicar migraciones
poetry run python manage.py migrate

# Ejecutar servidor
poetry run python manage.py runserver

# En otra terminal, ejecutar Celery
poetry run celery -A pgf_core worker -l info
poetry run celery -A pgf_core beat -l info
```

#### Frontend

```bash
cd frontend/pgf-frontend

# Instalar dependencias
npm install

# Ejecutar servidor de desarrollo
npm run dev
```

### Actualizar el Sistema

```bash
# Obtener últimos cambios
git pull

# Reconstruir imágenes
docker-compose build

# Reiniciar servicios
docker-compose down
docker-compose up -d

# Aplicar nuevas migraciones
docker-compose exec api poetry run python manage.py migrate
```

### Backup de Base de Datos

```bash
# Crear backup
docker-compose exec db pg_dump -U pgf_user pgf_db > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U pgf_user pgf_db < backup.sql
```

---

**¿Problemas?** Revisa la sección de Troubleshooting en el README.md o los logs de los servicios.

