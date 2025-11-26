#!/usr/bin/env python3
"""
Script para generar dump del esquema SQL desde PostgreSQL usando Django settings.

Uso:
    python scripts/dump_schema.py [output_file]
    
Ejemplo:
    python scripts/dump_schema.py docs/ESQUEMA_SQL_FROM_DB.sql
"""

import os
import sys
import subprocess
from pathlib import Path
from urllib.parse import urlparse

# Agregar el directorio raíz al path para importar Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pgf_core.settings.dev')
import django
django.setup()

from django.conf import settings

def get_db_config():
    """Obtiene la configuración de la base de datos desde Django settings."""
    db = settings.DATABASES['default']
    
    return {
        'host': db.get('HOST', 'localhost'),
        'port': db.get('PORT', '5432'),
        'name': db.get('NAME', 'pgf'),
        'user': db.get('USER', 'pgf'),
        'password': db.get('PASSWORD', 'pgf'),
    }

def check_pg_dump():
    """Verifica si pg_dump está instalado."""
    try:
        subprocess.run(['pg_dump', '--version'], 
                      capture_output=True, 
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_db_connection(config):
    """Verifica la conexión a la base de datos."""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['name'],
            user=config['user'],
            password=config['password']
        )
        conn.close()
        return True
    except ImportError:
        print("⚠️  psycopg2 no está instalado, omitiendo verificación de conexión")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def generate_dump(config, output_file):
    """Genera el dump del esquema usando pg_dump."""
    env = os.environ.copy()
    env['PGPASSWORD'] = config['password']
    
    cmd = [
        'pg_dump',
        '-h', config['host'],
        '-p', str(config['port']),
        '-d', config['name'],
        '-U', config['user'],
        '-s',  # Solo esquema (sin datos)
        '-F', 'p',  # Formato plain text
        '-E', 'UTF-8',
        '--no-owner',  # No incluir comandos de ownership
        '--no-privileges',  # No incluir comandos de privilegios
        '-f', str(output_file)
    ]
    
    try:
        result = subprocess.run(cmd, env=env, check=True, 
                               capture_output=True, text=True)
        return True, None
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def main():
    """Función principal."""
    # Obtener archivo de salida
    output_file = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE_DIR / 'docs' / 'ESQUEMA_SQL_FROM_DB.sql'
    output_file = Path(output_file)
    
    print("=" * 60)
    print("Generando dump del esquema SQL desde PostgreSQL")
    print("=" * 60)
    print()
    
    # Verificar pg_dump
    if not check_pg_dump():
        print("❌ Error: pg_dump no está instalado")
        print()
        print("Instalación:")
        print("  Ubuntu/Debian: sudo apt-get install postgresql-client")
        print("  macOS: brew install postgresql")
        print("  Windows: Descargar desde https://www.postgresql.org/download/")
        sys.exit(1)
    
    # Obtener configuración
    print("📋 Obteniendo configuración de Django...")
    config = get_db_config()
    
    print(f"   Host: {config['host']}")
    print(f"   Port: {config['port']}")
    print(f"   Database: {config['name']}")
    print(f"   User: {config['user']}")
    print()
    
    # Verificar conexión
    print("🔌 Verificando conexión a la base de datos...")
    if not check_db_connection(config):
        print("❌ No se pudo conectar a la base de datos")
        print()
        print("Verifica:")
        print("  1. Que la base de datos esté corriendo")
        print("  2. Que las credenciales sean correctas")
        print("  3. Que el host sea accesible")
        sys.exit(1)
    
    print("✓ Conexión exitosa")
    print()
    
    # Crear directorio si no existe
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Generar dump
    print(f"📦 Generando dump del esquema...")
    success, error = generate_dump(config, output_file)
    
    if success:
        print(f"✓ Dump generado exitosamente")
        print(f"📄 Archivo: {output_file}")
        print()
        
        # Mostrar tamaño del archivo
        file_size = output_file.stat().st_size
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        
        print(f"📊 Tamaño: {size_str}")
        print()
        print("=" * 60)
        print("Para usar en dbdiagram.io:")
        print("  1. Abre https://dbdiagram.io")
        print("  2. Haz clic en 'Import' o 'New Project'")
        print("  3. Selecciona 'PostgreSQL'")
        print("  4. Pega el contenido del archivo generado")
        print("=" * 60)
    else:
        print(f"❌ Error al generar el dump:")
        print(error)
        sys.exit(1)

if __name__ == '__main__':
    main()

