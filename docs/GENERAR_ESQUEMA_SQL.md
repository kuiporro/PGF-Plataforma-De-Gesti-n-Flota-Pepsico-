# Generar Esquema SQL desde PostgreSQL

Este documento explica cómo generar el esquema SQL directamente desde la base de datos PostgreSQL para usar en dbdiagram.io.

## Método 1: Script Automático (Recomendado)

### Usando el script bash

```bash
# Desde la raíz del proyecto
./scripts/dump_schema_simple.sh

# O especificando el archivo de salida
./scripts/dump_schema_simple.sh docs/ESQUEMA_SQL_FROM_DB.sql
```

El script:
- ✅ Lee la configuración desde `.env` o variables de entorno
- ✅ Detecta automáticamente si la BD está en Docker
- ✅ Verifica la conexión antes de generar el dump
- ✅ Genera solo el esquema (sin datos)
- ✅ Listo para usar en dbdiagram.io

### Requisitos

- `pg_dump` instalado (cliente de PostgreSQL)
- Base de datos corriendo y accesible

**Instalación de pg_dump:**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-client

# macOS
brew install postgresql

# Windows
# Descargar desde https://www.postgresql.org/download/
```

## Método 2: Desde Docker

Si la base de datos está corriendo en Docker:

```bash
# Generar dump desde el contenedor
docker exec pgf-db pg_dump \
    -U pgf \
    -d pgf \
    -s \
    --no-owner \
    --no-privileges \
    > docs/ESQUEMA_SQL_FROM_DB.sql
```

**Parámetros:**
- `-s`: Solo esquema (sin datos)
- `--no-owner`: No incluir comandos de ownership
- `--no-privileges`: No incluir comandos de privilegios

## Método 3: Comando pg_dump Manual

Si tienes acceso directo a PostgreSQL:

```bash
pg_dump \
    -h localhost \
    -p 5432 \
    -d pgf \
    -U pgf \
    -s \
    -F p \
    -E UTF-8 \
    --no-owner \
    --no-privileges \
    -f docs/ESQUEMA_SQL_FROM_DB.sql
```

**Parámetros explicados:**
- `-h`: Host de la base de datos
- `-p`: Puerto (por defecto 5432)
- `-d`: Nombre de la base de datos
- `-U`: Usuario
- `-s`: Solo esquema (estructura, sin datos)
- `-F p`: Formato plain text (SQL)
- `-E UTF-8`: Encoding UTF-8
- `--no-owner`: No incluir comandos de ownership
- `--no-privileges`: No incluir comandos de privilegios
- `-f`: Archivo de salida

## Usar en dbdiagram.io

Una vez generado el archivo SQL:

1. Ve a [https://dbdiagram.io](https://dbdiagram.io)
2. Haz clic en **"New Project"** o **"Import"**
3. Selecciona **"PostgreSQL"**
4. Copia y pega el contenido del archivo generado (`ESQUEMA_SQL_FROM_DB.sql`)
5. El diagrama se renderizará automáticamente

## Configuración de Conexión

El script lee la configuración en este orden:

1. **Variables de entorno:**
   ```bash
   export POSTGRES_HOST=localhost
   export POSTGRES_PORT=5432
   export POSTGRES_DB=pgf
   export POSTGRES_USER=pgf
   export POSTGRES_PASSWORD=pgf
   ```

2. **Archivo `.env`:**
   ```env
   DATABASE_URL=postgres://pgf:pgf@localhost:5432/pgf
   # O variables individuales
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=pgf
   POSTGRES_USER=pgf
   POSTGRES_PASSWORD=pgf
   ```

3. **Valores por defecto:**
   - Host: `localhost` (o `db` si está en Docker)
   - Port: `5432`
   - Database: `pgf`
   - User: `pgf`
   - Password: `pgf`

## Solución de Problemas

### Error: "pg_dump no está instalado"

**Solución:**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-client

# macOS
brew install postgresql

# O usar desde Docker
docker exec pgf-db pg_dump ...
```

### Error: "No se pudo conectar a la base de datos"

**Verifica:**
1. Que la base de datos esté corriendo
2. Que las credenciales sean correctas
3. Que el host sea accesible

**Si está en Docker:**
```bash
# Verificar que el contenedor esté corriendo
docker ps | grep pgf-db

# Si no está corriendo, iniciarlo
docker-compose up -d db
```

### Error: "Host no resuelto"

Si la BD está en Docker y usas `localhost`, intenta:
- Usar `db` como host (nombre del servicio en docker-compose)
- O usar el script que detecta Docker automáticamente

## Archivos Generados

- `docs/ESQUEMA_SQL_FROM_DB.sql` - Esquema SQL generado desde la BD
- `docs/ESQUEMA_SQL_COMPLETO.sql` - Esquema SQL manual (referencia)
- `docs/MER_DIAGRAMA.dbml` - Diagrama en formato DBML

## Comparación de Métodos

| Método | Ventajas | Desventajas |
|--------|----------|-------------|
| Script bash | Automático, detecta Docker | Requiere pg_dump instalado |
| Docker exec | No requiere pg_dump local | Requiere Docker corriendo |
| pg_dump manual | Control total | Requiere configuración manual |

## Notas

- El dump generado contiene **solo el esquema** (estructura), no los datos
- Los comandos de ownership y privilegios se omiten para compatibilidad
- El archivo está en formato UTF-8 para compatibilidad con dbdiagram.io
- Puedes regenerar el esquema en cualquier momento ejecutando el script

