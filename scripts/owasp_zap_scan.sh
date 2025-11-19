#!/bin/bash
# Script para ejecutar escaneo de seguridad con OWASP ZAP

set -e

echo "🔒 Iniciando escaneo de seguridad con OWASP ZAP"
echo "================================================"

# Configuración
TARGET_URL="${TARGET_URL:-http://localhost:3000}"
REPORT_DIR="${REPORT_DIR:-test-results/security}"
TIMEOUT="${TIMEOUT:-300}"

# Crear directorio de reportes
mkdir -p "$REPORT_DIR"

# Verificar que el target esté disponible
echo "📡 Verificando que $TARGET_URL esté disponible..."
if ! curl -s -o /dev/null -w "%{http_code}" "$TARGET_URL" | grep -q "200\|301\|302"; then
    echo "❌ Error: $TARGET_URL no está disponible"
    echo "   Asegúrate de que el servidor esté corriendo"
    exit 1
fi

echo "✅ Target disponible"
echo ""

# Opción 1: Escaneo Pasivo (Rápido, no intrusivo)
if [ "$1" == "baseline" ] || [ -z "$1" ]; then
    echo "🔍 Ejecutando escaneo pasivo (baseline)..."
    docker run -t \
        -v "$(pwd)/$REPORT_DIR:/zap/wrk/:rw" \
        owasp/zap2docker-stable \
        zap-baseline.py \
        -t "$TARGET_URL" \
        -J "$REPORT_DIR/zap-baseline.json" \
        -r "$REPORT_DIR/zap-baseline.html" \
        -I
    
    echo ""
    echo "✅ Escaneo pasivo completado"
    echo "📄 Reportes generados en: $REPORT_DIR/"
fi

# Opción 2: Escaneo Activo (Lento, intrusivo)
if [ "$1" == "full" ]; then
    echo "🔍 Ejecutando escaneo activo completo..."
    docker run -t \
        -v "$(pwd)/$REPORT_DIR:/zap/wrk/:rw" \
        owasp/zap2docker-stable \
        zap-full-scan.py \
        -t "$TARGET_URL" \
        -J "$REPORT_DIR/zap-full.json" \
        -r "$REPORT_DIR/zap-full.html" \
        -I \
        -T "$TIMEOUT"
    
    echo ""
    echo "✅ Escaneo activo completado"
    echo "📄 Reportes generados en: $REPORT_DIR/"
fi

# Opción 3: Escaneo con API (Requiere ZAP corriendo)
if [ "$1" == "api" ]; then
    ZAP_HOST="${ZAP_HOST:-localhost}"
    ZAP_PORT="${ZAP_PORT:-8080}"
    
    echo "🔍 Ejecutando escaneo vía API..."
    echo "   Asegúrate de que ZAP esté corriendo en $ZAP_HOST:$ZAP_PORT"
    
    # Iniciar escaneo
    SCAN_ID=$(curl -s "http://$ZAP_HOST:$ZAP_PORT/JSON/ascan/action/scan/?url=$TARGET_URL" | jq -r '.scan')
    
    echo "📊 Escaneo iniciado. ID: $SCAN_ID"
    echo "⏳ Esperando a que termine..."
    
    # Esperar a que termine
    while true; do
        STATUS=$(curl -s "http://$ZAP_HOST:$ZAP_PORT/JSON/ascan/view/status/?scanId=$SCAN_ID" | jq -r '.status')
        echo "   Estado: $STATUS%"
        
        if [ "$STATUS" == "100" ]; then
            break
        fi
        
        sleep 5
    done
    
    # Generar reporte
    curl -s "http://$ZAP_HOST:$ZAP_PORT/OTHER/core/other/htmlreport/" > "$REPORT_DIR/zap-api-report.html"
    curl -s "http://$ZAP_HOST:$ZAP_PORT/JSON/core/view/alerts/" | jq '.' > "$REPORT_DIR/zap-api-alerts.json"
    
    echo ""
    echo "✅ Escaneo completado"
    echo "📄 Reportes generados en: $REPORT_DIR/"
fi

# Mostrar resumen
if [ -f "$REPORT_DIR/zap-baseline.json" ] || [ -f "$REPORT_DIR/zap-full.json" ]; then
    echo ""
    echo "📊 Resumen de Vulnerabilidades:"
    echo "================================"
    
    if [ -f "$REPORT_DIR/zap-baseline.json" ]; then
        echo "Baseline Scan:"
        jq -r '.site[] | "  \(.alerts[] | "\(.riskcode) - \(.name)")"' "$REPORT_DIR/zap-baseline.json" 2>/dev/null || echo "  No se pudo parsear JSON"
    fi
    
    if [ -f "$REPORT_DIR/zap-full.json" ]; then
        echo "Full Scan:"
        jq -r '.site[] | "  \(.alerts[] | "\(.riskcode) - \(.name)")"' "$REPORT_DIR/zap-full.json" 2>/dev/null || echo "  No se pudo parsear JSON"
    fi
fi

echo ""
echo "✅ Escaneo completado. Revisa los reportes en: $REPORT_DIR/"

