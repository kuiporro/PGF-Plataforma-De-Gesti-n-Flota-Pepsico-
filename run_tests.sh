#!/bin/bash
# Script para ejecutar pruebas del proyecto PGF

echo "🧪 Ejecutando pruebas del proyecto PGF"
echo "========================================"

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para ejecutar pruebas
run_tests() {
    local test_path=$1
    local description=$2
    
    echo ""
    echo -e "${BLUE}📋 $description${NC}"
    echo "----------------------------------------"
    docker-compose exec api poetry run pytest $test_path -v
}

# Verificar que Docker está corriendo
if ! docker-compose ps | grep -q "api.*Up"; then
    echo "❌ Error: El contenedor 'api' no está corriendo."
    echo "   Ejecuta: docker-compose up -d"
    exit 1
fi

# Menú de opciones
if [ "$1" == "--all" ] || [ -z "$1" ]; then
    echo "Ejecutando todas las pruebas..."
    docker-compose exec api poetry run pytest apps/ -v --cov=apps --cov-report=term-missing
elif [ "$1" == "--validators" ]; then
    run_tests "apps/core/tests/test_validators.py" "Pruebas de Validadores"
elif [ "$1" == "--models" ]; then
    run_tests "apps/users/tests/test_models.py apps/vehicles/tests/test_models.py apps/workorders/tests/test_models.py" "Pruebas de Modelos"
elif [ "$1" == "--serializers" ]; then
    run_tests "apps/users/tests/test_serializers.py apps/vehicles/tests/test_serializers.py apps/workorders/tests/test_serializers.py" "Pruebas de Serializers"
elif [ "$1" == "--views" ]; then
    run_tests "apps/users/tests/test_views.py" "Pruebas de Views"
elif [ "$1" == "--coverage" ]; then
    echo "Generando reporte de cobertura..."
    docker-compose exec api poetry run pytest apps/ --cov=apps --cov-report=html --cov-report=term-missing
    echo -e "${GREEN}✅ Reporte de cobertura generado en htmlcov/index.html${NC}"
elif [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Uso: ./run_tests.sh [opción]"
    echo ""
    echo "Opciones:"
    echo "  --all          Ejecutar todas las pruebas con cobertura (por defecto)"
    echo "  --validators    Ejecutar solo pruebas de validadores"
    echo "  --models        Ejecutar solo pruebas de modelos"
    echo "  --serializers   Ejecutar solo pruebas de serializers"
    echo "  --views         Ejecutar solo pruebas de views"
    echo "  --coverage      Generar reporte de cobertura HTML"
    echo "  --help, -h      Mostrar esta ayuda"
else
    echo "❌ Opción desconocida: $1"
    echo "   Usa --help para ver las opciones disponibles"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Pruebas completadas${NC}"

