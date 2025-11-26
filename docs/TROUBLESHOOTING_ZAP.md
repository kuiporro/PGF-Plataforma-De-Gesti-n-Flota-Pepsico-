# 🔧 Solución de Problemas - OWASP ZAP

Esta guía ayuda a resolver problemas comunes con el escaneo de seguridad OWASP ZAP.

## ❌ Error: Connection Refused

### Síntoma
```
ERROR HTTPConnectionPool(host='localhost', port=42582): Max retries exceeded
Connection refused: [Errno 111] Connection refused
```

### Causas Comunes

1. **Servidor Frontend no está corriendo**
   - El servidor en `http://localhost:3000` se desconectó durante el escaneo
   - El servidor nunca se inició

2. **ZAP Proxy no está disponible**
   - El proxy interno de ZAP en el puerto dinámico se desconectó
   - Problemas de red entre contenedores

3. **Timeout durante el escaneo**
   - El escaneo activo es muy largo y el servidor se desconecta
   - El servidor no puede manejar la carga del escaneo

### Soluciones

#### 1. Verificar que el servidor esté corriendo

```bash
# Verificar estado del servidor
docker compose ps web

# Si no está corriendo, iniciarlo
docker compose up -d web

# Verificar que responda
curl -I http://localhost:3000
```

#### 2. Esperar a que el servidor esté completamente iniciado

```bash
# Esperar hasta que el servidor responda
timeout 60 bash -c 'until curl -s http://localhost:3000 > /dev/null; do sleep 2; done'
```

#### 3. Usar escaneo pasivo en lugar de activo

El escaneo pasivo es más rápido y menos intrusivo:

```bash
./scripts/owasp_zap_scan.sh baseline
```

En lugar de:

```bash
./scripts/owasp_zap_scan.sh full
```

#### 4. Aumentar el timeout

Si el escaneo es muy largo, aumenta el timeout:

```bash
TIMEOUT=600 ./scripts/owasp_zap_scan.sh full
```

#### 5. Verificar logs del servidor

```bash
# Ver logs del servidor frontend
docker compose logs web --tail=50

# Verificar si hay errores
docker compose logs web | grep -i error
```

#### 6. Ejecutar escaneo con reintentos

El script ahora incluye reintentos automáticos. Si aún falla:

```bash
# Ejecutar manualmente con más reintentos
MAX_RETRIES=5 RETRY_DELAY=10 ./scripts/owasp_zap_scan.sh baseline
```

## ⚠️ Error: Failed to obtain HTTP response

### Síntoma
```
WARN Failed to obtain the HTTP response for href [id=31, type=0, URL=http://localhost:3000/_next]
Connection refused
```

### Causa
El servidor se desconectó durante el escaneo activo, probablemente debido a:
- Carga excesiva del escaneo activo
- Timeout del servidor
- Recursos insuficientes

### Solución

1. **Usar escaneo pasivo** (recomendado para desarrollo):
   ```bash
   ./scripts/owasp_zap_scan.sh baseline
   ```

2. **Aumentar recursos del servidor**:
   - Aumentar memoria disponible para el contenedor `web`
   - Reducir la carga del escaneo activo

3. **Escanear en horarios de bajo tráfico**

## 🔍 Verificar Estado de Servicios

### Comandos Útiles

```bash
# Verificar todos los servicios
docker compose ps

# Verificar solo el servidor web
docker compose ps web

# Verificar logs en tiempo real
docker compose logs -f web

# Verificar conectividad desde ZAP
docker compose exec zap curl -I http://web:3000
```

## 📊 Interpretar Logs

### Logs de ZAP

Los logs de ZAP se guardan en:
- `test-results/security/zap-baseline.log` (escaneo pasivo)
- `test-results/security/zap-full.log` (escaneo activo)

### Buscar Errores Comunes

```bash
# Errores de conexión
grep -i "connection refused" test-results/security/zap-*.log

# Errores de proxy
grep -i "proxy" test-results/security/zap-*.log

# Timeouts
grep -i "timeout" test-results/security/zap-*.log
```

## 🛠️ Configuración Avanzada

### Variables de Entorno

Puedes configurar el comportamiento del escaneo:

```bash
# Número máximo de reintentos
export MAX_RETRIES=5

# Tiempo entre reintentos (segundos)
export RETRY_DELAY=10

# Timeout del escaneo (segundos)
export TIMEOUT=600

# URL objetivo
export TARGET_URL=http://localhost:3000

# Ejecutar escaneo
./scripts/owasp_zap_scan.sh baseline
```

### Ejecutar sin Docker Compose

Si tienes problemas con Docker Compose:

```bash
USE_COMPOSE=false ./scripts/owasp_zap_scan.sh baseline
```

## ✅ Verificación Pre-Escaneo

Antes de ejecutar el escaneo, verifica:

1. ✅ Servidor frontend corriendo y respondiendo
2. ✅ Docker Compose servicios activos
3. ✅ Red entre contenedores funcionando
4. ✅ Recursos suficientes (memoria, CPU)

### Script de Verificación

```bash
#!/bin/bash
echo "Verificando servicios..."

# Verificar servidor web
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Servidor web disponible"
else
    echo "❌ Servidor web no disponible"
    exit 1
fi

# Verificar Docker Compose
if docker compose ps | grep -q "Up"; then
    echo "✅ Docker Compose servicios activos"
else
    echo "❌ Docker Compose servicios no activos"
    exit 1
fi

echo "✅ Todo listo para el escaneo"
```

## 📚 Recursos Adicionales

- [Documentación OWASP ZAP](https://www.zaproxy.org/docs/)
- [ZAP Docker Hub](https://hub.docker.com/r/owasp/zap2docker-stable)
- [Guía de Escaneo](https://www.zaproxy.org/docs/docker/about/)

## 🆘 Obtener Ayuda

Si el problema persiste:

1. Revisa los logs completos en `test-results/security/`
2. Verifica la versión de ZAP: `docker run --rm ghcr.io/zaproxy/zaproxy:stable zap.sh -version`
3. Ejecuta el escaneo con más verbosidad
4. Consulta la documentación oficial de OWASP ZAP

---

**Última actualización**: 2025-11-20

