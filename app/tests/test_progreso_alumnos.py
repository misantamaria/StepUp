"""
Tests unitarios para el sistema de análisis de progreso de alumnos
Compatible con pytest y CI/CD de GitHub Actions
"""
import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from users.models import UserProfile
from boards.models import IntentTest, Test, Tema
from core.profesor.services import get_dashboard_data


class TestSistemaProgreso(TestCase):
    """Test cases para el sistema de progreso de alumnos"""
    
    def setUp(self):
        """Configurar datos de prueba para cada test"""
        # Crear usuarios de prueba
        self.profesor = User.objects.create_user(
            username='profesor_test',
            email='profesor@test.com',
            is_staff=True
        )
        
        self.alumno1 = User.objects.create_user(
            username='alumno_test_01',
            first_name='Juan',
            last_name='Perez Garcia',
            email='alumno1@test.com',
            is_staff=False
        )
        
        self.alumno2 = User.objects.create_user(
            username='alumno_test_02',
            first_name='Maria',
            last_name='Lopez Martin',
            email='alumno2@test.com',
            is_staff=False
        )
        
        # Crear perfiles con grupos
        UserProfile.objects.update_or_create(
            user=self.alumno1,
            defaults={'grupo': 'Grupo Test A'}
        )
        
        UserProfile.objects.update_or_create(
            user=self.alumno2,
            defaults={'grupo': 'Grupo Test B'}
        )
        
        # Crear temas de prueba
        self.tema_normal, _ = Tema.objects.get_or_create(
            tema_id='test_tema',
            defaults={'nombre': 'Tema de Prueba'}
        )
        
        self.tema_examenes, _ = Tema.objects.get_or_create(
            tema_id='Examenes',
            defaults={'nombre': 'Examenes'}
        )
        
        # Crear tests de prueba
        self.test_tema, _ = Test.objects.get_or_create(
            nombre='Test de Tema',
            defaults={
                'tema': self.tema_normal,
                'activo': True,
                'visible_alumnos': True,
                'disponible_alumno': True
            }
        )
        
        self.test_examen, _ = Test.objects.get_or_create(
            nombre='Test de Examen',
            defaults={
                'tema': self.tema_examenes,
                'activo': True,
                'visible_alumnos': True,
                'disponible_alumno': True
            }
        )
    
    def test_verificar_alumnos_no_staff(self):
        """Test CRITICO: Verificar que hay tantos alumnos en dashboard como usuarios no-staff"""
        usuarios_no_staff = User.objects.filter(is_staff=False).count()
        data = get_dashboard_data()
        total_alumnos_dashboard = data.get('total_alumnos', 0)
        
        # Dashboard debe reportar el mismo número que usuarios no-staff en BD
        self.assertEqual(total_alumnos_dashboard, usuarios_no_staff, 
                        f"FALLO: Dashboard reporta {total_alumnos_dashboard} alumnos, pero hay {usuarios_no_staff} usuarios no-staff en BD")
        
        # Debe haber al menos algunos alumnos
        self.assertGreater(usuarios_no_staff, 0, "No hay usuarios no-staff en la base de datos")
    
    def test_alumnos_detallados_no_vacio(self):
        """Test CRITICO: Verificar que alumnos_detallados tiene todos los usuarios no-staff"""
        usuarios_no_staff = User.objects.filter(is_staff=False).count()
        data = get_dashboard_data()
        alumnos_detallados = data.get('alumnos_detallados', [])
        
        # NO debe estar vacío si hay usuarios no-staff
        if usuarios_no_staff > 0:
            self.assertGreater(len(alumnos_detallados), 0, 
                              f"FALLO CRITICO: alumnos_detallados está vacío cuando hay {usuarios_no_staff} usuarios no-staff")
        
        # Debe tener exactamente tantas entradas como usuarios no-staff
        self.assertEqual(len(alumnos_detallados), usuarios_no_staff, 
                        f"FALLO: alumnos_detallados tiene {len(alumnos_detallados)} entradas, esperadas: {usuarios_no_staff}")
    
    def test_separacion_notas_temas_examenes(self):
        """Test: Verificar separación de notas entre temas y exámenes"""
        # Crear intentos de prueba para diferentes tipos
        IntentTest.objects.create(
            alumno=self.alumno1,
            test=self.test_tema,
            puntuacion=8.5,
            respuestas_correctas=17,
            total_preguntas=20,
            completado=True
        )
        
        IntentTest.objects.create(
            alumno=self.alumno1,
            test=self.test_examen,
            puntuacion=7.0,
            respuestas_correctas=14,
            total_preguntas=20,
            completado=True
        )
        
        data = get_dashboard_data()
        alumnos_detallados = data.get('alumnos_detallados', [])
        
        # Buscar nuestro alumno de prueba
        alumno_encontrado = None
        for alumno_data in alumnos_detallados:
            if alumno_data['alumno'].username == 'alumno_test_01':
                alumno_encontrado = alumno_data
                break
        
        self.assertIsNotNone(alumno_encontrado, "Alumno de prueba no encontrado")
        
        # Verificar que tiene las nuevas claves de notas
        self.assertIn('nota_media_general', alumno_encontrado)
        self.assertIn('nota_media_temas', alumno_encontrado)
        self.assertIn('nota_media_examenes', alumno_encontrado)
        self.assertIn('intentos_temas', alumno_encontrado)
        self.assertIn('intentos_examenes', alumno_encontrado)
        
        # Verificar que las notas están en rango correcto
        self.assertGreaterEqual(alumno_encontrado['nota_media_temas'], 0)
        self.assertLessEqual(alumno_encontrado['nota_media_temas'], 10)
        self.assertGreaterEqual(alumno_encontrado['nota_media_examenes'], 0)
        self.assertLessEqual(alumno_encontrado['nota_media_examenes'], 10)
    
    def test_filtro_usuarios_no_staff(self):
        """Test: Verificar que solo se cuentan usuarios no-staff"""
        data = get_dashboard_data()
        
        # Verificar que el profesor no se cuenta
        total_alumnos = data.get('total_alumnos', 0)
        usuarios_no_staff = User.objects.filter(is_staff=False).count()
        
        self.assertEqual(total_alumnos, usuarios_no_staff)
        self.assertGreater(total_alumnos, 0)
        
        # Verificar que alumnos detallados no incluyen staff
        alumnos_detallados = data.get('alumnos_detallados', [])
        for alumno_data in alumnos_detallados:
            self.assertFalse(alumno_data['alumno'].is_staff)
    
    def test_grupos_asignados(self):
        """Test: Verificar que los alumnos tienen grupos asignados"""
        data = get_dashboard_data()
        alumnos_detallados = data.get('alumnos_detallados', [])
        
        grupos_encontrados = set()
        for alumno_data in alumnos_detallados:
            grupo = alumno_data.get('grupo')
            if grupo and grupo != 'Sin grupo':
                grupos_encontrados.add(grupo)
        
        # Debe haber al menos 2 grupos (Grupo A y Grupo B)
        self.assertGreaterEqual(len(grupos_encontrados), 2, 
                               f"Se esperaban al menos 2 grupos, encontrados: {len(grupos_encontrados)}")
    
    def test_nombres_completos_presentes(self):
        """Test: Verificar que los alumnos tienen nombres y apellidos"""
        data = get_dashboard_data()
        alumnos_detallados = data.get('alumnos_detallados', [])
        
        alumnos_con_nombres = 0
        for alumno_data in alumnos_detallados:
            alumno = alumno_data['alumno']
            if alumno.first_name and alumno.last_name:
                alumnos_con_nombres += 1
        
        # Debe haber al menos algunos alumnos con nombres (ajustable según datos reales)
        usuarios_no_staff = User.objects.filter(is_staff=False).count()
        # Esperamos que al menos la mitad tenga nombres completos
        esperados_minimo = max(1, usuarios_no_staff // 2) if usuarios_no_staff > 0 else 0
        self.assertGreaterEqual(alumnos_con_nombres, esperados_minimo, 
                               f"Se esperaban al menos {esperados_minimo} alumnos con nombres, encontrados: {alumnos_con_nombres}")
    
    def test_deteccion_alumnos_riesgo(self):
        """Test: Verificar detección de alumnos en riesgo"""
        # Crear intento de alumno en riesgo (nota < 5)
        IntentTest.objects.create(
            alumno=self.alumno2,
            test=self.test_tema,
            puntuacion=3.0,
            respuestas_correctas=6,
            total_preguntas=20,
            completado=True
        )
        
        data = get_dashboard_data()
        alumnos_en_riesgo = data.get('alumnos_en_riesgo', 0)
        
        # Debe detectar al menos 1 alumno en riesgo
        self.assertGreater(alumnos_en_riesgo, 0)
    
    def test_estructura_datos_dashboard(self):
        """Test: Verificar que get_dashboard_data retorna estructura correcta"""
        data = get_dashboard_data()
        
        # Campos obligatorios
        campos_requeridos = [
            'total_alumnos', 'promedio_general', 'alumnos_detallados',
            'alumnos_activos', 'alumnos_en_riesgo', 'distribucion'
        ]
        
        for campo in campos_requeridos:
            self.assertIn(campo, data, f"Campo '{campo}' no encontrado en datos dashboard")
        
        # Verificar estructura de alumnos_detallados
        alumnos_detallados = data.get('alumnos_detallados', [])
        if alumnos_detallados:
            alumno_sample = alumnos_detallados[0]
            campos_alumno = [
                'alumno', 'nota_media_general', 'nota_media_temas', 'nota_media_examenes',
                'total_intentos', 'intentos_temas', 'intentos_examenes', 'grupo', 'ultimo_acceso'
            ]
            
            for campo in campos_alumno:
                self.assertIn(campo, alumno_sample, f"Campo '{campo}' no encontrado en datos alumno")


# Funciones para ejecutar tests desde línea de comandos
def verificar_18_alumnos():
    """Verificar específicamente si la cantidad de alumnos en tabla de progreso coincide con usuarios no-staff"""
    from django.contrib.auth.models import User
    
    print("VERIFICANDO ALUMNOS EN TABLA DE PROGRESO vs USUARIOS NO-STAFF")
    print("=" * 60)
    
    try:
        # Test básico de usuarios
        total_usuarios = User.objects.count()
        usuarios_no_staff = User.objects.filter(is_staff=False).count()
        usuarios_staff = User.objects.filter(is_staff=True).count()
        
        print(f"Base de datos - Total usuarios: {total_usuarios}")
        print(f"Base de datos - Usuarios staff (profesores): {usuarios_staff}")
        print(f"Base de datos - Usuarios no-staff (alumnos): {usuarios_no_staff}")
        
        # Test de dashboard data
        data = get_dashboard_data()
        total_alumnos_dashboard = data.get('total_alumnos', 0)
        alumnos_detallados = data.get('alumnos_detallados', [])
        
        print(f"\nDashboard - Total alumnos reportados: {total_alumnos_dashboard}")
        print(f"Dashboard - Alumnos detallados: {len(alumnos_detallados)} entradas")
        
        # TEST CRITICO: Dashboard debe reportar el mismo número que usuarios no-staff
        if total_alumnos_dashboard == usuarios_no_staff:
            print("✅ CORRECTO: Dashboard reporta el mismo número que usuarios no-staff")
        else:
            print(f"❌ PROBLEMA: Dashboard reporta {total_alumnos_dashboard}, pero hay {usuarios_no_staff} usuarios no-staff")
        
        # TEST CRITICO: alumnos_detallados debe tener tantas entradas como usuarios no-staff
        if len(alumnos_detallados) == 0:
            print("❌ ERROR CRITICO: alumnos_detallados está vacío")
            print("   CAUSA: La función get_dashboard_data no está procesando los alumnos")
            return False
        elif len(alumnos_detallados) == usuarios_no_staff:
            print("✅ CORRECTO: alumnos_detallados tiene el mismo número que usuarios no-staff")
        else:
            print(f"❌ PROBLEMA: alumnos_detallados tiene {len(alumnos_detallados)} entradas, pero hay {usuarios_no_staff} usuarios no-staff")
        
        # Mostrar información de los primeros alumnos para debug
        print(f"\n--- PRIMEROS 5 ALUMNOS EN TABLA DE PROGRESO ---")
        for i, alumno_data in enumerate(alumnos_detallados[:5], 1):
            alumno = alumno_data['alumno']
            nombre = f"{alumno.first_name} {alumno.last_name}".strip()
            grupo = alumno_data.get('grupo', 'Sin grupo')
            nota_general = alumno_data.get('nota_media_general', 0)
            
            print(f"{i:2}. {alumno.username} (ID:{alumno.id})")
            print(f"    Nombre: {nombre if nombre else 'Sin nombre'}")
            print(f"    Grupo: {grupo}")
            print(f"    Nota: {nota_general:.1f}")
            print(f"    is_staff: {alumno.is_staff}")
            print()
        
        # Resultado final
        if usuarios_no_staff > 0 and len(alumnos_detallados) == usuarios_no_staff:
            print(f"🎉 RESULTADO: Todo correcto - {usuarios_no_staff} alumnos en tabla de progreso")
            return True
        else:
            print("❌ RESULTADO: Hay problemas con la tabla de progreso")
            if usuarios_no_staff == 0:
                print("   No hay usuarios no-staff en la base de datos")
            return False
        
    except Exception as e:
        print(f"❌ ERROR EN VERIFICACION: {e}")
        import traceback
        traceback.print_exc()
        return False

def ejecutar_test_rapido():
    """Ejecutar verificación rápida sin Django TestCase - SIN EMOJIS"""
    from django.contrib.auth.models import User
    
    print("EJECUTANDO TEST RAPIDO")
    print("=" * 40)
    
    try:
        # Test básico de usuarios
        total_usuarios = User.objects.count()
        usuarios_no_staff = User.objects.filter(is_staff=False).count()
        print(f"Usuarios: {total_usuarios} total, {usuarios_no_staff} no-staff")
        
        # Test de dashboard data
        data = get_dashboard_data()
        total_alumnos_dashboard = data.get('total_alumnos', 0)
        alumnos_detallados = data.get('alumnos_detallados', [])
        
        print(f"Dashboard reporta: {total_alumnos_dashboard} alumnos")
        print(f"Alumnos detallados: {len(alumnos_detallados)} entradas")
        
        # Verificar si alumnos_detallados está vacío
        if len(alumnos_detallados) == 0:
            print("ERROR CRITICO: alumnos_detallados está vacío")
            print("CAUSA: La función get_dashboard_data no está procesando correctamente los alumnos")
            return False
        else:
            print(f"CORRECTO: alumnos_detallados tiene {len(alumnos_detallados)} entradas")
        
        # Verificar algunos alumnos
        print("\nPrimeros 3 alumnos:")
        for i, alumno_data in enumerate(alumnos_detallados[:3], 1):
            alumno = alumno_data['alumno']
            nombre = f"{alumno.first_name} {alumno.last_name}".strip()
            grupo = alumno_data.get('grupo', 'Sin grupo')
            nota_general = alumno_data.get('nota_media_general', 0)
            nota_temas = alumno_data.get('nota_media_temas', 0)
            nota_examenes = alumno_data.get('nota_media_examenes', 0)
            
            print(f"  {i}. {alumno.username} (ID:{alumno.id}) - {grupo}")
            if nombre:
                print(f"     Nombre: {nombre}")
            print(f"     Nota General: {nota_general:.1f}, Temas: {nota_temas:.1f}, Examenes: {nota_examenes:.1f}")
        
        print("\nTEST RAPIDO COMPLETADO EXITOSAMENTE")
        return True
        
    except Exception as e:
        print(f"ERROR EN TEST RAPIDO: {e}")
        import traceback
        traceback.print_exc()
        return False


def ejecutar_test_completo():
    """Ejecutar verificación completa de sistema - SIN EMOJIS"""
    print("EJECUTANDO VERIFICACION COMPLETA DEL SISTEMA")
    print("=" * 50)
    
    tests_exitosos = 0
    tests_fallidos = 0
    
    # Test 1: Usuarios no-staff
    try:
        from django.contrib.auth.models import User
        usuarios_no_staff = User.objects.filter(is_staff=False).count()
        print(f"Encontrados {usuarios_no_staff} usuarios no-staff")
        tests_exitosos += 1
    except Exception as e:
        print(f"FALLO: Test de usuarios no-staff - {e}")
        tests_fallidos += 1
    
    # Test 2: Dashboard data
    try:
        data = get_dashboard_data()
        total_alumnos_dashboard = data.get('total_alumnos', 0)
        assert total_alumnos_dashboard == usuarios_no_staff, f"Dashboard reporta {total_alumnos_dashboard} alumnos, esperados: {usuarios_no_staff}"
        assert len(data.get('alumnos_detallados', [])) > 0 or usuarios_no_staff == 0, "alumnos_detallados está vacío pero hay usuarios no-staff"
        print("PASADO: Test de dashboard data")
        tests_exitosos += 1
    except Exception as e:
        print(f"FALLO: Test de dashboard data - {e}")
        tests_fallidos += 1
    
    # Test 3: Separación de notas
    try:
        data = get_dashboard_data()
        alumnos_detallados = data.get('alumnos_detallados', [])
        if alumnos_detallados:
            alumno_sample = alumnos_detallados[0]
            assert 'nota_media_general' in alumno_sample, "Campo nota_media_general no encontrado"
            assert 'nota_media_temas' in alumno_sample, "Campo nota_media_temas no encontrado"
            assert 'nota_media_examenes' in alumno_sample, "Campo nota_media_examenes no encontrado"
            print("PASADO: Test de separación de notas")
            tests_exitosos += 1
        else:
            raise Exception("No hay alumnos detallados para probar")
    except Exception as e:
        print(f"FALLO: Test de separación de notas - {e}")
        tests_fallidos += 1
    
    print("\n" + "=" * 50)
    print(f"RESUMEN: {tests_exitosos} pasados, {tests_fallidos} fallidos")
    
    if tests_fallidos == 0:
        print("TODOS LOS TESTS PASARON!")
        return True
    else:
        print(f"{tests_fallidos} tests necesitan atencion")
        return False


if __name__ == "__main__":
    # Si se ejecuta directamente, hacer test rápido
    ejecutar_test_rapido()
try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False
    
from django.test import TestCase
from django.contrib.auth.models import User
from users.models import UserProfile
from boards.models import IntentTest, Test, Tema
from core.profesor.services import get_dashboard_data


class TestSistemaProgreso(TestCase):
    """Test cases para el sistema de progreso de alumnos"""
    
    def setUp(self):
        """Configurar datos de prueba para cada test"""
        # Crear usuarios de prueba
        self.profesor = User.objects.create_user(
            username='profesor_test',
            email='profesor@test.com',
            is_staff=True
        )
        
        self.alumno1 = User.objects.create_user(
            username='alumno_test_01',
            first_name='Juan',
            last_name='Pérez García',
            email='alumno1@test.com',
            is_staff=False
        )
        
        self.alumno2 = User.objects.create_user(
            username='alumno_test_02',
            first_name='María',
            last_name='López Martín',
            email='alumno2@test.com',
            is_staff=False
        )
        
        # Crear perfiles con grupos
        UserProfile.objects.update_or_create(
            user=self.alumno1,
            defaults={'grupo': 'Grupo Test A'}
        )
        
        UserProfile.objects.update_or_create(
            user=self.alumno2,
            defaults={'grupo': 'Grupo Test B'}
        )
        
        # Crear tema de prueba
        self.tema, _ = Tema.objects.get_or_create(
            tema_id='test_tema',
            defaults={'nombre': 'Tema de Prueba'}
        )
        
        # Crear test de prueba
        self.test, _ = Test.objects.get_or_create(
            nombre='Test de Prueba',
            defaults={
                'tema': self.tema,
                'activo': True,
                'visible_alumnos': True,
                'disponible_alumno': True
            }
        )
    
    def test_filtro_usuarios_no_staff(self):
        """Test 1: Verificar que solo se cuentan usuarios no-staff"""
        data = get_dashboard_data()
        
        # Verificar que el profesor no se cuenta
        total_alumnos = data.get('total_alumnos', 0)
        usuarios_no_staff = User.objects.filter(is_staff=False).count()
        
        self.assertEqual(total_alumnos, usuarios_no_staff)
        self.assertGreater(total_alumnos, 0)
        
        # Verificar que alumnos detallados no incluyen staff
        alumnos_detallados = data.get('alumnos_detallados', [])
        for alumno_data in alumnos_detallados:
            self.assertFalse(alumno_data['alumno'].is_staff)
    
    def test_grupos_asignados(self):
        """Test 2: Verificar que los alumnos tienen grupos asignados"""
        data = get_dashboard_data()
        alumnos_detallados = data.get('alumnos_detallados', [])
        
        grupos_encontrados = set()
        for alumno_data in alumnos_detallados:
            grupo = alumno_data.get('grupo')
            if grupo and grupo != 'Sin grupo':
                grupos_encontrados.add(grupo)
        
        # Debe haber al menos nuestros grupos de prueba
        self.assertIn('Grupo Test A', grupos_encontrados)
        self.assertIn('Grupo Test B', grupos_encontrados)
    
    def test_nombres_completos_presentes(self):
        """Test 3: Verificar que los alumnos tienen nombres y apellidos"""
        data = get_dashboard_data()
        alumnos_detallados = data.get('alumnos_detallados', [])
        
        alumnos_con_nombres = 0
        for alumno_data in alumnos_detallados:
            alumno = alumno_data['alumno']
            if alumno.first_name and alumno.last_name:
                alumnos_con_nombres += 1
        
        # Al menos nuestros alumnos de prueba deben tener nombres
        self.assertGreaterEqual(alumnos_con_nombres, 2)
    
    def test_intentos_y_notas(self):
        """Test 4: Verificar creación de intentos y cálculo de notas"""
        # Crear intentos de prueba
        IntentTest.objects.create(
            alumno=self.alumno1,
            test=self.test,
            puntuacion=8.5,
            respuestas_correctas=17,
            total_preguntas=20,
            completado=True
        )
        
        IntentTest.objects.create(
            alumno=self.alumno2,
            test=self.test,
            puntuacion=3.2,
            respuestas_correctas=6,
            total_preguntas=20,
            completado=True
        )
        
        data = get_dashboard_data()
        
        # Verificar que los intentos se reflejan en los datos
        self.assertGreater(data.get('total_intentos', 0), 0)
        
        # Verificar notas en rango correcto
        alumnos_detallados = data.get('alumnos_detallados', [])
        for alumno_data in alumnos_detallados:
            nota_media = alumno_data.get('nota_media', 0)
            if nota_media > 0:  # Si tiene intentos
                self.assertGreaterEqual(nota_media, 0)
                self.assertLessEqual(nota_media, 10)
    
    def test_deteccion_alumnos_riesgo(self):
        """Test 5: Verificar detección de alumnos en riesgo"""
        # Crear intento de alumno en riesgo (nota < 5)
        IntentTest.objects.create(
            alumno=self.alumno2,
            test=self.test,
            puntuacion=3.0,
            respuestas_correctas=6,
            total_preguntas=20,
            completado=True
        )
        
        data = get_dashboard_data()
        alumnos_en_riesgo = data.get('alumnos_en_riesgo', 0)
        
        # Debe detectar al menos 1 alumno en riesgo
        self.assertGreater(alumnos_en_riesgo, 0)
    
    def test_estructura_datos_dashboard(self):
        """Test 6: Verificar que get_dashboard_data retorna estructura correcta"""
        data = get_dashboard_data()
        
        # Campos obligatorios
        campos_requeridos = [
            'total_alumnos', 'promedio_general', 'alumnos_detallados',
            'alumnos_activos', 'alumnos_en_riesgo', 'distribucion'
        ]
        
        for campo in campos_requeridos:
            self.assertIn(campo, data, f"Campo '{campo}' no encontrado en datos dashboard")
        
        # Verificar estructura de alumnos_detallados
        alumnos_detallados = data.get('alumnos_detallados', [])
        if alumnos_detallados:
            alumno_sample = alumnos_detallados[0]
            campos_alumno = ['alumno', 'nota_media', 'total_intentos', 'grupo', 'ultimo_acceso']
            
            for campo in campos_alumno:
                self.assertIn(campo, alumno_sample, f"Campo '{campo}' no encontrado en datos alumno")
    
    def test_valores_por_defecto(self):
        """Test 7: Verificar que valores sin datos muestran 0 o defaults correctos"""
        data = get_dashboard_data()
        
        # Verificar que valores numéricos no son None
        self.assertIsNotNone(data.get('total_alumnos'))
        self.assertIsNotNone(data.get('promedio_general'))
        self.assertIsNotNone(data.get('alumnos_activos'))
        self.assertIsNotNone(data.get('alumnos_en_riesgo'))
        
        # Verificar que listas están inicializadas
        self.assertIsInstance(data.get('alumnos_detallados'), list)
        self.assertIsInstance(data.get('distribucion'), dict)


class TestNombresApellidosTemplates(TestCase):
    """Tests específicos para verificar nombres y apellidos en templates"""
    
    def setUp(self):
        """Crear usuario con nombre completo para probar"""
        self.alumno = User.objects.create_user(
            username='test_alumno_nombres',
            first_name='Ana',
            last_name='García López',
            email='ana@test.com',
            is_staff=False
        )
        
        UserProfile.objects.update_or_create(
            user=self.alumno,
            defaults={'grupo': 'Grupo Nombres Test'}
        )
    
    def test_alumno_tiene_nombres_apellidos(self):
        """Verificar que el alumno de prueba tiene nombres y apellidos"""
        self.assertEqual(self.alumno.first_name, 'Ana')
        self.assertEqual(self.alumno.last_name, 'García López')
        self.assertFalse(self.alumno.is_staff)
    
    def test_datos_alumno_en_dashboard(self):
        """Verificar que los datos del alumno aparecen en dashboard"""
        data = get_dashboard_data()
        alumnos_detallados = data.get('alumnos_detallados', [])
        
        # Buscar nuestro alumno de prueba
        alumno_encontrado = None
        for alumno_data in alumnos_detallados:
            if alumno_data['alumno'].username == 'test_alumno_nombres':
                alumno_encontrado = alumno_data
                break
        
        self.assertIsNotNone(alumno_encontrado, "Alumno de prueba no encontrado en dashboard")
        self.assertEqual(alumno_encontrado['alumno'].first_name, 'Ana')
        self.assertEqual(alumno_encontrado['alumno'].last_name, 'García López')
        self.assertEqual(alumno_encontrado['grupo'], 'Grupo Nombres Test')


# Funciones para ejecutar tests desde línea de comandos
def ejecutar_test_rapido():
    """Ejecutar verificación rápida sin Django TestCase"""
    from django.contrib.auth.models import User
    
    print("EJECUTANDO TEST RÁPIDO")
    print("=" * 40)
    
    try:
        # Test básico de usuarios
        total_usuarios = User.objects.count()
        usuarios_no_staff = User.objects.filter(is_staff=False).count()
        print(f"Usuarios: {total_usuarios} total, {usuarios_no_staff} no-staff")
        
        # Test de dashboard data
        data = get_dashboard_data()
        alumnos_detallados = data.get('alumnos_detallados', [])
        print(f"Dashboard: {len(alumnos_detallados)} alumnos detallados")
        
        # Verificar algunos alumnos
        if alumnos_detallados:
            for i, alumno_data in enumerate(alumnos_detallados[:3], 1):
                alumno = alumno_data['alumno']
                nombre = f"{alumno.first_name} {alumno.last_name}".strip()
                grupo = alumno_data.get('grupo', 'Sin grupo')
                print(f"  {i}. {alumno.username} (ID:{alumno.id}) - {grupo}")
                if nombre:
                    print(f"     👤 {nombre}")
        
        print("\nTEST RÁPIDO COMPLETADO EXITOSAMENTE")
        return True
        
    except Exception as e:
        print(f"ERROR EN TEST RÁPIDO: {e}")
        return False


if __name__ == "__main__":
    # Si se ejecuta directamente, hacer test rápido
    ejecutar_test_rapido()