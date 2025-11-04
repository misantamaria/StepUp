from django.utils import timezone
from django.db.models import Avg
from typing import Dict, Any

from boards.models import Test, IntentTest, RespuestaAlumno


def get_dashboard_data(user) -> Dict[str, Any]:
    """Datos para el dashboard del alumno."""
    tests_disponibles = Test.objects.filter(activo=True)
    intentos_previos = IntentTest.objects.filter(alumno=user).order_by('-fecha_inicio')[:10]
    total_intentos = IntentTest.objects.filter(alumno=user, completado=True).count()
    promedio_puntuacion = (
        IntentTest.objects.filter(alumno=user, completado=True)
        .aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
    )
    return {
        'tests_disponibles': tests_disponibles,
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

    preguntas = intento.test.preguntas.filter(activa=True)
    respuestas_correctas = 0

    for pregunta in preguntas:
        respuesta_key = f'pregunta_{pregunta.id}'
        respuesta = (post_data.get(respuesta_key, '') or '').strip()
        if not respuesta:
            continue

        es_correcta = False
        if pregunta.tipo == 'multiple':
            es_correcta = respuesta.upper() == (pregunta.respuesta_correcta or '').upper()
        elif pregunta.tipo == 'verdadero_falso':
            es_correcta = respuesta.lower() == (pregunta.respuesta_correcta or '').lower()
        else:
            es_correcta = respuesta.lower().strip() == (pregunta.respuesta_correcta or '').lower().strip()

        if es_correcta:
            respuestas_correctas += 1

        RespuestaAlumno.objects.create(
            intento=intento,
            pregunta=pregunta,
            respuesta=respuesta,
            es_correcta=es_correcta,
        )

    intento.respuestas_correctas = respuestas_correctas
    intento.completado = True
    intento.fecha_fin = timezone.now()
    intento.calcular_puntuacion()
    intento.save(update_fields=['respuestas_correctas', 'completado', 'fecha_fin', 'puntuacion'])
    return intento
