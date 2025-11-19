# 🚀 Inicio Rápido - Pruebas

## Backend (Pytest)

```bash
# Instalar dependencias (ya están en pyproject.toml)
docker compose exec api poetry install

# Ejecutar todas las pruebas
docker compose exec api poetry run pytest apps/ -v

# Con cobertura
docker compose exec api poetry run pytest apps/ --cov=apps --cov-report=html

# Ver reporte de cobertura
open test-results/coverage/index.html
```

## Frontend (Vitest)

```bash
cd frontend/pgf-frontend

# Instalar dependencias
npm install

# Ejecutar pruebas
npm run test

# Modo watch (desarrollo)
npm run test:watch

# Con UI interactiva
npm run test:ui

# Con cobertura
npm run test:coverage
```

## Postman

1. Abre Postman
2. Import → Selecciona `postman/PGF_API_Collection.json`
3. Crea environment "PGF Local" con variables:
   - `base_url`: `http://localhost:8000/api/v1`
4. Ejecuta "1. Autenticación > Login"
5. Las variables se llenan automáticamente

## OWASP ZAP

```bash
# Escaneo pasivo (rápido, seguro)
./scripts/owasp_zap_scan.sh baseline

# Escaneo activo (lento, intrusivo)
./scripts/owasp_zap_scan.sh full

# Ver reportes
open test-results/security/zap-baseline.html
```

## 📚 Documentación Completa

- **Plan de Pruebas**: `TESTING_PLAN.md`
- **Guía OWASP ZAP**: `OWASP_ZAP_GUIDE.md`
- **Postman**: `postman/README.md`

