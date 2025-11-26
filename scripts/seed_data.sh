#!/bin/bash
# Script para crear datos de seed relacionados con vehículos existentes

set -e

echo "🌱 Script de creación de datos de seed"
echo "========================================"
echo ""
echo "Este script creará:"
echo "- Un usuario por cada rol"
echo "- Choferes relacionados con vehículos existentes"
echo "- Órdenes de trabajo relacionadas"
echo "- Agendas relacionadas"
echo "- Emergencias relacionadas"
echo "- Ingresos relacionados"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: Este script debe ejecutarse desde la raíz del proyecto"
    exit 1
fi

# Verificar que el contenedor está corriendo
if ! docker compose ps api | grep -q "Up"; then
    echo "❌ Error: El contenedor 'api' no está corriendo"
    echo "   Ejecuta: docker compose up -d"
    exit 1
fi

# Ejecutar el comando de Django
echo "Ejecutando seed de datos..."
echo ""

docker compose exec -T api poetry run python manage.py seed_data "$@"

echo ""
echo "✅ Seed completado"

