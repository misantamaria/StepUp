"""
Módulo de vistas de la aplicación boards.

Organización:
- home.py: Navegación principal y gestión de modos
- alumno.py: Vistas del modo alumno
- profesor.py: Vistas del modo profesor  
- decorators.py: Decoradores de acceso y permisos
"""

# Importar vistas de navegación
from .home import (
    home,
    seleccionar_modo,
    cambiar_modo,
    restablecer_preferencia_modo,
)

# Importar vistas de alumno
from .alumno import (
    dashboard_alumno,
    seleccionar_modo_alumno,
    iniciar_examen,
    realizar_examen,
    detalle_tema,
    tests_nivel,
    iniciar_test,
    realizar_test,
    resultado_test,
    mi_progreso,
    estadisticas_temas,
    historial_intentos,
)

# Importar vistas de profesor
from .profesor import (
    dashboard_profesor,
    estadisticas_alumno,
    toggle_test_field,
    toggle_tema_field,
    get_test_details,
    delete_test,
    delete_tema,
)

# Importar decoradores
from .decorators import (
    es_alumno,
    es_profesor,
    modo_requerido,
)

# Exportar todo para que sea accesible desde boards.views
__all__ = [
    # Navegación
    'home',
    'seleccionar_modo',
    'cambiar_modo',
    'restablecer_preferencia_modo',
    
    # Alumno
    'dashboard_alumno',
    'seleccionar_modo_alumno',
    'iniciar_examen',
    'realizar_examen',
    'detalle_tema',
    'tests_nivel',
    'iniciar_test',
    'realizar_test',
    'resultado_test',
    'mi_progreso',
    'estadisticas_temas',
    'historial_intentos',
    
    # Profesor
    'dashboard_profesor',
    'estadisticas_alumno',
    'toggle_test_field',
    'toggle_tema_field',
    'get_test_details',
    'delete_test',
    'delete_tema',
    
    # Decoradores
    'es_alumno',
    'es_profesor',
    'modo_requerido',
]
