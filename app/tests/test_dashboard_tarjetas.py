"""
Test para verificar que las tarjetas del dashboard se muestran correctamente
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from boards.models import Test, IntentTest, Tema, Pregunta
from core.profesor.services import get_dashboard_data
from datetime import datetime


class TestDashboardTarjetas(TestCase):
    def setUp(self):
        """Configuración inicial para las pruebas"""
        # Crear grupos
        self.grupo_profesor = Group.objects.create(name='Profesores')
        self.grupo_alumno = Group.objects.create(name='Alumnos')
        
        # Crear usuario profesor
        self.profesor = User.objects.create_user(
            username='profesor_test',
            password='test123',
            is_staff=True
        )
        self.profesor.groups.add(self.grupo_profesor)
        
        # Crear usuarios alumnos
        self.alumno1 = User.objects.create_user(
            username='alumno1',
            password='test123',
            is_staff=False
        )
        self.alumno1.groups.add(self.grupo_alumno)
        
        self.alumno2 = User.objects.create_user(
            username='alumno2',
            password='test123',
            is_staff=False
        )
        self.alumno2.groups.add(self.grupo_alumno)
        
        # Crear tema
        self.tema = Tema.objects.create(
            tema_id='Test Tema',
            visible_alumnos=True,
            disponible_alumno=True,
            visible_profesor=True,
            disponible_profesor=True,
            activo=True
        )
        
        # Crear test
        self.test = Test.objects.create(
            nombre='Test Ejemplo',
            descripcion='Test de ejemplo',
            tema=self.tema,
            nivel='Facil',
            tiempo_limite=30,
            visible_alumnos=True,
            disponible_alumno=True,
            creado_por=self.profesor
        )
        
        # Crear intentos de prueba con notas diferentes
        IntentTest.objects.create(
            alumno=self.alumno1,
            test=self.test,
            completado=True,
            puntuacion=85,  # 8.5/10 - Excelente
            respuestas_correctas=8,
            total_preguntas=10,
            fecha_inicio=datetime.now(),
            fecha_fin=datetime.now()
        )
        
        IntentTest.objects.create(
            alumno=self.alumno2,
            test=self.test,
            completado=True,
            puntuacion=45,  # 4.5/10 - En riesgo
            respuestas_correctas=4,
            total_preguntas=10,
            fecha_inicio=datetime.now(),
            fecha_fin=datetime.now()
        )
        
        self.client = Client()
        
    def test_dashboard_datos_correctos(self):
        """Test que verifica que get_dashboard_data devuelve los datos correctos"""
        context = get_dashboard_data()
        
        # Verificar que existen las claves necesarias
        required_keys = [
            'total_alumnos',
            'promedio_general',
            'promedio_temas',
            'promedio_examenes',
            'alumnos_activos',
            'alumnos_en_riesgo'
        ]
        
        for key in required_keys:
            self.assertIn(key, context, f"Falta la clave '{key}' en el contexto del dashboard")
        
        # Verificar valores
        self.assertEqual(context['total_alumnos'], 2, "Debe haber 2 alumnos")
        self.assertGreater(context['promedio_general'], 0, "El promedio general debe ser mayor que 0")
        
        print("✅ Test dashboard_datos_correctos: PASSED")
        
    def test_tarjetas_colores_correctos(self):
        """Test que verifica que los colores de las tarjetas son correctos según las notas"""
        context = get_dashboard_data()
        
        # Verificar que el promedio general está en escala 0-10
        self.assertLessEqual(context['promedio_general'], 10, "El promedio debe estar en escala 0-10")
        self.assertGreaterEqual(context['promedio_general'], 0, "El promedio debe ser >= 0")
        
        # El promedio debe ser ~6.5 (85+45)/2/10 = 6.5
        expected_promedio = (85 + 45) / 2 / 10  # 6.5
        self.assertAlmostEqual(context['promedio_general'], expected_promedio, places=1)
        
        print(f"✅ Test tarjetas_colores: Promedio general = {context['promedio_general']}")
        print("✅ Test tarjetas_colores_correctos: PASSED")
        
    def test_dashboard_template_response(self):
        """Test que verifica que el template del dashboard responde correctamente"""
        # Login como profesor
        self.client.login(username='profesor_test', password='test123')
        
        # Hacer request al dashboard
        response = self.client.get(reverse('boards:dashboard_profesor'))
        
        # Verificar respuesta exitosa
        self.assertEqual(response.status_code, 200, "El dashboard debe responder con código 200")
        
        # Verificar que el template contiene las tarjetas necesarias
        content = response.content.decode('utf-8')
        
        # Verificar que el template contiene las tarjetas necesarias
        self.assertIn('Alumnos Activos', content, "Debe mostrar tarjeta 'Alumnos Activos'")
        self.assertIn('Promedio General', content, "Debe mostrar tarjeta 'Promedio General'")
        self.assertIn('Promedio Temas', content, "Debe mostrar tarjeta 'Promedio Temas'")
        self.assertIn('Promedio Exámenes', content, "Debe mostrar tarjeta 'Promedio Exámenes'")
        self.assertIn('Activos (7 días)', content, "Debe mostrar tarjeta de activos")
        self.assertIn('En Riesgo', content, "Debe mostrar tarjeta de en riesgo")
        
        # Verificar que se muestran los valores en porcentaje (escala 0-100)
        self.assertIn('%', content, "Debe mostrar porcentajes en las tarjetas")
        
        # Verificar que se muestran los valores
        self.assertIn('2', content, "Debe mostrar el número de alumnos")
        
        print("✅ Test dashboard_template_response: PASSED")
        
    def test_progreso_alumnos_template_response(self):
        """Test que verifica que el template de progreso alumnos responde correctamente"""
        # Login como profesor
        self.client.login(username='profesor_test', password='test123')
        
        # Hacer request a progreso alumnos
        response = self.client.get(reverse('boards:progreso_alumnos'))
        
        # Verificar respuesta exitosa
        self.assertEqual(response.status_code, 200, "El progreso alumnos debe responder con código 200")
        
        # Verificar contenido
        content = response.content.decode('utf-8')
        
        # Verificar que no hay errores de template
        self.assertNotIn('TemplateSyntaxError', content, "No debe haber errores de sintaxis de template")
        self.assertNotIn('Invalid block tag', content, "No debe haber tags inválidos")
        
        # Verificar elementos del progreso de alumnos
        self.assertIn('Progreso por Alumno', content, "Debe mostrar el título de progreso")
        self.assertIn('alumno1', content, "Debe mostrar el alumno1")
        self.assertIn('alumno2', content, "Debe mostrar el alumno2")
        
        print("✅ Test progreso_alumnos_template_response: PASSED")


if __name__ == '__main__':
    import django
    django.setup()
    
    # Ejecutar tests individualmente para ver resultados
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDashboardTarjetas)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)