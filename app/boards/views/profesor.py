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
    
    try:
        # Obtener preguntas del test con sus respuestas
        preguntas_data = []
        for pregunta in test.preguntas.all():
            # Usar el método get_respuestas() que consulta la tabla Respuesta
            respuestas = pregunta.get_respuestas()
            respuestas_data = [
                {
                    'texto': r['contenido'],
                    'correcta': r['es_correcta']
                }
                for r in respuestas
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
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al cargar detalles: {str(e)}'
        }, status=500)


@login_required
@user_passes_test(es_profesor, login_url='/')
@require_POST
def delete_tema(request, tema_id):
    """Elimina un tema y todos sus tests e intentos asociados"""
    try:
        tema = get_object_or_404(Tema, tema_id=tema_id)
        tema_nombre = tema.tema_id
        
        # Contar tests y preguntas antes de eliminar
        num_tests = tema.tests.count()
        from boards.models import Pregunta
        num_preguntas = Pregunta.objects.filter(tema=tema_id).count()
        
        # Eliminar el tema (CASCADE eliminará tests relacionados)
        tema.delete()
        
        # También eliminar las preguntas asociadas al tema
        Pregunta.objects.filter(tema=tema_id).delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Tema "{tema_nombre}" eliminado correctamente',
            'info': f'Se eliminaron {num_tests} test(s) y {num_preguntas} pregunta(s)'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


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


@login_required
@user_passes_test(es_profesor, login_url='/')
@require_POST
def crear_tema_modal(request):
    """Crea un nuevo tema desde el modal (usando SQL directo)"""
    import json
    from django.db import connection
    
    try:
        data = json.loads(request.body)
        tema_id = data.get('tema_id', '').strip()
        
        if not tema_id:
            return JsonResponse({'success': False, 'error': 'El nombre del tema es obligatorio'}, status=400)
        
        # Insertar directamente en la base de datos
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Tema (Tema_ID, visible_alumnos, disponible_alumno, visible_profesor, disponible_profesor, activo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [tema_id, False, False, True, True, True])
        
        return JsonResponse({
            'success': True,
            'message': f'Tema "{tema_id}" creado correctamente',
            'tema_id': tema_id
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al crear el tema: {str(e)}'
        }, status=400)


@login_required
@user_passes_test(es_profesor, login_url='/')
@require_POST
def crear_test_modal(request):
    """Crea un nuevo test desde el modal (usando SQL directo)"""
    import json
    from django.db import connection
    
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        tema_id = data.get('tema_id', '').strip()
        nivel = data.get('nivel', 'Facil')
        tiempo_limite = int(data.get('tiempo_limite', 30))
        
        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre del test es obligatorio'}, status=400)
        
        if not tema_id:
            return JsonResponse({'success': False, 'error': 'Debe seleccionar un tema'}, status=400)
        
        # Crear el test usando Django ORM para obtener el ID
        test = Test.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            tema_id=tema_id,
            nivel=nivel,
            tiempo_limite=tiempo_limite,
            visible_alumnos=False,
            visible_profesor=True,
            disponible_alumno=False,
            disponible_profesor=True,
            creado_por=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Test "{nombre}" creado correctamente',
            'test_id': test.id,
            'tema_id': tema_id
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al crear el test: {str(e)}'
        }, status=400)


@login_required
@user_passes_test(es_profesor, login_url='/')
@require_POST
def crear_pregunta_modal(request):
    """Crea una nueva pregunta con sus respuestas desde el modal (usando SQL directo)"""
    import json
    from django.db import connection
    
    try:
        data = json.loads(request.body)
        tema_id = data.get('tema_id', '').strip()
        enunciado = data.get('enunciado', '').strip()
        dificultad = data.get('dificultad', 'Facil')
        puntuacion = int(data.get('puntuacion', 1))
        respuestas = data.get('respuestas', [])
        
        # Validaciones
        if not tema_id:
            return JsonResponse({'success': False, 'error': 'Debe seleccionar un tema'}, status=400)
        
        if not enunciado:
            return JsonResponse({'success': False, 'error': 'El enunciado es obligatorio'}, status=400)
        
        if len(respuestas) < 2:
            return JsonResponse({'success': False, 'error': 'Debe proporcionar al menos 2 respuestas'}, status=400)
        
        # Verificar que haya exactamente una respuesta correcta
        correctas = [r for r in respuestas if r.get('es_correcta', False)]
        if len(correctas) != 1:
            return JsonResponse({'success': False, 'error': 'Debe haber exactamente una respuesta correcta'}, status=400)
        
        # Insertar pregunta y respuestas en la base de datos
        with connection.cursor() as cursor:
            # Obtener el siguiente ID de pregunta
            cursor.execute("SELECT MAX(Pregunta_ID) FROM Pregunta")
            max_id = cursor.fetchone()[0]
            pregunta_id = (max_id or 0) + 1
            
            # Insertar pregunta
            cursor.execute("""
                INSERT INTO Pregunta (Pregunta_ID, Tema, Enunciado, Dificultad, Puntuacion)
                VALUES (%s, %s, %s, %s, %s)
            """, [pregunta_id, tema_id, enunciado, dificultad, puntuacion])
            
            # Obtener el siguiente ID de respuesta
            cursor.execute("SELECT MAX(Respuesta_ID) FROM Respuesta")
            max_resp_id = cursor.fetchone()[0]
            respuesta_id = (max_resp_id or 0) + 1
            
            # Insertar respuestas
            for respuesta in respuestas:
                contenido = respuesta.get('contenido', '').strip()
                if not contenido:
                    continue
                
                es_correcta = respuesta.get('es_correcta', False)
                solucion = 'Correcta' if es_correcta else 'Incorrecta'
                
                cursor.execute("""
                    INSERT INTO Respuesta (Respuesta_ID, Pregunta_ID, Solucion, Contenido)
                    VALUES (%s, %s, %s, %s)
                """, [respuesta_id, pregunta_id, solucion, contenido])
                
                respuesta_id += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Pregunta creada correctamente con {len(respuestas)} respuestas',
            'pregunta_id': pregunta_id,
            'tema_id': tema_id
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al crear la pregunta: {str(e)}'
        }, status=400)
