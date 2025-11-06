"""
Vistas para el modo alumno: dashboard, tests, resultados.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import random
from ..models import Test, IntentTest, Tema, Pregunta, ProgresoTema, RespuestaAlumno
from core.alumno.services import (
    get_dashboard_data as alumno_dashboard_data,
    start_test as alumno_start_test,
    grade_attempt as alumno_grade_attempt
)


@login_required
def seleccionar_modo_alumno(request):
    """Vista para que el alumno seleccione entre modo Practicar o Examen"""
    # Contar preguntas disponibles para el examen
    es_profesor = request.user.is_staff
    
    # Obtener y guardar modo_test de la URL si es profesor
    modo_test = False
    if es_profesor:
        modo_test_param = request.GET.get('modo_test', '').lower()
        if modo_test_param == 'true':
            modo_test = True
            request.session['modo_test'] = True
        elif modo_test_param == 'false':
            modo_test = False
            request.session['modo_test'] = False
        else:
            # Si no viene en URL, usar el de la sesión
            modo_test = request.session.get('modo_test', False)
    
    # Contar preguntas según el modo
    if es_profesor:
        if modo_test:
            # Modo Test: solo disponible, incluye los no visibles
            tests_disponibles = Test.objects.filter(
                activo=True, 
                disponible_profesor=True
            )
        else:
            # Modo Normal: visible Y disponible
            tests_disponibles = Test.objects.filter(
                activo=True, 
                visible_profesor=True, 
                disponible_profesor=True
            )
    else:
        tests_disponibles = Test.objects.filter(
            activo=True, 
            visible_alumnos=True, 
            disponible_alumno=True
        )
    
    # Recopilar todas las preguntas de estos tests
    preguntas_ids = []
    for test in tests_disponibles:
        preguntas_ids.extend(list(test.preguntas.values_list('pregunta_id', flat=True)))
    
    # Eliminar duplicados
    preguntas_ids = list(set(preguntas_ids))
    total_preguntas_disponibles = len(preguntas_ids)
    examen_disponible = total_preguntas_disponibles >= 30
    
    context = {
        'total_preguntas_disponibles': total_preguntas_disponibles,
        'examen_disponible': examen_disponible,
        'modo_test': modo_test,
    }
    
    return render(request, 'boards/alumno/seleccionar_modo.html', context)


@login_required
def iniciar_examen(request):
    """Inicia un examen con 30 preguntas aleatorias y 20 minutos de tiempo"""
    # Si es staff en modo alumno, permitir
    es_profesor = request.user.is_staff
    
    # Respetar el modo_test de la sesión si es profesor
    modo_test = False
    if es_profesor:
        modo_test = request.session.get('modo_test', False)
    
    # Obtener todos los tests visibles y disponibles
    # En modo_test, solo verificar disponible_profesor (no visible_profesor)
    if es_profesor:
        if modo_test:
            # Modo Test: solo disponible, incluye los no visibles
            tests_disponibles = Test.objects.filter(
                activo=True, 
                disponible_profesor=True
            )
        else:
            # Modo Normal: visible Y disponible
            tests_disponibles = Test.objects.filter(
                activo=True, 
                visible_profesor=True, 
                disponible_profesor=True
            )
    else:
        tests_disponibles = Test.objects.filter(
            activo=True, 
            visible_alumnos=True, 
            disponible_alumno=True
        )
    
    # Recopilar todas las preguntas de estos tests
    preguntas_ids = []
    for test in tests_disponibles:
        preguntas_ids.extend(list(test.preguntas.values_list('pregunta_id', flat=True)))
    
    # Eliminar duplicados
    preguntas_ids = list(set(preguntas_ids))
    
    # Verificar que haya al menos 30 preguntas
    if len(preguntas_ids) < 30:
        if not es_profesor:
            # Los alumnos no pueden continuar
            messages.error(request, f'No hay suficientes preguntas disponibles. Se necesitan 30 y solo hay {len(preguntas_ids)}.')
            return redirect('boards:seleccionar_modo_alumno')
        else:
            # Los profesores pueden continuar pero con advertencia
            if not modo_test:
                messages.warning(
                    request, 
                    f'⚠️ Este examen está bloqueado para alumnos. Solo hay {len(preguntas_ids)} preguntas disponibles (se necesitan 30). '
                    f'Activa el "Modo Test" para incluir preguntas no visibles o añade más preguntas visibles.'
                )
            else:
                messages.warning(
                    request, 
                    f'⚠️ Este examen está bloqueado para alumnos. Solo hay {len(preguntas_ids)} preguntas disponibles (se necesitan 30). '
                    f'Añade más preguntas disponibles o hazlas visibles.'
                )
            
            # Si hay menos de 30, usar todas las disponibles
            if len(preguntas_ids) < 30:
                num_preguntas = len(preguntas_ids)
                preguntas_seleccionadas = preguntas_ids
            else:
                num_preguntas = 30
                preguntas_seleccionadas = random.sample(preguntas_ids, 30)
    else:
        # Hay suficientes preguntas, seleccionar 30 aleatorias
        num_preguntas = 30
        preguntas_seleccionadas = random.sample(preguntas_ids, 30)
    
    # Crear un intento de examen (usaremos un IntentTest especial)
    # Primero, necesitamos crear o obtener un Test especial para exámenes
    test_examen, created = Test.objects.get_or_create(
        nombre='EXAMEN_ALEATORIO',
        defaults={
            'descripcion': 'Examen con preguntas aleatorias',
            'tiempo_limite': 20,  # 20 minutos
            'activo': False,  # No visible en listados normales
            'visible_alumnos': False,
            'visible_profesor': False,
            'disponible_alumno': False,
            'disponible_profesor': False,
            'nivel': 'Media',
        }
    )
    
    # Crear el intento
    intento = IntentTest.objects.create(
        alumno=request.user,
        test=test_examen,
        fecha_inicio=timezone.now(),
        completado=False,
        es_examen=True  # Marcar como examen
    )
    
    # Guardar las preguntas seleccionadas en la sesión
    request.session[f'examen_{intento.id}_preguntas'] = preguntas_seleccionadas
    request.session[f'examen_{intento.id}_tiempo_inicio'] = timezone.now().isoformat()
    
    return redirect('boards:realizar_examen', intento_id=intento.id)


@login_required
def cambiar_modo_examen(request):
    """Cambia el modo test y reinicia el examen"""
    # Solo profesores pueden cambiar el modo
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para cambiar el modo.')
        return redirect('boards:seleccionar_modo_alumno')
    
    # Cambiar el modo en la sesión
    modo_actual = request.session.get('modo_test', False)
    nuevo_modo = not modo_actual
    request.session['modo_test'] = nuevo_modo
    
    # Redirigir a iniciar un nuevo examen
    return redirect('boards:iniciar_examen')


@login_required
def realizar_examen(request, intento_id):
    """Realiza un examen con tiempo límite de 20 minutos"""
    intento = get_object_or_404(IntentTest, id=intento_id, alumno=request.user)
    
    # Verificar que es un examen
    if not intento.es_examen:
        messages.error(request, 'Este no es un intento de examen válido.')
        return redirect('boards:dashboard_alumno')
    
    if intento.completado:
        return redirect('boards:resultado_test', intento_id=intento.id)
    
    # Obtener preguntas del examen desde la sesión
    session_key_preguntas = f'examen_{intento_id}_preguntas'
    session_key_tiempo = f'examen_{intento_id}_tiempo_inicio'
    
    if session_key_preguntas not in request.session:
        messages.error(request, 'Examen no válido o expirado.')
        return redirect('boards:seleccionar_modo_alumno')
    
    preguntas_ids = request.session[session_key_preguntas]
    tiempo_inicio = timezone.datetime.fromisoformat(request.session[session_key_tiempo])
    
    # Obtener las preguntas
    preguntas = list(Pregunta.objects.filter(pregunta_id__in=preguntas_ids))
    # Ordenar según el orden en preguntas_ids
    preguntas.sort(key=lambda p: preguntas_ids.index(p.pregunta_id))
    
    total_preguntas = len(preguntas)
    
    # Calcular tiempo restante
    tiempo_transcurrido = timezone.now() - tiempo_inicio
    tiempo_limite = timedelta(minutes=20)
    tiempo_restante = tiempo_limite - tiempo_transcurrido
    
    # Si se acabó el tiempo, finalizar automáticamente
    if tiempo_restante.total_seconds() <= 0:
        # Calificar con las respuestas que tenga
        session_key_respuestas = f'test_{intento_id}_respuestas'
        respuestas_guardadas = request.session.get(session_key_respuestas, {})
        
        from django.http import QueryDict
        query_dict = QueryDict('', mutable=True)
        for idx, pregunta in enumerate(preguntas):
            if str(idx) in respuestas_guardadas:
                query_dict[f'pregunta_{pregunta.pregunta_id}'] = respuestas_guardadas[str(idx)]
        
        intento = alumno_grade_attempt(intento, query_dict)
        
        # Limpiar sesión
        del request.session[session_key_preguntas]
        del request.session[session_key_tiempo]
        if session_key_respuestas in request.session:
            del request.session[session_key_respuestas]
        
        messages.warning(request, 'El tiempo del examen ha finalizado.')
        return redirect('boards:resultado_test', intento_id=intento.id)
    
    # Inicializar sesión de respuestas si no existe
    session_key_respuestas = f'test_{intento_id}_respuestas'
    if session_key_respuestas not in request.session:
        request.session[session_key_respuestas] = {}
    
    respuestas_guardadas = request.session[session_key_respuestas]
    
    # Manejar POST - guardar respuesta y navegar
    if request.method == 'POST':
        action = request.POST.get('action')
        pregunta_actual = int(request.POST.get('pregunta_actual', 0))
        
        # Guardar respuesta si existe
        respuesta_id = request.POST.get(f'pregunta_{preguntas[pregunta_actual].pregunta_id}')
        if respuesta_id:
            respuestas_guardadas[str(pregunta_actual)] = respuesta_id
            request.session.modified = True
        
        # Finalizar examen
        if action == 'finalizar':
            from django.http import QueryDict
            query_dict = QueryDict('', mutable=True)
            for idx, pregunta in enumerate(preguntas):
                if str(idx) in respuestas_guardadas:
                    query_dict[f'pregunta_{pregunta.pregunta_id}'] = respuestas_guardadas[str(idx)]
            
            intento = alumno_grade_attempt(intento, query_dict)
            
            # Limpiar sesión
            del request.session[session_key_preguntas]
            del request.session[session_key_tiempo]
            del request.session[session_key_respuestas]
            
            return redirect('boards:resultado_test', intento_id=intento.id)
        
        # Navegación entre preguntas
        elif action == 'siguiente' and pregunta_actual < total_preguntas - 1:
            pregunta_actual += 1
        elif action == 'anterior' and pregunta_actual > 0:
            pregunta_actual -= 1
        elif action == 'ir_a':
            ir_a = request.POST.get('ir_a_pregunta')
            if ir_a:
                pregunta_actual = int(ir_a)
        elif action.startswith('ir_'):
            pregunta_actual = int(action.split('_')[1])
    else:
        pregunta_actual = 0
    
    # Preparar datos de la pregunta actual
    pregunta = preguntas[pregunta_actual]
    respuestas = pregunta.get_respuestas()
    
    # Marcar respuesta seleccionada
    respuesta_seleccionada = respuestas_guardadas.get(str(pregunta_actual))
    
    # Crear mapa de estado de preguntas (contestadas/no contestadas)
    estado_preguntas = []
    for idx in range(total_preguntas):
        estado_preguntas.append({
            'numero': idx + 1,
            'contestada': str(idx) in respuestas_guardadas,
            'actual': idx == pregunta_actual,
        })
    
    context = {
        'intento': intento,
        'pregunta': pregunta,
        'respuestas': respuestas,
        'pregunta_numero': pregunta_actual + 1,
        'total_preguntas': total_preguntas,
        'pregunta_actual': pregunta_actual,
        'pregunta_actual_idx': pregunta_actual,
        'respuesta_seleccionada': respuesta_seleccionada,
        'es_primera': pregunta_actual == 0,
        'es_ultima': pregunta_actual == total_preguntas - 1,
        'estado_preguntas': estado_preguntas,
        'preguntas_contestadas': len(respuestas_guardadas),
        'preguntas_sin_contestar': total_preguntas - len(respuestas_guardadas),
        'contestadas': len(respuestas_guardadas),
        'tiempo_restante_segundos': int(tiempo_restante.total_seconds()),
        'es_examen': True,
        'modo_test': request.session.get('modo_test', False) if request.user.is_staff else False,
    }
    
    return render(request, 'boards/alumno/realizar_test.html', context)


@login_required
def dashboard_alumno(request):
    """Dashboard para alumnos - muestra tests disponibles"""
    # Si no viene de la selección de modo, redirigir allí primero
    if 'desde_seleccion' not in request.GET:
        return redirect('boards:seleccionar_modo_alumno')
    
    # Permitir a staff ver el modo alumno cuando está en sesión
    if request.user.is_staff:
        request.session['modo_actual'] = 'alumno'
        # Verificar si está en modo test (parámetro GET)
        modo_test = request.GET.get('modo_test', 'false').lower() == 'true'
        request.session['modo_test'] = modo_test
    else:
        modo_test = False
    
    context = alumno_dashboard_data(request.user, modo_test=modo_test)
    context['modo_test'] = modo_test  # Pasar al template
    return render(request, 'boards/alumno/dashboard.html', context)


@login_required
def detalle_tema(request, tema_id):
    """Vista detallada de un tema con sus tests organizados por nivel"""
    # Determinar si es profesor en modo alumno
    es_profesor = request.user.is_staff
    
    # Obtener tema verificando que esté visible y disponible
    if es_profesor:
        tema = get_object_or_404(Tema, tema_id=tema_id, activo=True, visible_profesor=True, disponible_profesor=True)
    else:
        tema = get_object_or_404(Tema, tema_id=tema_id, activo=True, visible_alumnos=True, disponible_alumno=True)
    
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
    
    # Filtrar tests según si es profesor o alumno
    if es_profesor:
        tests_tema = tema.tests.filter(activo=True, visible_profesor=True, disponible_profesor=True).order_by('nombre')
    else:
        tests_tema = tema.tests.filter(activo=True, visible_alumnos=True, disponible_alumno=True).order_by('nombre')
    
    for test in tests_tema:
        # Verificar si está visible y cumple requisitos
        disponible = test.alumno_cumple_requisitos(request.user)
        
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
    
    # Determinar si es profesor en modo alumno
    es_profesor = request.user.is_staff
    
    # Mapear nivel URL a nivel en BD
    nivel_map = {
        'facil': 'Facil',
        'intermedio': 'Media',
        'dificil': 'Dificil',
    }
    
    nivel_bd = nivel_map.get(nivel)
    if not nivel_bd:
        return redirect('boards:detalle_tema', tema_id=tema_id)
    
    # Obtener tests del nivel según si es profesor o alumno
    if es_profesor:
        tests_tema = tema.tests.filter(activo=True, nivel=nivel_bd, visible_profesor=True, disponible_profesor=True).order_by('nombre')
    else:
        tests_tema = tema.tests.filter(activo=True, nivel=nivel_bd, visible_alumnos=True, disponible_alumno=True).order_by('nombre')
    
    tests_data = []
    for test in tests_tema:
        # Verificar si cumple requisitos
        disponible = test.alumno_cumple_requisitos(request.user)
        
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
        'facil': {'nombre': 'Fácil', 'color': '#2c5282', 'color_light': '#3b69b0'},
        'intermedio': {'nombre': 'Intermedio', 'color': '#1a4d7a', 'color_light': '#2563a8'},
        'dificil': {'nombre': 'Difícil', 'color': '#0f3057', 'color_light': '#1a4d7a'},
    }
    
    context = {
        'tema': tema,
        'nivel': nivel,
        'nivel_nombre': nivel_info[nivel]['nombre'],
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
    
    # Determinar qué preguntas mostrar según el tipo de test
    if intento.es_examen:
        # En exámenes, solo mostrar preguntas contestadas
        preguntas_a_mostrar = [resp.pregunta for resp in respuestas_alumno]
    else:
        # En tests normales, mostrar TODAS las preguntas del test
        preguntas_a_mostrar = list(intento.test.preguntas.all())
    
    # Crear un diccionario de respuestas del alumno para búsqueda rápida
    respuestas_dict = {resp.pregunta.pregunta_id: resp for resp in respuestas_alumno}
    
    for pregunta in preguntas_a_mostrar:
        # Obtener todas las opciones de respuesta de esta pregunta
        opciones = pregunta.get_respuestas()
        
        # Obtener la respuesta del alumno si existe
        resp_alumno = respuestas_dict.get(pregunta.pregunta_id)
        
        # Encontrar la respuesta correcta y la del alumno
        respuesta_correcta_obj = None
        respuesta_alumno_obj = None
        
        for opcion in opciones:
            if opcion['es_correcta']:
                respuesta_correcta_obj = opcion
            if resp_alumno and str(opcion['id']) == str(resp_alumno.respuesta):
                respuesta_alumno_obj = opcion
        
        respuestas_detalle.append({
            'pregunta': pregunta,
            'respuesta_alumno': resp_alumno,
            'respuesta_alumno_texto': respuesta_alumno_obj['contenido'] if respuesta_alumno_obj else 'No respondida',
            'respuesta_correcta_texto': respuesta_correcta_obj['contenido'] if respuesta_correcta_obj else '',
            'es_correcta': resp_alumno.es_correcta if resp_alumno else False,
            'todas_opciones': opciones,
            'fue_contestada': resp_alumno is not None,
        })
    
    # Separar fallidas y correctas
    respuestas_fallidas = [r for r in respuestas_detalle if not r['es_correcta']]
    respuestas_correctas = [r for r in respuestas_detalle if r['es_correcta']]
    
    # Calcular sin contestar
    total_sin_contestar = intento.total_preguntas - len(respuestas_correctas) - len(respuestas_fallidas)
    
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
        'total_sin_contestar': total_sin_contestar,
    }
    return render(request, 'boards/alumno/resultado.html', context)


@login_required
def mi_progreso(request):
    """Muestra estadísticas detalladas del progreso del alumno"""
    from django.db.models import Avg, Count, Sum, Max
    
    # Total de tests disponibles para el alumno
    total_tests_disponibles = Test.objects.filter(activo=True, visible_alumnos=True).count()
    
    # Estadísticas generales
    total_intentos = IntentTest.objects.filter(alumno=request.user, completado=True).count()
    
    # Tests únicos completados (distintos)
    tests_completados = IntentTest.objects.filter(
        alumno=request.user,
        completado=True
    ).values('test').distinct().count()
    
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
        
        total_fallidas = RespuestaAlumno.objects.filter(
            intento__alumno=request.user,
            intento__completado=True,
            es_correcta=False
        ).count()
        
        # Calcular preguntas esperadas y no respondidas
        total_preguntas_esperadas = IntentTest.objects.filter(
            alumno=request.user,
            completado=True
        ).aggregate(Sum('total_preguntas'))['total_preguntas__sum'] or 0
        
        total_sin_responder = max(0, total_preguntas_esperadas - total_respuestas)
        
        # Calcular tests superados (nota >= 5 = puntuación >= 50)
        tests_superados = IntentTest.objects.filter(
            alumno=request.user,
            completado=True,
            puntuacion__gte=50
        ).values('test').distinct().count()
        
        porcentaje_acierto = (total_correctas / total_respuestas * 100) if total_respuestas > 0 else 0
    else:
        promedio_general = 0
        nota_general = 0
        total_respuestas = 0
        total_correctas = 0
        total_fallidas = 0
        total_sin_responder = 0
        tests_completados = 0
        tests_superados = 0
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
        'tests_completados': tests_completados,
        'total_tests_disponibles': total_tests_disponibles,
        'tests_superados': tests_superados,
        'nota_general': nota_general,
        'promedio_general': promedio_general,
        'total_respuestas': total_respuestas,
        'total_correctas': total_correctas,
        'total_fallidas': total_fallidas,
        'total_sin_responder': total_sin_responder,
        'porcentaje_acierto': porcentaje_acierto,
        'estadisticas_temas': estadisticas_temas,
        'ultimos_intentos': ultimos_intentos,
    }
    
    return render(request, 'boards/alumno/mi_progreso.html', context)


@login_required
def estadisticas_temas(request):
    """Muestra estadísticas detalladas por tema"""
    from django.db.models import Avg, Count, Q
    
    estadisticas_temas = []
    
    # Determinar si es profesor en modo alumno
    es_profesor = request.user.is_staff
    
    # Obtener solo los temas que están activos, visibles Y disponibles, y que tienen al menos un test activo, visible Y disponible
    if es_profesor:
        temas_con_tests_visibles = Tema.objects.filter(
            activo=True,
            visible_profesor=True,
            disponible_profesor=True,
            tests__activo=True,
            tests__visible_profesor=True,
            tests__disponible_profesor=True
        ).distinct().order_by('tema_id')
    else:
        temas_con_tests_visibles = Tema.objects.filter(
            activo=True,
            visible_alumnos=True,
            disponible_alumno=True,
            tests__activo=True,
            tests__visible_alumnos=True,
            tests__disponible_alumno=True
        ).distinct().order_by('tema_id')
    
    for tema in temas_con_tests_visibles:
        # Tests del tema que están activos, visibles Y disponibles
        if es_profesor:
            tests_tema = Test.objects.filter(tema=tema, visible_profesor=True, disponible_profesor=True, activo=True)
        else:
            tests_tema = Test.objects.filter(tema=tema, visible_alumnos=True, disponible_alumno=True, activo=True)
        
        # Filtrar tests según requisitos del alumno
        tests_disponibles = []
        for test in tests_tema:
            if test.alumno_cumple_requisitos(request.user):
                tests_disponibles.append(test)
        
        total_tests_tema = len(tests_disponibles)
        total_tests_tema_completo = tests_tema.count()  # Total de tests del tema (incluso no disponibles por requisitos)
        bloqueado = total_tests_tema == 0 and total_tests_tema_completo > 0
        
        # Intentos completados
        intentos_tema = IntentTest.objects.filter(
            alumno=request.user,
            test__tema=tema,
            completado=True
        )
        
        # Mostrar tema bloqueado si tiene tests pero ninguno está disponible
        if bloqueado:
            estadisticas_temas.append({
                'tema': tema,
                'bloqueado': True,
                'nota': 0,
                'tests_resueltos': 0,
                'tests_completados': 0,
                'total_tests_tema': total_tests_tema_completo,
                'tests_pendientes': total_tests_tema_completo,
                'porcentaje_superados': 0,
                'correctas': 0,
                'fallidas': 0,
                'no_respondidas': 0,
                'porcentaje_correctas': 0,
                'porcentaje_falladas': 0,
                'porcentaje_no_respondidas': 0,
            })
            continue
        
        if intentos_tema.exists():
            promedio_tema = intentos_tema.aggregate(Avg('puntuacion'))['puntuacion__avg']
            tests_resueltos = intentos_tema.values('test').distinct().count()
            tests_pendientes = total_tests_tema - tests_resueltos
            
            # Tests superados (nota >= 5)
            tests_superados = intentos_tema.filter(puntuacion__gte=50).values('test').distinct().count()
            porcentaje_superados = (tests_superados / tests_resueltos * 100) if tests_resueltos > 0 else 0
            
            # Todas las preguntas del tema
            total_preguntas_tema = Pregunta.objects.filter(tema=tema.tema_id).count()
            
            # Respuestas del alumno a preguntas de este tema
            respuestas_tema = RespuestaAlumno.objects.filter(
                intento__in=intentos_tema,
                pregunta__tema=tema.tema_id
            )
            
            total_respondidas = respuestas_tema.count()
            correctas = respuestas_tema.filter(es_correcta=True).count()
            fallidas = respuestas_tema.filter(es_correcta=False).count()
            
            # Calcular preguntas no respondidas (aproximado basado en tests realizados)
            preguntas_esperadas = tests_resueltos * 10  # Asumiendo ~10 preguntas por test
            no_respondidas = max(0, preguntas_esperadas - total_respondidas)
            
            # Porcentajes
            total_calculado = correctas + fallidas + no_respondidas
            if total_calculado > 0:
                porcentaje_correctas = (correctas / total_calculado * 100)
                porcentaje_falladas = (fallidas / total_calculado * 100)
                porcentaje_no_respondidas = (no_respondidas / total_calculado * 100)
            else:
                porcentaje_correctas = porcentaje_falladas = porcentaje_no_respondidas = 0
            
            estadisticas_temas.append({
                'tema': tema,
                'bloqueado': False,
                'nota': promedio_tema / 10,
                'tests_resueltos': tests_resueltos,
                'tests_completados': tests_resueltos,  # Tests únicos completados
                'total_tests_tema': total_tests_tema,  # Total tests disponibles en el tema
                'tests_pendientes': tests_pendientes,
                'porcentaje_superados': porcentaje_superados,
                'correctas': correctas,
                'fallidas': fallidas,
                'no_respondidas': no_respondidas,
                'porcentaje_correctas': porcentaje_correctas,
                'porcentaje_falladas': porcentaje_falladas,
                'porcentaje_no_respondidas': porcentaje_no_respondidas,
            })
        else:
            # Tema sin intentos: mostrar con valores en 0
            estadisticas_temas.append({
                'tema': tema,
                'bloqueado': False,
                'nota': 0,
                'tests_resueltos': 0,
                'tests_completados': 0,
                'total_tests_tema': total_tests_tema,
                'tests_pendientes': total_tests_tema,
                'porcentaje_superados': 0,
                'correctas': 0,
                'fallidas': 0,
                'no_respondidas': 0,
                'porcentaje_correctas': 0,
                'porcentaje_falladas': 0,
                'porcentaje_no_respondidas': 0,
            })
    
    # NO ordenar - mantener orden original de los temas
    # estadisticas_temas.sort(key=lambda x: x['nota'], reverse=True)
    
    context = {
        'estadisticas_temas': estadisticas_temas,
    }
    
    return render(request, 'boards/alumno/estadisticas_temas.html', context)


@login_required
def historial_intentos(request):
    """Muestra el historial completo de intentos"""
    ultimos_intentos = IntentTest.objects.filter(
        alumno=request.user,
        completado=True
    ).select_related('test', 'test__tema').order_by('-fecha_fin')[:50]
    
    context = {
        'ultimos_intentos': ultimos_intentos,
    }
    
    return render(request, 'boards/alumno/historial_intentos.html', context)
