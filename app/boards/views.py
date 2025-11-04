from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Count
from django.http import JsonResponse
from .models import Test, IntentTest, RespuestaAlumno, Tema, Pregunta
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
    """Vista principal que redirige según el tipo de usuario y preferencias"""
    # Obtener o crear perfil
    from users.models import UserProfile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Si el usuario estableció un modo en la sesión, usarlo
    if 'modo_actual' in request.session:
        modo = request.session['modo_actual']
        if modo == 'profesor' and request.user.is_staff:
            return redirect('boards:dashboard_profesor')
        else:
            return redirect('boards:dashboard_alumno')
    
    # Si el usuario marcó "no preguntar", usar su preferencia
    if profile.no_preguntar_modo:
        if profile.modo_preferido == 'profesor' and request.user.is_staff:
            request.session['modo_actual'] = 'profesor'
            return redirect('boards:dashboard_profesor')
        else:
            request.session['modo_actual'] = 'alumno'
            return redirect('boards:dashboard_alumno')
    
    # Si es staff (incluye superusers), mostrar selector de modo
    if request.user.is_staff:
        return render(request, 'boards/seleccionar_modo.html')
    
    # Si es alumno regular, ir directo al dashboard de alumno
    request.session['modo_actual'] = 'alumno'
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


# ==================== VISTAS DE GESTIÓN DE MODO ====================

@login_required
def seleccionar_modo(request):
    """Permite al usuario seleccionar su modo (profesor/alumno)"""
    if request.method == 'POST':
        modo = request.POST.get('modo', 'alumno')
        no_preguntar = request.POST.get('no_preguntar') == 'on'
        
        # Debug: verificar datos recibidos
        print(f"🔍 POST recibido - Modo: {modo}, No preguntar: {no_preguntar}, POST data: {request.POST}")
        
        # Validar modo
        if modo not in ['alumno', 'profesor']:
            from django.contrib import messages
            messages.error(request, f'Modo inválido: {modo}')
            return render(request, 'boards/seleccionar_modo.html')
        
        # Guardar en sesión
        request.session['modo_actual'] = modo
        print(f"✅ Modo guardado en sesión: {request.session.get('modo_actual')}")
        
        # Guardar preferencia si lo solicitó
        if no_preguntar:
            from users.models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.modo_preferido = modo
            profile.no_preguntar_modo = True
            profile.save()
            print(f"💾 Preferencia guardada en perfil: modo={modo}, no_preguntar=True")
        
        # Redirigir al dashboard correspondiente
        if modo == 'profesor' and request.user.is_staff:
            print(f"🎓 Redirigiendo a dashboard_profesor (user.is_staff={request.user.is_staff})")
            return redirect('boards:dashboard_profesor')
        else:
            print(f"📚 Redirigiendo a dashboard_alumno (modo={modo}, is_staff={request.user.is_staff})")
            return redirect('boards:dashboard_alumno')
    
    return render(request, 'boards/seleccionar_modo.html')


@login_required
def cambiar_modo(request):
    """Cambia entre modo profesor y alumno"""
    modo_actual = request.session.get('modo_actual', 'alumno')
    
    if request.user.is_staff:
        # Alternar entre modos
        nuevo_modo = 'alumno' if modo_actual == 'profesor' else 'profesor'
        request.session['modo_actual'] = nuevo_modo
        
        # Actualizar preferencia si existe
        from users.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        if profile.no_preguntar_modo:
            profile.modo_preferido = nuevo_modo
            profile.save()
        
        messages.success(request, f'Cambiado a modo {nuevo_modo.title()}')
        
        # Redirigir al dashboard correspondiente
        if nuevo_modo == 'profesor':
            return redirect('boards:dashboard_profesor')
        else:
            return redirect('boards:dashboard_alumno')
    
    # Si no es staff, solo puede estar en modo alumno
    return redirect('boards:dashboard_alumno')


@login_required
def restablecer_preferencia_modo(request):
    """Restablece la preferencia de modo para que vuelva a preguntar"""
    from users.models import UserProfile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    profile.no_preguntar_modo = False
    profile.save()
    
    # Limpiar sesión
    if 'modo_actual' in request.session:
        del request.session['modo_actual']
    
    messages.success(request, 'Preferencia restablecida. Se preguntará el modo la próxima vez.')
    return redirect('boards:home')