"""
Vistas para el modo alumno: dashboard, tests, resultados.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Test, IntentTest, Tema, Pregunta, ProgresoTema
from core.alumno.services import (
    get_dashboard_data as alumno_dashboard_data,
    start_test as alumno_start_test,
    grade_attempt as alumno_grade_attempt
)


@login_required
def dashboard_alumno(request):
    """Dashboard para alumnos - muestra tests disponibles"""
    # Permitir a staff ver el modo alumno cuando está en sesión
    if request.user.is_staff:
        request.session['modo_actual'] = 'alumno'
    
    context = alumno_dashboard_data(request.user)
    return render(request, 'boards/alumno/dashboard.html', context)


@login_required
def detalle_tema(request, tema_id):
    """Vista detallada de un tema con sus tests organizados por nivel"""
    tema = get_object_or_404(Tema, tema_id=tema_id)
    
    # Obtener progreso del tema
    progreso, _ = ProgresoTema.objects.get_or_create(
        alumno=request.user,
        tema=tema,
        defaults={'total_preguntas': Pregunta.objects.filter(tema=tema_id).count()}
    )
    progreso.actualizar_progreso()
    
    # Obtener tests por nivel y calcular estadísticas
    tests_por_nivel = {
        'Facil': [],
        'Media': [],
        'Dificil': [],
    }
    
    tests_tema = tema.tests.filter(activo=True).order_by('nombre')
    
    for test in tests_tema:
        # Verificar si está visible y cumple requisitos
        disponible = test.visible_alumnos and test.alumno_cumple_requisitos(request.user)
        
        # Obtener mejor intento
        mejor_intento = IntentTest.objects.filter(
            alumno=request.user,
            test=test,
            completado=True
        ).order_by('-puntuacion').first()
        
        test_data = {
            'test': test,
            'disponible': disponible,
            'completado': mejor_intento is not None,
            'mejor_puntuacion': mejor_intento.puntuacion if mejor_intento else None,
        }
        
        tests_por_nivel[test.nivel].append(test_data)
    
    # Calcular progreso y disponibilidad por nivel
    def calcular_info_nivel(tests_nivel):
        total = len(tests_nivel)
        if total == 0:
            return {'progreso': 0, 'completados': 0, 'total': 0, 'disponible': False}
        completados = sum(1 for t in tests_nivel if t['completado'])
        disponibles = sum(1 for t in tests_nivel if t['disponible'])
        return {
            'progreso': (completados / total * 100) if total > 0 else 0,
            'completados': completados,
            'total': total,
            'disponible': disponibles > 0
        }
    
    niveles_info = {
        'facil': calcular_info_nivel(tests_por_nivel['Facil']),
        'intermedio': calcular_info_nivel(tests_por_nivel['Media']),
        'dificil': calcular_info_nivel(tests_por_nivel['Dificil']),
    }
    
    context = {
        'tema': tema,
        'progreso': progreso,
        'niveles_info': niveles_info,
    }
    
    return render(request, 'boards/alumno/detalle_tema.html', context)


@login_required
def tests_nivel(request, tema_id, nivel):
    """Muestra los tests de un nivel específico de un tema"""
    tema = get_object_or_404(Tema, tema_id=tema_id)
    
    # Mapear nivel URL a nivel en BD
    nivel_map = {
        'facil': 'Facil',
        'intermedio': 'Media',
        'dificil': 'Dificil',
    }
    
    nivel_bd = nivel_map.get(nivel)
    if not nivel_bd:
        return redirect('boards:detalle_tema', tema_id=tema_id)
    
    # Obtener tests del nivel
    tests_tema = tema.tests.filter(activo=True, nivel=nivel_bd).order_by('nombre')
    
    tests_data = []
    for test in tests_tema:
        # Verificar si está visible y cumple requisitos
        disponible = test.visible_alumnos and test.alumno_cumple_requisitos(request.user)
        
        # Obtener mejor intento
        mejor_intento = IntentTest.objects.filter(
            alumno=request.user,
            test=test,
            completado=True
        ).order_by('-puntuacion').first()
        
        # Calcular intentos del alumno en este test
        total_intentos = IntentTest.objects.filter(
            alumno=request.user,
            test=test,
            completado=True
        ).count()
        
        tests_data.append({
            'test': test,
            'disponible': disponible,
            'completado': mejor_intento is not None,
            'mejor_puntuacion': mejor_intento.puntuacion if mejor_intento else None,
            'total_intentos': total_intentos,
        })
    
    # Información del nivel
    nivel_info = {
        'facil': {'nombre': 'Fácil', 'emoji': '📗', 'color': '#2c5282', 'color_light': '#3b69b0'},
        'intermedio': {'nombre': 'Intermedio', 'emoji': '📙', 'color': '#1a4d7a', 'color_light': '#2563a8'},
        'dificil': {'nombre': 'Difícil', 'emoji': '📕', 'color': '#0f3057', 'color_light': '#1a4d7a'},
    }
    
    context = {
        'tema': tema,
        'nivel': nivel,
        'nivel_nombre': nivel_info[nivel]['nombre'],
        'nivel_emoji': nivel_info[nivel]['emoji'],
        'nivel_color': nivel_info[nivel]['color'],
        'nivel_color_light': nivel_info[nivel]['color_light'],
        'tests': tests_data,
    }
    
    return render(request, 'boards/alumno/tests_nivel.html', context)


@login_required
def iniciar_test(request, test_id):
    """Inicia un nuevo intento de test"""
    test = get_object_or_404(Test, id=test_id, activo=True)
    intento = alumno_start_test(request.user, test)
    return redirect('boards:realizar_test', intento_id=intento.id)


@login_required
def realizar_test(request, intento_id):
    """Muestra el test con navegación estilo DGT - pregunta por pregunta"""
    intento = get_object_or_404(IntentTest, id=intento_id, alumno=request.user)
    
    if intento.completado:
        return redirect('boards:resultado_test', intento_id=intento.id)
    
    # Obtener todas las preguntas del test
    preguntas = list(intento.test.preguntas.all())
    total_preguntas = len(preguntas)
    
    # Inicializar sesión de respuestas si no existe
    session_key = f'test_{intento_id}_respuestas'
    if session_key not in request.session:
        request.session[session_key] = {}
    
    respuestas_guardadas = request.session[session_key]
    
    # Manejar POST - guardar respuesta y navegar
    if request.method == 'POST':
        action = request.POST.get('action')
        pregunta_actual = int(request.POST.get('pregunta_actual', 0))
        
        # Guardar respuesta si existe
        respuesta_id = request.POST.get(f'pregunta_{preguntas[pregunta_actual].pregunta_id}')
        if respuesta_id:
            respuestas_guardadas[str(pregunta_actual)] = respuesta_id
            request.session.modified = True
        
        # Finalizar test
        if action == 'finalizar':
            # Crear POST data con todas las respuestas guardadas
            post_data = {}
            for idx, pregunta in enumerate(preguntas):
                if str(idx) in respuestas_guardadas:
                    post_data[f'pregunta_{pregunta.pregunta_id}'] = respuestas_guardadas[str(idx)]
            
            # Convertir dict a QueryDict
            from django.http import QueryDict
            query_dict = QueryDict('', mutable=True)
            query_dict.update(post_data)
            
            # Calificar el intento
            intento = alumno_grade_attempt(intento, query_dict)
            
            # Limpiar sesión
            del request.session[session_key]
            
            messages.success(request, f'Test completado! Puntuación: {intento.puntuacion:.1f}%')
            return redirect('boards:resultado_test', intento_id=intento.id)
        
        # Navegar entre preguntas
        if action == 'siguiente' and pregunta_actual < total_preguntas - 1:
            pregunta_actual += 1
        elif action == 'anterior' and pregunta_actual > 0:
            pregunta_actual -= 1
        elif action == 'ir_a':
            pregunta_actual = int(request.POST.get('ir_a_pregunta', pregunta_actual))
        
        # Guardar índice actual en sesión
        request.session[f'test_{intento_id}_pregunta_actual'] = pregunta_actual
        request.session.modified = True
    
    # Obtener pregunta actual
    pregunta_actual_idx = request.session.get(f'test_{intento_id}_pregunta_actual', 0)
    if pregunta_actual_idx >= total_preguntas:
        pregunta_actual_idx = 0
    
    pregunta = preguntas[pregunta_actual_idx]
    
    # Preparar estado de preguntas para el grid
    estado_preguntas = []
    for idx, p in enumerate(preguntas):
        estado_preguntas.append({
            'numero': idx + 1,
            'contestada': str(idx) in respuestas_guardadas,
            'actual': idx == pregunta_actual_idx
        })
    
    # Contar preguntas contestadas
    preguntas_contestadas = len(respuestas_guardadas)
    preguntas_sin_contestar = total_preguntas - preguntas_contestadas
    
    # Obtener respuesta guardada para pregunta actual
    respuesta_seleccionada = respuestas_guardadas.get(str(pregunta_actual_idx))
    
    context = {
        'intento': intento,
        'test': intento.test,
        'pregunta': pregunta,
        'pregunta_actual': pregunta_actual_idx,
        'total_preguntas': total_preguntas,
        'es_primera': pregunta_actual_idx == 0,
        'es_ultima': pregunta_actual_idx == total_preguntas - 1,
        'estado_preguntas': estado_preguntas,
        'preguntas_contestadas': preguntas_contestadas,
        'preguntas_sin_contestar': preguntas_sin_contestar,
        'respuesta_seleccionada': respuesta_seleccionada,
    }
    
    return render(request, 'boards/alumno/realizar_test.html', context)


@login_required
def resultado_test(request, intento_id):
    """Muestra los resultados de un test completado con retroalimentación detallada"""
    intento = get_object_or_404(IntentTest, id=intento_id, alumno=request.user, completado=True)
    respuestas_alumno = intento.respuestas.all().select_related('pregunta')
    
    # Preparar información detallada de cada respuesta
    respuestas_detalle = []
    for resp_alumno in respuestas_alumno:
        pregunta = resp_alumno.pregunta
        
        # Obtener todas las opciones de respuesta de esta pregunta
        opciones = pregunta.get_respuestas()
        
        # Encontrar la respuesta correcta y la del alumno
        respuesta_correcta_obj = None
        respuesta_alumno_obj = None
        
        for opcion in opciones:
            if opcion['es_correcta']:
                respuesta_correcta_obj = opcion
            if str(opcion['id']) == str(resp_alumno.respuesta):
                respuesta_alumno_obj = opcion
        
        respuestas_detalle.append({
            'pregunta': pregunta,
            'respuesta_alumno': resp_alumno,
            'respuesta_alumno_texto': respuesta_alumno_obj['contenido'] if respuesta_alumno_obj else 'No respondida',
            'respuesta_correcta_texto': respuesta_correcta_obj['contenido'] if respuesta_correcta_obj else '',
            'es_correcta': resp_alumno.es_correcta,
            'todas_opciones': opciones,
        })
    
    # Separar fallidas y correctas
    respuestas_fallidas = [r for r in respuestas_detalle if not r['es_correcta']]
    respuestas_correctas = [r for r in respuestas_detalle if r['es_correcta']]
    
    # Limpiar la sesión del test
    session_key = f'test_{intento_id}_respuestas'
    session_key_pregunta = f'test_{intento_id}_pregunta_actual'
    if session_key in request.session:
        del request.session[session_key]
    if session_key_pregunta in request.session:
        del request.session[session_key_pregunta]
    
    context = {
        'intento': intento,
        'respuestas_detalle': respuestas_detalle,
        'respuestas_fallidas': respuestas_fallidas,
        'respuestas_correctas': respuestas_correctas,
        'total_fallidas': len(respuestas_fallidas),
        'total_correctas': len(respuestas_correctas),
    }
    return render(request, 'boards/alumno/resultado.html', context)


@login_required
def mi_progreso(request):
    """Muestra estadísticas detalladas del progreso del alumno"""
    from django.db.models import Avg, Count, Sum, Max
    
    # Estadísticas generales
    total_intentos = IntentTest.objects.filter(alumno=request.user, completado=True).count()
    
    if total_intentos > 0:
        promedio_general = IntentTest.objects.filter(
            alumno=request.user, 
            completado=True
        ).aggregate(Avg('puntuacion'))['puntuacion__avg']
        
        nota_general = promedio_general / 10 if promedio_general else 0
        
        # Total de preguntas respondidas
        total_respuestas = RespuestaAlumno.objects.filter(
            intento__alumno=request.user,
            intento__completado=True
        ).count()
        
        total_correctas = RespuestaAlumno.objects.filter(
            intento__alumno=request.user,
            intento__completado=True,
            es_correcta=True
        ).count()
        
        total_fallidas = total_respuestas - total_correctas
        
        porcentaje_acierto = (total_correctas / total_respuestas * 100) if total_respuestas > 0 else 0
    else:
        promedio_general = 0
        nota_general = 0
        total_respuestas = 0
        total_correctas = 0
        total_fallidas = 0
        porcentaje_acierto = 0
    
    # Estadísticas por tema
    estadisticas_temas = []
    temas = Tema.objects.all()
    
    for tema in temas:
        intentos_tema = IntentTest.objects.filter(
            alumno=request.user,
            test__tema=tema,
            completado=True
        )
        
        if intentos_tema.exists():
            promedio_tema = intentos_tema.aggregate(Avg('puntuacion'))['puntuacion__avg']
            total_tests_tema = intentos_tema.count()
            mejor_intento = intentos_tema.order_by('-puntuacion').first()
            
            # Preguntas por tema
            respuestas_tema = RespuestaAlumno.objects.filter(
                intento__in=intentos_tema,
                pregunta__tema=tema.tema_id
            )
            
            total_preg_tema = respuestas_tema.count()
            correctas_tema = respuestas_tema.filter(es_correcta=True).count()
            fallidas_tema = total_preg_tema - correctas_tema
            
            estadisticas_temas.append({
                'tema': tema,
                'promedio': promedio_tema,
                'nota': promedio_tema / 10,
                'total_tests': total_tests_tema,
                'mejor_puntuacion': mejor_intento.puntuacion,
                'total_preguntas': total_preg_tema,
                'correctas': correctas_tema,
                'fallidas': fallidas_tema,
                'porcentaje_acierto': (correctas_tema / total_preg_tema * 100) if total_preg_tema > 0 else 0
            })
    
    # Ordenar por promedio descendente
    estadisticas_temas.sort(key=lambda x: x['promedio'], reverse=True)
    
    # Últimos 10 intentos
    ultimos_intentos = IntentTest.objects.filter(
        alumno=request.user,
        completado=True
    ).select_related('test', 'test__tema').order_by('-fecha_fin')[:10]
    
    context = {
        'total_intentos': total_intentos,
        'nota_general': nota_general,
        'promedio_general': promedio_general,
        'total_respuestas': total_respuestas,
        'total_correctas': total_correctas,
        'total_fallidas': total_fallidas,
        'porcentaje_acierto': porcentaje_acierto,
        'estadisticas_temas': estadisticas_temas,
        'ultimos_intentos': ultimos_intentos,
    }
    
    return render(request, 'boards/alumno/mi_progreso.html', context)
