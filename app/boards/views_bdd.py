"""
Vistas para gestionar preguntas directamente desde las tablas de la base de datos
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .bdd_adapter import (
    get_all_temas,
    get_preguntas_por_tema,
    get_pregunta_con_respuestas,
    get_estadisticas_preguntas,
    crear_pregunta,
    actualizar_pregunta,
    eliminar_pregunta
)


def es_profesor(user):
    """Verifica si el usuario es profesor o admin"""
    return user.is_staff


@login_required
@user_passes_test(es_profesor, login_url='/')
def listar_preguntas(request):
    """Lista todas las preguntas agrupadas por tema"""
    temas = get_all_temas()
    tema_seleccionado = request.GET.get('tema')
    
    preguntas = []
    if tema_seleccionado:
        preguntas = get_preguntas_por_tema(tema_seleccionado)
    
    context = {
        'temas': temas,
        'tema_seleccionado': tema_seleccionado,
        'preguntas': preguntas,
        'stats': get_estadisticas_preguntas()
    }
    return render(request, 'boards/profesor/preguntas_bdd.html', context)


@login_required
@user_passes_test(es_profesor, login_url='/')
def crear_pregunta_view(request):
    """Crea una nueva pregunta con sus respuestas"""
    if request.method == 'POST':
        tema = request.POST.get('tema')
        enunciado = request.POST.get('enunciado')
        dificultad = request.POST.get('dificultad', 'Media')
        puntuacion = int(request.POST.get('puntuacion', 1))
        
        # Procesar respuestas
        respuestas = []
        for i in range(1, 5):  # Máximo 4 respuestas
            contenido = request.POST.get(f'respuesta_{i}')
            if contenido:
                es_correcta = request.POST.get(f'correcta_{i}') == 'on'
                respuestas.append({
                    'contenido': contenido,
                    'es_correcta': es_correcta
                })
        
        if not respuestas:
            messages.error(request, 'Debes agregar al menos una respuesta')
            return redirect('boards:crear_pregunta_bdd')
        
        if not any(r['es_correcta'] for r in respuestas):
            messages.error(request, 'Debes marcar al menos una respuesta como correcta')
            return redirect('boards:crear_pregunta_bdd')
        
        try:
            pregunta_id = crear_pregunta(tema, enunciado, dificultad, puntuacion, respuestas)
            messages.success(request, f'Pregunta #{pregunta_id} creada exitosamente')
            return redirect('boards:listar_preguntas_bdd')
        except Exception as e:
            messages.error(request, f'Error al crear pregunta: {str(e)}')
    
    context = {
        'temas': get_all_temas(),
        'dificultades': ['Facil', 'Media', 'Dificil']
    }
    return render(request, 'boards/profesor/crear_pregunta_bdd.html', context)


@login_required
@user_passes_test(es_profesor, login_url='/')
def editar_pregunta_view(request, pregunta_id):
    """Edita una pregunta existente"""
    pregunta = get_pregunta_con_respuestas(pregunta_id)
    if not pregunta:
        messages.error(request, 'Pregunta no encontrada')
        return redirect('boards:listar_preguntas_bdd')
    
    if request.method == 'POST':
        enunciado = request.POST.get('enunciado')
        dificultad = request.POST.get('dificultad')
        puntuacion = int(request.POST.get('puntuacion'))
        
        try:
            actualizar_pregunta(pregunta_id, enunciado, dificultad, puntuacion)
            messages.success(request, 'Pregunta actualizada exitosamente')
            return redirect('boards:listar_preguntas_bdd')
        except Exception as e:
            messages.error(request, f'Error al actualizar pregunta: {str(e)}')
    
    context = {
        'pregunta': pregunta,
        'dificultades': ['Facil', 'Media', 'Dificil']
    }
    return render(request, 'boards/profesor/editar_pregunta_bdd.html', context)


@login_required
@user_passes_test(es_profesor, login_url='/')
@require_http_methods(["POST"])
def eliminar_pregunta_view(request, pregunta_id):
    """Elimina una pregunta"""
    # Solo profesores completos y admins pueden eliminar
    if not (request.user.is_superuser or request.user.groups.filter(name='Profesores').exists()):
        messages.error(request, 'No tienes permisos para eliminar preguntas')
        return redirect('boards:listar_preguntas_bdd')
    
    try:
        eliminar_pregunta(pregunta_id)
        messages.success(request, f'Pregunta #{pregunta_id} eliminada exitosamente')
    except Exception as e:
        messages.error(request, f'Error al eliminar pregunta: {str(e)}')
    
    return redirect('boards:listar_preguntas_bdd')


@login_required
@user_passes_test(es_profesor, login_url='/')
def ver_pregunta_detalle(request, pregunta_id):
    """Ver detalles de una pregunta en formato JSON"""
    pregunta = get_pregunta_con_respuestas(pregunta_id)
    if not pregunta:
        return JsonResponse({'error': 'Pregunta no encontrada'}, status=404)
    
    return JsonResponse(pregunta)
