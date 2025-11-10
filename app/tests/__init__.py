# Tests de StepUp - Sistema de análisis de progreso de alumnos

# Importar todos los módulos de tests para que estén disponibles con pytest
try:
    from .test_progreso_alumnos import *
except ImportError as e:
    print(f"Error importando test_progreso_alumnos: {e}")

try:
    from .test_progreso_sistema import *
except ImportError as e:
    print(f"Error importando test_progreso_sistema: {e}")

try:
    from .test_datos_dashboard import *
except ImportError as e:
    print(f"Error importando test_datos_dashboard: {e}")

# Funciones utilitarias para ejecutar tests rápidos
try:
    from .test_progreso_alumnos import verificar_18_alumnos, ejecutar_test_rapido, ejecutar_test_completo
except ImportError:
    pass

try:
    from .test_datos_dashboard import verificar_datos_rapido
except ImportError:
    pass

try:
    from .test_progreso_sistema import ejecutar_tests_rapidos
except ImportError:
    pass

# Lista de todas las clases de test disponibles
__all__ = [
    # Tests de progreso de alumnos
    'TestSistemaProgreso',
    'TestNombresApellidosTemplates', 
    
    # Tests del sistema general
    'TestSistemaGeneralProgreso',
    'TestBaseDatos', 
    'TestConfiguracion',
    'TestModelos',
    
    # Tests de dashboard
    'TestDatosDashboard',
    'TestRendimientoSistema',
    
    # Funciones utilitarias
    'verificar_18_alumnos',
    'ejecutar_test_rapido', 
    'ejecutar_test_completo',
    'verificar_datos_rapido',
    'ejecutar_tests_rapidos',
]
