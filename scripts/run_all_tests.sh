#!/bin/bash
# Script para ejecutar todas las pruebas y generar reportes consolidados
# Uso: ./scripts/run_all_tests.sh [--coverage] [--security]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
REPORT_DIR="test-results"
COVERAGE_DIR="$REPORT_DIR/coverage"
FRONTEND_COVERAGE_DIR="$REPORT_DIR/frontend-coverage"
SECURITY_DIR="$REPORT_DIR/security"
JUNIT_DIR="$REPORT_DIR/junit"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Flags
RUN_COVERAGE=false
RUN_SECURITY=false

# Parsear argumentos
while [[ $# -gt 0 ]]; do
  case $1 in
    --coverage)
      RUN_COVERAGE=true
      shift
      ;;
    --security)
      RUN_SECURITY=true
      shift
      ;;
    *)
      echo "Opción desconocida: $1"
      echo "Uso: $0 [--coverage] [--security]"
      exit 1
      ;;
  esac
done

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🧪 Ejecutando Suite Completa de Pruebas - PGF${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Crear directorios de reportes
mkdir -p "$COVERAGE_DIR" "$FRONTEND_COVERAGE_DIR" "$SECURITY_DIR" "$JUNIT_DIR"

# ============================================================================
# 1. PRUEBAS BACKEND (Pytest)
# ============================================================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📦 Ejecutando Pruebas Backend (Pytest)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ "$RUN_COVERAGE" = true ]; then
  echo "  → Ejecutando con cobertura..."
  docker compose exec -T api poetry run pytest apps/ \
    --cov=apps \
    --cov-report=html:"$COVERAGE_DIR" \
    --cov-report=xml:"$COVERAGE_DIR/coverage.xml" \
    --cov-report=json:"$COVERAGE_DIR/coverage.json" \
    --cov-report=term-missing \
    --junit-xml="$JUNIT_DIR/backend-junit-$TIMESTAMP.xml" \
    --html="$REPORT_DIR/backend-report-$TIMESTAMP.html" \
    --self-contained-html \
    -v || {
    echo -e "${RED}❌ Pruebas backend fallaron${NC}"
    BACKEND_FAILED=true
  }
else
  echo "  → Ejecutando sin cobertura..."
  docker compose exec -T api poetry run pytest apps/ \
    --junit-xml="$JUNIT_DIR/backend-junit-$TIMESTAMP.xml" \
    --html="$REPORT_DIR/backend-report-$TIMESTAMP.html" \
    --self-contained-html \
    -v || {
    echo -e "${RED}❌ Pruebas backend fallaron${NC}"
    BACKEND_FAILED=true
  }
fi

if [ -z "$BACKEND_FAILED" ]; then
  echo -e "${GREEN}✅ Pruebas backend completadas${NC}"
  echo "  📄 Reportes generados en:"
  echo "     - $REPORT_DIR/backend-report-$TIMESTAMP.html"
  echo "     - $JUNIT_DIR/backend-junit-$TIMESTAMP.xml"
  if [ "$RUN_COVERAGE" = true ]; then
    echo "     - $COVERAGE_DIR/index.html (cobertura HTML)"
    echo "     - $COVERAGE_DIR/coverage.xml (cobertura XML)"
    echo "     - $COVERAGE_DIR/coverage.json (cobertura JSON)"
  fi
fi

echo ""

# ============================================================================
# 2. PRUEBAS FRONTEND (Vitest)
# ============================================================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🎨 Ejecutando Pruebas Frontend (Vitest)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ "$RUN_COVERAGE" = true ]; then
  echo "  → Ejecutando con cobertura..."
  docker compose exec -T web sh -c "cd /app && npm run test:coverage" 2>&1 | tee "$REPORT_DIR/frontend-output-$TIMESTAMP.log" || {
    echo -e "${RED}❌ Pruebas frontend fallaron${NC}"
    FRONTEND_FAILED=true
  }
else
  echo "  → Ejecutando sin cobertura..."
  docker compose exec -T web sh -c "cd /app && npm run test" 2>&1 | tee "$REPORT_DIR/frontend-output-$TIMESTAMP.log" || {
    echo -e "${RED}❌ Pruebas frontend fallaron${NC}"
    FRONTEND_FAILED=true
  }
fi

if [ -z "$FRONTEND_FAILED" ]; then
  echo -e "${GREEN}✅ Pruebas frontend completadas${NC}"
  echo "  📄 Reportes generados en:"
  if [ "$RUN_COVERAGE" = true ]; then
    echo "     - $FRONTEND_COVERAGE_DIR/index.html (cobertura HTML)"
    echo "     - $FRONTEND_COVERAGE_DIR/coverage.json (cobertura JSON)"
  fi
fi

echo ""

# ============================================================================
# 3. ESCANEO DE SEGURIDAD (OWASP ZAP) - Opcional
# ============================================================================
if [ "$RUN_SECURITY" = true ]; then
  echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${YELLOW}🔒 Ejecutando Escaneo de Seguridad (OWASP ZAP)${NC}"
  echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  
  # Verificar que el servidor esté corriendo
  if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200\|301\|302"; then
    echo -e "${RED}❌ Error: El servidor frontend no está disponible en http://localhost:3000${NC}"
    echo "   Inicia el servidor con: docker compose up -d web"
    SECURITY_FAILED=true
  else
    echo "  → Ejecutando escaneo pasivo (baseline)..."
    ./scripts/owasp_zap_scan.sh baseline || {
      echo -e "${RED}❌ Escaneo de seguridad falló${NC}"
      SECURITY_FAILED=true
    }
    
    if [ -z "$SECURITY_FAILED" ]; then
      echo -e "${GREEN}✅ Escaneo de seguridad completado${NC}"
      echo "  📄 Reportes generados en:"
      echo "     - $SECURITY_DIR/zap-baseline.html"
      echo "     - $SECURITY_DIR/zap-baseline.json"
    fi
  fi
  
  echo ""
fi

# ============================================================================
# 4. RESUMEN Y REPORTES CONSOLIDADOS
# ============================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  📊 Resumen de Pruebas${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# Generar reporte consolidado
SUMMARY_FILE="$REPORT_DIR/test-summary-$TIMESTAMP.md"
cat > "$SUMMARY_FILE" << EOF
# Resumen de Pruebas - $(date)

## Backend (Pytest)
- Estado: $([ -z "$BACKEND_FAILED" ] && echo "✅ PASÓ" || echo "❌ FALLÓ")
- Reporte HTML: backend-report-$TIMESTAMP.html
- Reporte JUnit: backend-junit-$TIMESTAMP.xml
$([ "$RUN_COVERAGE" = true ] && echo "- Cobertura HTML: coverage/index.html" || echo "")

## Frontend (Vitest)
- Estado: $([ -z "$FRONTEND_FAILED" ] && echo "✅ PASÓ" || echo "❌ FALLÓ")
$([ "$RUN_COVERAGE" = true ] && echo "- Cobertura HTML: frontend-coverage/index.html" || echo "")

$([ "$RUN_SECURITY" = true ] && cat << EOSEC
## Seguridad (OWASP ZAP)
- Estado: $([ -z "$SECURITY_FAILED" ] && echo "✅ COMPLETADO" || echo "❌ FALLÓ")
- Reporte HTML: security/zap-baseline.html
- Reporte JSON: security/zap-baseline.json
EOSEC
)

## Ubicación de Reportes
Todos los reportes están en: \`test-results/\`

EOF

echo -e "${GREEN}📄 Resumen generado en: $SUMMARY_FILE${NC}"
echo ""

# Mostrar estadísticas de cobertura si se ejecutó
if [ "$RUN_COVERAGE" = true ]; then
  echo -e "${BLUE}📈 Cobertura de Código:${NC}"
  
  # Backend coverage
  if [ -f "$COVERAGE_DIR/coverage.json" ]; then
    BACKEND_COV=$(python3 -c "import json; data=json.load(open('$COVERAGE_DIR/coverage.json')); print(f\"{data['totals']['percent_covered']:.1f}%\")" 2>/dev/null || echo "N/A")
    echo "  Backend: $BACKEND_COV"
  fi
  
  # Frontend coverage
  if [ -f "$FRONTEND_COVERAGE_DIR/coverage-summary.json" ]; then
    FRONTEND_COV=$(python3 -c "import json; data=json.load(open('$FRONTEND_COVERAGE_DIR/coverage-summary.json')); print(f\"{data['total']['lines']['pct']:.1f}%\")" 2>/dev/null || echo "N/A")
    echo "  Frontend: $FRONTEND_COV"
  fi
  
  echo ""
fi

# Estado final
if [ -n "$BACKEND_FAILED" ] || [ -n "$FRONTEND_FAILED" ] || [ -n "$SECURITY_FAILED" ]; then
  echo -e "${RED}❌ Algunas pruebas fallaron. Revisa los reportes para más detalles.${NC}"
  exit 1
else
  echo -e "${GREEN}✅ Todas las pruebas pasaron exitosamente${NC}"
  exit 0
fi

