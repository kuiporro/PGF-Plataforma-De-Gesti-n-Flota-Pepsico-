@echo off
REM Script para ejecutar pruebas del proyecto PGF (Windows)

echo 🧪 Ejecutando pruebas del proyecto PGF
echo ========================================

REM Verificar que Docker está corriendo
docker-compose ps | findstr "api.*Up" >nul
if errorlevel 1 (
    echo ❌ Error: El contenedor 'api' no está corriendo.
    echo    Ejecuta: docker-compose up -d
    exit /b 1
)

REM Menú de opciones
if "%1"=="--all" goto all
if "%1"=="" goto all
if "%1"=="--validators" goto validators
if "%1"=="--models" goto models
if "%1"=="--serializers" goto serializers
if "%1"=="--views" goto views
if "%1"=="--coverage" goto coverage
if "%1"=="--help" goto help
if "%1"=="-h" goto help
goto unknown

:all
echo Ejecutando todas las pruebas...
docker-compose exec api poetry run pytest apps/ -v --cov=apps --cov-report=term-missing
goto end

:validators
echo 📋 Pruebas de Validadores
echo ----------------------------------------
docker-compose exec api poetry run pytest apps/core/tests/test_validators.py -v
goto end

:models
echo 📋 Pruebas de Modelos
echo ----------------------------------------
docker-compose exec api poetry run pytest apps/users/tests/test_models.py apps/vehicles/tests/test_models.py apps/workorders/tests/test_models.py -v
goto end

:serializers
echo 📋 Pruebas de Serializers
echo ----------------------------------------
docker-compose exec api poetry run pytest apps/users/tests/test_serializers.py apps/vehicles/tests/test_serializers.py apps/workorders/tests/test_serializers.py -v
goto end

:views
echo 📋 Pruebas de Views
echo ----------------------------------------
docker-compose exec api poetry run pytest apps/users/tests/test_views.py -v
goto end

:coverage
echo Generando reporte de cobertura...
docker-compose exec api poetry run pytest apps/ --cov=apps --cov-report=html --cov-report=term-missing
echo ✅ Reporte de cobertura generado en htmlcov/index.html
goto end

:help
echo Uso: run_tests.bat [opción]
echo.
echo Opciones:
echo   --all          Ejecutar todas las pruebas con cobertura (por defecto)
echo   --validators    Ejecutar solo pruebas de validadores
echo   --models        Ejecutar solo pruebas de modelos
echo   --serializers   Ejecutar solo pruebas de serializers
echo   --views         Ejecutar solo pruebas de views
echo   --coverage      Generar reporte de cobertura HTML
echo   --help, -h      Mostrar esta ayuda
goto end

:unknown
echo ❌ Opción desconocida: %1
echo    Usa --help para ver las opciones disponibles
exit /b 1

:end
echo.
echo ✅ Pruebas completadas

