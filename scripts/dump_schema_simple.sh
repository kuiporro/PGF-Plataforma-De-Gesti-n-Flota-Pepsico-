#!/bin/bash
# ============================================================================
# Script simplificado para generar dump del esquema SQL desde PostgreSQL
# ============================================================================
# Uso: ./scripts/dump_schema_simple.sh [output_file]
# ============================================================================

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Archivo de salida
OUTPUT_FILE="${1:-docs/ESQUEMA_SQL_FROM_DB.sql}"

echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}Generando dump del esquema SQL desde PostgreSQL${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Valores por defecto (desde docker-compose.yml)
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-pgf}"
DB_USER="${POSTGRES_USER:-pgf}"
DB_PASSWORD="${POSTGRES_PASSWORD:-pgf}"

# Intentar leer desde .env si existe
if [ -f .env ]; then
    echo -e "${YELLOW}Leyendo configuración desde .env...${NC}"
    # Extraer DATABASE_URL si existe
    if grep -q "DATABASE_URL" .env; then
        DATABASE_URL=$(grep "^DATABASE_URL" .env | cut -d '=' -f2- | tr -d '"' | tr -d "'")
        if [ ! -z "$DATABASE_URL" ]; then
            # Parsear DATABASE_URL (formato: postgres://user:password@host:port/dbname)
            DB_URL=$(echo $DATABASE_URL | sed -e 's|postgres://||' -e 's|postgresql://||')
            DB_USER=$(echo $DB_URL | cut -d: -f1)
            DB_PASSWORD=$(echo $DB_URL | cut -d: -f2 | cut -d@ -f1)
            DB_HOST=$(echo $DB_URL | cut -d@ -f2 | cut -d: -f1)
            DB_PORT=$(echo $DB_URL | cut -d: -f3 | cut -d/ -f1)
            DB_NAME=$(echo $DB_URL | cut -d/ -f2)
        fi
    fi
    
    # Intentar leer variables individuales si existen
    [ -z "$POSTGRES_HOST" ] && [ -f .env ] && grep -q "^POSTGRES_HOST" .env && \
        DB_HOST=$(grep "^POSTGRES_HOST" .env | cut -d '=' -f2- | tr -d '"' | tr -d "'" | xargs)
    [ -z "$POSTGRES_PORT" ] && [ -f .env ] && grep -q "^POSTGRES_PORT" .env && \
        DB_PORT=$(grep "^POSTGRES_PORT" .env | cut -d '=' -f2- | tr -d '"' | tr -d "'" | xargs)
    [ -z "$POSTGRES_DB" ] && [ -f .env ] && grep -q "^POSTGRES_DB" .env && \
        DB_NAME=$(grep "^POSTGRES_DB" .env | cut -d '=' -f2- | tr -d '"' | tr -d "'" | xargs)
    [ -z "$POSTGRES_USER" ] && [ -f .env ] && grep -q "^POSTGRES_USER" .env && \
        DB_USER=$(grep "^POSTGRES_USER" .env | cut -d '=' -f2- | tr -d '"' | tr -d "'" | xargs)
    [ -z "$POSTGRES_PASSWORD" ] && [ -f .env ] && grep -q "^POSTGRES_PASSWORD" .env && \
        DB_PASSWORD=$(grep "^POSTGRES_PASSWORD" .env | cut -d '=' -f2- | tr -d '"' | tr -d "'" | xargs)
fi

# Si la base de datos está en Docker, usar 'db' como host
if [ "$DB_HOST" = "localhost" ] && docker ps | grep -q "pgf-db\|postgres"; then
    echo -e "${YELLOW}Base de datos detectada en Docker, usando 'db' como host${NC}"
    DB_HOST="db"
fi

echo -e "${GREEN}Configuración de conexión:${NC}"
echo -e "  ${BLUE}Host:${NC}     ${DB_HOST}"
echo -e "  ${BLUE}Port:${NC}     ${DB_PORT}"
echo -e "  ${BLUE}Database:${NC} ${DB_NAME}"
echo -e "  ${BLUE}User:${NC}     ${DB_USER}"
echo ""

# Verificar pg_dump
if ! command -v pg_dump &> /dev/null; then
    echo -e "${RED}❌ Error: pg_dump no está instalado${NC}"
    echo ""
    echo -e "${YELLOW}Instalación:${NC}"
    echo "  Ubuntu/Debian: sudo apt-get install postgresql-client"
    echo "  macOS:         brew install postgresql"
    echo "  Windows:       Descargar desde https://www.postgresql.org/download/"
    echo ""
    echo -e "${YELLOW}Alternativa: Usar desde el contenedor Docker${NC}"
    echo "  docker exec pgf-db pg_dump -U pgf -d pgf -s > $OUTPUT_FILE"
    exit 1
fi

# Verificar conexión
echo -e "${GREEN}🔌 Verificando conexión...${NC}"
export PGPASSWORD="$DB_PASSWORD"
if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${RED}❌ No se pudo conectar a la base de datos${NC}"
    echo ""
    echo -e "${YELLOW}Opciones:${NC}"
    echo "  1. Verifica que la base de datos esté corriendo"
    echo "  2. Si está en Docker, usa: docker exec pgf-db pg_dump -U pgf -d pgf -s > $OUTPUT_FILE"
    echo "  3. Verifica las credenciales en .env o variables de entorno"
    unset PGPASSWORD
    exit 1
fi

echo -e "${GREEN}✓ Conexión exitosa${NC}"
echo ""

# Crear directorio
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Generar dump
echo -e "${GREEN}📦 Generando dump del esquema...${NC}"
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
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${GREEN}📄 Archivo: ${OUTPUT_FILE}${NC}"
    FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    echo -e "${GREEN}📊 Tamaño: ${FILE_SIZE}${NC}"
    echo ""
    echo -e "${YELLOW}Para usar en dbdiagram.io:${NC}"
    echo "  1. Abre https://dbdiagram.io"
    echo "  2. Haz clic en 'Import' o 'New Project'"
    echo "  3. Selecciona 'PostgreSQL'"
    echo "  4. Pega el contenido del archivo generado"
    echo -e "${BLUE}============================================================${NC}"
else
    echo -e "${RED}❌ Error al generar el dump${NC}"
    unset PGPASSWORD
    exit 1
fi

unset PGPASSWORD

