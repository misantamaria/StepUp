from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Count
from .models import Question, Test, IntentTest, RespuestaAlumno
from core.alumno.services import get_dashboard_data as alumno_dashboard_data, start_test as alumno_start_test, grade_attempt as alumno_grade_attempt
from core.profesor.services import get_dashboard_data as profesor_dashboard_data, get_student_stats


def es_profesor(user):
    """Verifica si el usuario es profesor o admin"""
    return user.is_staff


def es_alumno(user):
    """Verifica si el usuario es alumno (no staff)"""
    return not user.is_staff and not user.is_superuser


@login_required
def home(request):
    """Vista principal que redirige según el tipo de usuario"""
    if request.user.is_superuser:
        return redirect('/admin/')
    elif request.user.is_staff:
        return redirect('boards:dashboard_profesor')
    else:
        return redirect('boards:dashboard_alumno')


# ==================== VISTAS PARA ALUMNOS ====================

@login_required
@user_passes_test(es_alumno, login_url='/admin/')
def dashboard_alumno(request):
    """Dashboard para alumnos - muestra tests disponibles"""
    context = alumno_dashboard_data(request.user)
    return render(request, 'boards/alumno/dashboard.html', context)


@login_required
@user_passes_test(es_alumno, login_url='/admin/')
def iniciar_test(request, test_id):
    """Inicia un nuevo intento de test"""
    test = get_object_or_404(Test, id=test_id, activo=True)
    intento = alumno_start_test(request.user, test)
    return redirect('boards:realizar_test', intento_id=intento.id)


@login_required
@user_passes_test(es_alumno, login_url='/admin/')
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
@user_passes_test(es_alumno, login_url='/admin/')
def resultado_test(request, intento_id):
    """Muestra los resultados de un test completado"""
    intento = get_object_or_404(IntentTest, id=intento_id, alumno=request.user, completado=True)
    respuestas = intento.respuestas.all().select_related('pregunta')
    
    context = {
        'intento': intento,
        'respuestas': respuestas,
    }
    return render(request, 'boards/alumno/resultado.html', context)


# ==================== VISTAS PARA PROFESORES ====================

@login_required
@user_passes_test(es_profesor, login_url='/')
def dashboard_profesor(request):
    """Dashboard para profesores - estadísticas y gestión"""
    context = profesor_dashboard_data()
    return render(request, 'boards/profesor/dashboard.html', context)


@login_required
@user_passes_test(es_profesor, login_url='/')
def estadisticas_alumno(request, alumno_id):
    """Ver estadísticas detalladas de un alumno"""
    from django.contrib.auth.models import User
    alumno = get_object_or_404(User, id=alumno_id)
    intentos, promedio = get_student_stats(alumno)
    context = {'alumno': alumno, 'intentos': intentos, 'promedio': promedio}
    return render(request, 'boards/profesor/estadisticas_alumno.html', context)