# Plan de Pruebas - PGF Plataforma de Gestión de Flota

## 📋 Índice

1. [Estrategia de Pruebas](#estrategia-de-pruebas)
2. [Pruebas Automatizadas](#pruebas-automatizadas)
3. [Pruebas Manuales con Postman](#pruebas-manuales-con-postman)
4. [Pruebas de Seguridad con OWASP ZAP](#pruebas-de-seguridad-con-owasp-zap)
5. [Criterios de Aceptación](#criterios-de-aceptación)
6. [Herramientas y Frameworks](#herramientas-y-frameworks)

---

## 🎯 Estrategia de Pruebas

### Niveles de Pruebas

#### 1. Pruebas Unitarias
- **Backend**: Modelos, Serializers, Validadores, Permisos
- **Frontend**: Componentes, Hooks, Utilidades, Stores (Zustand)
- **Cobertura objetivo**: 80%+

#### 2. Pruebas de Integración
- **API**: Endpoints completos con base de datos
- **Frontend-Backend**: Flujos completos de usuario
- **Servicios**: S3, Redis, Celery, WebSockets

#### 3. Pruebas E2E (End-to-End)
- **Flujos críticos**: Login, Crear OT, Subir Evidencias, Generar Reportes
- **Roles y permisos**: Verificar acceso según roles

#### 4. Pruebas de Seguridad
- **OWASP Top 10**: Vulnerabilidades comunes
- **Autenticación y Autorización**: JWT, RBAC
- **Validación de entrada**: SQL Injection, XSS, CSRF

#### 5. Pruebas de Rendimiento
- **Carga**: 100 usuarios concurrentes
- **Estrés**: Límites del sistema
- **Escalabilidad**: Crecimiento de datos

---

## 🤖 Pruebas Automatizadas

### Backend (Pytest + Django)

#### Estructura de Pruebas
```
apps/
├── users/tests/
│   ├── test_models.py          ✅ Existe
│   ├── test_serializers.py     ✅ Existe
│   ├── test_views.py           ✅ Existe
│   └── test_permissions.py     ⚠️ Crear
├── vehicles/tests/
│   ├── test_models.py          ✅ Existe
│   ├── test_serializers.py     ✅ Existe
│   └── test_views.py           ⚠️ Crear
├── workorders/tests/
│   ├── test_models.py          ✅ Existe
│   ├── test_serializers.py     ✅ Existe
│   ├── test_views.py           ⚠️ Crear
│   └── test_evidencias.py      ⚠️ Crear
├── reports/tests/
│   └── test_views.py           ⚠️ Crear
└── core/tests/
    └── test_validators.py      ✅ Existe
```

#### Ejecutar Pruebas Backend

```bash
# Todas las pruebas
docker compose exec api poetry run pytest apps/ -v

# Con cobertura
docker compose exec api poetry run pytest apps/ --cov=apps --cov-report=html

# Por módulo
docker compose exec api poetry run pytest apps/users/tests/ -v

# Por marcador
docker compose exec api poetry run pytest -m unit apps/
docker compose exec api poetry run pytest -m api apps/
```

### Frontend (Vitest + React Testing Library)

#### ¿Por qué Vitest?

✅ **Ventajas de Vitest para este proyecto:**
- **Rápido**: Ejecuta pruebas en paralelo con ESM nativo
- **Compatible con Jest**: Misma API, fácil migración
- **Excelente con TypeScript**: Soporte nativo sin configuración extra
- **Hot Module Replacement**: Recarga automática en desarrollo
- **Cobertura integrada**: `@vitest/coverage` incluido
- **Perfecto para Next.js**: Funciona bien con React Server Components
- **Mejor que Jest**: Más rápido, mejor DX, menos configuración

❌ **Alternativas consideradas:**
- **Jest**: Más lento, requiere más configuración para Next.js 15
- **Playwright**: Solo para E2E, no para unitarias
- **Cypress**: Solo para E2E, más pesado

#### Configuración Vitest

```bash
# Instalar dependencias
cd frontend/pgf-frontend
npm install -D vitest @vitest/ui @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

#### Estructura de Pruebas Frontend
```
frontend/pgf-frontend/
├── src/
│   ├── __tests__/
│   │   ├── components/
│   │   │   ├── Nav.test.tsx
│   │   │   ├── RoleGuard.test.tsx
│   │   │   └── EvidenceUploader.test.tsx
│   │   ├── hooks/
│   │   │   └── useEvidence.test.ts
│   │   ├── store/
│   │   │   └── auth.test.ts
│   │   └── lib/
│   │       ├── http.test.ts
│   │       └── constants.test.ts
│   └── app/
│       └── (tests)/
│           ├── login.test.tsx
│           └── dashboard.test.tsx
```

#### Ejecutar Pruebas Frontend

```bash
# Todas las pruebas
npm run test

# Modo watch
npm run test:watch

# Con UI
npm run test:ui

# Con cobertura
npm run test:coverage
```

---

## 📮 Pruebas Manuales con Postman

### Colección de Postman

La colección incluye:

1. **Autenticación**
   - Login (obtener token)
   - Refresh token
   - Logout

2. **Usuarios**
   - Listar usuarios (con filtros)
   - Crear usuario
   - Obtener usuario por ID
   - Actualizar usuario
   - Eliminar usuario
   - Cambiar contraseña

3. **Vehículos**
   - Listar vehículos
   - Crear vehículo
   - Obtener vehículo por ID
   - Actualizar vehículo
   - Historial de vehículo

4. **Órdenes de Trabajo**
   - Listar OT
   - Crear OT
   - Obtener OT por ID
   - Actualizar estado de OT
   - Agregar items a OT
   - Crear presupuesto
   - Aprobar presupuesto

5. **Evidencias**
   - Obtener presigned URL
   - Subir evidencia (simulado)
   - Listar evidencias
   - Obtener evidencia por ID
   - Eliminar evidencia

6. **Reportes**
   - Dashboard ejecutivo
   - Reporte de productividad
   - Generar PDF (diario/semanal/mensual)

7. **Notificaciones**
   - Listar notificaciones
   - Marcar como leída
   - Contador de no leídas

### Variables de Entorno Postman

```json
{
  "base_url": "http://localhost:8000/api/v1",
  "frontend_url": "http://localhost:3000",
  "access_token": "",
  "refresh_token": "",
  "user_id": "",
  "ot_id": "",
  "vehicle_id": ""
}
```

### Flujos de Prueba Manual

#### Flujo 1: Autenticación y Acceso
1. Login con credenciales válidas
2. Verificar token en respuesta
3. Acceder a endpoint protegido con token
4. Refresh token
5. Logout

#### Flujo 2: Gestión de Usuarios (Admin)
1. Listar usuarios
2. Crear nuevo usuario
3. Obtener usuario creado
4. Actualizar usuario
5. Verificar restricción de usuario admin

#### Flujo 3: Crear Orden de Trabajo
1. Listar vehículos disponibles
2. Crear OT para vehículo
3. Agregar items a OT
4. Crear presupuesto
5. Aprobar presupuesto
6. Cambiar estado a EN_EJECUCION

#### Flujo 4: Subir Evidencia
1. Obtener presigned URL
2. Simular subida de archivo
3. Crear registro de evidencia
4. Listar evidencias de OT
5. Verificar acceso según roles

#### Flujo 5: Generar Reporte
1. Obtener datos del dashboard ejecutivo
2. Generar reporte de productividad
3. Generar PDF diario
4. Generar PDF semanal
5. Verificar descarga de PDF

---

## 🔒 Pruebas de Seguridad con OWASP ZAP

### Instalación OWASP ZAP

```bash
# Docker (recomendado)
docker pull owasp/zap2docker-stable

# O descargar desde: https://www.zaproxy.org/download/
```

### Configuración

#### 1. Escaneo Pasivo (Automático)
```bash
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:3000 \
  -J zap-report.json \
  -r zap-report.html
```

#### 2. Escaneo Activo (Requiere autenticación)
```bash
# Crear script de autenticación
docker run -t \
  -v $(pwd):/zap/wrk/:rw \
  owasp/zap2docker-stable \
  zap-full-scan.py \
  -t http://localhost:3000 \
  -g gen.conf \
  -J zap-report.json \
  -r zap-report.html
```

#### 3. Escaneo con API
```bash
# Iniciar ZAP en modo daemon
docker run -d -p 8080:8080 owasp/zap2docker-stable zap.sh -daemon

# Ejecutar escaneo vía API
curl "http://localhost:8080/JSON/ascan/action/scan/?url=http://localhost:3000"
```

### Checklist de Seguridad OWASP Top 10

#### A01:2021 – Broken Access Control
- [ ] Verificar que usuarios no pueden acceder a recursos de otros usuarios
- [ ] Verificar restricción de usuario admin
- [ ] Verificar permisos por roles (RBAC)
- [ ] Probar acceso directo a URLs sin autenticación

#### A02:2021 – Cryptographic Failures
- [ ] Verificar que contraseñas están hasheadas (bcrypt)
- [ ] Verificar que tokens JWT están firmados correctamente
- [ ] Verificar uso de HTTPS en producción
- [ ] Verificar que datos sensibles no están en logs

#### A03:2021 – Injection
- [ ] SQL Injection en filtros y búsquedas
- [ ] XSS en campos de entrada (descripciones, comentarios)
- [ ] Command Injection en subida de archivos
- [ ] Path Traversal en acceso a evidencias

#### A04:2021 – Insecure Design
- [ ] Verificar validación de entrada en todos los endpoints
- [ ] Verificar rate limiting
- [ ] Verificar manejo de errores (no exponer información sensible)

#### A05:2021 – Security Misconfiguration
- [ ] Verificar que DEBUG=False en producción
- [ ] Verificar headers de seguridad (CORS, CSP, HSTS)
- [ ] Verificar que secretos no están en código
- [ ] Verificar configuración de S3 (permisos)

#### A06:2021 – Vulnerable Components
- [ ] Verificar dependencias con vulnerabilidades conocidas
- [ ] Ejecutar `npm audit` y `poetry audit`
- [ ] Mantener dependencias actualizadas

#### A07:2021 – Authentication Failures
- [ ] Verificar fuerza de contraseñas
- [ ] Verificar expiración de tokens
- [ ] Verificar protección contra brute force
- [ ] Verificar manejo de sesiones

#### A08:2021 – Software and Data Integrity
- [ ] Verificar integridad de archivos subidos
- [ ] Verificar validación de tipos de archivo
- [ ] Verificar firmas digitales si aplica

#### A09:2021 – Security Logging Failures
- [ ] Verificar que acciones críticas están logueadas
- [ ] Verificar que logs no contienen información sensible
- [ ] Verificar rotación de logs

#### A10:2021 – Server-Side Request Forgery (SSRF)
- [ ] Verificar validación de URLs en presigned URLs
- [ ] Verificar que no se pueden hacer requests a recursos internos

### Reporte de Seguridad

Después de ejecutar OWASP ZAP, revisar:
- `zap-report.html`: Reporte visual
- `zap-report.json`: Datos estructurados
- Priorizar vulnerabilidades HIGH y CRITICAL
- Documentar falsos positivos

---

## ✅ Criterios de Aceptación

### Cobertura de Código
- **Backend**: ≥ 80%
- **Frontend**: ≥ 70%
- **Crítico**: 100% (autenticación, permisos, pagos)

### Pruebas Exitosas
- **Unitarias**: 100% deben pasar
- **Integración**: 95% deben pasar
- **E2E**: Flujos críticos 100%

### Seguridad
- **OWASP ZAP**: 0 vulnerabilidades CRITICAL
- **OWASP ZAP**: ≤ 5 vulnerabilidades HIGH
- **Dependencias**: 0 vulnerabilidades conocidas CRITICAL

### Rendimiento
- **Tiempo de respuesta API**: < 500ms (p95)
- **Carga de página**: < 2s
- **Concurrencia**: 100 usuarios simultáneos

---

## 🛠️ Herramientas y Frameworks

### Backend
- **Pytest**: Framework de pruebas
- **pytest-django**: Integración con Django
- **pytest-cov**: Cobertura de código
- **factory-boy**: Fixtures de datos
- **faker**: Datos de prueba realistas

### Frontend
- **Vitest**: Framework de pruebas (recomendado)
- **@testing-library/react**: Pruebas de componentes
- **@testing-library/user-event**: Simulación de eventos
- **jsdom**: Entorno DOM para pruebas

### Seguridad
- **OWASP ZAP**: Escaneo de vulnerabilidades
- **npm audit**: Auditoría de dependencias NPM
- **poetry audit**: Auditoría de dependencias Python
- **bandit**: Análisis estático de seguridad Python

### API Testing
- **Postman**: Pruebas manuales y automatizadas
- **Newman**: Ejecución CLI de colecciones Postman
- **REST Client (VS Code)**: Alternativa ligera

### E2E (Futuro)
- **Playwright**: Pruebas E2E completas
- **Cypress**: Alternativa para E2E

---

## 📊 Métricas y Reportes

### Reportes Generados

1. **Cobertura de Código**
   - HTML: `test-results/coverage/index.html`
   - XML: `test-results/coverage.xml`

2. **Resultados de Pruebas**
   - HTML: `test-results/report.html`
   - JUnit XML: `test-results/junit.xml`

3. **Seguridad**
   - OWASP ZAP: `zap-report.html`
   - Auditoría dependencias: `audit-report.json`

### CI/CD Integration

```yaml
# Ejemplo GitHub Actions
- name: Run Tests
  run: |
    docker compose exec api poetry run pytest apps/ --cov=apps
    cd frontend/pgf-frontend && npm run test:coverage

- name: Security Scan
  run: |
    docker run owasp/zap2docker-stable zap-baseline.py -t ${{ secrets.APP_URL }}
```

---

## 📝 Próximos Pasos

1. ✅ Configurar Vitest en frontend
2. ✅ Crear colección Postman completa
3. ✅ Configurar OWASP ZAP
4. ⚠️ Crear pruebas unitarias faltantes
5. ⚠️ Crear pruebas de integración
6. ⚠️ Configurar CI/CD con pruebas automáticas
7. ⚠️ Implementar pruebas E2E con Playwright

---

**Última actualización**: 2025-11-19
**Versión**: 1.0.0

