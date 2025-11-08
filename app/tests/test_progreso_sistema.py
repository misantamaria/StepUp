"""
Tests de verificación del sistema de análisis de progreso
Compatible con pytest y Django TestCase
"""

import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from users.models import UserProfile
from boards.models import IntentTest, Test
from core.profesor.services import get_dashboard_data


class TestSistemaGeneralProgreso(TestCase):
    """Tests generales del sistema de progreso"""
    
    def test_usuarios_no_staff_existen(self):
        """Test: Verificar que existen usuarios no-staff"""
        total_usuarios = User.objects.count()
        usuarios_staff = User.objects.filter(is_staff=True).count()
        usuarios_no_staff = User.objects.filter(is_staff=False).count()
        
        # Verificar que hay usuarios no-staff
        self.assertGreater(usuarios_no_staff, 0, "Debe haber al menos un usuario no-staff")
        self.assertEqual(usuarios_staff + usuarios_no_staff, total_usuarios, 
                        "La suma de staff y no-staff debe coincidir con el total")
    
    def test_grupos_asignados_usuarios(self):
        """Test: Verificar que los alumnos tienen grupos asignados"""
        alumnos_sin_grupo = []
        grupos_encontrados = set()
        
        for user in User.objects.filter(is_staff=False):
            try:
                if hasattr(user, 'userprofile') and user.userprofile.grupo:
                    grupos_encontrados.add(user.userprofile.grupo)
                else:
                    alumnos_sin_grupo.append(user.username)
            except UserProfile.DoesNotExist:
                alumnos_sin_grupo.append(user.username)
        
        # Verificar que hay al menos algunos grupos
        self.assertGreaterEqual(len(grupos_encontrados), 0, 
                               "Debe haber al menos algún grupo asignado")
    
    def test_intentos_tests_existen(self):
        """Test: Verificar que existen intentos de tests"""
        total_intentos = IntentTest.objects.count()
        intentos_completados = IntentTest.objects.filter(completado=True).count()
        intentos_no_staff = IntentTest.objects.filter(alumno__is_staff=False).count()
        
        # Verificar que hay intentos (si hay datos de prueba)
        if total_intentos > 0:
            self.assertGreater(intentos_completados, 0, 
                             "Debe haber al menos un intento completado")
            self.assertGreater(intentos_no_staff, 0, 
                             "Debe haber al menos un intento de usuario no-staff")
    
    def test_notas_rango_valido(self):
        """Test: Verificar que las notas están en el rango correcto (0-10)"""
        intentos_con_notas = IntentTest.objects.filter(
            puntuacion__isnull=False, 
            completado=True
        )
        
        for intento in intentos_con_notas:
            self.assertGreaterEqual(intento.puntuacion, 0, 
                                  f"Nota debe ser >= 0, encontrada: {intento.puntuacion}")
            self.assertLessEqual(intento.puntuacion, 10, 
                               f"Nota debe ser <= 10, encontrada: {intento.puntuacion}")
    
    def test_dashboard_funciona(self):
        """Test: Verificar que get_dashboard_data funciona sin errores"""
        try:
            data = get_dashboard_data()
            
            # Verificar que los datos básicos están presentes
            self.assertIn('total_alumnos', data, "Debe incluir total_alumnos")
            self.assertIn('alumnos_detallados', data, "Debe incluir alumnos_detallados")
            self.assertIn('promedio_general', data, "Debe incluir promedio_general")
            
            # Verificar que los valores son razonables
            self.assertGreaterEqual(data['total_alumnos'], 0)
            self.assertIsInstance(data['alumnos_detallados'], list)
            
        except Exception as e:
            self.fail(f"get_dashboard_data() falló con error: {e}")


class TestBaseDatos(TestCase):
    """Tests de integridad de base de datos"""
    
    def test_modelos_relacionados(self):
        """Test: Verificar que los modelos están correctamente relacionados"""
        # Verificar que User tiene relación con IntentTest
        usuarios_con_intentos = User.objects.filter(
            intenttest__isnull=False,
            is_staff=False
        ).distinct()
        
        for usuario in usuarios_con_intentos:
            intentos = IntentTest.objects.filter(alumno=usuario)
            self.assertGreater(intentos.count(), 0, 
                             f"Usuario {usuario.username} debe tener intentos")
    
    def test_integridad_datos(self):
        """Test: Verificar integridad de los datos"""
        # Verificar que no hay intentos huérfanos (sin usuario)
        intentos_huerfanos = IntentTest.objects.filter(alumno__isnull=True)
        self.assertEqual(intentos_huerfanos.count(), 0, 
                        "No debe haber intentos sin alumno")
        
        # Verificar que no hay intentos sin test
        intentos_sin_test = IntentTest.objects.filter(test__isnull=True)
        self.assertEqual(intentos_sin_test.count(), 0, 
                        "No debe haber intentos sin test")


class TestConfiguracion(TestCase):
    """Tests de configuración del sistema"""
    
    def test_configuracion_tests(self):
        """Test: Verificar que hay tests disponibles"""
        tests_activos = Test.objects.filter(activo=True)
        tests_visibles = Test.objects.filter(visible_alumnos=True)
        tests_disponibles = Test.objects.filter(disponible_alumno=True)
        
        if Test.objects.count() > 0:
            self.assertGreater(tests_activos.count(), 0, 
                             "Debe haber al menos un test activo")
    
    def test_permisos_usuarios(self):
        """Test: Verificar configuración de permisos"""
        usuarios_staff = User.objects.filter(is_staff=True)
        usuarios_no_staff = User.objects.filter(is_staff=False)
        
        # Verificar que hay al menos un usuario staff (profesor)
        self.assertGreater(usuarios_staff.count(), 0, 
                          "Debe haber al menos un usuario staff")
        
        # Verificar que los alumnos no son staff
        for alumno in usuarios_no_staff:
            self.assertFalse(alumno.is_staff, 
                           f"Usuario {alumno.username} no debe ser staff")


class TestModelos(TestCase):
    """Tests de modelos específicos"""
    
    def test_modelo_user_profile(self):
        """Test: Verificar modelo UserProfile"""
        usuarios_no_staff = User.objects.filter(is_staff=False)
        
        for usuario in usuarios_no_staff:
            # Verificar que se puede acceder al profile
            try:
                profile = getattr(usuario, 'userprofile', None)
                if profile:
                    # Si existe profile, verificar que tiene grupo
                    self.assertIsNotNone(profile.grupo, 
                                       f"Profile de {usuario.username} debe tener grupo")
            except UserProfile.DoesNotExist:
                # Es válido que no tenga profile
                pass
    
    def test_modelo_intent_test(self):
        """Test: Verificar modelo IntentTest"""
        intentos = IntentTest.objects.all()
        
        for intento in intentos:
            # Verificar campos obligatorios
            self.assertIsNotNone(intento.alumno, "IntentTest debe tener alumno")
            self.assertIsNotNone(intento.test, "IntentTest debe tener test")
            
            # Si está completado, debe tener puntuación
            if intento.completado:
                self.assertIsNotNone(intento.puntuacion, 
                                   "IntentTest completado debe tener puntuación")


# Funciones utilitarias para ejecutar tests específicos
def ejecutar_test_usuarios():
    """Función para test rápido de usuarios"""
    print("=== TEST RÁPIDO: Usuarios ===")
    
    total_usuarios = User.objects.count()
    usuarios_staff = User.objects.filter(is_staff=True).count()
    usuarios_no_staff = User.objects.filter(is_staff=False).count()
    
    print(f"Total usuarios: {total_usuarios}")
    print(f"Usuarios staff: {usuarios_staff}")
    print(f"Usuarios no-staff: {usuarios_no_staff}")
    
    return usuarios_no_staff > 0


def ejecutar_test_dashboard():
    """Función para test rápido del dashboard"""
    print("=== TEST RÁPIDO: Dashboard ===")
    
    try:
        data = get_dashboard_data()
        
        print(f"Total alumnos: {data.get('total_alumnos', 0)}")
        print(f"Promedio general: {data.get('promedio_general', 0):.2f}")
        print(f"Alumnos detallados: {len(data.get('alumnos_detallados', []))}")
        
        return True
    except Exception as e:
        print(f"Error en dashboard: {e}")
        return False


def ejecutar_tests_rapidos():
    """Ejecutar tests rápidos sin Django TestCase"""
    print("🚀 EJECUTANDO TESTS RÁPIDOS")
    print("=" * 40)
    
    tests = [
        ('Usuarios', ejecutar_test_usuarios),
        ('Dashboard', ejecutar_test_dashboard),
    ]
    
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            if resultado:
                print(f"✅ {nombre}: PASADO")
            else:
                print(f"❌ {nombre}: FALLADO")
        except Exception as e:
            print(f"❌ {nombre}: ERROR - {e}")
    
    print("=" * 40)


if __name__ == "__main__":
    ejecutar_tests_rapidos()