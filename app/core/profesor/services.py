from django.db.models import Avg, Count, Max, Min, Sum
from typing import Dict, Any, Tuple

from boards.models import Test, IntentTest, Tema, Pregunta, ProgresoTema
from django.contrib.auth.models import User


def get_dashboard_data() -> Dict[str, Any]:
    """Datos agregados para el dashboard del profesor."""
    # Estadísticas generales
    total_alumnos = IntentTest.objects.values('alumno').distinct().count()
    total_intentos = IntentTest.objects.filter(completado=True).count()
    promedio_general = (
        IntentTest.objects.filter(completado=True).aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
    )

    # Todos los intentos (ordenados por fecha)
    todos_intentos = (
        IntentTest.objects.filter(completado=True)
        .select_related('alumno', 'test', 'test__tema')
        .order_by('-fecha_fin')
    )
    
    # Obtener listas únicas para filtros
    alumnos_unicos = todos_intentos.values_list('alumno__username', flat=True).distinct().order_by('alumno__username')
    tests_unicos = todos_intentos.values_list('test__nombre', flat=True).distinct().order_by('test__nombre')
    temas_unicos = Tema.objects.all().order_by('tema_id')
    
    # Estadísticas agregadas de los intentos
    estadisticas_intentos = todos_intentos.aggregate(
        promedio=Avg('puntuacion'),
        puntuacion_maxima=Max('puntuacion'),
        puntuacion_minima=Min('puntuacion'),
        total_respuestas_correctas=Sum('respuestas_correctas'),
        total_preguntas_respondidas=Sum('total_preguntas'),
    )
    
    # Calcular tasa de acierto global
    tasa_acierto_global = 0
    if estadisticas_intentos['total_preguntas_respondidas']:
        tasa_acierto_global = (
            estadisticas_intentos['total_respuestas_correctas'] / 
            estadisticas_intentos['total_preguntas_respondidas'] * 100
        )

    # Todos los temas con sus tests
    temas_con_tests = []
    temas = Tema.objects.all().prefetch_related('tests')
    
    for tema in temas:
        total_preguntas = Pregunta.objects.filter(tema=tema.tema_id).count()
        tests = tema.tests.all().annotate(num_intentos=Count('intentos'))
        
        # Obtener estadísticas de dificultad
        preguntas_faciles = Pregunta.objects.filter(tema=tema.tema_id, dificultad='Facil').count()
        preguntas_medias = Pregunta.objects.filter(tema=tema.tema_id, dificultad='Media').count()
        preguntas_dificiles = Pregunta.objects.filter(tema=tema.tema_id, dificultad='Dificil').count()
        
        temas_con_tests.append({
            'tema': tema,
            'total_preguntas': total_preguntas,
            'tests': tests,
            'preguntas_faciles': preguntas_faciles,
            'preguntas_medias': preguntas_medias,
            'preguntas_dificiles': preguntas_dificiles,
        })
    
    # Totales
    total_tests = Test.objects.count()
    total_preguntas = Pregunta.objects.count()
    total_temas = temas.count()

    return {
        'total_alumnos': total_alumnos,
        'total_intentos': total_intentos,
        'promedio_general': promedio_general,
        'todos_intentos': todos_intentos,
        'estadisticas_intentos': estadisticas_intentos,
        'tasa_acierto_global': tasa_acierto_global,
        'total_tests': total_tests,
        'total_preguntas': total_preguntas,
        'total_temas': total_temas,
        'temas_con_tests': temas_con_tests,
        'alumnos_unicos': alumnos_unicos,
        'tests_unicos': tests_unicos,
        'temas_unicos': temas_unicos,
    }


def get_student_stats(alumno) -> Tuple:
    """Devuelve intentos completados y promedio del alumno."""
    intentos = (
        IntentTest.objects.filter(alumno=alumno, completado=True)
        .select_related('test')
        .order_by('-fecha_fin')
    )
    promedio = intentos.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
    return intentos, promedio
