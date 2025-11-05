from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ['modo_preferido', 'no_preguntar_modo']
    
    def get_queryset(self, request):
        """Asegurar que siempre haya un perfil"""
        qs = super().get_queryset(request)
        return qs
    
    def has_add_permission(self, request, obj=None):
        """Prevenir creación manual si ya existe perfil (por la señal)"""
        return False


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    
    def save_related(self, request, form, formsets, change):
        """Asegurar que el perfil exista antes de guardar el inline"""
        super().save_related(request, form, formsets, change)
        # La señal ya crea el perfil, así que solo lo obtenemos
        if hasattr(form.instance, 'profile'):
            # El perfil ya existe por la señal
            pass
        else:
            # Por si acaso la señal no se ejecutó, crearlo manualmente
            UserProfile.objects.get_or_create(user=form.instance)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'modo_preferido', 'no_preguntar_modo']
    list_filter = ['modo_preferido', 'no_preguntar_modo']
    search_fields = ['user__username', 'user__email']
