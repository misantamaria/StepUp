"""
Vistas para el modo profesor: dashboard, estadísticas.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Avg, Max, Min
from .decorators import es_profesor
from core.profesor.services import get_dashboard_data as profesor_dashboard_data, get_student_stats
from boards.models import Test, Tema, IntentTest, Pregunta


@login_required
@user_passes_test(es_profesor, login_url='/')
def dashboard_profesor(request):
    """Dashboard para profesores - estadísticas y gestión"""
    print(f"Accediendo a dashboard_profesor - Usuario: {request.user.username}")
    context = profesor_dashboard_data()
    print(f"Context generado: {list(context.keys())}")
    
    # Debug: verificar datos específicos para las nuevas secciones
    print(f"Alumnos detallados: {len(context.get('alumnos_detallados', []))}")
    print(f"Distribución: {context.get('distribucion', {})}")
    print(f"Mejores alumnos: {len(context.get('mejores_alumnos', []))}")
    
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
        tiempo_limite = int(data.get('tiempo_limite', 0)) if data.get('tiempo_limite') else 0
        es_aleatorio = data.get('es_aleatorio', False)
        
        # Si tiempo_limite es 0 o None, significa tiempo infinito
        if tiempo_limite < 0:
            tiempo_limite = 0
        
        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre del test es obligatorio'}, status=400)
        
        if not tema_id:
            return JsonResponse({'success': False, 'error': 'Debe seleccionar un tema'}, status=400)
        
        # Preparar configuración aleatoria si aplica
        configuracion_aleatoria = None
        if es_aleatorio:
            temas_aleatorios = data.get('temas_aleatorios', [])
            num_preguntas = data.get('num_preguntas_aleatorias', 10)
            
            if not temas_aleatorios:
                return JsonResponse({'success': False, 'error': 'Debe seleccionar al menos un tema para el examen aleatorio'}, status=400)
            
            configuracion_aleatoria = {
                'temas': temas_aleatorios,
                'num_preguntas': num_preguntas
            }
        
        # Crear el test usando Django ORM para obtener el ID
        test = Test.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            tema_id=tema_id,
            nivel=nivel,
            tiempo_limite=tiempo_limite,
            es_aleatorio=es_aleatorio,
            configuracion_aleatoria=configuracion_aleatoria,
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


@login_required
@user_passes_test(es_profesor, login_url='/')
def get_tema_details(request, tema_id):
    """Obtiene los detalles de un tema para edición"""
    try:
        tema = get_object_or_404(Tema, tema_id=tema_id)
        tests = tema.tests.all().annotate(num_preguntas=Count('preguntas'))
        
        tests_data = [{
            'id': test.id,
            'nombre': test.nombre,
            'preguntas': test.num_preguntas,
            'tiempo': test.tiempo_limite
        } for test in tests]
        
        return JsonResponse({
            'success': True,
            'tema_id': tema.tema_id,
            'tests': tests_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@user_passes_test(es_profesor, login_url='/')
@require_POST
def update_tema(request, tema_id):
    """Actualiza el nombre de un tema"""
    import json
    from django.db import connection
    
    try:
        tema = get_object_or_404(Tema, tema_id=tema_id)
        data = json.loads(request.body)
        nuevo_nombre = data.get('nuevo_nombre', '').strip()
        
        if not nuevo_nombre:
            return JsonResponse({'success': False, 'error': 'El nombre del tema es obligatorio'}, status=400)
        
        # Si el nombre cambió, actualizar en la base de datos
        if nuevo_nombre != tema_id:
            with connection.cursor() as cursor:
                # Actualizar el nombre del tema
                cursor.execute("""
                    UPDATE Tema SET Tema_ID = %s WHERE Tema_ID = %s
                """, [nuevo_nombre, tema_id])
                
                # Actualizar las referencias en otras tablas
                cursor.execute("""
                    UPDATE Pregunta SET Tema = %s WHERE Tema = %s
                """, [nuevo_nombre, tema_id])
                
                cursor.execute("""
                    UPDATE Test SET Tema_ID = %s WHERE Tema_ID = %s
                """, [nuevo_nombre, tema_id])
        
        return JsonResponse({
            'success': True,
            'message': f'Tema actualizado correctamente'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@user_passes_test(es_profesor, login_url='/')
def get_test_data(request, test_id):
    """Obtiene todos los datos de un test para edición"""
    try:
        test = get_object_or_404(Test, id=test_id)
        preguntas = test.preguntas.all()
        
        preguntas_data = []
        for pregunta in preguntas:
            respuestas = pregunta.get_respuestas()
            preguntas_data.append({
                'id': pregunta.pregunta_id,
                'enunciado': pregunta.enunciado,
                'dificultad': pregunta.dificultad,
                'respuestas': len(respuestas)
            })
        
        return JsonResponse({
            'success': True,
            'id': test.id,
            'tema': test.tema.tema_id if test.tema else '',
            'nombre': test.nombre,
            'descripcion': test.descripcion or '',
            'nivel': test.nivel or 'Facil',
            'tiempo_limite': test.tiempo_limite,
            'preguntas': preguntas_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@user_passes_test(es_profesor, login_url='/')
@require_POST
def update_test(request, test_id):
    """Actualiza los datos de un test"""
    import json
    
    try:
        test = get_object_or_404(Test, id=test_id)
        data = json.loads(request.body)
        
        test.tema_id = data.get('tema')
        test.nombre = data.get('nombre', '').strip()
        test.descripcion = data.get('descripcion', '').strip()
        test.nivel = data.get('nivel', 'Facil')
        tiempo_limite = int(data.get('tiempo_limite', 0)) if data.get('tiempo_limite') else 0
        
        # Si tiempo_limite es 0 o None, significa tiempo infinito
        if tiempo_limite < 0:
            tiempo_limite = 0
            
        test.tiempo_limite = tiempo_limite
        test.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Test actualizado correctamente'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@user_passes_test(es_profesor, login_url='/')
def get_pregunta_data(request, pregunta_id):
    """Obtiene todos los datos de una pregunta para edición"""
    try:
        from boards.models import Pregunta
        pregunta = get_object_or_404(Pregunta, pregunta_id=pregunta_id)
        respuestas = pregunta.get_respuestas()
        
        respuestas_data = [{
            'contenido': r['contenido'],
            'es_correcta': r['es_correcta']
        } for r in respuestas]
        
        return JsonResponse({
            'success': True,
            'id': pregunta.pregunta_id,
            'tema': pregunta.tema,
            'enunciado': pregunta.enunciado,
            'dificultad': pregunta.dificultad,
            'puntuacion': pregunta.puntuacion,
            'respuestas': respuestas_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@user_passes_test(es_profesor, login_url='/')
@require_POST
def update_pregunta(request, pregunta_id):
    """Actualiza una pregunta y sus respuestas"""
    import json
    from django.db import connection
    
    try:
        from boards.models import Pregunta
        pregunta = get_object_or_404(Pregunta, pregunta_id=pregunta_id)
        data = json.loads(request.body)
        
        tema = data.get('tema', '').strip()
        enunciado = data.get('enunciado', '').strip()
        dificultad = data.get('dificultad', 'Facil')
        puntuacion = int(data.get('puntuacion', 1))
        respuestas = data.get('respuestas', [])
        
        # Validaciones
        if not tema or not enunciado:
            return JsonResponse({'success': False, 'error': 'Tema y enunciado son obligatorios'}, status=400)
        
        if len(respuestas) < 2:
            return JsonResponse({'success': False, 'error': 'Debe haber al menos 2 respuestas'}, status=400)
        
        correctas = [r for r in respuestas if r.get('es_correcta', False)]
        if len(correctas) != 1:
            return JsonResponse({'success': False, 'error': 'Debe haber exactamente una respuesta correcta'}, status=400)
        
        # Actualizar pregunta y respuestas
        with connection.cursor() as cursor:
            # Actualizar pregunta
            cursor.execute("""
                UPDATE Pregunta 
                SET Tema = %s, Enunciado = %s, Dificultad = %s, Puntuacion = %s
                WHERE Pregunta_ID = %s
            """, [tema, enunciado, dificultad, puntuacion, pregunta_id])
            
            # Eliminar respuestas antiguas
            cursor.execute("DELETE FROM Respuesta WHERE Pregunta_ID = %s", [pregunta_id])
            
            # Obtener el siguiente ID de respuesta
            cursor.execute("SELECT MAX(Respuesta_ID) FROM Respuesta")
            max_resp_id = cursor.fetchone()[0]
            respuesta_id = (max_resp_id or 0) + 1
            
            # Insertar nuevas respuestas
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
            'message': 'Pregunta actualizada correctamente'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@user_passes_test(es_profesor, login_url='/')
def progreso_alumnos(request):
    """Vista de progreso individual de todos los alumnos no-staff"""
    context = profesor_dashboard_data()
    
    # Filtrar solo datos de alumnos (no staff)
    alumnos_detallados = context.get('alumnos_detallados', [])
    
    # Agregar estadísticas por tema para cada alumno
    from boards.models import Tema, Pregunta
    temas = Tema.objects.exclude(tema_id='Exámenes').order_by('tema_id')
    
    for alumno_data in alumnos_detallados:
        alumno = alumno_data['alumno']
        estadisticas_por_tema = []
        
        for tema in temas:
            # Intentos del alumno en tests de este tema
            intentos_tema = IntentTest.objects.filter(
                alumno=alumno, 
                completado=True, 
                test__tema=tema
            )
            
            if intentos_tema.exists():
                nota_media_tema = intentos_tema.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
                total_intentos_tema = intentos_tema.count()
                mejor_puntuacion = intentos_tema.aggregate(Max('puntuacion'))['puntuacion__max'] or 0
                
                estadisticas_por_tema.append({
                    'tema': tema.tema_id,
                    'nota_media': nota_media_tema,
                    'total_intentos': total_intentos_tema,
                    'mejor_puntuacion': mejor_puntuacion,
                })
        
        alumno_data['estadisticas_por_tema'] = estadisticas_por_tema
    
    # Agregar estadísticas generales por temas para mostrar al final
    estadisticas_temas = []
    for tema in temas:
        # Todos los intentos en tests de este tema (solo usuarios no-staff)
        from django.contrib.auth.models import User
        alumnos_no_staff = User.objects.filter(is_staff=False)
        
        intentos_tema = IntentTest.objects.filter(
            completado=True,
            test__tema=tema,
            alumno__in=alumnos_no_staff
        )
        
        if intentos_tema.exists():
            nota_media_tema = intentos_tema.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
            total_intentos_tema = intentos_tema.count()
            alumnos_participantes = intentos_tema.values('alumno').distinct().count()
            
            estadisticas_temas.append({
                'tema': tema.tema_id,
                'nota_media': nota_media_tema,
                'total_intentos': total_intentos_tema,
                'alumnos_participantes': alumnos_participantes,
            })
    
    context.update({
        'alumnos_detallados': alumnos_detallados,
        'estadisticas_temas': estadisticas_temas,
        'page_title': 'Progreso por Alumno'
    })
    
    return render(request, 'boards/profesor/progreso_alumnos.html', context)


@login_required
@user_passes_test(es_profesor, login_url='/')
def progreso_clase(request):
    """Vista de progreso general de toda la clase"""
    context = profesor_dashboard_data()
    
    # Agregar estadísticas por tema para toda la clase
    from boards.models import Tema
    temas = Tema.objects.exclude(tema_id='Exámenes').order_by('tema_id')
    
    estadisticas_temas = []
    for tema in temas:
        # Todos los intentos en tests de este tema (solo usuarios no-staff)
        from django.contrib.auth.models import User
        alumnos_no_staff = User.objects.filter(is_staff=False)
        
        intentos_tema = IntentTest.objects.filter(
            completado=True,
            test__tema=tema,
            alumno__in=alumnos_no_staff
        )
        
        if intentos_tema.exists():
            nota_media_tema = intentos_tema.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
            total_intentos_tema = intentos_tema.count()
            alumnos_participantes = intentos_tema.values('alumno').distinct().count()
            mejor_puntuacion = intentos_tema.aggregate(Max('puntuacion'))['puntuacion__max'] or 0
            peor_puntuacion = intentos_tema.aggregate(Min('puntuacion'))['puntuacion__min'] or 0
            
            # Total de preguntas en este tema
            total_preguntas_tema = Pregunta.objects.filter(tema=tema.tema_id).count()
            
            estadisticas_temas.append({
                'tema': tema.tema_id,
                'nota_media': nota_media_tema,
                'total_intentos': total_intentos_tema,
                'alumnos_participantes': alumnos_participantes,
                'mejor_puntuacion': mejor_puntuacion,
                'peor_puntuacion': peor_puntuacion,
                'total_preguntas': total_preguntas_tema,
            })
    
    context.update({
        'estadisticas_temas': estadisticas_temas,
        'page_title': 'Progreso por Clase'
    })
    
    return render(request, 'boards/profesor/progreso_clase.html', context)


@login_required
@user_passes_test(es_profesor, login_url='/')
def detalle_alumno(request, alumno_id):
    """Vista detallada individual de un alumno específico"""
    from django.contrib.auth.models import User
    from datetime import datetime, timedelta
    
    alumno = get_object_or_404(User, id=alumno_id, is_staff=False)
    
    # Estadísticas básicas del alumno
    intentos, promedio = get_student_stats(alumno)
    total_intentos = intentos.count()
    
    # Estadísticas por tema
    from boards.models import Tema, Pregunta
    temas = Tema.objects.exclude(tema_id='Exámenes').order_by('tema_id')
    
    estadisticas_por_tema = []
    for tema in temas:
        intentos_tema = intentos.filter(test__tema=tema)
        
        if intentos_tema.exists():
            nota_media_tema = intentos_tema.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
            total_intentos_tema = intentos_tema.count()
            mejor_puntuacion = intentos_tema.aggregate(Max('puntuacion'))['puntuacion__max'] or 0
            ultimo_intento = intentos_tema.first()  # Ya están ordenados por fecha
            
            estadisticas_por_tema.append({
                'tema': tema.tema_id,
                'nota_media': nota_media_tema,
                'total_intentos': total_intentos_tema,
                'mejor_puntuacion': mejor_puntuacion,
                'ultimo_intento': ultimo_intento,
            })
    
    # Timeline de actividad (últimos 30 días)
    hace_30_dias = datetime.now() - timedelta(days=30)
    intentos_recientes = intentos.filter(fecha_inicio__gte=hace_30_dias).order_by('fecha_inicio')
    
    # Determinar estado del alumno (riesgo/top/normal)
    estado_alumno = 'normal'
    if promedio >= 8.0:
        estado_alumno = 'top'
    elif promedio < 6.0 and total_intentos > 0:
        estado_alumno = 'riesgo'
    elif total_intentos == 0:
        estado_alumno = 'inactivo'
    
    # Posición en el ranking de la clase
    todos_promedios = IntentTest.objects.filter(
        completado=True, 
        alumno__is_staff=False
    ).values('alumno').annotate(
        promedio=Avg('puntuacion')
    ).order_by('-promedio')
    
    posicion_ranking = None
    for i, datos in enumerate(todos_promedios, 1):
        if datos['alumno'] == alumno.id:
            posicion_ranking = i
            break
    
    context = {
        'alumno': alumno,
        'intentos': intentos,
        'promedio': promedio,
        'total_intentos': total_intentos,
        'estadisticas_por_tema': estadisticas_por_tema,
        'intentos_recientes': intentos_recientes,
        'estado_alumno': estado_alumno,
        'posicion_ranking': posicion_ranking,
        'total_alumnos': User.objects.filter(is_staff=False).count(),
        'page_title': f'Detalle de {alumno.username}'
    }
    
    return render(request, 'boards/profesor/detalle_alumno.html', context)


@login_required
@user_passes_test(es_profesor, login_url='/')
def obtener_respuestas_pregunta(request, pregunta_id):
    """Obtiene las respuestas de una pregunta (para mostrar en modal de eliminar)"""
    from django.db import connection
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT Respuesta_ID, Contenido, Solucion
                FROM Respuesta
                WHERE Pregunta_ID = %s
                ORDER BY Respuesta_ID
            """, [pregunta_id])
            
            respuestas = []
            for row in cursor.fetchall():
                respuestas.append({
                    'id': row[0],
                    'texto': row[1],
                    'es_correcta': row[2] == 1 or row[2] == '1' or row[2] is True
                })
        
        return JsonResponse({
            'success': True,
            'respuestas': respuestas
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
