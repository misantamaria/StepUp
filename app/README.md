# StepUp - Estructuras de Datos

Aplicación Django para el Proyecto de Innovación Educativa (PIE) de la asignatura Estructuras de Datos.

## Requisitos
- Python 3.11+
- MySQL/MariaDB (o SQLite para desarrollo)
- pip/venv

## 🔒 Configuración de seguridad

1. **Copia la configuración:**
   ```powershell
   copy .env.example .env
   ```

2. **Edita `.env`** con tus configuraciones reales (emails, contraseñas, base de datos, etc.)

## Instalación y ejecución

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

Luego abre [http://127.0.0.1:8000](http://127.0.0.1:8000) y entra con:

* **Usuario:** `alumno`
* **Contraseña:** `alumno`

## Acceso al Admin Django

Para acceder al panel de administración en [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/):

* **Usuario:** `admin`
* **Contraseña:** `admin`

## Crear usuarios con email automático

### **Opción 1: Desde la web (recomendado)**
1. Entra como **admin** en http://127.0.0.1:8000/
2. Haz clic en **"Crear Usuario"** en el menú
3. Introduce el nombre de usuario y email

### **Opción 2: Comando de línea**
```powershell
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_user('usuario', email='usuario@example.com')"
```

### **Reset de contraseñas:**
- URL: http://127.0.0.1:8000/accounts/password_reset/
- Los emails se envían realmente si configuras SMTP en `.env`
- Para desarrollo, usa `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` para imprimir en consola

## Base de datos

### MySQL/MariaDB (Por defecto en este proyecto)
1. Crea la base de datos:
   ```sql
   CREATE DATABASE stepup_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'stepup_user'@'localhost' IDENTIFIED BY 'tu_contraseña';
   GRANT ALL PRIVILEGES ON stepup_db.* TO 'stepup_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

2. Configura en `.env` (o variables de entorno):
   ```
   DB_ENGINE=django.db.backends.mysql
   DB_NAME=stepup_db
   DB_USER=stepup_user
   DB_PASSWORD=tu_contraseña
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```
3. Driver Python: este proyecto usa PyMySQL (ya incluido en `requirements.txt`). Si aparece `ModuleNotFoundError: No module named 'pymysql'`, ejecuta en el venv:
    ```powershell
    python -m pip install PyMySQL==1.1.1
    ```

### SQLite (Desarrollo)
Para desarrollo rápido, puedes usar SQLite, pero debes editar `stepup_config/settings.py` para cambiar el motor:
```python
DATABASES = {
      'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
      }
}
```
Nota: Por defecto el proyecto usa MySQL. Cambiar a SQLite requiere modificar `settings.py` como se muestra.

## Estructura del proyecto

```
app/
├── stepup_config/       # Configuración principal del proyecto
│   ├── settings.py      # Configuración de Django
│   ├── urls.py          # URLs principales
│   └── wsgi.py          # WSGI para producción
├── boards/              # App de tableros/tests
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── users/               # App de gestión de usuarios
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── management/
│   │   └── commands/
│   │       └── initusers.py
│   └── templates/
│       ├── base.html
│       ├── registration/  # Templates de login/password reset
│       └── users/         # Templates de usuarios
├── tests/
│   └── preguntas/       # Archivos XML de preguntas
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## Configuración de Email

Para enviar emails reales (password reset, notificaciones):

### Gmail
1. Habilita la verificación en 2 pasos en tu cuenta de Google
2. Genera una "Contraseña de aplicación": https://myaccount.google.com/apppasswords
3. Configura en `.env`:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=tu-email@gmail.com
   EMAIL_HOST_PASSWORD=tu-app-password-de-16-caracteres
   ```

### Desarrollo (sin enviar emails reales)
```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```
Los emails se imprimirán en la consola del servidor.

## Tests de preguntas

Los archivos XML de preguntas se encuentran en `tests/preguntas/`. 

Para importar preguntas (implementación futura):
```powershell
python manage.py import_questions tests/preguntas/preguntas-Test-PIE-20251001-1749.xml
```

## Comandos útiles

```powershell
# Crear superusuario
python manage.py createsuperuser

# Crear usuarios iniciales
python manage.py initusers

# Limpiar y recrear la base de datos
python manage.py flush

# Ver migraciones
python manage.py showmigrations

# Shell de Django
python manage.py shell
```

## Solución de problemas

### "Couldn't import Django" o ImportError al ejecutar manage.py
Esto suele ocurrir en Windows si instalas dependencias en el entorno virtual, pero ejecutas los comandos con `py`, que ignora el venv. Solución:

```powershell
# 1) Activa el entorno virtual
.venv\Scripts\activate

# 2) Verifica que estás usando el Python del venv
python -c "import sys; print(sys.executable)"

# 3) Comprueba que Django está instalado en este entorno
python -c "import django; print(django.get_version())"

# 4) Si falla, reinstala dependencias en el venv
python -m pip install -r requirements.txt

# 5) Ejecuta SIEMPRE con 'python' (no 'py')
python manage.py migrate
python manage.py runserver
```

### Error: No module named 'pymysql'
El proyecto usa el driver PyMySQL para conectarse a MySQL (configurado en `stepup_config/__init__.py`). Si ves este error, instala la dependencia en el entorno virtual:
```powershell
python -m pip install PyMySQL==1.1.1
```
Nota: Ya está añadido en `requirements.txt`. Si persiste, asegúrate de haber ejecutado:
```powershell
python -m pip install -r requirements.txt
```

### Error de permisos en PowerShell
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Base de datos bloqueada (SQLite)
Si usas SQLite y la base de datos está bloqueada:
```powershell
# Detén el servidor y elimina el archivo
del db.sqlite3
# Vuelve a crear la base de datos
python manage.py migrate
python manage.py initusers
```

## Licencia

Proyecto educativo - Universidad Politécnica de Madrid
