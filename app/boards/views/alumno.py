"""
Vistas para el modo alumno: dashboard, tests, resultados.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Test, IntentTest
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
    
    preguntas = intento.test.preguntas.filter(activa=True)
    
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
