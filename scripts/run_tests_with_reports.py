#!/usr/bin/env python
"""
Script para ejecutar pruebas y generar reportes detallados por módulo.
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Configuración
BASE_DIR = Path(__file__).resolve().parent.parent
TEST_RESULTS_DIR = BASE_DIR / "test-results"
REPORTS_DIR = TEST_RESULTS_DIR / "reports"

# Módulos a probar
MODULES = {
    "validators": {
        "path": "apps/core/tests/test_validators.py",
        "name": "Validadores",
        "description": "Pruebas de validadores reutilizables"
    },
    "users_models": {
        "path": "apps/users/tests/test_models.py",
        "name": "Modelos de Usuarios",
        "description": "Pruebas de modelos de usuarios"
    },
    "users_serializers": {
        "path": "apps/users/tests/test_serializers.py",
        "name": "Serializers de Usuarios",
        "description": "Pruebas de serializers de usuarios"
    },
    "users_views": {
        "path": "apps/users/tests/test_views.py",
        "name": "Views de Usuarios",
        "description": "Pruebas de views de usuarios"
    },
    "vehicles_models": {
        "path": "apps/vehicles/tests/test_models.py",
        "name": "Modelos de Vehículos",
        "description": "Pruebas de modelos de vehículos"
    },
    "vehicles_serializers": {
        "path": "apps/vehicles/tests/test_serializers.py",
        "name": "Serializers de Vehículos",
        "description": "Pruebas de serializers de vehículos"
    },
    "workorders_models": {
        "path": "apps/workorders/tests/test_models.py",
        "name": "Modelos de Órdenes de Trabajo",
        "description": "Pruebas de modelos de órdenes de trabajo"
    },
    "workorders_serializers": {
        "path": "apps/workorders/tests/test_serializers.py",
        "name": "Serializers de Órdenes de Trabajo",
        "description": "Pruebas de serializers de órdenes de trabajo"
    }
}


def create_directories():
    """Crear directorios necesarios para reportes"""
    TEST_RESULTS_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)
    (REPORTS_DIR / "json").mkdir(exist_ok=True)
    (REPORTS_DIR / "html").mkdir(exist_ok=True)
    (REPORTS_DIR / "txt").mkdir(exist_ok=True)


def run_tests_for_module(module_key, module_info):
    """Ejecutar pruebas para un módulo específico y generar reportes"""
    print(f"\n{'='*80}")
    print(f"🧪 Ejecutando pruebas: {module_info['name']}")
    print(f"{'='*80}")
    print(f"📝 Descripción: {module_info['description']}")
    print(f"📁 Archivo: {module_info['path']}")
    print(f"{'='*80}\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    module_dir = REPORTS_DIR / module_key
    module_dir.mkdir(exist_ok=True)
    
    # Archivos de salida
    json_report = module_dir / f"report_{timestamp}.json"
    html_report = module_dir / f"report_{timestamp}.html"
    txt_report = module_dir / f"report_{timestamp}.txt"
    junit_xml = module_dir / f"junit_{timestamp}.xml"
    
    # Comando pytest
    cmd = [
        "pytest",
        module_info["path"],
        "-v",
        "--tb=short",
        f"--junit-xml={junit_xml}",
        f"--html={html_report}",
        "--self-contained-html",
        f"--cov={module_info['path'].split('/')[0]}",
        f"--cov-report=html:{module_dir / 'coverage'}",
        f"--cov-report=term-missing",
        f"--cov-report=json:{json_report}",
    ]
    
    # Ejecutar pruebas
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )
        
        # Guardar salida completa
        with open(txt_report, "w", encoding="utf-8") as f:
            f.write(f"Reporte de Pruebas: {module_info['name']}\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Archivo: {module_info['path']}\n")
            f.write(f"{'='*80}\n\n")
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\n\nSTDERR:\n")
            f.write(result.stderr)
            f.write(f"\n\nCódigo de salida: {result.returncode}\n")
        
        # Generar resumen JSON
        summary = {
            "module": module_key,
            "name": module_info["name"],
            "description": module_info["description"],
            "path": module_info["path"],
            "timestamp": timestamp,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "reports": {
                "json": str(json_report),
                "html": str(html_report),
                "txt": str(txt_report),
                "junit": str(junit_xml)
            }
        }
        
        # Guardar resumen
        summary_file = module_dir / f"summary_{timestamp}.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Mostrar resultado
        if result.returncode == 0:
            print(f"✅ Pruebas completadas exitosamente para {module_info['name']}")
        else:
            print(f"❌ Pruebas fallaron para {module_info['name']}")
            print(f"   Ver detalles en: {txt_report}")
        
        return summary
        
    except Exception as e:
        print(f"❌ Error ejecutando pruebas: {e}")
        return None


def generate_summary_report(all_summaries):
    """Generar reporte resumen de todas las pruebas"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = REPORTS_DIR / f"summary_all_{timestamp}.json"
    
    total_modules = len(all_summaries)
    passed_modules = sum(1 for s in all_summaries if s and s.get("exit_code") == 0)
    failed_modules = total_modules - passed_modules
    
    summary = {
        "timestamp": timestamp,
        "total_modules": total_modules,
        "passed_modules": passed_modules,
        "failed_modules": failed_modules,
        "success_rate": f"{(passed_modules/total_modules*100):.2f}%" if total_modules > 0 else "0%",
        "modules": all_summaries
    }
    
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Generar reporte HTML resumen
    html_summary = REPORTS_DIR / f"summary_all_{timestamp}.html"
    with open(html_summary, "w", encoding="utf-8") as f:
        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Resumen de Pruebas - PGF</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #003DA5; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .module {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }}
        .passed {{ border-left-color: #28a745; }}
        .failed {{ border-left-color: #dc3545; }}
        .stats {{ display: flex; gap: 20px; }}
        .stat {{ background: white; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>🧪 Resumen de Pruebas - PGF</h1>
    <p>Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="summary">
        <div class="stats">
            <div class="stat">
                <h3>Total Módulos</h3>
                <p style="font-size: 24px; font-weight: bold;">{total_modules}</p>
            </div>
            <div class="stat">
                <h3>Exitosos</h3>
                <p style="font-size: 24px; font-weight: bold; color: #28a745;">{passed_modules}</p>
            </div>
            <div class="stat">
                <h3>Fallidos</h3>
                <p style="font-size: 24px; font-weight: bold; color: #dc3545;">{failed_modules}</p>
            </div>
            <div class="stat">
                <h3>Tasa de Éxito</h3>
                <p style="font-size: 24px; font-weight: bold;">{summary['success_rate']}</p>
            </div>
        </div>
    </div>
    
    <h2>Módulos Probados</h2>
""")
        for module_summary in all_summaries:
            if module_summary:
                status_class = "passed" if module_summary.get("exit_code") == 0 else "failed"
                status_icon = "✅" if module_summary.get("exit_code") == 0 else "❌"
                f.write(f"""
    <div class="module {status_class}">
        <h3>{status_icon} {module_summary.get('name', 'Unknown')}</h3>
        <p><strong>Descripción:</strong> {module_summary.get('description', 'N/A')}</p>
        <p><strong>Archivo:</strong> {module_summary.get('path', 'N/A')}</p>
        <p><strong>Estado:</strong> {'Exitoso' if module_summary.get('exit_code') == 0 else 'Fallido'}</p>
        <p><strong>Reportes:</strong></p>
        <ul>
            <li><a href="{module_summary.get('reports', {}).get('html', '#')}">Reporte HTML</a></li>
            <li><a href="{module_summary.get('reports', {}).get('txt', '#')}">Reporte Texto</a></li>
            <li><a href="{module_summary.get('reports', {}).get('json', '#')}">Reporte JSON</a></li>
        </ul>
    </div>
""")
        f.write("""
</body>
</html>
""")
    
    print(f"\n{'='*80}")
    print(f"📊 Resumen General")
    print(f"{'='*80}")
    print(f"Total de módulos: {total_modules}")
    print(f"✅ Exitosos: {passed_modules}")
    print(f"❌ Fallidos: {failed_modules}")
    print(f"📈 Tasa de éxito: {summary['success_rate']}")
    print(f"\n📄 Reportes generados:")
    print(f"   - JSON: {summary_file}")
    print(f"   - HTML: {html_summary}")
    print(f"{'='*80}\n")


def main():
    """Función principal"""
    print("🚀 Iniciando ejecución de pruebas con reportes detallados")
    print(f"📁 Directorio base: {BASE_DIR}")
    
    create_directories()
    
    # Ejecutar pruebas para cada módulo
    all_summaries = []
    for module_key, module_info in MODULES.items():
        summary = run_tests_for_module(module_key, module_info)
        all_summaries.append(summary)
    
    # Generar resumen general
    generate_summary_report(all_summaries)
    
    print("✅ Proceso completado")


if __name__ == "__main__":
    main()

