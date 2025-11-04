from django.utils import timezone
from django.db.models import Avg, Count
from typing import Dict, Any, List
from collections import defaultdict

from boards.models import Test, IntentTest, RespuestaAlumno, Tema, ProgresoTema, Pregunta, Respuesta


def get_dashboard_data(user) -> Dict[str, Any]:
    """Datos para el dashboard del alumno - organizado por temas."""
    # Obtener todos los temas con tests visibles
    temas_con_tests = Tema.objects.filter(
        tests__activo=True,
        tests__visible_alumnos=True
    ).distinct().prefetch_related('tests')
    
    # Organizar tests por tema
    tests_por_tema = []
    for tema in temas_con_tests:
        # Obtener o crear el progreso del tema para este alumno
        progreso, created = ProgresoTema.objects.get_or_create(
            alumno=user,
            tema=tema
        )
        
        # Si se creó, inicializar el progreso
        if created:
            progreso.total_preguntas = Pregunta.objects.filter(tema=tema.tema_id).count()
            progreso.save()
        
        # Actualizar el progreso
        progreso.actualizar_progreso()
        
        # Obtener tests del tema visibles para alumnos
        tests = tema.tests.filter(activo=True, visible_alumnos=True)
        
        tests_por_tema.append({
            'tema': tema,
            'progreso': progreso,
            'tests': tests,
        })
    
    # Últimos intentos del alumno
    intentos_previos = IntentTest.objects.filter(
        alumno=user
    ).select_related('test', 'test__tema').order_by('-fecha_inicio')[:10]
    
    # Estadísticas generales
    total_intentos = IntentTest.objects.filter(alumno=user, completado=True).count()
    promedio_puntuacion = (
        IntentTest.objects.filter(alumno=user, completado=True)
        .aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
    )
    
    return {
        'tests_por_tema': tests_por_tema,
        'intentos_previos': intentos_previos,
        'total_intentos': total_intentos,
        'promedio_puntuacion': promedio_puntuacion,
    }


def start_test(user, test: Test) -> IntentTest:
    """Crea un nuevo intento para el usuario en el test dado."""
    intento = IntentTest.objects.create(
        alumno=user,
        test=test,
        total_preguntas=test.total_preguntas(),
    )
    return intento


def grade_attempt(intento: IntentTest, post_data) -> IntentTest:
    """Corrige un intento con los datos del formulario y actualiza métricas."""
    if intento.completado:
        return intento

    preguntas = intento.test.preguntas.all()
    respuestas_correctas = 0

    for pregunta in preguntas:
        respuesta_key = f'pregunta_{pregunta.pregunta_id}'
        respuesta_id = post_data.get(respuesta_key, '')
        
        if not respuesta_id:
            continue

        try:
            # Obtener la respuesta seleccionada por el alumno
            respuesta_obj = Respuesta.objects.get(
                pregunta_id=pregunta.pregunta_id,
                respuesta_id=respuesta_id
            )
            
            # Verificar si es correcta
            es_correcta = respuesta_obj.solucion == 'Correcta'
            
            if es_correcta:
                respuestas_correctas += 1

            # Guardar la respuesta del alumno
            RespuestaAlumno.objects.create(
                intento=intento,
                pregunta=pregunta,
                respuesta=str(respuesta_id),
                es_correcta=es_correcta,
            )
        except Respuesta.DoesNotExist:
            # Si no existe la respuesta, marcar como incorrecta
            RespuestaAlumno.objects.create(
                intento=intento,
                pregunta=pregunta,
                respuesta=str(respuesta_id),
                es_correcta=False,
            )

    intento.respuestas_correctas = respuestas_correctas
    intento.completado = True
    intento.fecha_fin = timezone.now()
    intento.calcular_puntuacion()
    intento.save(update_fields=['respuestas_correctas', 'completado', 'fecha_fin', 'puntuacion'])
    
    # Actualizar el progreso del tema
    if intento.test.tema:
        progreso, created = ProgresoTema.objects.get_or_create(
            alumno=intento.alumno,
            tema=intento.test.tema
        )
        progreso.actualizar_progreso()
    
    return intento
