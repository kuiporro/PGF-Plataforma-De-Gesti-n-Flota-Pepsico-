#!/bin/bash
# ============================================================================
# Script para generar dump del esquema SQL desde PostgreSQL
# ============================================================================
# Uso: ./scripts/dump_schema.sh [output_file]
# ============================================================================

set -e

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Archivo de salida (por defecto)
OUTPUT_FILE="${1:-docs/ESQUEMA_SQL_FROM_DB.sql}"

echo -e "${GREEN}=== Generando dump del esquema SQL desde PostgreSQL ===${NC}"

# Intentar leer DATABASE_URL desde .env o usar valores por defecto
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep DATABASE_URL | xargs)
fi

# Valores por defecto (desde docker-compose.yml y settings)
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-pgf}"
DB_USER="${POSTGRES_USER:-pgf}"
DB_PASSWORD="${POSTGRES_PASSWORD:-pgf}"

# Si existe DATABASE_URL, parsearlo
if [ ! -z "$DATABASE_URL" ]; then
    echo -e "${YELLOW}Usando DATABASE_URL de variable de entorno${NC}"
    # Parsear DATABASE_URL (formato: postgres://user:password@host:port/dbname)
    DB_URL=$(echo $DATABASE_URL | sed -e 's|postgres://||' -e 's|postgresql://||')
    DB_USER=$(echo $DB_URL | cut -d: -f1)
    DB_PASSWORD=$(echo $DB_URL | cut -d: -f2 | cut -d@ -f1)
    DB_HOST=$(echo $DB_URL | cut -d@ -f2 | cut -d: -f1)
    DB_PORT=$(echo $DB_URL | cut -d: -f3 | cut -d/ -f1)
    DB_NAME=$(echo $DB_URL | cut -d/ -f2)
fi

echo -e "${GREEN}Configuración de conexión:${NC}"
echo -e "  Host: ${DB_HOST}"
echo -e "  Port: ${DB_PORT}"
echo -e "  Database: ${DB_NAME}"
echo -e "  User: ${DB_USER}"
echo ""

# Verificar si pg_dump está instalado
if ! command -v pg_dump &> /dev/null; then
    echo -e "${RED}Error: pg_dump no está instalado${NC}"
    echo -e "${YELLOW}Instalación:${NC}"
    echo "  Ubuntu/Debian: sudo apt-get install postgresql-client"
    echo "  macOS: brew install postgresql"
    echo "  Windows: Descargar desde https://www.postgresql.org/download/"
    exit 1
fi

# Verificar conexión a la base de datos
echo -e "${GREEN}Verificando conexión a la base de datos...${NC}"
export PGPASSWORD="$DB_PASSWORD"
if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${RED}Error: No se pudo conectar a la base de datos${NC}"
    echo -e "${YELLOW}Verifica:${NC}"
    echo "  1. Que la base de datos esté corriendo"
    echo "  2. Que las credenciales sean correctas"
    echo "  3. Que el host sea accesible (si es 'db', asegúrate de estar en Docker)"
    exit 1
fi

echo -e "${GREEN}✓ Conexión exitosa${NC}"
echo ""

# Crear directorio si no existe
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Generar dump del esquema (solo estructura, sin datos)
echo -e "${GREEN}Generando dump del esquema...${NC}"
pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -d "$DB_NAME" \
    -U "$DB_USER" \
    -s \
    -F p \
    -E UTF-8 \
    --no-owner \
    --no-privileges \
    -f "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dump generado exitosamente${NC}"
    echo -e "${GREEN}Archivo: ${OUTPUT_FILE}${NC}"
    echo ""
    echo -e "${YELLOW}Para usar en dbdiagram.io:${NC}"
    echo "  1. Abre https://dbdiagram.io"
    echo "  2. Haz clic en 'Import' o 'New Project'"
    echo "  3. Selecciona 'PostgreSQL'"
    echo "  4. Pega el contenido del archivo generado"
    echo ""
    # Mostrar tamaño del archivo
    FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    echo -e "Tamaño del archivo: ${FILE_SIZE}"
else
    echo -e "${RED}Error al generar el dump${NC}"
    exit 1
fi

# Limpiar variable de entorno
unset PGPASSWORD

