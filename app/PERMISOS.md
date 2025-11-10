# SISTEMA DE PERMISOS - STEPUP

##  Resumen de Roles y Permisos

| Rol | Usuario | Contraseña | Permisos |
|-----|---------|------------|----------|
| **Alumno** | `alumno` | `alumno` | Solo interfaz web de tests |
| **Profesor Ayudante** | `profesor_ayudante` | `ayudante` | Crear/editar preguntas y tests (sin eliminar) |
| **Profesor** | `profesor` | `profesor` | Control total de preguntas y tests |
| **Administrador** | `admin` | `admin` | Control total del sistema |

---

## Permisos Detallados

### ALUMNO
**Grupo Django**: `Alumnos`  
**is_staff**: `False`  
**is_superuser**: `False`

**Puede:**
-  Acceder a la interfaz web (no admin)
-  Ver tests disponibles
-  Realizar tests
-  Ver sus propios resultados
-  Ver explicaciones de respuestas

**NO puede:**
-  Acceder al panel de administración Django
-  Ver o modificar preguntas
-  Ver resultados de otros alumnos
-  Crear, editar o eliminar nada en la base de datos

---

### PROFESOR AYUDANTE
**Grupo Django**: `Profesores Ayudantes`  
**is_staff**: `True`  
**is_superuser**: `False`

**Permisos en modelos:**
- **Question**: `add`, `change`, `view` ( NO `delete`)
- **Test**: `add`, `change`, `view` ( NO `delete`)
- **IntentTest**: `view` (solo lectura)
- **RespuestaAlumno**: `view` (solo lectura)

**Puede:**
-  Acceder al panel de administración
-  Crear nuevas preguntas
-  Editar preguntas existentes
-  Crear nuevos tests
-  Editar tests existentes
-  Ver estadísticas de alumnos
-  Ver intentos y respuestas (solo lectura)

**NO puede:**
-  Eliminar preguntas
-  Eliminar tests
-  Modificar o eliminar intentos de tests
-  Modificar o eliminar respuestas de alumnos
-  Gestionar usuarios

**Uso ideal:** Profesores en prácticas, ayudantes de laboratorio que necesitan crear contenido pero no deben poder eliminar material existente.

---

### PROFESOR
**Grupo Django**: `Profesores`  
**is_staff**: `True`  
**is_superuser**: `False`

**Permisos en modelos:**
- **Question**: `add`, `change`, `delete`, `view` (todos)
- **Test**: `add`, `change`, `delete`, `view` (todos)
- **IntentTest**: `view` (solo lectura)
- **RespuestaAlumno**: `view` (solo lectura)

**Puede:**
-  Acceder al panel de administración
-  Crear, editar y **eliminar** preguntas
-  Crear, editar y **eliminar** tests
-  Ver estadísticas de alumnos
-  Ver intentos y respuestas (solo lectura)

**NO puede:**
-  Modificar o eliminar intentos de tests (protección de datos)
-  Modificar o eliminar respuestas de alumnos (protección de datos)
-  Gestionar usuarios
-  Acceder a configuraciones del sistema

**Uso ideal:** Profesores titulares de la asignatura con control total sobre el contenido educativo.

---

### ADMINISTRADOR
**Grupo Django**: Ninguno (superuser)  
**is_staff**: `True`  
**is_superuser**: `True`

**Puede:**
-  **TODO** - Control absoluto del sistema
-  Gestionar usuarios (crear, editar, eliminar)
-  Modificar cualquier dato en la base de datos
-  Eliminar intentos y respuestas de alumnos (si necesario)
-  Acceder a todas las configuraciones de Django
-  Ejecutar comandos de gestión

**Uso ideal:** Administrador técnico del sistema, coordinador de asignatura.

---

## Cómo Crear Usuarios con Roles Específicos

### Usuarios predefinidos (automático)
```powershell
python manage.py initusers
```
Esto crea automáticamente:
- alumno/alumno
- profesor_ayudante/ayudante
- profesor/profesor
- admin/admin

### Crear profesor ayudante adicional
```python
# En Django shell: python manage.py shell
from django.contrib.auth.models import User, Group

# Crear usuario
usuario = User.objects.create_user(
    username='ayudante2',
    password='password123',
    email='ayudante2@upm.es',
    is_staff=True
)

# Asignar al grupo
grupo = Group.objects.get(name='Profesores Ayudantes')
usuario.groups.add(grupo)
```

### Crear profesor adicional
```python
from django.contrib.auth.models import User, Group

usuario = User.objects.create_user(
    username='profesor2',
    password='password123',
    email='profesor2@upm.es',
    is_staff=True
)

grupo = Group.objects.get(name='Profesores')
usuario.groups.add(grupo)
```

### Promover ayudante a profesor
```python
from django.contrib.auth.models import User, Group

usuario = User.objects.get(username='ayudante2')
usuario.groups.clear()
grupo_profesores = Group.objects.get(name='Profesores')
usuario.groups.add(grupo_profesores)
```

---

## Verificar Permisos de un Usuario

```python
# En Django shell
from django.contrib.auth.models import User

usuario = User.objects.get(username='profesor_ayudante')

# Ver grupos
print(usuario.groups.all())

# Ver si puede eliminar preguntas
from boards.models import Question
print(usuario.has_perm('boards.delete_question'))  # False para ayudante

# Ver todos los permisos
for perm in usuario.user_permissions.all():
    print(perm)
```

---

## Protecciones Implementadas

### En el Admin (`boards/admin.py`)
- **QuestionAdmin**: `has_delete_permission()` verifica grupo Profesores o superuser
- **TestAdmin**: `has_delete_permission()` verifica grupo Profesores o superuser
- **IntentTestAdmin**: 
  - `has_add_permission()` → False (se crean automáticamente)
  - `has_delete_permission()` → Solo superuser
  - `has_change_permission()` → Solo superuser
- **RespuestaAlumnoAdmin**:
  - `has_add_permission()` → False (se crean automáticamente)
  - `has_delete_permission()` → Solo superuser
  - `has_change_permission()` → Solo superuser

### En las Vistas (`boards/views.py`)
- `@user_passes_test(es_alumno)` → Solo alumnos (no staff)
- `@user_passes_test(es_profesor)` → Solo staff (profesores y ayudantes)
- Alumnos solo ven sus propios intentos (filtrado por `request.user`)

---

## Notas Importantes

1. **Profesor Ayudante vs Profesor**:
   - La única diferencia es el permiso de eliminación
   - Ambos pueden crear y editar contenido
   - Ambos ven las mismas estadísticas

2. **Protección de datos de alumnos**:
   - Los intentos y respuestas son de **solo lectura** para profesores
   - Solo el administrador puede modificar/eliminar estos datos
   - Esto evita manipulación accidental de calificaciones

3. **Promoción de roles**:
   - Un ayudante puede ser promovido a profesor cambiando su grupo
   - Los permisos se heredan del grupo, no se asignan individualmente

4. **Auditoría**:
   - Todas las preguntas guardan `creada_por` (ForeignKey a User)
   - Todos los tests guardan `creado_por`
   - Esto permite rastrear quién creó cada contenido

---

## Cambiar Permisos (si necesitas personalizarlos)

Para modificar los permisos de un grupo:

```python
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from boards.models import Question

# Obtener el grupo
grupo = Group.objects.get(name='Profesores Ayudantes')

# Añadir permiso de eliminación (ejemplo)
ct = ContentType.objects.get_for_model(Question)
perm_delete = Permission.objects.get(content_type=ct, codename='delete_question')
grupo.permissions.add(perm_delete)

# O ejecuta de nuevo initusers para resetear permisos
# python manage.py initusers
```

---

Última actualización: Noviembre 2025
