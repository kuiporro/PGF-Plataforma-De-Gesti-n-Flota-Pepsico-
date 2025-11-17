# 🚀 Guía para Subir el Proyecto a GitHub

## Pasos para Subir tu Proyecto

### 1. Crear el Repositorio en GitHub

1. Ve a [GitHub](https://github.com) e inicia sesión
2. Haz clic en el botón **"+"** en la esquina superior derecha
3. Selecciona **"New repository"**
4. Completa el formulario:
   - **Repository name**: `pgf` (o el nombre que prefieras)
   - **Description**: "Plataforma de Gestión de Flota"
   - **Visibility**: Elige **Private** o **Public**
   - ⚠️ **NO marques** "Initialize this repository with a README" (ya tenemos uno)
5. Haz clic en **"Create repository"**

### 2. Conectar tu Repositorio Local con GitHub

Después de crear el repositorio, GitHub te mostrará instrucciones. Ejecuta estos comandos en tu terminal:

```bash
# Asegúrate de estar en la raíz del proyecto
cd C:\Users\luxo_\Documents\pepsicco\pgf

# Agrega el remoto (reemplaza TU_USUARIO con tu usuario de GitHub)
git remote add origin https://github.com/TU_USUARIO/pgf.git

# Verifica que se agregó correctamente
git remote -v
```

### 3. Subir el Código

```bash
# Sube el código a GitHub
git push -u origin main
```

Si GitHub te pide autenticación:
- Puedes usar un **Personal Access Token** en lugar de tu contraseña
- O configurar SSH keys (más seguro para el futuro)

### 4. Verificar

Ve a tu repositorio en GitHub y verifica que todos los archivos estén ahí.

## 🔐 Autenticación con GitHub

### Opción 1: Personal Access Token (Más Fácil)

1. Ve a GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Genera un nuevo token con permisos `repo`
3. Cuando git te pida la contraseña, usa el token en su lugar

### Opción 2: SSH (Más Seguro)

```bash
# Generar clave SSH (si no tienes una)
ssh-keygen -t ed25519 -C "tu-email@example.com"

# Copiar la clave pública
cat ~/.ssh/id_ed25519.pub

# Agregar la clave en GitHub: Settings → SSH and GPG keys → New SSH key
```

Luego cambia la URL del remoto:
```bash
git remote set-url origin git@github.com:TU_USUARIO/pgf.git
```

## 📋 Comandos Útiles para el Futuro

```bash
# Ver estado de cambios
git status

# Agregar cambios
git add .

# Hacer commit
git commit -m "Descripción de los cambios"

# Subir cambios
git push

# Ver historial
git log --oneline

# Crear una nueva rama
git checkout -b nombre-de-rama

# Cambiar de rama
git checkout main
```

## ⚠️ Notas Importantes

1. **Nunca subas archivos `.env`** - Ya están en `.gitignore`
2. **No subas `node_modules`** - Ya está en `.gitignore`
3. **No subas `__pycache__`** - Ya está en `.gitignore`
4. El archivo `.env.example` está incluido como plantilla

## 🎉 ¡Listo!

Una vez subido, tu proyecto estará disponible en:
`https://github.com/TU_USUARIO/pgf`

