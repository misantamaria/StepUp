"""
Vistas para el modo profesor: dashboard, estadísticas.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .decorators import es_profesor
from core.profesor.services import get_dashboard_data as profesor_dashboard_data, get_student_stats
from boards.models import Test, Tema


@login_required
@user_passes_test(es_profesor, login_url='/')
def dashboard_profesor(request):
    """Dashboard para profesores - estadísticas y gestión"""
    print(f" Accediendo a dashboard_profesor - Usuario: {request.user.username}")
    context = profesor_dashboard_data()
    print(f" Context generado: {list(context.keys())}")
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


@login_required
@user_passes_test(es_profesor, login_url='/')
@require_POST
def toggle_test_field(request, test_id):
    """Cambia el estado de un campo booleano de un test (AJAX)"""
    import json
    test = get_object_or_404(Test, id=test_id)
    
    try:
        data = json.loads(request.body)
        field = data.get('field')
        
        # Validar que el campo sea uno de los permitidos
        allowed_fields = ['visible_alumnos', 'disponible_alumno', 'visible_profesor', 'disponible_profesor']
        if field not in allowed_fields:
            return JsonResponse({'success': False, 'error': 'Campo no válido'}, status=400)
        
        # Toggle del campo
        current_value = getattr(test, field)
        setattr(test, field, not current_value)
        test.save()
        
        return JsonResponse({
            'success': True,
            field: getattr(test, field)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@user_passes_test(es_profesor, login_url='/')
def get_test_details(request, test_id):
    """Obtiene los detalles de un test para mostrar en el modal de confirmación"""
    test = get_object_or_404(Test, id=test_id)
    
    # Obtener preguntas del test con sus respuestas
    preguntas_data = []
    for pregunta in test.preguntas.all():
        respuestas_data = [
            {
                'texto': respuesta.texto,
                'correcta': respuesta.correcta
            }
            for respuesta in pregunta.respuestas.all()
        ]
        
        preguntas_data.append({
            'enunciado': pregunta.enunciado,
            'respuestas': respuestas_data
        })
    
    # Contar intentos
    from boards.models import IntentTest
    num_intentos = IntentTest.objects.filter(test=test).count()
    
    return JsonResponse({
        'success': True,
        'total_preguntas': test.preguntas.count(),
        'tiempo_limite': test.tiempo_limite,
        'descripcion': test.descripcion or '',
        'num_intentos': num_intentos,
        'preguntas': preguntas_data
    })


@login_required
@user_passes_test(es_profesor, login_url='/')
@require_POST
def delete_test(request, test_id):
    """Elimina un test y todos sus intentos asociados"""
    try:
        test = get_object_or_404(Test, id=test_id)
        test_nombre = test.nombre
        
        # Django eliminará automáticamente los intentos relacionados si está configurado CASCADE
        test.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Test "{test_nombre}" eliminado correctamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_profesor, login_url='/')
@require_POST
def toggle_tema_field(request, tema_id):
    """Cambia el estado de un campo booleano de un tema (AJAX)"""
    import json
    tema = get_object_or_404(Tema, tema_id=tema_id)
    
    try:
        data = json.loads(request.body)
        field = data.get('field')
        
        # Validar que el campo sea uno de los permitidos
        allowed_fields = ['visible_alumnos', 'disponible_alumno', 'visible_profesor', 'disponible_profesor', 'activo']
        if field not in allowed_fields:
            return JsonResponse({'success': False, 'error': 'Campo no válido'}, status=400)
        
        # Toggle del campo
        current_value = getattr(tema, field)
        setattr(tema, field, not current_value)
        tema.save()
        
        return JsonResponse({
            'success': True,
            field: getattr(tema, field)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
