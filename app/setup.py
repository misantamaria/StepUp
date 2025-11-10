"""
Script de configuración inicial para StepUp

Este script ayuda a configurar el entorno inicial:
1. Crea el archivo .env desde .env.example
2. Verifica dependencias
3. Proporciona instrucciones de setup
"""
import os
import sys
import shutil

def main():
    print("=" * 60)
    print("  CONFIGURACIÓN INICIAL DE STEPUP")
    print("  Estructuras de Datos - UPM")
    print("=" * 60)
    print()
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('manage.py'):
        print(" ERROR: Este script debe ejecutarse desde la carpeta 'app'")
        print("   Usa: cd app")
        sys.exit(1)
    
    # Crear .env desde .env.example si no existe
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print(" Archivo .env creado desde .env.example")
            print("⚠️  IMPORTANTE: Edita el archivo .env con tus configuraciones reales")
            print()
        else:
            print(" ERROR: No se encuentra .env.example")
            sys.exit(1)
    else:
        print("ℹ️  El archivo .env ya existe")
        print()
    
    # Mostrar siguientes pasos
    print("=" * 60)
    print("  SIGUIENTES PASOS")
    print("=" * 60)
    print()
    print("1️⃣  Edita el archivo .env con tus configuraciones:")
    print("   - SECRET_KEY")
    print("   - Configuración de base de datos (MySQL o SQLite)")
    print("   - Configuración de email (Gmail, etc.)")
    print("   - Contraseñas de usuarios")
    print()
    print("2️⃣  Crea y activa el entorno virtual:")
    print("   py -3.11 -m venv .venv")
    print("   .venv\\Scripts\\activate")
    print()
    print("3️⃣  Instala las dependencias:")
    print("   pip install -r requirements.txt")
    print()
    print("4️⃣  Aplica las migraciones:")
    print("   py manage.py makemigrations")
    print("   py manage.py migrate")
    print()
    print("5️⃣  Crea los usuarios iniciales:")
    print("   py manage.py initusers")
    print()
    print("6️⃣  Inicia el servidor:")
    print("   py manage.py runserver")
    print()
    print("7️⃣  Abre tu navegador en:")
    print("   http://127.0.0.1:8000")
    print()
    print("=" * 60)
    print("  CREDENCIALES POR DEFECTO")
    print("=" * 60)
    print("Usuario: alumno | Contraseña: alumno")
    print("Admin:   admin  | Contraseña: admin123")
    print("=" * 60)
    print()

if __name__ == '__main__':
    main()
