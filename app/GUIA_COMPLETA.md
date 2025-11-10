# 🚀 GUÍA DE INSTALACIÓN Y USO - STEPUP

## 📋 Descripción General

StepUp es una plataforma educativa para gestionar tests y evaluar el progreso de alumnos en Estructuras de Datos.

### 👥 Usuarios del Sistema

1. **Alumno** (`alumno` / `alumno`)
   - Realiza tests de preguntas
   - Ve sus resultados y estadísticas
   - Accede a explicaciones de respuestas
   - **Sin acceso al panel de administración**

2. **Profesor** (`profesor` / `profesor`)
   - Gestiona preguntas y tests (crear, editar, eliminar)
   - Ve estadísticas de todos los alumnos
   - Monitoriza el progreso de los alumnos
   - **Control total sobre preguntas y tests**

3. **Profesor Ayudante** (`profesor_ayudante` / `ayudante`)
   - Crea y edita preguntas y tests
   - Ve estadísticas de alumnos
   - **NO puede eliminar preguntas ni tests**
   - Ideal para profesores en prácticas o ayudantes

4. **Administrador** (`admin` / `admin`)
   - Gestiona usuarios del sistema
   - Acceso completo al panel de administración Django
   - Control total del sistema (incluye eliminar intentos y respuestas)

---

## 🛠️ INSTALACIÓN

### Paso 1: Preparar el entorno

```powershell
# Navega a la carpeta del proyecto
cd c:\Users\macu\StepUp\app

# Crea el entorno virtual
py -3.11 -m venv .venv

# Habilita la ejecución de scripts
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Activa el entorno virtual
.venv\Scripts\activate
```

### Paso 2: Instalar dependencias

```powershell
python -m pip install -r requirements.txt
```

### Paso 3: Configurar variables de entorno

```powershell
# Copia el archivo de ejemplo
copy .env.example .env

# Edita .env con tu configuración
notepad .env
```

**Configuración mínima en `.env`:**
```env
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Para SQLite (desarrollo rápido)
# Comenta las líneas de MySQL en settings.py

# Emails (opcional para desarrollo)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Paso 4: Configurar la base de datos

#### Opción A: MySQL (Configuración por defecto del proyecto)

Este proyecto está configurado por defecto para usar MySQL/MariaDB (`ENGINE='django.db.backends.mysql'` y `pymysql` en `stepup_config/__init__.py`). Asegúrate de tener un servidor MySQL funcionando y crea la base de datos/usuario:

```sql
CREATE DATABASE stepup_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'stepup_user'@'localhost' IDENTIFIED BY 'tu_password';
GRANT ALL PRIVILEGES ON stepup_db.* TO 'stepup_user'@'localhost';
FLUSH PRIVILEGES;
```

Y en `.env` (o variables de entorno):
```env
DB_NAME=stepup_db
DB_USER=stepup_user
DB_PASSWORD=tu_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

Además, el driver Python necesario ya está en `requirements.txt`: `PyMySQL`. Si ves `ModuleNotFoundError: No module named 'pymysql'`, ejecuta:
```powershell
python -m pip install PyMySQL==1.1.1
```

#### Opción B: SQLite (Solo para desarrollo opcional)

Si prefieres un arranque rápido sin MySQL, edita `stepup_config/settings.py` y cambia la configuración de base de datos a:

```python
DATABASES = {
   'default': {
      'ENGINE': 'django.db.backends.sqlite3',
      'NAME': BASE_DIR / 'db.sqlite3',
   }
}
```
Nota: Por defecto el proyecto usa MySQL. Cambiar a SQLite requiere modificar `settings.py` como se muestra.

#### Opción C: Importar la base de datos desde `Gestion/dump_PIE_ED.sql`

El archivo `Gestion/dump_PIE_ED.sql` define tablas históricas (Alumno, Tema, Pregunta, etc.) en la base de datos `PIE_ED`. Este dump NO incluye las tablas de Django (por ejemplo, `boards_intenttest`). Si quieres partir de ese dump:

1) Crea primero la base de datos `PIE_ED` y un usuario (si no lo tienes) y luego importa el dump:

```powershell
# Crear la base de datos (como root u otro usuario con permisos)
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS PIE_ED CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Importar el dump (forzando juego de caracteres UTF-8 para evitar errores con acentos)
mysql --default-character-set=utf8mb4 -u root -p PIE_ED < "c:\Users\macu\StepUp\Gestion\dump_PIE_ED.sql"

# Si tu consola no está en UTF-8, puedes forzarla temporalmente
# (opcional) Cambiar a codepage UTF-8 en PowerShell
chcp 65001
```

2) Configura tu `.env` para apuntar a `PIE_ED`:

```env
DB_NAME=PIE_ED
DB_USER=stepup_user
DB_PASSWORD=tu_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

3) Ejecuta las migraciones de Django igualmente. Esto creará las tablas necesarias (como `boards_intenttest`) en esa misma base de datos `PIE_ED` junto con las tablas del dump:

```powershell
python manage.py makemigrations
python manage.py migrate
```

Si ves un error como «Table pie_ed.boards_intenttest doesn't exist», significa que faltan migraciones. Solución: ejecuta `python manage.py migrate` (y si es la primera vez, también `python manage.py makemigrations`).

### Paso 5: Crear la base de datos y usuarios

```powershell
# Aplicar migraciones (esto crea tablas como boards_intenttest)
python manage.py makemigrations
python manage.py migrate

# Crear los 3 usuarios del sistema
python manage.py initusers
```

### Paso 6: Iniciar el servidor

```powershell
python manage.py runserver
```

---

## 🎯 CÓMO USAR LA APLICACIÓN

### 📱 Acceder a la aplicación

Abre tu navegador en: **http://127.0.0.1:8000**

---

###  COMO ALUMNO

**Credenciales:** `alumno` / `alumno`

1. **Iniciar sesión**
   - Ve a http://127.0.0.1:8000
   - Usuario: `alumno`
   - Contraseña: `alumno`

2. **Ver tests disponibles**
   - Verás una lista de todos los tests activos
   - Cada test muestra: nombre, descripción, tiempo límite y número de preguntas

3. **Realizar un test**
   - Haz clic en "Iniciar Test"
   - Responde todas las preguntas
   - Haz clic en "Enviar Test"

4. **Ver resultados**
   - Después de enviar, verás tu puntuación
   - Revisa cada pregunta con:
     - Tu respuesta
     - La respuesta correcta (si fallaste)
     - Explicación (si está disponible)

5. **Ver historial**
   - En el dashboard verás todos tus intentos previos
   - Puedes revisar los resultados de tests anteriores

---

### 👨‍🏫 COMO PROFESOR

**Credenciales:** `profesor` / `profesor`

1. **Iniciar sesión**
   - Ve a http://127.0.0.1:8000
   - Usuario: `profesor`
   - Contraseña: `profesor`

2. **Ver dashboard**
   - Estadísticas generales: alumnos activos, tests realizados, promedio
   - Últimos intentos de todos los alumnos
   - Tests disponibles

3. **Gestionar Preguntas**
   - Clic en "Crear Pregunta" o "Gestionar Preguntas"
   - Tipos de preguntas:
     - **Opción Múltiple**: 4 opciones (A, B, C, D)
     - **Verdadero/Falso**
     - **Texto Corto**: respuesta abierta
   
   - Campos importantes:
     - Título: El enunciado de la pregunta
     - Tipo: Selecciona el tipo
     - Dificultad: Fácil, Media, Difícil
     - Tema: Categoría (ej: "Listas", "Pilas", "Árboles")
     - Respuesta correcta: La respuesta válida
     - Explicación: Ayuda al alumno a entender (opcional)

4. **Crear Tests**
   - Clic en "Crear Test"
   - Nombre y descripción del test
   - Tiempo límite en minutos
   - Selecciona las preguntas a incluir
   - Marca como "Activo" para que los alumnos lo vean

5. **Ver estadísticas de alumnos**
   - Clic en "Ver alumno" en la lista de últimos intentos
   - Ver todos los tests del alumno
   - Ver promedio y progreso

---

### 🔧 COMO ADMINISTRADOR

**Credenciales:** `admin` / `admin`

1. **Acceder al panel de administración**
   - Ve a http://127.0.0.1:8000/admin/
   - Usuario: `admin`
   - Contraseña: `admin`

2. **Gestionar usuarios**
   - Crear nuevos alumnos o profesores
   - Editar permisos
   - Asignar a grupos (Alumnos, Profesores)

3. **Control total**
   - Acceso a todas las preguntas, tests e intentos
   - Puede editar cualquier elemento del sistema

---

##  CREAR CONTENIDO DE EJEMPLO

### Crear preguntas de ejemplo:

1. Accede como **profesor** (`profesor` / `profesor`)
2. Clic en "Crear Pregunta" desde el dashboard
3. Ejemplo de pregunta:

```
Título: ¿Cuál es la complejidad de insertar un elemento al inicio de una lista enlazada?
Tipo: Opción Múltiple
Dificultad: Media
Tema: Listas Enlazadas

Opciones:
A) O(n)
B) O(1)
C) O(log n)
D) O(n²)

Respuesta correcta: B
Explicación: Insertar al inicio de una lista enlazada es O(1) porque solo requiere cambiar el puntero de cabeza.
```

4. Crea al menos 5-10 preguntas
5. Luego crea un test y añade esas preguntas

### Crear un test:

1. Clic en "Crear Test"
2. Ejemplo:

```
Nombre: Test 1 - Listas
Descripción: Evaluación sobre estructuras de datos tipo lista
Tiempo límite: 20 (minutos)
Preguntas: [Selecciona las preguntas creadas]
Activo: ✓ (marcado)
```

---

## 🔄 FLUJO COMPLETO DE USO

1. **Profesor crea preguntas** (http://127.0.0.1:8000/admin/boards/question/add/)
2. **Profesor crea un test** con esas preguntas (http://127.0.0.1:8000/admin/boards/test/add/)
3. **Alumno hace login** y ve el test disponible
4. **Alumno realiza el test** y ve sus resultados
5. **Profesor revisa estadísticas** del alumno desde su dashboard

---

## ⚡ COMANDOS ÚTILES

```powershell
# Crear usuarios
python manage.py initusers

# Crear un superusuario nuevo
python manage.py createsuperuser

# Abrir shell de Django
python manage.py shell

# Limpiar base de datos
python manage.py flush

# Ver migraciones pendientes
python manage.py showmigrations

# Rehacer migraciones (si hay problemas)
# CUIDADO: Esto borra datos
del db.sqlite3
python manage.py migrate
python manage.py initusers
```

---

## 🎨 PERSONALIZACIÓN

### Cambiar títulos y branding

Edita `users/templates/base.html`:
- Línea 5: Título de la página
- Línea 85: Título del header
- Línea 105: Texto del footer

### Añadir más tipos de preguntas

Edita `boards/models.py` y añade nuevos tipos en `TIPO_CHOICES`

---

##  SOLUCIÓN DE PROBLEMAS

### Error: No module named 'django'
```powershell
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

### "Couldn't import Django" o ImportError al ejecutar manage.py
Esto pasa si instalas en el venv pero ejecutas con `py` (que ignora el venv). Usa SIEMPRE `python` tras activar el venv:
```powershell
.venv\Scripts\activate
python -c "import sys; print(sys.executable)"
python -c "import django; print(django.get_version())"
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Error: No module named 'pymysql'
El proyecto usa PyMySQL como driver de MySQL. Instálalo en el venv:
```powershell
python -m pip install PyMySQL==1.1.1
```

### Error: tabla no existe
```powershell
py manage.py migrate
```

### No veo los tests
- Verifica que el test esté marcado como "Activo"
- Verifica que tenga preguntas asignadas
- Recarga la página

### No puedo crear preguntas
- Asegúrate de estar logueado como `profesor` o `admin`
- Ve al admin: http://127.0.0.1:8000/admin/

---

##  URLs IMPORTANTES

- **Inicio:** http://127.0.0.1:8000
- **Login:** http://127.0.0.1:8000/accounts/login/
- **Admin:** http://127.0.0.1:8000/admin/
- **Logout:** http://127.0.0.1:8000/users/logout/

---

##  RESUMEN RÁPIDO

**4 tipos de usuarios con diferentes permisos:**
- `alumno` / `alumno` → Hace tests (sin acceso admin)
- `profesor` / `profesor` → Gestiona preguntas y ve estadísticas (puede eliminar)
- `profesor_ayudante` / `ayudante` → Crea/edita preguntas (NO puede eliminar)
- `admin` / `admin` → Administra todo el sistema

**Permisos por rol:**
- **Alumno**: Solo interfaz web de tests, sin acceso a admin
- **Profesor Ayudante**: Crear y editar preguntas/tests, ver estadísticas (sin eliminar)
- **Profesor**: Control total de preguntas/tests/estadísticas (incluye eliminar)
- **Admin**: Superusuario, gestiona usuarios y puede modificar/eliminar intentos

**Para empezar:**
1. `cd app`
2. `.venv\Scripts\activate`
3. `python manage.py runserver`
4. Abre http://127.0.0.1:8000
5. Login como profesor, crea preguntas y un test
6. Login como alumno, realiza el test
7. Login como profesor, ve las estadísticas

¡Listo para usar! 🚀
