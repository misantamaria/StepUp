"""
Decoradores personalizados para controlar el acceso a las vistas.
"""
from functools import wraps
from django.shortcuts import redirect


def es_alumno(user):
    """Verifica si el usuario es alumno (no es staff)"""
    return not user.is_staff


def es_profesor(user):
    """Verifica si el usuario es profesor (staff o superuser)"""
    return user.is_staff or user.is_superuser


def modo_requerido(modo):
    """
    Decorador que verifica que el usuario esté en el modo correcto.
    
    Args:
        modo: 'alumno' o 'profesor'
    
    Uso:
        @modo_requerido('profesor')
        def vista_profesor(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            modo_actual = request.session.get('modo_actual')
            
            # Si el modo requerido es profesor, verificar permisos
            if modo == 'profesor' and not es_profesor(request.user):
                return redirect('boards:home')
            
            # Si no hay modo en sesión, redirigir a selección
            if not modo_actual and request.user.is_staff:
                return redirect('boards:seleccionar_modo')
            
            # Si el modo actual no coincide, redirigir
            if modo_actual != modo and request.user.is_staff:
                # Permitir que profesores vean ambos modos
                pass
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
