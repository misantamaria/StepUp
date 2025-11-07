from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import os


@login_required
def dashboard(request):
    """Vista principal para usuarios autenticados"""
    return render(request, 'users/dashboard.html', {
        'user': request.user
    })


def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    return redirect('/accounts/login/')


@login_required
def create_user_with_email(request):
    """Vista para crear usuarios con email y enviar notificación"""
    # Solo admin puede crear usuarios
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para crear usuarios')
        return redirect('users:dashboard')
    
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        
        # Mapeo de emails desde variables de entorno
        email_map = {
            'admin': os.getenv('ADMIN_EMAIL', 'admin@example.com'),
            'macu': os.getenv('MACU_EMAIL', 'macu@example.com'),
        }
        
        # Usar email del mapeo si coincide, sino usar el proporcionado
        final_email = email_map.get(username, email)
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f'El usuario {username} ya existe')
        else:
            # Crear usuario sin contraseña (debe establecerla por email)
            user = User.objects.create_user(username=username, email=final_email)
            user.set_unusable_password()  # No puede hacer login hasta establecer contraseña
            user.save()
            
            try:
                # Enviar email de bienvenida
                subject = f'Bienvenido a StepUp - {username}'
                message = f'''Hola {username},

Tu cuenta en StepUp ha sido creada.

Para establecer tu contraseña, visita:
{request.build_absolute_uri('/accounts/password_reset/')}

Usuario: {username}
Email: {final_email}

Saludos,
El equipo de StepUp
'''
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [final_email]
                
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                
                messages.success(request, f''' Usuario {username} creado correctamente. 
📧 Email de bienvenida enviado a {final_email}
📬 Revisa tu bandeja de entrada (y carpeta de spam)''')
                    
            except Exception as e:
                messages.error(request, f'Usuario creado pero error enviando email: {e}')
    
    # Obtener todos los usuarios para mostrar
    users = User.objects.all()
    
    return render(request, 'users/create_user.html', {
        'users': users
    })
