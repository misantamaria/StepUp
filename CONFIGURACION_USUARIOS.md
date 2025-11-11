# Configuración de Usuarios del Sistema StepUp

## Resumen de la Configuración

El sistema StepUp tiene configurada una base de datos **persistente** usando volúmenes de Docker, lo que garantiza que los usuarios y datos se mantienen después de reiniciar los contenedores.

## Estado Actual del Sistema

### ✅ Usuarios Básicos Configurados

| Usuario | Contraseña | Rol | Descripción |
|---------|------------|-----|-------------|
| `admin` | `admin` | Administrador | Acceso completo al sistema y panel de administración |
| `profesor` | `profesor` | Profesor | Puede crear, editar y eliminar preguntas y tests |
| `profesor_ayudante` | `ayudante` | Profesor Ayudante | Puede crear y editar preguntas, pero NO eliminar |
| `alumno` | `alumno` | Alumno de prueba | Usuario básico para pruebas |

### 👨‍🎓 Alumnos Demo (18 usuarios)

Se han creado **18 alumnos** distribuidos en **2 clases** con perfiles de rendimiento realistas:

#### Clase A (9 alumnos)
- **Ana García** (`ana_garcia`) - Excelente
- **Carlos Ruiz** (`carlos_ruiz`) - Bueno
- **Lucía Martín** (`lucia_martin`) - Bueno
- **David López** (`david_lopez`) - Regular
- **Sara González** (`sara_gonzalez`) - Regular
- **Javier Torres** (`javier_torres`) - Regular
- **Paula Herrera** (`paula_herrera`) - Bajo
- **Miguel Jiménez** (`miguel_jimenez`) - En riesgo
- **Elena Morales** (`elena_morales`) - Bajo

#### Clase B (9 alumnos)
- **Roberto Silva** (`roberto_silva`) - Especialmente bueno
- **María Castro** (`maria_castro`) - Bueno
- **Pedro Vargas** (`pedro_vargas`) - Bueno
- **Carmen Ramos** (`carmen_ramos`) - Bueno
- **Alberto Ortega** (`alberto_ortega`) - Regular
- **Natalia Cruz** (`natalia_cruz`) - Regular
- **Diego Méndez** (`diego_mendez`) - Bajo
- **Julia Vega** (`julia_vega`) -  En riesgo
- **Sergio Blanco** (`sergio_blanco`) - Bajo

**Contraseña para todos los alumnos:** `alumno123`

## Persistencia de Datos 

### Configuración de Volúmenes
- La base de datos MySQL usa el volumen `mysql_data` 
- Los datos persisten después de `docker-compose down`
- **Verificado:** Los 22 usuarios se mantienen tras reiniciar contenedores

### Estructura de Persistencia
```yaml
volumes:
  mysql_data:  # Volumen persistente para MySQL
```

## Comandos de Gestión

### Comandos Disponibles

1. **Crear usuarios básicos:**
   ```bash
   python manage.py initusers
   ```

2. **Crear alumnos demo:**
   ```bash
   python manage.py crear_alumnos_demo
   ```

3. **Ver estado del sistema:**
   ```bash
   python manage.py estado_sistema --detallado
   ```

### Ejecución en Docker
```bash
cd docker
docker-compose exec web python manage.py [comando]
```

## Verificación de la Configuración

### Test de Persistencia Realizado ✅
1. **Antes del down:** 22 usuarios
2. **`docker-compose down`** 
3. **`docker-compose up -d`**
4. **Después del up:** 22 usuarios (todos los datos intactos)

### Grupos y Permisos ✅
- **Alumnos:** 19 usuarios, sin permisos de admin
- **Profesores:** 1 usuario, 16 permisos (todos)
- **Profesores Ayudantes:** 1 usuario, 8 permisos (add/change, sin delete)

## Perfiles de Rendimiento

Los alumnos están configurados con perfiles realistas para demo:

- **1 especialmente bueno** (Roberto Silva - Clase B)
- **2 en riesgo** (Miguel Jiménez - Clase A, Julia Vega - Clase B)
- **6 buenos** (3 en cada clase)
- **6 regulares** (3 en cada clase)
- **4 de rendimiento bajo**

## Estado de la Base de Datos

- **Total usuarios:** 22
- **Alumnos:** 19 (18 con clase + 1 sin clase)
- **Staff:** 3 (profesor, profesor_ayudante, admin)
- **Superusuarios:** 1 (admin)

---

**Última verificación:** 8 de noviembre de 2025
**Estado:** ✅ Sistema completamente configurado y funcionando