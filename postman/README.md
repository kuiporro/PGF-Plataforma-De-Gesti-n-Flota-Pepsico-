# Colección Postman - PGF API

## 📥 Importar Colección

1. Abre Postman
2. Click en "Import"
3. Selecciona el archivo `PGF_API_Collection.json`
4. La colección se importará con todas las carpetas y requests

## 🔧 Configurar Variables de Entorno

1. En Postman, click en "Environments" (lado izquierdo)
2. Crea un nuevo environment llamado "PGF Local"
3. Agrega las siguientes variables:

| Variable | Valor Inicial | Descripción |
|----------|---------------|-------------|
| `base_url` | `http://localhost:8000/api/v1` | URL base de la API |
| `frontend_url` | `http://localhost:3000` | URL del frontend |
| `access_token` | (vacío) | Se llena automáticamente al hacer login |
| `refresh_token` | (vacío) | Se llena automáticamente al hacer login |
| `user_id` | (vacío) | Se llena automáticamente al hacer login |
| `ot_id` | (vacío) | Se llena al crear una OT |
| `vehicle_id` | (vacío) | Se llena al crear un vehículo |

4. Selecciona este environment antes de ejecutar las requests

## 🚀 Flujos de Prueba

### Flujo 1: Autenticación Completa

1. **Login**
   - Ejecuta "1. Autenticación > Login"
   - Verifica que `access_token` y `refresh_token` se guardaron
   - Verifica que `user_id` se guardó

2. **Obtener Usuario Actual**
   - Ejecuta "1. Autenticación > Obtener Usuario Actual (Me)"
   - Verifica que retorna los datos del usuario logueado

3. **Refresh Token**
   - Espera 1 hora (o modifica expiración)
   - Ejecuta "1. Autenticación > Refresh Token"
   - Verifica que se obtiene un nuevo token

### Flujo 2: Gestión de Usuarios (Requiere ADMIN)

1. **Listar Usuarios**
   - Ejecuta "2. Usuarios > Listar Usuarios"
   - Verifica que retorna lista paginada
   - Verifica que usuario "admin" NO aparece si no eres admin

2. **Crear Usuario**
   - Ejecuta "2. Usuarios > Crear Usuario"
   - Modifica los datos en el body según necesites
   - Verifica que se crea correctamente

3. **Obtener Usuario**
   - Ejecuta "2. Usuarios > Obtener Usuario por ID"
   - Usa el ID del usuario creado
   - Verifica que retorna los datos correctos

### Flujo 3: Crear Orden de Trabajo Completa

1. **Listar Vehículos**
   - Ejecuta "3. Vehículos > Listar Vehículos"
   - Copia un `vehicle_id` de la respuesta
   - Actualiza la variable `vehicle_id` en el environment

2. **Crear OT**
   - Ejecuta "4. Órdenes de Trabajo > Crear OT"
   - Verifica que `ot_id` se guarda automáticamente
   - Verifica que la OT se crea con estado "ABIERTA"

3. **Obtener OT**
   - Ejecuta "4. Órdenes de Trabajo > Obtener OT por ID"
   - Verifica que retorna todos los datos de la OT

### Flujo 4: Subir Evidencia

1. **Obtener Presigned URL**
   - Ejecuta "5. Evidencias > Obtener Presigned URL"
   - Verifica que retorna `upload.url` y `file_url`
   - Las variables se guardan automáticamente

2. **Subir Archivo a S3** (Manual)
   - Usa la `presigned_url` obtenida
   - En Postman, crea un nuevo request tipo POST
   - Body: form-data
   - Agrega los campos de `upload.fields` de la respuesta
   - Agrega el archivo en el campo "file"
   - Ejecuta el request

3. **Crear Evidencia**
   - Ejecuta "5. Evidencias > Crear Evidencia"
   - Verifica que se crea correctamente

4. **Listar Evidencias**
   - Ejecuta "5. Evidencias > Listar Evidencias"
   - Verifica que aparece la evidencia creada

### Flujo 5: Generar Reportes

1. **Dashboard Ejecutivo**
   - Ejecuta "6. Reportes > Dashboard Ejecutivo"
   - Verifica que retorna KPIs y datos

2. **Generar PDF**
   - Ejecuta "6. Reportes > Generar PDF Diario"
   - Verifica que descarga un PDF válido
   - Cambia `tipo` a "semanal" o "mensual" para otros reportes

## 🧪 Pruebas de Seguridad

### Probar Acceso No Autorizado

1. Elimina o invalida `access_token`
2. Intenta acceder a cualquier endpoint protegido
3. Verifica que retorna 401 Unauthorized

### Probar Permisos por Roles

1. Login con usuario MECANICO
2. Intenta acceder a "Listar Usuarios"
3. Verifica que retorna 403 Forbidden

### Probar Validaciones

1. Intenta crear usuario sin campos obligatorios
2. Verifica que retorna 400 Bad Request con errores
3. Intenta crear OT con vehículo inexistente
4. Verifica que retorna error de validación

## 📊 Ejecutar con Newman (CLI)

```bash
# Instalar Newman
npm install -g newman

# Ejecutar colección completa
newman run postman/PGF_API_Collection.json \
  -e postman/PGF_Local_Environment.json \
  --reporters cli,html \
  --reporter-html-export test-results/postman-report.html

# Ejecutar solo una carpeta
newman run postman/PGF_API_Collection.json \
  -e postman/PGF_Local_Environment.json \
  --folder "1. Autenticación"
```

## 🔄 Integración CI/CD

```yaml
# GitHub Actions
- name: Run Postman Tests
  run: |
    newman run postman/PGF_API_Collection.json \
      -e postman/PGF_CI_Environment.json \
      --reporters junit \
      --reporter-junit-export test-results/postman-junit.xml
```

## 📝 Notas

- Los tokens JWT expiran en 1 hora por defecto
- Algunos endpoints requieren roles específicos
- Las variables se actualizan automáticamente con scripts de test
- Para pruebas de carga, usa Postman Runner con múltiples iteraciones

