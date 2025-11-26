# 🧪 Guía Rápida: Ejecutar Pruebas con Pytest

## 📍 Ubicación de Archivos de Pruebas

Los archivos de configuración y pruebas están en:

- **Configuración principal**: `pytest.ini` (raíz del proyecto)
- **Fixtures globales**: `conftest.py` (raíz del proyecto)
- **Pruebas por módulo**: `apps/*/tests/` (cada app tiene su carpeta `tests/`)

## 🚀 Comandos para Ejecutar Pruebas

### Opción 1: Usar el Script (Recomendado)

```bash
# Ejecutar todas las pruebas
./scripts/run_pytest.sh

# Ejecutar pruebas de un módulo específico
./scripts/run_pytest.sh apps/users/tests/ -v

# Ejecutar una prueba específica
./scripts/run_pytest.sh apps/core/tests/test_validators.py::TestValidarRutChileno::test_rut_valido_con_guion -v
```

### Opción 2: Comando Directo desde Docker

```bash
# Ejecutar todas las pruebasd
docker compose exec api poetry run pytest apps/ -v

# Ejecutar pruebas de un módulo específico
docker compose exec api poetry run pytest apps/users/tests/ -v

# Ejecutar pruebas de vehículos
docker compose exec api poetry run pytest apps/vehicles/tests/ -v

# Ejecutar pruebas de órdenes de trabajo
docker compose exec api poetry run pytest apps/workorders/tests/ -v
```

### Opción 3: Desde dentro del contenedor

```bash
# Entrar al contenedor
docker compose exec api bash

# Dentro del contenedor, ejecutar:
poetry run pytest apps/ -v
```

## 📊 Ejecutar con Cobertura

```bash
# Cobertura en terminal
docker compose exec api poetry run pytest apps/ --cov=apps --cov-report=term-missing

# Cobertura con reporte HTML
docker compose exec api poetry run pytest apps/ --cov=apps --cov-report=html:test-results/coverage --cov-report=term-missing
```

## 🎯 Ejemplos de Uso

### Ejecutar todas las pruebas
```bash
docker compose exec api poetry run pytest apps/ -v
```

### Ejecutar pruebas de un módulo
```bash
# Usuarios
docker compose exec api poetry run pytest apps/users/tests/ -v

# Vehículos
docker compose exec api poetry run pytest apps/vehicles/tests/ -v

# Órdenes de trabajo
docker compose exec api poetry run pytest apps/workorders/tests/ -v

# Core (validadores, utils)
docker compose exec api poetry run pytest apps/core/tests/ -v
```

### Ejecutar una prueba específica
```bash
docker compose exec api poetry run pytest apps/core/tests/test_validators.py::TestValidarRutChileno::test_rut_valido_con_guion -v
```

### Ejecutar pruebas marcadas
```bash
# Solo pruebas unitarias
docker compose exec api poetry run pytest apps/ -m unit -v

# Solo pruebas de API
docker compose exec api poetry run pytest apps/ -m api -v

# Solo pruebas de modelos
docker compose exec api poetry run pytest apps/ -m model -v
```

## ⚠️ Solución de Problemas

### Error: "command not found: pytest"

**Causa**: Las dependencias de desarrollo (pytest) no están instaladas en el contenedor.

**Solución 1**: Instalar dependencias de desarrollo:

```bash
# Instalar dependencias de desarrollo
docker compose exec api poetry install --with dev --no-root

# Luego ejecutar pytest
docker compose exec api poetry run pytest apps/ -v
```

**Solución 2**: Usar `poetry run pytest` (si ya están instaladas):

```bash
# ❌ Incorrecto
docker compose exec api pytest apps/

# ✅ Correcto
docker compose exec api poetry run pytest apps/
```

### Error: "Container not found"

**Solución**: Asegúrate de que los contenedores estén corriendo:

```bash
# Verificar estado
docker compose ps

# Iniciar contenedores si no están corriendo
docker compose up -d
```

### Error: "Module not found"

**Solución**: Asegúrate de estar ejecutando desde el contenedor correcto:

```bash
# Verificar que estás en el contenedor api
docker compose exec api poetry run pytest apps/ -v
```

## 📁 Estructura de Pruebas

```
apps/
├── core/
│   └── tests/
│       ├── test_validators.py
│       └── test_utils.py
├── users/
│   └── tests/
│       ├── test_models.py
│       ├── test_serializers.py
│       ├── test_views.py
│       └── test_permissions.py
├── vehicles/
│   └── tests/
│       ├── test_models.py
│       ├── test_serializers.py
│       ├── test_views.py
│       └── test_utils.py
└── workorders/
    └── tests/
        ├── test_models.py
        ├── test_serializers.py
        ├── test_views.py
        └── test_permissions.py
```

## 🔍 Ver Reportes

Después de ejecutar las pruebas, los reportes se generan en:

- **HTML**: `test-results/backend-report.html`
- **Cobertura HTML**: `test-results/coverage/index.html`
- **JUnit XML**: `test-results/junit/backend-junit.xml`

Para ver el reporte HTML:
```bash
# En Linux/Mac
open test-results/backend-report.html

# O simplemente abrir el archivo en tu navegador
```

## 📚 Más Información

Para información detallada sobre todas las opciones de pruebas, ver:
- [docs/GUIA_PRUEBAS.md](GUIA_PRUEBAS.md) - Guía completa de pruebas
- [pytest.ini](pytest.ini) - Configuración de pytest
- [conftest.py](conftest.py) - Fixtures globales

