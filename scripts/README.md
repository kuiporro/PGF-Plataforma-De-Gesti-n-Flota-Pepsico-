# Scripts de Pruebas

Este directorio contiene scripts para ejecutar pruebas y generar reportes detallados.

## Scripts Disponibles

### `run_tests_with_reports.py`

Script principal para ejecutar todas las pruebas y generar reportes detallados por módulo.

**Uso:**
```bash
# Desde el contenedor Docker
docker-compose exec api poetry run python scripts/run_tests_with_reports.py

# O directamente (si tienes las dependencias instaladas)
python scripts/run_tests_with_reports.py
```

**Características:**
- Ejecuta pruebas para cada módulo por separado
- Genera reportes en múltiples formatos (HTML, JSON, TXT, JUnit XML)
- Crea un resumen general con estadísticas
- Organiza los reportes por módulo en `test-results/reports/`

**Estructura de Reportes:**
```
test-results/
├── reports/
│   ├── validators/
│   │   ├── report_YYYYMMDD_HHMMSS.html
│   │   ├── report_YYYYMMDD_HHMMSS.json
│   │   ├── report_YYYYMMDD_HHMMSS.txt
│   │   ├── junit_YYYYMMDD_HHMMSS.xml
│   │   └── summary_YYYYMMDD_HHMMSS.json
│   ├── users_models/
│   ├── users_serializers/
│   ├── users_views/
│   ├── vehicles_models/
│   ├── vehicles_serializers/
│   ├── workorders_models/
│   ├── workorders_serializers/
│   ├── summary_all_YYYYMMDD_HHMMSS.json
│   └── summary_all_YYYYMMDD_HHMMSS.html
└── junit.xml
```

## Otros Scripts

### `run_tests.sh` (Linux/Mac)
Script bash para ejecutar pruebas con opciones.

### `run_tests.bat` (Windows)
Script batch para ejecutar pruebas en Windows.

## Visualizar Reportes

Los reportes HTML se pueden abrir directamente en el navegador:
- Reporte general: `test-results/reports/summary_all_*.html`
- Reporte por módulo: `test-results/reports/{modulo}/report_*.html`
- Cobertura: `test-results/reports/{modulo}/coverage/index.html`

