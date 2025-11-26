#!/bin/bash
# Script para verificar y crear el usuario admin permanente

echo "🔍 Verificando usuario admin permanente..."

# Intentar con Docker (si está disponible)
if command -v docker &> /dev/null && docker ps &> /dev/null; then
    echo "📦 Ejecutando con Docker..."
    
    # Primero ejecutar migraciones si es necesario
    echo "🔄 Ejecutando migraciones..."
    docker compose exec api poetry run python manage.py migrate users 2>&1 || true
    
    # Crear/actualizar admin
    echo "👤 Creando/actualizando usuario admin..."
    docker compose exec api poetry run python manage.py create_permanent_admin
    exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "✅ Usuario admin verificado/creado exitosamente"
        exit 0
    fi
fi

# Intentar con Poetry directamente
if command -v poetry &> /dev/null; then
    echo "📦 Ejecutando con Poetry..."
    
    # Primero ejecutar migraciones si es necesario
    echo "🔄 Ejecutando migraciones..."
    poetry run python manage.py migrate users 2>&1 || true
    
    # Crear/actualizar admin
    echo "👤 Creando/actualizando usuario admin..."
    poetry run python manage.py create_permanent_admin
    exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "✅ Usuario admin verificado/creado exitosamente"
        exit 0
    fi
fi

# Intentar con Python directamente (si el entorno virtual está activado)
echo "🐍 Ejecutando con Python..."
echo "🔄 Ejecutando migraciones..."
python manage.py migrate users 2>&1 || true

echo "👤 Creando/actualizando usuario admin..."
python manage.py create_permanent_admin
exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo "✅ Usuario admin verificado/creado exitosamente"
    exit 0
fi

echo "❌ Error: No se pudo ejecutar el comando"
echo "💡 Asegúrate de tener:"
echo "   - Docker y docker-compose instalados, O"
echo "   - Poetry instalado y el entorno activado, O"
echo "   - Un entorno virtual de Python activado con Django instalado"
echo ""
echo "📝 Ejecuta manualmente:"
echo "   docker compose exec api poetry run python manage.py migrate users"
echo "   docker compose exec api poetry run python manage.py create_permanent_admin"

exit 1

