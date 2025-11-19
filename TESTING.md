# 🧪 Guía de Pruebas - PGF Plataforma

Esta guía explica cómo ejecutar todas las pruebas del proyecto desde los contenedores Docker.

## 📋 Índice

1. [Pruebas Backend (Pytest)](#pruebas-backend-pytest)
2. [Pruebas Frontend (Vitest)](#pruebas-frontend-vitest)
3. [Escaneo de Seguridad (OWASP ZAP)](#escaneo-de-seguridad-owasp-zap)
4. [Ver Cobertura](#ver-cobertura)

---

## 🔧 Pruebas Backend (Pytest)

### Ejecutar todas las pruebas

```bash
docker compose exec api poetry run pytest apps/ -v
```

### Ejecutar pruebas de un módulo específico

```bash
# Validadores
docker compose exec api poetry run pytest apps/core/tests/test_validators.py -v

# Usuarios
docker compose exec api poetry run pytest apps/users/tests/ -v

# Vehículos
docker compose exec api poetry run pytest apps/vehicles/tests/ -v

# Órdenes de Trabajo
docker compose exec api poetry run pytest apps/workorders/tests/ -v
```

### Ejecutar una prueba específica

```bash
docker compose exec api poetry run pytest apps/core/tests/test_validators.py::TestValidarRutChileno::test_rut_valido_con_guion -v
```

### Ver cobertura de código

```bash
# Cobertura en terminal
docker compose exec api poetry run pytest apps/ --cov=apps --cov-report=term-missing

# Cobertura HTML (se genera en test-results/coverage/index.html)
docker compose exec api poetry run pytest apps/ --cov=apps --cov-report=html
```

### Modo watch (desarrollo)

```bash
docker compose exec api poetry run pytest-watch apps/ -- -v
```

### Ejecutar solo pruebas que fallaron

```bash
docker compose exec api poetry run pytest apps/ --lf -v
```

---

## 🎨 Pruebas Frontend (Vitest)

### Ejecutar todas las pruebas

```bash
docker compose exec web sh -c "cd /app && npm run test"
```

### Modo watch (desarrollo)

```bash
docker compose exec web sh -c "cd /app && npm run test:watch"
```

### UI interactiva

```bash
docker compose exec web sh -c "cd /app && npm run test:ui"
```

### Ver cobertura

```bash
docker compose exec web sh -c "cd /app && npm run test:coverage"
```

### Ejecutar pruebas de un archivo específico

```bash
docker compose exec web sh -c "cd /app && npm run test src/__tests__/components/Nav.test.tsx"
```

---

## 🔒 Escaneo de Seguridad (OWASP ZAP)

### Requisitos

- Docker instalado
- Servidor web corriendo en `http://localhost:3000`

### Escaneo Pasivo (Rápido, Recomendado)

```bash
./scripts/owasp_zap_scan.sh baseline
```

Este escaneo:
- ✅ Es rápido (~2-5 minutos)
- ✅ No es intrusivo (no modifica datos)
- ✅ Seguro para producción
- ✅ Detecta vulnerabilidades comunes

**Reportes generados:**
- `test-results/security/zap-baseline.html`
- `test-results/security/zap-baseline.json`

### Escaneo Activo (Completo, Solo Desarrollo)

```bash
./scripts/owasp_zap_scan.sh full
```

Este escaneo:
- ⚠️ Es lento (~10-30 minutos)
- ⚠️ Es intrusivo (puede modificar datos)
- ⚠️ Solo para desarrollo/testing
- ✅ Detecta más vulnerabilidades

**Reportes generados:**
- `test-results/security/zap-full.html`
- `test-results/security/zap-full.json`

### Escaneo vía API (ZAP corriendo)

```bash
# Primero inicia ZAP
docker run -d -p 8080:8080 owasp/zap2docker-stable zap.sh -daemon -host 0.0.0.0 -port 8080

# Luego ejecuta el escaneo
./scripts/owasp_zap_scan.sh api
```

### Ver reportes

```bash
# Abrir reporte HTML
open test-results/security/zap-baseline.html

# O en Linux
xdg-open test-results/security/zap-baseline.html
```

---

## 📊 Ver Cobertura

### Backend

```bash
# Generar reporte HTML
docker compose exec api poetry run pytest apps/ --cov=apps --cov-report=html

# Abrir en navegador
open test-results/coverage/index.html
```

### Frontend

```bash
# Generar reporte
docker compose exec web sh -c "cd /app && npm run test:coverage"

# Los reportes se generan automáticamente en:
# - test-results/frontend-coverage/ (HTML, JSON)
#   - index.html (cobertura HTML interactiva)
#   - coverage.json (cobertura completa)
#   - coverage-summary.json (resumen de cobertura)

# Abrir reporte HTML
open test-results/frontend-coverage/index.html
```

---

## 🚀 Ejecutar Todo (Script Rápido)

### Backend + Frontend

```bash
# Backend
echo "🔧 Ejecutando pruebas backend..."
docker compose exec api poetry run pytest apps/ -v --tb=short

# Frontend
echo "🎨 Ejecutando pruebas frontend..."
docker compose exec web sh -c "cd /app && npm run test"
```

### Con Cobertura

```bash
# Backend con cobertura
docker compose exec api poetry run pytest apps/ --cov=apps --cov-report=term-missing --cov-report=html

# Frontend con cobertura
docker compose exec web sh -c "cd /app && npm run test:coverage"
```

---

## 🐛 Solución de Problemas

### Error: "pytest not found"

```bash
# Instalar dependencias
docker compose exec api poetry install
```

### Error: "vitest not found"

```bash
# Instalar dependencias frontend
docker compose exec web sh -c "cd /app && npm install --legacy-peer-deps"
```

### Error: "Cannot find module"

```bash
# Limpiar e reinstalar
docker compose exec web sh -c "cd /app && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps"
```

### Error: OWASP ZAP no encuentra el target

```bash
# Verificar que el servidor esté corriendo
curl http://localhost:3000

# Si no está corriendo, iniciar servicios
docker compose up -d web
```

---

## 📝 Estructura de Pruebas

### Backend

```
apps/
├── core/tests/
│   └── test_validators.py      # Validadores (RUT, patentes, etc.)
├── users/tests/
│   ├── test_models.py           # Modelos de usuarios
│   ├── test_serializers.py     # Serializers
│   └── test_views.py           # Vistas/API
├── vehicles/tests/
│   ├── test_models.py
│   └── test_serializers.py
└── workorders/tests/
    ├── test_models.py
    └── test_serializers.py
```

### Frontend

```
src/
└── __tests__/
    ├── setup.ts                 # Configuración global
    └── components/
        ├── Nav.test.tsx        # Pruebas del componente Nav
        ├── Sidebar.test.tsx    # Pruebas del Sidebar
        └── ...
```

---

## ✅ Checklist de Pruebas

Antes de hacer commit, ejecuta:

- [ ] Pruebas backend: `docker compose exec api poetry run pytest apps/ -v`
- [ ] Pruebas frontend: `docker compose exec web sh -c "cd /app && npm run test"`
- [ ] Cobertura backend > 20%: `docker compose exec api poetry run pytest apps/ --cov=apps --cov-report=term-missing`
- [ ] Sin errores de linting

---

---

## 📊 Estado Actual de Pruebas

### Backend (Pytest)
- ✅ **52 pruebas pasando** (100% en core y users)
- ✅ **Cobertura**: ~21%
- ✅ Validadores: 35/35 pasando (100%)
- ✅ Tests de integración: 11 tests
- ✅ Tests de permisos: 6 tests
- ✅ **Reportes**: HTML, XML, JUnit en `test-results/`

### Frontend (Vitest)
- ✅ **28 pruebas pasando** (100%)
- ✅ **5 archivos de test** pasando
- ✅ Componentes probados: Nav, Pagination, Toast, RoleGate, ConfirmDialog
- ✅ Cobertura en aumento
- ✅ **Reportes**: HTML, JSON, JUnit en `test-results/frontend-coverage/`

### OWASP ZAP
- ✅ **Reportes**: HTML y JSON en `test-results/security/`
- ✅ Escaneo pasivo (baseline) configurado
- ✅ Escaneo activo (full) configurado

### Scripts Disponibles
- ✅ `scripts/owasp_zap_scan.sh` - Escaneo de seguridad

---

## 📄 Reportes Generados

Todos los reportes se generan automáticamente en `test-results/`:

### Backend
- `test-results/report.html` - Reporte HTML completo de pruebas
- `test-results/junit.xml` - Reporte JUnit XML
- `test-results/coverage/index.html` - Cobertura HTML interactiva
- `test-results/coverage.xml` - Cobertura XML

### Frontend
- `test-results/frontend-coverage/index.html` - Cobertura HTML interactiva
- `test-results/frontend-coverage/coverage.json` - Cobertura JSON
- `test-results/frontend-coverage/coverage-summary.json` - Resumen de cobertura

### Seguridad (OWASP ZAP)
- `test-results/security/zap-baseline.html` - Reporte HTML (baseline)
- `test-results/security/zap-baseline.json` - Reporte JSON (baseline)
- `test-results/security/zap-full.html` - Reporte HTML (full scan)
- `test-results/security/zap-full.json` - Reporte JSON (full scan)

---

**Última actualización**: 2025-01-19

