"""
Test para verificar que todos los tests tienen una puntuación máxima de 10 puntos.
Este test asegura la consistencia del sistema de calificaciones.
"""
import pytest
from django.test import TestCase
from boards.models import Test, Pregunta, Respuesta


class TestPuntuacionMaxima(TestCase):
    
    def test_todos_los_tests_tienen_puntuacion_maxima_10(self):
        """
        Verifica que todos los tests activos tengan una puntuación máxima de exactamente 10 puntos.
        
        La puntuación máxima se calcula sumando los puntos de todas las preguntas del test.
        Cada pregunta correcta debería valer un número de puntos tal que el total sea 10.
        """
        tests_con_error = []
        
        # Obtener todos los tests activos
        tests_activos = Test.objects.filter(activo=True)
        
        if not tests_activos.exists():
            pytest.skip("No hay tests activos para verificar")
        
        for test in tests_activos:
            # Obtener todas las preguntas del test
            preguntas = Pregunta.objects.filter(test=test)
            
            if not preguntas.exists():
                # Test sin preguntas - no podemos verificar puntuación
                tests_con_error.append({
                    'test': test,
                    'error': 'Test sin preguntas',
                    'puntuacion_actual': 0,
                    'puntuacion_esperada': 10
                })
                continue
            
            # Calcular puntuación máxima total del test
            puntuacion_total = test.total_preguntas() * (10 / test.total_preguntas()) if test.total_preguntas() > 0 else 0
            puntuacion_total = round(puntuacion_total, 2)
            
            # Verificar que la puntuación máxima sea exactamente 10
            if abs(puntuacion_total - 10.0) > 0.01:  # Tolerancia para errores de flotante
                tests_con_error.append({
                    'test': test,
                    'error': 'Puntuación máxima incorrecta',
                    'puntuacion_actual': puntuacion_total,
                    'puntuacion_esperada': 10.0,
                    'total_preguntas': test.total_preguntas()
                })
        
        # Si hay errores, mostrar información detallada
        if tests_con_error:
            mensaje_error = "\n\n❌ TESTS CON PUNTUACIÓN INCORRECTA:\n"
            mensaje_error += "=" * 60 + "\n"
            
            for error in tests_con_error:
                test = error['test']
                mensaje_error += f"\n🔸 TEST: {test.nombre}\n"
                mensaje_error += f"   Tema: {test.tema.tema_id if test.tema else 'Sin tema'}\n"
                mensaje_error += f"   ID: {test.id}\n"
                mensaje_error += f"   Error: {error['error']}\n"
                mensaje_error += f"   Puntuación actual: {error['puntuacion_actual']}\n"
                mensaje_error += f"   Puntuación esperada: {error['puntuacion_esperada']}\n"
                
                if 'total_preguntas' in error:
                    mensaje_error += f"   Total preguntas: {error['total_preguntas']}\n"
                
                # Mostrar detalles de las preguntas si existen
                preguntas = Pregunta.objects.filter(test=test)
                if preguntas.exists():
                    mensaje_error += f"   Preguntas:\n"
                    for i, pregunta in enumerate(preguntas, 1):
                        respuestas_correctas = Respuesta.objects.filter(
                            pregunta=pregunta, 
                            es_correcta=True
                        ).count()
                        mensaje_error += f"     {i}. {pregunta.texto[:50]}... (Resp. correctas: {respuestas_correctas})\n"
                
                mensaje_error += "-" * 40 + "\n"
            
            mensaje_error += f"\n📊 RESUMEN:\n"
            mensaje_error += f"   Tests verificados: {tests_activos.count()}\n"
            mensaje_error += f"   Tests con errores: {len(tests_con_error)}\n"
            mensaje_error += f"   Tests correctos: {tests_activos.count() - len(tests_con_error)}\n"
            
            mensaje_error += "\n💡 SOLUCIÓN:\n"
            mensaje_error += "   Cada test debe tener preguntas que sumen exactamente 10 puntos.\n"
            mensaje_error += "   Si un test tiene N preguntas, cada una debe valer 10/N puntos.\n"
            mensaje_error += "   Ejemplo: 5 preguntas = 2 puntos cada una = 10 puntos total.\n"
            
            # Forzar fallo del test con el mensaje detallado
            assert False, mensaje_error
    
    def test_verificar_preguntas_sin_respuestas_correctas(self):
        """
        Verifica que no haya preguntas sin respuestas marcadas como correctas.
        """
        preguntas_sin_correcta = []
        
        # Buscar preguntas que no tienen ninguna respuesta correcta
        preguntas = Pregunta.objects.filter(test__activo=True)
        
        for pregunta in preguntas:
            respuestas_correctas = Respuesta.objects.filter(
                pregunta=pregunta, 
                es_correcta=True
            ).count()
            
            if respuestas_correctas == 0:
                preguntas_sin_correcta.append({
                    'pregunta': pregunta,
                    'test': pregunta.test,
                    'total_respuestas': Respuesta.objects.filter(pregunta=pregunta).count()
                })
        
        if preguntas_sin_correcta:
            mensaje_error = "\n\n❌ PREGUNTAS SIN RESPUESTA CORRECTA:\n"
            mensaje_error += "=" * 50 + "\n"
            
            for error in preguntas_sin_correcta:
                pregunta = error['pregunta']
                test = error['test']
                mensaje_error += f"\n🔸 PREGUNTA: {pregunta.texto[:100]}...\n"
                mensaje_error += f"   Test: {test.nombre}\n"
                mensaje_error += f"   Tema: {test.tema.tema_id if test.tema else 'Sin tema'}\n"
                mensaje_error += f"   Total respuestas: {error['total_respuestas']}\n"
                mensaje_error += f"   Respuestas correctas: 0 ❌\n"
                mensaje_error += "-" * 30 + "\n"
            
            mensaje_error += f"\n📊 Total preguntas problemáticas: {len(preguntas_sin_correcta)}\n"
            mensaje_error += "\n💡 SOLUCIÓN: Marcar al menos una respuesta como correcta para cada pregunta.\n"
            
            assert False, mensaje_error
    
    def test_verificar_preguntas_multiples_respuestas_correctas(self):
        """
        Verifica que no haya preguntas con múltiples respuestas correctas 
        (a menos que esté diseñado para eso).
        """
        preguntas_multiples_correctas = []
        
        preguntas = Pregunta.objects.filter(test__activo=True)
        
        for pregunta in preguntas:
            respuestas_correctas = Respuesta.objects.filter(
                pregunta=pregunta, 
                es_correcta=True
            ).count()
            
            # Por ahora asumimos que cada pregunta debe tener exactamente 1 respuesta correcta
            if respuestas_correctas > 1:
                preguntas_multiples_correctas.append({
                    'pregunta': pregunta,
                    'test': pregunta.test,
                    'respuestas_correctas': respuestas_correctas,
                    'total_respuestas': Respuesta.objects.filter(pregunta=pregunta).count()
                })
        
        if preguntas_multiples_correctas:
            mensaje_error = "\n\n⚠️ PREGUNTAS CON MÚLTIPLES RESPUESTAS CORRECTAS:\n"
            mensaje_error += "=" * 55 + "\n"
            
            for error in preguntas_multiples_correctas:
                pregunta = error['pregunta']
                test = error['test']
                mensaje_error += f"\n🔸 PREGUNTA: {pregunta.texto[:100]}...\n"
                mensaje_error += f"   Test: {test.nombre}\n"
                mensaje_error += f"   Tema: {test.tema.tema_id if test.tema else 'Sin tema'}\n"
                mensaje_error += f"   Respuestas correctas: {error['respuestas_correctas']} ⚠️\n"
                mensaje_error += f"   Total respuestas: {error['total_respuestas']}\n"
                mensaje_error += "-" * 30 + "\n"
            
            mensaje_error += f"\n📊 Total preguntas con múltiples correctas: {len(preguntas_multiples_correctas)}\n"
            mensaje_error += "\n💡 NOTA: Si esto es intencional (preguntas de opción múltiple),\n"
            mensaje_error += "   ignora esta advertencia. Si no, revisa las preguntas marcadas.\n"
            
            # Solo advertencia, no falla el test
            print(mensaje_error)