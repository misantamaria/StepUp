# App

Esta carpeta contiene la parte de la aplicación Django asociada a StepUP.

Para instalarla y usarla de manera básica puedes usar los comandos siguientes. 

```powershell
# 1) Ve al directorio de la aplicación
cd c:\Users\macu\StepUp\app

# 2) Crea y activa entorno virtual  
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\activate

# 3) Instala dependencias (asegúrate de usar el Python del venv)
python -m pip install -r requirements.txt

# 4) Configura las variables de entorno
# Copia .env.example a .env y edita con tus valores
copy .env.example .env

# 5) Migraciones de Django (usa "python", no "py")
python manage.py makemigrations
python manage.py migrate

# 6) Crea los 3 usuarios predefinidos (alumno/alumno, profesor/profesor, admin/admin)
python manage.py initusers

# 7) Arranca el servidor
python manage.py runserver
```