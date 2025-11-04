# 🚀 INSTALACIÓN RÁPIDA - STEPUP

## Pasos para poner en marcha StepUp

### 1️⃣ Configuración inicial
```powershell
cd c:\Users\macu\StepUp\app
py setup.py
```

### 2️⃣ Editar configuración
Abre `.env` y configura:
- `SECRET_KEY` (genera una nueva para producción)
- Configuración de base de datos (MySQL o SQLite)
- Configuración de email (Gmail con App Password)
- Contraseñas de usuarios

### 3️⃣ Crear entorno virtual
```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\activate
```

### 4️⃣ Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 5️⃣ Base de datos

#### Opción A: SQLite (rápido para desarrollo)
En `.env`:
```env
# Comenta las líneas de MySQL y deja solo:
# La base de datos SQLite se creará automáticamente
```

En `settings.py`, cambia temporalmente:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### Opción B: MySQL (recomendado)
```sql
CREATE DATABASE stepup_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'stepup_user'@'localhost' IDENTIFIED BY 'tu_password';
GRANT ALL PRIVILEGES ON stepup_db.* TO 'stepup_user'@'localhost';
FLUSH PRIVILEGES;
```

En `.env`:
```env
DB_NAME=stepup_db
DB_USER=stepup_user
DB_PASSWORD=tu_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

### 6️⃣ Migraciones
```powershell
py manage.py makemigrations
py manage.py migrate
```

### 7️⃣ Crear usuarios
```powershell
py manage.py initusers
```

### 8️⃣ Iniciar servidor
```powershell
py manage.py runserver
```

### 9️⃣ Acceder
Abre tu navegador en: http://127.0.0.1:8000

**Credenciales:**
- Usuario: `alumno` / Password: `alumno`
- Admin: `admin` / Password: `admin123`

---

## 📧 Configuración de Email (Gmail)

### Generar App Password de Gmail
1. Ve a https://myaccount.google.com/apppasswords
2. Habilita verificación en 2 pasos si no lo has hecho
3. Genera una "App Password" para "Correo"
4. Copia el password de 16 caracteres

### Configurar en .env
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx-xxxx-xxxx-xxxx  # El app password de 16 caracteres
DEFAULT_FROM_EMAIL=tu-email@gmail.com
```

### Para desarrollo (sin enviar emails reales)
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

## ⚠️ Solución de problemas comunes

### Error: mysqlclient no se instala
```powershell
# Opción 1: Usa SQLite temporalmente (ver arriba)
# Opción 2: Instala Visual Studio Build Tools
# Opción 3: pip install pymysql y añade en settings.py:
import pymysql
pymysql.install_as_MySQLdb()
```

### Error: No se encuentra manage.py
```powershell
cd c:\Users\macu\StepUp\app
```

### Error: Permisos de PowerShell
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Base de datos bloqueada (SQLite)
```powershell
# Detén el servidor (Ctrl+C)
del db.sqlite3
py manage.py migrate
py manage.py initusers
```

---

## 📚 Siguientes pasos

1. **Explorar el admin**: http://127.0.0.1:8000/admin/
2. **Crear usuarios**: http://127.0.0.1:8000/users/create-user/
3. **Password reset**: http://127.0.0.1:8000/accounts/password_reset/
4. **Ver preguntas**: `app/tests/preguntas/`

---

## 📖 Documentación completa

Ver `app/README.md` para documentación completa.
