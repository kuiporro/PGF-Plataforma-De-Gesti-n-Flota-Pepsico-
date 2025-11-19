# Guía de Uso de OWASP ZAP para PGF

## 📋 Índice

1. [Instalación](#instalación)
2. [Escaneo Pasivo (Baseline)](#escaneo-pasivo-baseline)
3. [Escaneo Activo (Full Scan)](#escaneo-activo-full-scan)
4. [Escaneo con Autenticación](#escaneo-con-autenticación)
5. [Interpretación de Resultados](#interpretación-de-resultados)
6. [Remediación](#remediación)

---

## 🚀 Instalación

### Opción 1: Docker (Recomendado)

```bash
# Descargar imagen
docker pull owasp/zap2docker-stable

# Verificar instalación
docker run owasp/zap2docker-stable zap.sh -version
```

### Opción 2: Instalación Local

**Linux:**
```bash
# Descargar desde https://www.zaproxy.org/download/
# O usar snap
snap install zaproxy
```

**Windows/Mac:**
- Descargar desde: https://www.zaproxy.org/download/
- Instalar el ejecutable

---

## 🔍 Escaneo Pasivo (Baseline)

El escaneo pasivo es **no intrusivo** y seguro para producción. Solo observa el tráfico.

### Usando el Script

```bash
# Escaneo básico
./scripts/owasp_zap_scan.sh baseline

# O especificar URL
TARGET_URL=http://localhost:3000 ./scripts/owasp_zap_scan.sh baseline
```

### Manualmente con Docker

```bash
docker run -t \
  -v $(pwd)/test-results/security:/zap/wrk/:rw \
  owasp/zap2docker-stable \
  zap-baseline.py \
  -t http://localhost:3000 \
  -J test-results/security/zap-baseline.json \
  -r test-results/security/zap-baseline.html \
  -I  # Ignorar advertencias de certificados
```

### Parámetros Importantes

- `-t URL`: URL objetivo
- `-J archivo.json`: Salida JSON
- `-r archivo.html`: Salida HTML
- `-I`: Ignorar advertencias de certificados SSL
- `-g archivo.conf`: Archivo de configuración

---

## 🔥 Escaneo Activo (Full Scan)

El escaneo activo es **intrusivo** y puede afectar la aplicación. Solo usar en desarrollo/staging.

### Usando el Script

```bash
# Escaneo completo
./scripts/owasp_zap_scan.sh full

# Con timeout personalizado (segundos)
TIMEOUT=600 ./scripts/owasp_zap_scan.sh full
```

### Manualmente con Docker

```bash
docker run -t \
  -v $(pwd)/test-results/security:/zap/wrk/:rw \
  owasp/zap2docker-stable \
  zap-full-scan.py \
  -t http://localhost:3000 \
  -J test-results/security/zap-full.json \
  -r test-results/security/zap-full.html \
  -I \
  -T 300  # Timeout en segundos
```

---

## 🔐 Escaneo con Autenticación

Para escanear endpoints protegidos, necesitas autenticarte primero.

### 1. Crear Script de Autenticación

Crea `zap-auth-script.js`:

```javascript
// Script de autenticación para ZAP
function authenticate(helper, paramsValues, credentials) {
    // Hacer login
    var loginUrl = 'http://localhost:8000/api/v1/auth/login/';
    var loginData = {
        username: credentials.getParam('username'),
        password: credentials.getParam('password')
    };
    
    var loginResponse = helper.postUrl(loginUrl, JSON.stringify(loginData));
    
    if (loginResponse.getStatusCode() === 200) {
        var jsonData = JSON.parse(loginResponse.getResponseBody().toString());
        var token = jsonData.access;
        
        // Retornar token para usar en headers
        return {
            'Authorization': 'Bearer ' + token
        };
    }
    
    return null;
}

function getRequiredParamsNames() {
    return ['username', 'password'];
}

function getOptionalParamsNames() {
    return [];
}
```

### 2. Ejecutar Escaneo con Autenticación

```bash
docker run -t \
  -v $(pwd):/zap/wrk/:rw \
  owasp/zap2docker-stable \
  zap-full-scan.py \
  -t http://localhost:3000 \
  -a zap-auth-script.js \
  -c username=admin \
  -c password=admin123 \
  -J test-results/security/zap-auth.json \
  -r test-results/security/zap-auth.html
```

---

## 📊 Interpretación de Resultados

### Niveles de Riesgo

- **Informational (0)**: Solo información, no es una vulnerabilidad
- **Low (1)**: Baja prioridad, generalmente no crítico
- **Medium (2)**: Prioridad media, debe revisarse
- **High (3)**: Alta prioridad, debe corregirse
- **Critical (4)**: Crítico, debe corregirse inmediatamente

### Vulnerabilidades Comunes

#### 1. Missing Anti-CSRF Tokens
- **Riesgo**: Medium
- **Descripción**: Falta protección CSRF
- **Solución**: Implementar tokens CSRF en formularios

#### 2. X-Frame-Options Header Missing
- **Riesgo**: Medium
- **Descripción**: Vulnerable a clickjacking
- **Solución**: Agregar header `X-Frame-Options: DENY`

#### 3. Content Security Policy (CSP) Header Not Set
- **Riesgo**: Medium
- **Descripción**: Falta política de seguridad de contenido
- **Solución**: Agregar header CSP

#### 4. X-Content-Type-Options Header Missing
- **Riesgo**: Low
- **Descripción**: Falta protección MIME sniffing
- **Solución**: Agregar header `X-Content-Type-Options: nosniff`

#### 5. SQL Injection
- **Riesgo**: High/Critical
- **Descripción**: Posible inyección SQL
- **Solución**: Usar ORM, validar entrada, usar prepared statements

#### 6. Cross-Site Scripting (XSS)
- **Riesgo**: High
- **Descripción**: Posible XSS
- **Solución**: Escapar entrada, validar datos, usar CSP

---

## 🛠️ Remediación

### Headers de Seguridad (Django)

Agregar en `settings/base.py`:

```python
# Headers de seguridad
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
```

### Protección CSRF

Ya está implementado en Django, pero verificar:

```python
# En settings
CSRF_COOKIE_SECURE = True  # Solo en producción (HTTPS)
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
```

### Validación de Entrada

```python
# Siempre validar entrada
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def validate_user_input(data):
    # Validar email
    try:
        validate_email(data['email'])
    except ValidationError:
        raise serializers.ValidationError({"email": "Email inválido"})
    
    # Escapar HTML
    from django.utils.html import escape
    data['description'] = escape(data['description'])
```

---

## 📈 Integración CI/CD

### GitHub Actions

```yaml
name: Security Scan

on:
  schedule:
    - cron: '0 0 * * 0'  # Semanal
  workflow_dispatch:

jobs:
  zap-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run ZAP Baseline Scan
        run: |
          docker run -t \
            -v ${{ github.workspace }}/test-results/security:/zap/wrk/:rw \
            owasp/zap2docker-stable \
            zap-baseline.py \
            -t ${{ secrets.APP_URL }} \
            -J test-results/security/zap-baseline.json \
            -r test-results/security/zap-baseline.html \
            -I
      
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: zap-results
          path: test-results/security/
```

---

## ✅ Checklist de Seguridad

Después de cada escaneo, verificar:

- [ ] 0 vulnerabilidades Critical
- [ ] ≤ 5 vulnerabilidades High
- [ ] Todas las vulnerabilidades High documentadas
- [ ] Falsos positivos identificados y documentados
- [ ] Plan de remediación para vulnerabilidades reales
- [ ] Headers de seguridad implementados
- [ ] Validación de entrada en todos los endpoints
- [ ] Autenticación y autorización funcionando correctamente

---

## 📚 Recursos

- [OWASP ZAP Documentation](https://www.zaproxy.org/docs/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [ZAP API Documentation](https://www.zaproxy.org/docs/api/)
- [ZAP Scripts](https://github.com/zaproxy/community-scripts)

---

**Última actualización**: 2025-11-19

