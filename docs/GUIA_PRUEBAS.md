# 🧪 Guía Completa de Pruebas - PGF

Esta guía explica paso a paso cómo ejecutar todas las pruebas del proyecto PGF desde VS Code o la terminal.

## 📋 Tabla de Contenidos

1. [Pruebas Backend (Pytest)](#pruebas-backend-pytest)
2. [Pruebas Frontend (Vitest)](#pruebas-frontend-vitest)
3. [Script Consolidado de Pruebas](#script-consolidado-de-pruebas)
4. [Escaneo de Seguridad (OWASP ZAP)](#escaneo-de-seguridad-owasp-zap)
5. [Ver Reportes de Cobertura](#ver-reportes-de-cobertura)
6. [Solución de Problemas](#solución-de-problemas)

---

## 🔧 Pruebas Backend (Pytest)

### Requisitos Previos

1. Asegúrate de que los contenedores Docker estén corriendo:
   ```bash
   docker compose up -d
   ```

2. Verifica que el contenedor `api` esté activo:
   ```bash
   docker compose ps
   ```

### Ejecutar Todas las Pruebas Backend

**Desde VS Code Terminal:**
```bash
docker compose exec api poetry run pytest apps/ -v
```

**Explicación:**
- `docker compose exec api` - Ejecuta el comando dentro del contenedor `api`
- `poetry run pytest` - Ejecuta pytest usando Poetry
- `apps/` - Directorio donde están todas las pruebas
- `-v` - Modo verbose (muestra detalles de cada prueba)

### Ejecutar Pruebas de un Módulo Específico

**Validadores:**
```bash
docker compose exec api poetry run pytest apps/core/tests/test_validators.py -v
```

**Usuarios:**
```bash
docker compose exec api poetry run pytest apps/users/tests/ -v
```

**Vehículos:**
```bash
docker compose exec api poetry run pytest apps/vehicles/tests/ -v
```

**Órdenes de Trabajo:**
```bash
docker compose exec api poetry run pytest apps/workorders/tests/ -v
```

**Choferes:**
```bash
docker compose exec api poetry run pytest apps/drivers/tests/ -v
```

**Emergencias:**
```bash
docker compose exec api poetry run pytest apps/emergencies/tests/ -v
```

### Ejecutar una Prueba Específica

```bash
docker compose exec api poetry run pytest apps/core/tests/test_validators.py::TestValidarRutChileno::test_rut_valido_con_guion -v
```

**Formato:** `ruta/al/archivo.py::ClaseTest::metodo_test`

### Ejecutar Pruebas con Cobertura

**Cobertura en Terminal:**
```bash
docker compose exec api poetry run pytest apps/ --cov=apps --cov-report=term-missing
```

**Cobertura con Reporte HTML:**
```bash
docker compose exec api poetry run pytest apps/ --cov=apps --cov-report=html:test-results/coverage --cov-report=term-missing
```

**Cobertura Completa (HTML, XML, JSON):**
```bash
docker compose exec api poetry run pytest apps/ \
  --cov=apps \
  --cov-config=.coveragerc \
  --cov-report=html:test-results/coverage \
  --cov-report=xml:test-results/coverage/coverage.xml \
  --cov-report=json:test-results/coverage/coverage.json \
  --cov-report=term-missing
```

### Ver Reporte HTML de Cobertura

Después de ejecutar las pruebas con cobertura HTML:

1. Abre el archivo: `test-results/coverage/index.html`
2. Puedes abrirlo desde VS Code haciendo clic derecho → "Open with Live Server" o desde el navegador

### Ejecutar Solo Pruebas que Fallaron

```bash
docker compose exec api poetry run pytest apps/ --lf -v
```

### Ejecutar Pruebas con Marcadores Específicos

```bash
# Solo pruebas unitarias
docker compose exec api poetry run pytest apps/ -m unit -v

# Solo pruebas de integración
docker compose exec api poetry run pytest apps/ -m integration -v

# Solo pruebas de API
docker compose exec api poetry run pytest apps/ -m api -v
```

### Modo Watch (Desarrollo)

Para ejecutar pruebas automáticamente cuando cambies archivos:

```bash
docker compose exec api poetry run pytest-watch apps/ -- -v
```

**Nota:** Requiere instalar `pytest-watch`:
```bash
docker compose exec api poetry add --group dev pytest-watch
```

---

## 🎨 Pruebas Frontend (Vitest)

### Requisitos Previos

1. Asegúrate de que el contenedor `web` esté corriendo:
   ```bash
   docker compose up -d web
   ```

2. Verifica que las dependencias estén instaladas:
   ```bash
   docker compose exec web sh -c "cd /app && npm list vitest"
   ```

### Ejecutar Todas las Pruebas Frontend

**Desde VS Code Terminal:**
```bash
docker compose exec web sh -c "cd /app && npm run test"
```

**Explicación:**
- `docker compose exec web` - Ejecuta el comando dentro del contenedor `web`
- `sh -c "cd /app && npm run test"` - Cambia al directorio y ejecuta el script de pruebas

### Ejecutar Pruebas de un Archivo Específico

```bash
docker compose exec web sh -c "cd /app && npm run test src/__tests__/components/Nav.test.tsx"
```

### Ejecutar Pruebas con Cobertura

**Cobertura Completa:**
```bash
docker compose exec web sh -c "cd /app && npm run test:coverage"
```

Esto generará:
- `test-results/frontend-coverage/index.html` - Reporte HTML interactivo
- `test-results/frontend-coverage/coverage.json` - Cobertura completa en JSON
- `test-results/frontend-coverage/coverage-summary.json` - Resumen de cobertura

### Modo Watch (Desarrollo)

Para ejecutar pruebas automáticamente cuando cambies archivos:

```bash
docker compose exec web sh -c "cd /app && npm run test:watch"
```

### UI Interactiva de Vitest

Para abrir la interfaz gráfica de Vitest:

```bash
docker compose exec web sh -c "cd /app && npm run test:ui"
```

**Nota:** Necesitarás configurar el puerto en `vitest.config.ts` y hacer port forwarding en Docker.

### Ver Reporte HTML de Cobertura

Después de ejecutar `npm run test:coverage`:

1. Abre el archivo: `test-results/frontend-coverage/index.html`
2. Puedes abrirlo desde VS Code o desde el navegador

---

## 🚀 Script Consolidado de Pruebas

El proyecto incluye un script que ejecuta todas las pruebas y genera reportes consolidados.

### Ubicación

El script está en: `scripts/run_all_tests.sh`

### Uso Básico

**Ejecutar todas las pruebas (sin cobertura):**
```bash
./scripts/run_all_tests.sh
```

**Con cobertura:**
```bash
./scripts/run_all_tests.sh --coverage
```

**Con escaneo de seguridad:**
```bash
./scripts/run_all_tests.sh --security
```

**Todo (cobertura + seguridad):**
```bash
./scripts/run_all_tests.sh --coverage --security
```

### Dar Permisos de Ejecución

Si es la primera vez que usas el script:

```bash
chmod +x scripts/run_all_tests.sh
```

### Qué Hace el Script

1. **Ejecuta pruebas backend** (Pytest)
   - Genera reportes HTML, XML, JSON
   - Genera reporte JUnit
   - Si `--coverage`: genera reportes de cobertura

2. **Ejecuta pruebas frontend** (Vitest)
   - Genera reportes JSON y HTML
   - Si `--coverage`: genera reportes de cobertura

3. **Ejecuta escaneo de seguridad** (si `--security`)
   - Escaneo pasivo con OWASP ZAP
   - Genera reportes HTML y JSON

4. **Genera resumen consolidado**
   - Crea `test-results/test-summary-{timestamp}.md`
   - Incluye estadísticas de cobertura
   - Lista todos los reportes generados

### Reportes Generados

Todos los reportes se guardan en `test-results/`:

```
test-results/
├── coverage/                    # Cobertura backend
│   ├── index.html
│   ├── coverage.xml
│   └── coverage.json
├── frontend-coverage/           # Cobertura frontend
│   ├── index.html
│   ├── coverage.json
│   └── coverage-summary.json
├── junit/                       # Reportes JUnit
│   ├── backend-junit-{timestamp}.xml
│   └── frontend-junit.json
├── security/                    # Reportes OWASP ZAP
│   ├── zap-baseline.html
│   └── zap-baseline.json
├── backend-report-{timestamp}.html
├── frontend-report.html
└── test-summary-{timestamp}.md
```

---

## 🔒 Escaneo de Seguridad (OWASP ZAP)

### Requisitos Previos

1. **Docker instalado** (OWASP ZAP se ejecuta en un contenedor)
2. **Servidor frontend corriendo** en `http://localhost:3000`

### Verificar que el Servidor Esté Corriendo

```bash
curl http://localhost:3000
```

Si no está corriendo:
```bash
docker compose up -d web
```

### Escaneo Pasivo (Recomendado)

**Qué es:** Escaneo rápido y no intrusivo que detecta vulnerabilidades comunes sin modificar datos.

**Comando:**
```bash
./scripts/owasp_zap_scan.sh baseline
```

**Tiempo estimado:** 2-5 minutos

**Reportes generados:**
- `test-results/security/zap-baseline.html` - Reporte HTML detallado
- `test-results/security/zap-baseline.json` - Reporte JSON para análisis

**Cuándo usar:**
- ✅ Antes de cada release
- ✅ En integración continua
- ✅ Para verificación rápida de seguridad

### Escaneo Activo (Solo Desarrollo)

**Qué es:** Escaneo completo e intrusivo que intenta explotar vulnerabilidades.

**⚠️ ADVERTENCIA:** Este escaneo puede modificar datos. Solo úsalo en entornos de desarrollo/testing.

**Comando:**
```bash
./scripts/owasp_zap_scan.sh full
```

**Tiempo estimado:** 10-30 minutos

**Reportes generados:**
- `test-results/security/zap-full.html` - Reporte HTML detallado
- `test-results/security/zap-full.json` - Reporte JSON para análisis

**Cuándo usar:**
- ⚠️ Solo en desarrollo/testing
- ⚠️ Cuando necesites análisis profundo
- ❌ Nunca en producción

### Escaneo vía API (ZAP Corriendo)

Si tienes ZAP corriendo como servicio:

1. **Iniciar ZAP:**
   ```bash
   docker run -d -p 8080:8080 owasp/zap2docker-stable zap.sh -daemon -host 0.0.0.0 -port 8080
   ```

2. **Ejecutar escaneo:**
   ```bash
   ./scripts/owasp_zap_scan.sh api
   ```

### Ver Reportes de OWASP ZAP

**Reporte HTML:**
```bash
# Linux
xdg-open test-results/security/zap-baseline.html

# macOS
open test-results/security/zap-baseline.html

# Windows
start test-results/security/zap-baseline.html
```

O simplemente abre el archivo desde VS Code.

### Interpretar los Reportes

**Niveles de riesgo:**
- 🔴 **High (Alto)**: Vulnerabilidades críticas que deben corregirse inmediatamente
- 🟠 **Medium (Medio)**: Vulnerabilidades importantes que deben corregirse pronto
- 🟡 **Low (Bajo)**: Problemas menores que pueden corregirse después
- ℹ️ **Informational (Informativo)**: Información útil pero no crítica

**Ejemplos comunes:**
- **Missing Security Headers**: Falta de headers de seguridad (X-Frame-Options, CSP, etc.)
- **Cookie Without Secure Flag**: Cookies sin flag de seguridad
- **XSS (Cross-Site Scripting)**: Vulnerabilidades de inyección de scripts
- **SQL Injection**: Vulnerabilidades de inyección SQL

---

## 📊 Ver Reportes de Cobertura

### Backend

**1. Generar reporte de cobertura:**
```bash
docker compose exec api poetry run pytest apps/ --cov=apps --cov-report=html:test-results/coverage
```

**2. Abrir reporte HTML:**
- Abre: `test-results/coverage/index.html`
- Navega por los módulos para ver qué líneas están cubiertas
- Las líneas en verde están cubiertas, en rojo no

**3. Ver cobertura en terminal:**
```bash
docker compose exec api poetry run pytest apps/ --cov=apps --cov-report=term-missing
```

Esto muestra:
- Porcentaje de cobertura por módulo
- Líneas que faltan cubrir (con números de línea)

### Frontend

**1. Generar reporte de cobertura:**
```bash
docker compose exec web sh -c "cd /app && npm run test:coverage"
```

**2. Abrir reporte HTML:**
- Abre: `test-results/frontend-coverage/index.html`
- Navega por los archivos para ver cobertura
- Revisa líneas, funciones, branches y statements

**3. Ver resumen en terminal:**
El comando anterior también muestra un resumen en la terminal con porcentajes por archivo.

### Cobertura Combinada

Para ver la cobertura total del proyecto:

1. Ejecuta el script consolidado con cobertura:
   ```bash
   ./scripts/run_all_tests.sh --coverage
   ```

2. Revisa el resumen en:
   - `test-results/test-summary-{timestamp}.md`
   - Incluye porcentajes de backend y frontend

---

## 🐛 Solución de Problemas

### Error: "pytest not found"

**Problema:** Pytest no está instalado en el contenedor.

**Solución:**
```bash
docker compose exec api poetry install
```

### Error: "vitest not found"

**Problema:** Vitest no está instalado en el contenedor.

**Solución:**
```bash
docker compose exec web sh -c "cd /app && npm install --legacy-peer-deps"
```

### Error: "Cannot find module" en frontend

**Problema:** Dependencias faltantes o node_modules corrupto.

**Solución:**
```bash
docker compose exec web sh -c "cd /app && rm -rf node_modules package-lock.json && npm install --legacy-peer-deps"
```

### Error: OWASP ZAP no encuentra el target

**Problema:** El servidor frontend no está disponible.

**Solución:**
1. Verifica que el servidor esté corriendo:
   ```bash
   curl http://localhost:3000
   ```

2. Si no está corriendo:
   ```bash
   docker compose up -d web
   ```

3. Espera unos segundos y vuelve a intentar.

### Error: "Permission denied" al ejecutar script

**Problema:** El script no tiene permisos de ejecución.

**Solución:**
```bash
chmod +x scripts/run_all_tests.sh
chmod +x scripts/owasp_zap_scan.sh
```

### Error: Tests fallan por base de datos

**Problema:** La base de datos no está inicializada o tiene datos inconsistentes.

**Solución:**
```bash
# Recrear la base de datos
docker compose exec api poetry run python manage.py migrate --run-syncdb

# O limpiar todos los datos
docker compose exec api poetry run python manage.py clear_all_data --confirm
```

### Error: "No data was collected" en cobertura

**Problema:** La configuración de cobertura no está encontrando archivos.

**Solución:**
1. Verifica que `.coveragerc` existe en la raíz del proyecto
2. Verifica que estás ejecutando desde el directorio correcto
3. Intenta ejecutar con `--cov-config=.coveragerc` explícitamente

### Tests de frontend fallan por mocks

**Problema:** Los mocks no están configurados correctamente.

**Solución:**
1. Verifica que `src/__tests__/setup.ts` tiene los mocks globales
2. Asegúrate de que los tests no sobrescriban los mocks globales
3. Revisa la consola para ver qué mock está fallando

---

## 📝 Ejemplos de Uso Común

### Antes de hacer Commit

```bash
# 1. Ejecutar pruebas backend
docker compose exec api poetry run pytest apps/ -v

# 2. Ejecutar pruebas frontend
docker compose exec web sh -c "cd /app && npm run test"

# 3. Verificar que todo pasa
```

### Antes de un Release

```bash
# Ejecutar todo con cobertura y seguridad
./scripts/run_all_tests.sh --coverage --security

# Revisar reportes en test-results/
```

### Durante Desarrollo

```bash
# Backend en modo watch
docker compose exec api poetry run pytest-watch apps/ -- -v

# Frontend en modo watch (en otra terminal)
docker compose exec web sh -c "cd /app && npm run test:watch"
```

### Verificar Cobertura Específica

```bash
# Ver cobertura de un módulo específico
docker compose exec api poetry run pytest apps/users/tests/ --cov=apps.users --cov-report=term-missing

# Ver cobertura de un archivo específico
docker compose exec api poetry run pytest apps/users/tests/test_views.py --cov=apps.users.views --cov-report=term-missing
```

---

## ✅ Checklist de Pruebas

Antes de hacer commit, ejecuta:

- [ ] Pruebas backend: `docker compose exec api poetry run pytest apps/ -v`
- [ ] Pruebas frontend: `docker compose exec web sh -c "cd /app && npm run test"`
- [ ] Cobertura backend > 70%: `docker compose exec api poetry run pytest apps/ --cov=apps --cov-report=term-missing`
- [ ] Sin errores de linting
- [ ] Tests pasan sin warnings importantes

Antes de un release:

- [ ] Ejecutar script consolidado: `./scripts/run_all_tests.sh --coverage`
- [ ] Escaneo de seguridad: `./scripts/owasp_zap_scan.sh baseline`
- [ ] Revisar reportes de cobertura
- [ ] Revisar reportes de seguridad
- [ ] Verificar que no hay vulnerabilidades críticas

---

## 📚 Recursos Adicionales

- **Documentación de Pytest**: https://docs.pytest.org/
- **Documentación de Vitest**: https://vitest.dev/
- **Documentación de OWASP ZAP**: https://www.zaproxy.org/docs/
- **Guía de Cobertura**: Ver `docs/ANALISIS_COBERTURA.md` (si existe)

---

**Última actualización**: 2025-01-XX  
**Versión**: 1.0.0

