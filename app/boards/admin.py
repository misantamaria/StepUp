from django.contrib import admin
from django.utils.html import format_html
from .models import Pregunta, Respuesta, Tema, IntentTest, RespuestaAlumno, Test, ProgresoTema


# Modelos de la BDD (editables desde admin)
@admin.register(Tema)
class TemaAdmin(admin.ModelAdmin):
    list_display = ['tema_id', 'total_preguntas', 'total_tests']
    search_fields = ['tema_id']
    fields = ['tema_id']
    
    def total_preguntas(self, obj):
        return Pregunta.objects.filter(tema=obj.tema_id).count()
    total_preguntas.short_description = 'N° Preguntas'
    
    def total_tests(self, obj):
        return obj.tests.count()
    total_tests.short_description = 'N° Tests'
    
    def has_delete_permission(self, request, obj=None):
        """Solo profesores completos y admins pueden eliminar temas"""
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Profesores').exists():
            return True
        return False
    
    def has_change_permission(self, request, obj=None):
        """Admins, profesores y profesores ayudantes pueden editar"""
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name__in=['Profesores', 'Profesores Ayudantes']).exists():
            return True
        return False
    
    def has_add_permission(self, request):
        """Admins, profesores y profesores ayudantes pueden crear"""
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name__in=['Profesores', 'Profesores Ayudantes']).exists():
            return True
        return False


@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    list_display = ['pregunta_id', 'enunciado_corto', 'tema', 'dificultad', 'puntuacion']
    list_filter = ['dificultad', 'tema']
    search_fields = ['enunciado', 'tema']
    fields = ['pregunta_id', 'tema', 'enunciado', 'dificultad', 'puntuacion']
    
    def enunciado_corto(self, obj):
        return obj.enunciado[:50] + '...' if len(obj.enunciado) > 50 else obj.enunciado
    enunciado_corto.short_description = 'Enunciado'
    
    def has_delete_permission(self, request, obj=None):
        """Solo profesores completos y admins pueden eliminar preguntas"""
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Profesores').exists():
            return True
        return False
    
    def has_change_permission(self, request, obj=None):
        """Admins, profesores y profesores ayudantes pueden editar"""
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name__in=['Profesores', 'Profesores Ayudantes']).exists():
            return True
        return False
    
    def has_add_permission(self, request):
        """Admins, profesores y profesores ayudantes pueden crear"""
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name__in=['Profesores', 'Profesores Ayudantes']).exists():
            return True
        return False


@admin.register(Respuesta)
class RespuestaAdmin(admin.ModelAdmin):
    list_display = ['respuesta_id', 'pregunta_id', 'contenido_corto', 'solucion']
    list_filter = ['solucion', 'pregunta_id']
    search_fields = ['contenido']
    fields = ['respuesta_id', 'pregunta_id', 'solucion', 'contenido']
    
    def contenido_corto(self, obj):
        return obj.contenido[:30] + '...' if len(obj.contenido) > 30 else obj.contenido
    contenido_corto.short_description = 'Contenido'
    
    def has_delete_permission(self, request, obj=None):
        """Solo profesores completos y admins pueden eliminar respuestas"""
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Profesores').exists():
            return True
        return False
    
    def has_change_permission(self, request, obj=None):
        """Admins, profesores y profesores ayudantes pueden editar"""
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name__in=['Profesores', 'Profesores Ayudantes']).exists():
            return True
        return False
    
    def has_add_permission(self, request):
        """Admins, profesores y profesores ayudantes pueden crear"""
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name__in=['Profesores', 'Profesores Ayudantes']).exists():
            return True
        return False


# Modelo Test (temporal - usa Question antiguo)
@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tema', 'total_preguntas_count', 'visible_alumnos', 'tiempo_limite', 'activo', 'fecha_creacion']
    list_filter = ['tema', 'visible_alumnos', 'activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion', 'tema__tema_id']
    filter_horizontal = ['preguntas']
    readonly_fields = ['creado_por', 'fecha_creacion']
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'tema')
        }),
        ('Configuración', {
            'fields': ('tiempo_limite', 'visible_alumnos', 'activo')
        }),
        ('Preguntas', {
            'fields': ('preguntas',),
            'description': 'Selecciona las preguntas para este test, o deja vacío para incluir automáticamente todas las preguntas del tema.'
        }),
        ('Metadata', {
            'fields': ('creado_por', 'fecha_creacion'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['marcar_visible', 'marcar_no_visible', 'agregar_todas_preguntas_tema']
    
    def total_preguntas_count(self, obj):
        return obj.total_preguntas()
    total_preguntas_count.short_description = 'N° Preguntas'
    
    def marcar_visible(self, request, queryset):
        count = queryset.update(visible_alumnos=True)
        self.message_user(request, f'{count} tests marcados como visibles para alumnos.')
    marcar_visible.short_description = 'Marcar como visible para alumnos'
    
    def marcar_no_visible(self, request, queryset):
        count = queryset.update(visible_alumnos=False)
        self.message_user(request, f'{count} tests marcados como NO visibles para alumnos.')
    marcar_no_visible.short_description = 'Marcar como NO visible para alumnos'
    
    def agregar_todas_preguntas_tema(self, request, queryset):
        total = 0
        for test in queryset:
            if test.tema:
                count = test.agregar_preguntas_tema()
                total += count
        self.message_user(request, f'Se agregaron {total} preguntas a los tests seleccionados.')
    agregar_todas_preguntas_tema.short_description = 'Agregar todas las preguntas del tema'
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name='Profesores').exists()
    
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name__in=['Profesores', 'Profesores Ayudantes']).exists()
    
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name__in=['Profesores', 'Profesores Ayudantes']).exists()
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)
        
        # Si no tiene preguntas seleccionadas y tiene tema, agregar automáticamente
        if obj.tema and obj.preguntas.count() == 0:
            obj.agregar_preguntas_tema()


# Modelos de seguimiento de intentos (no relacionados con Question/Test antiguos)
@admin.register(IntentTest)
class IntentTestAdmin(admin.ModelAdmin):
    list_display = ['alumno', 'test', 'fecha_inicio', 'completado', 'puntuacion_display', 'respuestas_correctas_display']
    list_filter = ['completado', 'fecha_inicio', 'test']
    search_fields = ['alumno__username', 'test__nombre']
    readonly_fields = ['alumno', 'test', 'fecha_inicio', 'fecha_fin', 'puntuacion', 'total_preguntas', 'respuestas_correctas']
    
    def has_add_permission(self, request):
        """Nadie puede crear intentos desde el admin (se crean automáticamente)"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Solo admins pueden eliminar intentos"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Solo admins pueden modificar intentos"""
        return request.user.is_superuser
    
    def puntuacion_display(self, obj):
        return f"{obj.puntuacion:.1f}%"
    puntuacion_display.short_description = 'Puntuación'
    
    def respuestas_correctas_display(self, obj):
        return f"{obj.respuestas_correctas}/{obj.total_preguntas}"
    respuestas_correctas_display.short_description = 'Correctas'


@admin.register(RespuestaAlumno)
class RespuestaAlumnoAdmin(admin.ModelAdmin):
    list_display = ['intento', 'pregunta_corta', 'respuesta', 'es_correcta', 'fecha_respuesta']
    list_filter = ['es_correcta', 'fecha_respuesta']
    search_fields = ['intento__alumno__username', 'pregunta__enunciado']
    readonly_fields = ['intento', 'pregunta', 'respuesta', 'es_correcta', 'fecha_respuesta']
    
    def has_add_permission(self, request):
        """Nadie puede crear respuestas desde el admin (se crean automáticamente)"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Solo admins pueden eliminar respuestas"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Solo admins pueden modificar respuestas"""
        return request.user.is_superuser
    
    def pregunta_corta(self, obj):
        return obj.pregunta.enunciado[:40] + '...' if len(obj.pregunta.enunciado) > 40 else obj.pregunta.enunciado
    pregunta_corta.short_description = 'Pregunta'


@admin.register(ProgresoTema)
class ProgresoTemaAdmin(admin.ModelAdmin):
    list_display = ['alumno', 'tema', 'barra_progreso', 'porcentaje_aciertos_display', 'completado_icon', 'fecha_ultima_actividad']
    list_filter = ['completado', 'tema', 'fecha_ultima_actividad']
    search_fields = ['alumno__username', 'tema__tema_id']
    readonly_fields = ['alumno', 'tema', 'total_preguntas', 'preguntas_respondidas', 'preguntas_correctas', 
                       'porcentaje_completado', 'porcentaje_aciertos', 'completado', 
                       'fecha_inicio', 'fecha_ultima_actividad', 'fecha_completado']
    
    fieldsets = (
        ('Información', {
            'fields': ('alumno', 'tema')
        }),
        ('Progreso', {
            'fields': ('total_preguntas', 'preguntas_respondidas', 'preguntas_correctas', 
                      'porcentaje_completado', 'porcentaje_aciertos')
        }),
        ('Estado', {
            'fields': ('completado', 'fecha_inicio', 'fecha_ultima_actividad', 'fecha_completado')
        }),
    )
    
    def has_add_permission(self, request):
        """Se crea automáticamente"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Solo admins pueden eliminar"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Solo para lectura"""
        return True
    
    def barra_progreso(self, obj):
        """Muestra una barra de progreso visual"""
        porcentaje = int(obj.porcentaje_completado)
        porcentaje_texto = f"{obj.porcentaje_completado:.0f}"
        color = '#28a745' if obj.completado else '#007bff'
        if porcentaje < 30:
            color = '#dc3545'
        elif porcentaje < 70:
            color = '#ffc107'
        
        return format_html(
            '<div style="width:100px; height:20px; border:1px solid #ccc; border-radius:3px; background:#f8f9fa;">'
            '<div style="width:{0}%; height:100%; background:{1}; border-radius:2px;"></div>'
            '</div>'
            '<span style="margin-left:5px;">{2}%</span>',
            porcentaje, color, porcentaje_texto
        )
    barra_progreso.short_description = 'Progreso'
    
    def porcentaje_aciertos_display(self, obj):
        return f"{obj.porcentaje_aciertos:.1f}%"
    porcentaje_aciertos_display.short_description = '% Aciertos'
    
    def completado_icon(self, obj):
        if obj.completado:
            return format_html('<span style="color:green; font-size:18px;">✓</span>')
        return format_html('<span style="color:#ccc;">○</span>')
    completado_icon.short_description = 'Completado'
