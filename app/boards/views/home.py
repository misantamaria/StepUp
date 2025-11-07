"""
Vistas de navegación principal y gestión de modos.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def home(request):
    """Vista principal que redirige según el tipo de usuario y preferencias"""
    from users.models import UserProfile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Si el usuario estableció un modo en la sesión, usarlo
    if 'modo_actual' in request.session:
        modo = request.session['modo_actual']
        if modo == 'profesor' and request.user.is_staff:
            return redirect('boards:dashboard_profesor')
        else:
            # Asegurar que la sesión tenga modo_actual = alumno
            request.session['modo_actual'] = 'alumno'
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


@login_required
def seleccionar_modo(request):
    """Permite al usuario seleccionar su modo (profesor/alumno)"""
    if request.method == 'POST':
        modo = request.POST.get('modo', 'alumno')
        no_preguntar = request.POST.get('no_preguntar') == 'on'
        
        # Debug: verificar datos recibidos
        print(f" POST recibido - Modo: {modo}, No preguntar: {no_preguntar}, POST data: {request.POST}")
        
        # Validar modo
        if modo not in ['alumno', 'profesor']:
            messages.error(request, f'Modo inválido: {modo}')
            return render(request, 'boards/seleccionar_modo.html')
        
        # Guardar en sesión
        request.session['modo_actual'] = modo
        print(f" Modo guardado en sesión: {request.session.get('modo_actual')}")
        
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
            print(f" Redirigiendo a dashboard_profesor (user.is_staff={request.user.is_staff})")
            return redirect('boards:dashboard_profesor')
        else:
            print(f" Redirigiendo a dashboard_alumno (modo={modo}, is_staff={request.user.is_staff})")
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
    
    messages.success(request, 'Preferencia restablecida. Se te preguntará el modo en el próximo acceso.')
    return redirect('boards:home')
