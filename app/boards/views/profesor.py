"""
Vistas para el modo profesor: dashboard, estadísticas.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import es_profesor
from core.profesor.services import get_dashboard_data as profesor_dashboard_data, get_student_stats


@login_required
@user_passes_test(es_profesor, login_url='/')
def dashboard_profesor(request):
    """Dashboard para profesores - estadísticas y gestión"""
    print(f"📊 Accediendo a dashboard_profesor - Usuario: {request.user.username}")
    context = profesor_dashboard_data()
    print(f"📊 Context generado: {list(context.keys())}")
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
