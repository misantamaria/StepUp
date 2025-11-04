from django.db.models import Avg, Count
from typing import Dict, Any, Tuple

from boards.models import Question, Test, IntentTest


def get_dashboard_data() -> Dict[str, Any]:
    """Datos agregados para el dashboard del profesor."""
    total_alumnos = IntentTest.objects.values('alumno').distinct().count()
    total_intentos = IntentTest.objects.filter(completado=True).count()
    promedio_general = (
        IntentTest.objects.filter(completado=True).aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
    )

    ultimos_intentos = (
        IntentTest.objects.filter(completado=True)
        .select_related('alumno', 'test')
        .order_by('-fecha_fin')[:10]
    )

    tests = Test.objects.all().annotate(num_intentos=Count('intentos'))
    preguntas_por_tema = (
        Question.objects.values('tema').annotate(total=Count('id')).order_by('-total')
    )

    return {
        'total_alumnos': total_alumnos,
        'total_intentos': total_intentos,
        'promedio_general': promedio_general,
        'ultimos_intentos': ultimos_intentos,
        'tests': tests,
        'preguntas_por_tema': preguntas_por_tema,
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
