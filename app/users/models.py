from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Perfil de usuario extendido con preferencias"""
    MODO_CHOICES = [
        ('alumno', 'Modo Alumno'),
        ('profesor', 'Modo Profesor'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    modo_preferido = models.CharField(max_length=10, choices=MODO_CHOICES, default='alumno')
    no_preguntar_modo = models.BooleanField(default=False, help_text='No volver a preguntar el modo al entrar')
    grupo = models.CharField(max_length=50, blank=True, null=True, help_text='Grupo del alumno')
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
    
    def __str__(self):
        return f"Perfil de {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crear perfil automáticamente al crear un usuario"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Guardar perfil al guardar usuario"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
