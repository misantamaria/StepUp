from django.utils import timezone
from django.db.models import Avg, Count
from typing import Dict, Any, List
from collections import defaultdict

from boards.models import Test, IntentTest, RespuestaAlumno, Tema, ProgresoTema, Pregunta, Respuesta


def get_dashboard_data(user, modo_test=False) -> Dict[str, Any]:
    """Datos para el dashboard del alumno - organizado por temas.
    
    Args:
        user: Usuario actual
        modo_test: Si True, el profesor ve TODOS los temas disponibles para él (visibles o no)
                   para poder testear. Los no visibles aparecen bloqueados/grises.
    """
    # Determinar si el usuario es staff (profesor en modo alumno)
    es_profesor = user.is_staff
    
    # Obtener temas según el modo
    if es_profesor and modo_test:
        # MODO TEST: Mostrar TODOS los temas disponibles para profesor (visibles o no)
        # Esto permite ver qué hay en borrador vs qué está publicado
        # EXCLUIR siempre el tema "Exámenes" que es solo para modo examen
        temas_base = Tema.objects.filter(
            activo=True,
            disponible_profesor=True
        ).exclude(tema_id="Exámenes").prefetch_related('tests').order_by('tema_id')
    else:
        # MODO ALUMNO NORMAL: Mostrar TODOS los temas disponibles (incluidos no visibles)
        # Esto permite mostrar temas bloqueados secuencialmente con indicadores visuales
        # EXCLUIR siempre el tema "Exámenes" que es solo para modo examen
        temas_base = Tema.objects.filter(
            activo=True, 
            disponible_alumno=True
        ).exclude(tema_id="Exámenes").prefetch_related('tests').order_by('tema_id')
    
    # APLICAR LÓGICA SECUENCIAL: Mostrar TODOS los temas con indicadores de bloqueo
    # Tanto alumnos como profesores pueden ver todos los temas para progreso visual
    temas_disponibles = list(temas_base)
    
    # Organizar tests por tema
    tests_por_tema = []
    for tema in temas_disponibles:
        # En modo test, verificar si el tema está visible o solo disponible
        tema_visible = True
        if es_profesor and modo_test:
            tema_visible = tema.visible_profesor
        
        # Obtener o crear el progreso del tema para este alumno
        progreso, created = ProgresoTema.objects.get_or_create(
            alumno=user,
            tema=tema
        )
        
        # Si se creó, inicializar el progreso
        if created:
            progreso.total_preguntas = Pregunta.objects.filter(tema=tema.tema_id).count()
            progreso.save()
        
        # Obtener tests del tema que están activos
        # En modo test, mostrar tests con disponible_profesor=True
        # En modo normal (profesor o alumno), mostrar tests con visible_alumnos=True AND disponible_alumno=True
        if es_profesor and modo_test:
            tests_del_tema = tema.tests.filter(activo=True, disponible_profesor=True)
        else:
            tests_del_tema = tema.tests.filter(activo=True, visible_alumnos=True, disponible_alumno=True)
        
        # Filtrar tests según requisitos del alumno y organizar por nivel
        tests_por_nivel = {
            'Facil': [],
            'Media': [],
            'Dificil': [],
        }
        
        for test in tests_del_tema:
            if test.alumno_cumple_requisitos(user):
                tests_por_nivel[test.nivel].append(test)
        
        # Calcular tests disponibles totales
        tests_disponibles = (
            tests_por_nivel['Facil'] +
            tests_por_nivel['Media'] +
            tests_por_nivel['Dificil']
        )
        
        # Actualizar el progreso si hay tests completados
        if tests_disponibles:
            progreso.actualizar_progreso()
        
        tiene_tests_visibles = len(tests_disponibles) > 0
        
        # Determinar si el tema está bloqueado secuencialmente
        bloqueado_secuencial = False
        motivo_bloqueo = None
        
        # Verificar bloqueo secuencial - SOLO para alumnos
        # Los profesores en modo test pueden acceder a cualquier tema
        tema_index = list(temas_base).index(tema)
        if tema_index > 0 and not (es_profesor and modo_test):
            # Verificar si el tema anterior está completado
            tema_anterior = list(temas_base)[tema_index - 1]
            progreso_anterior, _ = ProgresoTema.objects.get_or_create(
                alumno=user,
                tema=tema_anterior,
                defaults={'total_preguntas': Pregunta.objects.filter(tema=tema_anterior.tema_id).count()}
            )
            progreso_anterior.actualizar_progreso()
            
            if not progreso_anterior.completado:
                bloqueado_secuencial = True
                # Solo asignar motivo secuencial si el tema ES visible para alumnos
                if tema.visible_alumnos:
                    motivo_bloqueo = f"Completa el tema '{tema_anterior.tema_id}' primero"
        
        # Determinar bloqueo final
        bloqueado = not tiene_tests_visibles or bloqueado_secuencial
        
        # Para ALUMNOS: Si el tema no es visible (temas 4, 5, 6), usar mensaje docente
        if not es_profesor and not tema.visible_alumnos:
            bloqueado = True
            motivo_bloqueo = "Próximamente disponible"
        
        # Para PROFESORES en modo test: Permitir acceso a todos los temas visibles
        if es_profesor and modo_test and tema_visible:
            bloqueado = False
            motivo_bloqueo = None
        
        # En modo test para profesores, marcar como bloqueado si el tema NO es visible (aunque sea disponible)
        if es_profesor and modo_test and not tema_visible:
            bloqueado = True
        
        tests_por_tema.append({
            'tema': tema,
            'progreso': progreso,
            'tests': tests_disponibles,
            'tests_por_nivel': tests_por_nivel,
            'tiene_tests_visibles': tiene_tests_visibles,
            'bloqueado': bloqueado,
            'bloqueado_secuencial': bloqueado_secuencial,
            'motivo_bloqueo': motivo_bloqueo,
            'tema_visible': tema_visible,  # Nuevo: indica si el tema está visible o solo disponible
        })
    
    # Últimos intentos del alumno
    intentos_previos = IntentTest.objects.filter(
        alumno=user
    ).select_related('test', 'test__tema').order_by('-fecha_inicio')[:10]
    
    # Estadísticas generales
    total_intentos = IntentTest.objects.filter(alumno=user, completado=True).count()
    promedio_puntuacion = (
        IntentTest.objects.filter(alumno=user, completado=True)
        .aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
    )
    
    # Convertir promedio a nota del 1 al 10
    promedio_nota = (promedio_puntuacion / 10) if promedio_puntuacion > 0 else 0
    
    # Calcular progreso como % de tests completados
    tests_disponibles_total = Test.objects.filter(activo=True, visible_alumnos=True).count()
    tests_completados = IntentTest.objects.filter(
        alumno=user,
        completado=True
    ).values('test').distinct().count()
    progreso_tests = (tests_completados / tests_disponibles_total * 100) if tests_disponibles_total > 0 else 0
    
    return {
        'tests_por_tema': tests_por_tema,
        'intentos_previos': intentos_previos,
        'total_intentos': total_intentos,
        'promedio_puntuacion': promedio_puntuacion,
        'promedio_nota': promedio_nota,
        'progreso_tests': progreso_tests,
        'tests_completados': tests_completados,
        'tests_disponibles_total': tests_disponibles_total,
    }


def start_test(user, test: Test) -> IntentTest:
    """Crea un nuevo intento para el usuario en el test dado."""
    intento = IntentTest.objects.create(
        alumno=user,
        test=test,
        total_preguntas=test.total_preguntas(),
    )
    return intento


def grade_attempt(intento: IntentTest, post_data) -> IntentTest:
    """Corrige un intento con los datos del formulario y actualiza métricas."""
    if intento.completado:
        return intento

    preguntas = intento.test.preguntas.all()
    respuestas_correctas = 0

    for pregunta in preguntas:
        respuesta_key = f'pregunta_{pregunta.pregunta_id}'
        respuesta_id = post_data.get(respuesta_key, '')
        
        if not respuesta_id:
            continue

        try:
            # Obtener la respuesta seleccionada por el alumno
            respuesta_obj = Respuesta.objects.get(
                pregunta_id=pregunta.pregunta_id,
                respuesta_id=respuesta_id
            )
            
            # Verificar si es correcta
            es_correcta = respuesta_obj.solucion == 'Correcta'
            
            if es_correcta:
                respuestas_correctas += 1

            # Guardar la respuesta del alumno
            RespuestaAlumno.objects.create(
                intento=intento,
                pregunta=pregunta,
                respuesta=str(respuesta_id),
                es_correcta=es_correcta,
            )
        except Respuesta.DoesNotExist:
            # Si no existe la respuesta, marcar como incorrecta
            RespuestaAlumno.objects.create(
                intento=intento,
                pregunta=pregunta,
                respuesta=str(respuesta_id),
                es_correcta=False,
            )

    intento.respuestas_correctas = respuestas_correctas
    intento.completado = True
    intento.fecha_fin = timezone.now()
    intento.calcular_puntuacion()
    intento.save(update_fields=['respuestas_correctas', 'completado', 'fecha_fin', 'puntuacion'])
    
    # Actualizar el progreso del tema
    if intento.test.tema:
        progreso, created = ProgresoTema.objects.get_or_create(
            alumno=intento.alumno,
            tema=intento.test.tema
        )
        progreso.actualizar_progreso()
    
    return intento
