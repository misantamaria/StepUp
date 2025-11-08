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
    
    print("🔍 EJECUTANDO TEST RÁPIDO")
    print("=" * 40)
    
    try:
        # Test básico de usuarios
        total_usuarios = User.objects.count()
        usuarios_no_staff = User.objects.filter(is_staff=False).count()
        print(f"✅ Usuarios: {total_usuarios} total, {usuarios_no_staff} no-staff")
        
        # Test de dashboard data
        data = get_dashboard_data()
        alumnos_detallados = data.get('alumnos_detallados', [])
        print(f"✅ Dashboard: {len(alumnos_detallados)} alumnos detallados")
        
        # Verificar algunos alumnos
        if alumnos_detallados:
            for i, alumno_data in enumerate(alumnos_detallados[:3], 1):
                alumno = alumno_data['alumno']
                nombre = f"{alumno.first_name} {alumno.last_name}".strip()
                grupo = alumno_data.get('grupo', 'Sin grupo')
                print(f"  {i}. {alumno.username} (ID:{alumno.id}) - {grupo}")
                if nombre:
                    print(f"     👤 {nombre}")
        
        print("\n🎉 TEST RÁPIDO COMPLETADO EXITOSAMENTE")
        return True
        
    except Exception as e:
        print(f"❌ ERROR EN TEST RÁPIDO: {e}")
        return False


if __name__ == "__main__":
    # Si se ejecuta directamente, hacer test rápido
    ejecutar_test_rapido()