from django.db.models import Avg, Count, Max, Min, Sum
from typing import Dict, Any, Tuple

from boards.models import Test, IntentTest, Tema, Pregunta, ProgresoTema
from django.contrib.auth.models import User


def get_dashboard_data() -> Dict[str, Any]:
    """Datos agregados para el dashboard del profesor."""
    # Estadísticas generales (solo alumnos no-staff)
    alumnos_no_staff = User.objects.filter(is_staff=False)
    total_alumnos = alumnos_no_staff.count()
    
    # Solo contar intentos de alumnos no-staff
    total_intentos = IntentTest.objects.filter(completado=True, alumno__is_staff=False).count()
    promedio_general = (
        IntentTest.objects.filter(completado=True, alumno__is_staff=False)
        .aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
    )  # Mantener en escala 0-100 para dashboard
    
    # Promedio de temas (excluyendo exámenes) 
    promedio_temas = (
        IntentTest.objects.filter(completado=True, alumno__is_staff=False)
        .exclude(test__tema__tema_id='Exámenes')
        .aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
    )  # Mantener en escala 0-100 para dashboard
    
    # Promedio de exámenes
    promedio_examenes = (
        IntentTest.objects.filter(completado=True, alumno__is_staff=False)
        .filter(test__tema__tema_id='Exámenes')
        .aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
    )  # Mantener en escala 0-100 para dashboard

    # Todos los intentos (ordenados por fecha, solo alumnos no-staff)
    todos_intentos = (
        IntentTest.objects.filter(completado=True, alumno__is_staff=False)
        .select_related('alumno', 'test', 'test__tema')
        .order_by('-fecha_fin')
    )
    
    # Obtener listas únicas para filtros (excluyendo tema especial "Exámenes")
    alumnos_unicos = todos_intentos.values_list('alumno__username', flat=True).distinct().order_by('alumno__username')
    tests_unicos = todos_intentos.values_list('test__nombre', flat=True).distinct().order_by('test__nombre')
    temas_unicos = Tema.objects.filter(
        visible_alumnos=True, 
        disponible_alumno=True, 
        activo=True
    ).exclude(tema_id='Exámenes').order_by('tema_id')
    
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

    # Todos los temas con sus tests (excluyendo el tema especial "Exámenes")
    temas_con_tests = []
    temas = Tema.objects.exclude(tema_id='Exámenes').prefetch_related('tests')
    
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
    
    # Totales (excluyendo tema especial "Exámenes" del conteo)
    total_tests = Test.objects.count()
    total_preguntas = Pregunta.objects.count()
    total_temas = temas.count()
    
    # Todos los tests (para la vista simplificada)
    todos_tests = Test.objects.all().select_related('tema').annotate(num_intentos=Count('intentos')).order_by('tema__tema_id', 'nombre')
    
    # Todas las preguntas (para la vista de preguntas)
    todas_preguntas = Pregunta.objects.all().order_by('tema', 'pregunta_id')

    # Datos detallados de alumnos para la sección "Alumnos"
    alumnos_detallados = []
    
    try:
        for alumno in alumnos_no_staff.order_by('username'):
            try:
                intentos_alumno = IntentTest.objects.filter(alumno=alumno, completado=True)
                total_intentos_alumno = intentos_alumno.count()
                
                # Separar intentos por tipo: temas vs exámenes
                intentos_temas = intentos_alumno.exclude(test__tema__tema_id='Exámenes')
                intentos_examenes = intentos_alumno.filter(test__tema__tema_id='Exámenes')
                
                # Calcular notas medias separadas SOBRE 10
                nota_media_temas = (intentos_temas.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0)
                nota_media_examenes = (intentos_examenes.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0)
                nota_media_general = (intentos_alumno.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0)
                
                # Calcular promedios por cada tema visible/disponible
                promedios_por_tema = {}
                temas_disponibles = Tema.objects.filter(
                    visible_alumnos=True, 
                    disponible_alumno=True,
                    activo=True
                ).exclude(tema_id='Exámenes')
                
                for tema in temas_disponibles:
                    intentos_tema = intentos_alumno.filter(test__tema=tema)
                    if intentos_tema.exists():
                        promedio_tema = (intentos_tema.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0)
                        promedios_por_tema[tema.tema_id] = {
                            'promedio': promedio_tema,
                            'intentos': intentos_tema.count()
                        }
                    else:
                        promedios_por_tema[tema.tema_id] = {
                            'promedio': 0,
                            'intentos': 0
                        }
                
                # Calcular progreso como % de tests únicos completados
                tests_completados = intentos_alumno.values('test').distinct().count()
                tests_disponibles_alumno = Test.objects.filter(activo=True, visible_alumnos=True, disponible_alumno=True).count()
                progreso_porcentaje = (tests_completados / tests_disponibles_alumno * 100) if tests_disponibles_alumno > 0 else 0
                
                # Último acceso
                ultimo_intento = intentos_alumno.order_by('-fecha_inicio').first()
                ultimo_acceso = ultimo_intento.fecha_inicio if ultimo_intento else None
                
                # Determinar estado del alumno
                estado_alumno = "EXCELENTE"
                if nota_media_general < 5.0:
                    estado_alumno = "EN RIESGO"
                elif nota_media_general < 6.0:
                    estado_alumno = "REGULAR"
                elif nota_media_general < 8.0:
                    estado_alumno = "BUENO"
                
                # Obtener grupo del alumno (manejo seguro de profile)
                grupo = 'Sin grupo'
                try:
                    if hasattr(alumno, 'userprofile'):
                        grupo = alumno.userprofile.grupo or 'Sin grupo'
                    elif hasattr(alumno, 'profile'):
                        grupo = alumno.profile.grupo or 'Sin grupo'
                except Exception:
                    grupo = 'Sin grupo'
                
                alumnos_detallados.append({
                    'alumno': alumno,
                    'total_intentos': total_intentos_alumno,
                    'nota_media_general': nota_media_general,
                    'nota_media_temas': nota_media_temas,
                    'nota_media_examenes': nota_media_examenes,
                    'promedios_por_tema': promedios_por_tema,
                    'estado_alumno': estado_alumno,
                    'intentos_temas': intentos_temas.count(),
                    'intentos_examenes': intentos_examenes.count(),
                    'progreso_porcentaje': progreso_porcentaje,
                    'ultimo_acceso': ultimo_acceso,
                    'grupo': grupo,
                })
            except Exception as e:
                # Si un alumno falla, continuar con el siguiente
                print(f"Error procesando alumno {alumno.username}: {e}")
                continue
                
    except Exception as e:
        print(f"Error general en alumnos_detallados: {e}")
        alumnos_detallados = []

    # Datos para la sección "Clases" - solo alumnos no-staff
    # Alumnos activos (con actividad en los últimos 7 días)
    from datetime import datetime, timedelta
    hace_7_dias = datetime.now() - timedelta(days=7)
    alumnos_activos = IntentTest.objects.filter(
        fecha_inicio__gte=hace_7_dias,
        alumno__is_staff=False
    ).values('alumno').distinct().count()
    
    # Clasificación de alumnos por rendimiento (incluir alumnos en riesgo por suspenso)
    alumnos_con_notas = [a for a in alumnos_detallados if a['total_intentos'] > 0]
    
    # Ordenar por estado: EN RIESGO primero, luego por nota
    def ordenar_alumnos(alumno):
        if alumno['estado_alumno'] == 'EN RIESGO':
            return (0, -alumno['nota_media_general'])  # EN RIESGO primero, luego por nota descendente
        else:
            return (1, -alumno['nota_media_general'])  # Otros después, por nota descendente
    
    alumnos_con_notas_ordenados = sorted(alumnos_con_notas, key=ordenar_alumnos)
    
    mejores_alumnos = sorted(alumnos_con_notas, key=lambda x: x['nota_media_general'], reverse=True)
    # En riesgo: nota general < 5 o sin intentos
    alumnos_riesgo = [a for a in alumnos_con_notas if a['nota_media_general'] < 5.0]
    alumnos_sin_intentos = [a for a in alumnos_detallados if a['total_intentos'] == 0]
    alumnos_en_riesgo_count = len(alumnos_riesgo) + len(alumnos_sin_intentos)
    
    # Distribución de notas (actualizar rangos para notas 0-10) - usar nota general
    distribucion = {
        'excelente': len([a for a in alumnos_con_notas if a['nota_media_general'] >= 8.0]),
        'bien': len([a for a in alumnos_con_notas if 6.0 <= a['nota_media_general'] < 8.0]),
        'regular': len([a for a in alumnos_con_notas if 5.0 <= a['nota_media_general'] < 6.0]),
        'mal': len([a for a in alumnos_con_notas if a['nota_media_general'] < 5.0]),
        'sin_actividad': len(alumnos_sin_intentos),
    }

    # Estadísticas por grupo
    estadisticas_grupos = {}
    grupos_unicos = set()
    
    for alumno_data in alumnos_detallados:
        grupo = alumno_data.get('grupo')
        if grupo:
            grupos_unicos.add(grupo)
    
    for grupo in grupos_unicos:
        alumnos_grupo = [a for a in alumnos_detallados if a.get('grupo') == grupo]
        alumnos_grupo_con_notas = [a for a in alumnos_grupo if a['total_intentos'] > 0]
        
        if alumnos_grupo_con_notas:
            promedio_grupo = sum(a['nota_media_general'] for a in alumnos_grupo_con_notas) / len(alumnos_grupo_con_notas)
            en_riesgo_grupo = len([a for a in alumnos_grupo_con_notas if a['nota_media_general'] < 5.0])
            sin_actividad_grupo = len([a for a in alumnos_grupo if a['total_intentos'] == 0])
        else:
            promedio_grupo = 0
            en_riesgo_grupo = 0
            sin_actividad_grupo = len(alumnos_grupo)
        
        estadisticas_grupos[grupo] = {
            'total_alumnos': len(alumnos_grupo),
            'promedio': promedio_grupo,
            'en_riesgo': en_riesgo_grupo + sin_actividad_grupo,
            'sin_actividad': sin_actividad_grupo,
        }

    return {
        'total_alumnos': total_alumnos,
        'total_intentos': total_intentos,
        'promedio_general': promedio_general,
        'promedio_temas': promedio_temas,
        'promedio_examenes': promedio_examenes,
        'todos_intentos': todos_intentos,
        'estadisticas_intentos': estadisticas_intentos,
        'tasa_acierto_global': tasa_acierto_global,
        'total_tests': total_tests,
        'total_preguntas': total_preguntas,
        'total_temas': total_temas,
        'temas_con_tests': temas_con_tests,
        'todos_tests': todos_tests,
        'todas_preguntas': todas_preguntas,
        'alumnos_unicos': alumnos_unicos,
        'tests_unicos': tests_unicos,
        'temas_unicos': temas_unicos,
        # Datos para las nuevas vistas de progreso
        'alumnos_detallados': alumnos_con_notas_ordenados,  # Ordenados con EN RIESGO primero
        'alumnos_activos': alumnos_activos,
        'alumnos_en_riesgo': alumnos_en_riesgo_count,
        'distribucion': distribucion,
        'mejores_alumnos': mejores_alumnos,
        'alumnos_riesgo': alumnos_riesgo,
        'estadisticas_grupos': estadisticas_grupos,
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
