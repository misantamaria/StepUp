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
    """Muestra y procesa el test"""
    intento = get_object_or_404(IntentTest, id=intento_id, alumno=request.user)
    
    if intento.completado:
        return redirect('boards:resultado_test', intento_id=intento.id)
    
    # Las preguntas de PIE_ED no tienen campo 'activa', obtenerlas todas
    preguntas = intento.test.preguntas.all()
    
    if request.method == 'POST':
        intento = alumno_grade_attempt(intento, request.POST)
        messages.success(request, f'Test completado! Puntuación: {intento.puntuacion:.1f}%')
        return redirect('boards:resultado_test', intento_id=intento.id)
    
    context = {
        'intento': intento,
        'preguntas': preguntas,
        'test': intento.test,
    }
    return render(request, 'boards/alumno/realizar_test.html', context)


@login_required
def resultado_test(request, intento_id):
    """Muestra los resultados de un test completado"""
    intento = get_object_or_404(IntentTest, id=intento_id, alumno=request.user, completado=True)
    respuestas = intento.respuestas.all().select_related('pregunta')
    
    context = {
        'intento': intento,
        'respuestas': respuestas,
    }
    return render(request, 'boards/alumno/resultado.html', context)
