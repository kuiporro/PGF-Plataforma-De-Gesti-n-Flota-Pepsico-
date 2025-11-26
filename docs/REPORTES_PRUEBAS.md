# 📊 Guía de Reportes de Pruebas - PGF

Esta guía explica dónde encontrar y cómo interpretar los reportes generados por las pruebas automatizadas.

## 📍 Ubicación de Reportes

Todos los reportes se generan en el directorio `test-results/` en la raíz del proyecto:

```
test-results/
├── backend-report-*.html          # Reporte HTML de pytest (más reciente)
├── backend-report.html             # Último reporte (symlink)
├── analysis-*.html                # Análisis detallado HTML
├── analysis-*.txt                 # Análisis detallado texto
├── test-summary-*.md              # Resumen en Markdown
├── coverage/                      # Reportes de cobertura
│   ├── index.html                 # Cobertura HTML interactiva
│   ├── coverage.json              # Cobertura en JSON
│   ├── coverage.xml               # Cobertura en XML (CI/CD)
│   └── *.html                     # Cobertura por archivo
├── junit/                         # Reportes JUnit XML
│   └── backend-junit-*.xml        # Para integración CI/CD
├── frontend-coverage/             # Cobertura del frontend
└── security/                     # Reportes de seguridad (OWASP ZAP)
```

## 🔍 Tipos de Reportes

### 1. Reporte HTML de Pytest (`backend-report-*.html`)

**Ubicación**: `test-results/backend-report-*.html`

**Contenido**:
- Resumen general de todas las pruebas
- Lista detallada de pruebas pasadas/fallidas
- Stack traces de errores
- Tiempo de ejecución por prueba
- Estadísticas por módulo

**Cómo abrir**:
```bash
# Desde la terminal
xdg-open test-results/backend-report.html  # Linux
open test-results/backend-report.html     # Mac
start test-results/backend-report.html    # Windows

# O simplemente abrir el archivo en tu navegador
```

### 2. Análisis Detallado (`analysis-*.html` / `analysis-*.txt`)

**Ubicación**: `test-results/analysis-*.html` y `test-results/analysis-*.txt`

**Contenido**:
- Resumen ejecutivo con estadísticas clave
- Lista de pruebas fallidas con detalles
- Análisis de cobertura por módulo
- Archivos con menor cobertura
- Recomendaciones de mejora

**Generar manualmente**:
```bash
# Análisis en texto
python3 scripts/analyze_test_reports.py --latest

# Análisis en HTML
python3 scripts/analyze_test_reports.py --latest --html
```

### 3. Reporte de Cobertura (`coverage/index.html`)

**Ubicación**: `test-results/coverage/index.html`

**Contenido**:
- Cobertura total del proyecto
- Cobertura por módulo y archivo
- Líneas no cubiertas resaltadas
- Gráficos y estadísticas visuales

**Cómo abrir**:
```bash
xdg-open test-results/coverage/index.html
```

**Interpretación**:
- **Verde**: Líneas cubiertas por pruebas
- **Rojo**: Líneas no cubiertas
- **Amarillo**: Líneas parcialmente cubiertas
- **Gris**: Líneas excluidas del análisis

### 4. Reporte JUnit XML (`junit/backend-junit-*.xml`)

**Ubicación**: `test-results/junit/backend-junit-*.xml`

**Uso**: Integración con CI/CD (Jenkins, GitLab CI, GitHub Actions, etc.)

**Contenido**:
- Resultados en formato estándar JUnit
- Compatible con herramientas de CI/CD
- Incluye tiempos, errores y fallos

### 5. Resumen Markdown (`test-summary-*.md`)

**Ubicación**: `test-results/test-summary-*.md`

**Contenido**:
- Resumen ejecutivo en formato Markdown
- Enlaces a todos los reportes
- Estado de cada suite de pruebas

## 📊 Interpretación de Resultados

### Estadísticas Clave

1. **Tasa de Éxito**: Porcentaje de pruebas que pasaron
   - ✅ **> 95%**: Excelente
   - ⚠️ **80-95%**: Bueno, pero hay que revisar fallos
   - ❌ **< 80%**: Requiere atención inmediata

2. **Cobertura de Código**: Porcentaje de código cubierto por pruebas
   - ✅ **> 80%**: Excelente
   - ⚠️ **60-80%**: Aceptable, pero se puede mejorar
   - ❌ **< 60%**: Necesita más pruebas

3. **Tiempo de Ejecución**: Tiempo total de las pruebas
   - Monitorear tendencias (no debería aumentar significativamente)

### Pruebas Fallidas

Cuando hay pruebas fallidas, el reporte incluye:

1. **Nombre de la prueba**: Identifica qué funcionalidad falló
2. **Mensaje de error**: Explica por qué falló
3. **Stack trace**: Muestra dónde ocurrió el error
4. **Tiempo de ejecución**: Cuánto tardó antes de fallar

**Ejemplo de interpretación**:
```
❌ test_ingreso_requires_guardia_role
   Mensaje: assert 201 == 403
   Significado: La prueba esperaba un error 403 (Forbidden) pero recibió 201 (Created)
   Problema: El endpoint permite registrar ingresos sin validar el rol GUARDIA
   Solución: Agregar validación de permisos en el endpoint
```

## 🔧 Generar Reportes

### Ejecutar Todas las Pruebas con Reportes

```bash
# Con cobertura
./scripts/run_all_tests.sh --coverage

# Sin cobertura (más rápido)
./scripts/run_all_tests.sh
```

### Generar Análisis Detallado

```bash
# Análisis del reporte más reciente
python3 scripts/analyze_test_reports.py --latest

# Análisis en HTML
python3 scripts/analyze_test_reports.py --latest --html

# Análisis de un reporte específico
python3 scripts/analyze_test_reports.py --junit test-results/junit/backend-junit-YYYYMMDD_HHMMSS.xml
```

## 📈 Mejores Prácticas

### 1. Revisar Reportes Regularmente

- Después de cada commit importante
- Antes de hacer merge a main
- En cada release

### 2. Enfocarse en Pruebas Fallidas

1. Identificar el problema
2. Corregir el código o la prueba
3. Verificar que todas las pruebas pasen
4. Re-ejecutar el análisis

### 3. Mejorar Cobertura Gradualmente

- Priorizar archivos con < 50% de cobertura
- Enfocarse en código crítico primero
- Agregar pruebas para nuevos features

### 4. Monitorear Tendencias

- Cobertura debería aumentar o mantenerse
- Tiempo de ejecución no debería aumentar mucho
- Número de pruebas fallidas debería disminuir

## 🐛 Solución de Problemas Comunes

### No se generan reportes

**Problema**: El directorio `test-results/` está vacío o no existe.

**Solución**:
```bash
# Crear directorio si no existe
mkdir -p test-results/{coverage,junit,security,frontend-coverage}

# Ejecutar pruebas nuevamente
./scripts/run_all_tests.sh --coverage
```

### Reportes HTML no se abren

**Problema**: El navegador no puede abrir el archivo.

**Solución**:
```bash
# Verificar que el archivo existe
ls -lh test-results/backend-report*.html

# Abrir manualmente
firefox test-results/backend-report.html
# o
google-chrome test-results/backend-report.html
```

### Análisis muestra errores

**Problema**: El script de análisis no puede leer los reportes.

**Solución**:
```bash
# Verificar que los archivos existen
ls -lh test-results/junit/backend-junit-*.xml
ls -lh test-results/coverage/coverage.json

# Verificar permisos
chmod +r test-results/**/*.xml test-results/**/*.json
```

## 📚 Recursos Adicionales

- [Guía Completa de Pruebas](GUIA_PRUEBAS.md) - Cómo escribir y ejecutar pruebas
- [Comandos de Pytest](COMANDOS_PYTEST.md) - Referencia rápida de comandos
- [pytest.ini](pytest.ini) - Configuración de pytest
- [conftest.py](conftest.py) - Fixtures globales

## 🎯 Próximos Pasos

Después de revisar los reportes:

1. **Corregir pruebas fallidas**: Priorizar las más críticas
2. **Mejorar cobertura**: Agregar pruebas para código no cubierto
3. **Optimizar tiempo**: Identificar pruebas lentas y optimizarlas
4. **Documentar cambios**: Actualizar documentación si es necesario

---

**Última actualización**: 2025-11-20
**Versión**: 1.0

