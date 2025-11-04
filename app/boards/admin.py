from django.contrib import admin
from .models import Question, Test, IntentTest, RespuestaAlumno


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['titulo_corto', 'tipo', 'dificultad', 'tema', 'activa', 'fecha_creacion']
    list_filter = ['tipo', 'dificultad', 'tema', 'activa', 'fecha_creacion']
    search_fields = ['titulo', 'tema']
    readonly_fields = ['creada_por', 'fecha_creacion', 'fecha_modificacion']
    
    fieldsets = (
        ('Información básica', {
            'fields': ('titulo', 'tipo', 'dificultad', 'tema', 'activa')
        }),
        ('Opciones (para opción múltiple)', {
            'fields': ('opcion_a', 'opcion_b', 'opcion_c', 'opcion_d'),
            'classes': ('collapse',)
        }),
        ('Respuesta', {
            'fields': ('respuesta_correcta', 'explicacion')
        }),
        ('Metadatos', {
            'fields': ('creada_por', 'fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
    
    def titulo_corto(self, obj):
        return obj.titulo[:50] + '...' if len(obj.titulo) > 50 else obj.titulo
    titulo_corto.short_description = 'Pregunta'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es una nueva pregunta
            obj.creada_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'total_preguntas_count', 'tiempo_limite', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    filter_horizontal = ['preguntas']
    readonly_fields = ['creado_por', 'fecha_creacion']
    
    fieldsets = (
        ('Información básica', {
            'fields': ('nombre', 'descripcion', 'tiempo_limite', 'activo')
        }),
        ('Preguntas', {
            'fields': ('preguntas',)
        }),
        ('Metadatos', {
            'fields': ('creado_por', 'fecha_creacion'),
            'classes': ('collapse',)
        }),
    )
    
    def total_preguntas_count(self, obj):
        return obj.total_preguntas()
    total_preguntas_count.short_description = 'N° Preguntas'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(IntentTest)
class IntentTestAdmin(admin.ModelAdmin):
    list_display = ['alumno', 'test', 'fecha_inicio', 'completado', 'puntuacion_display', 'respuestas_correctas_display']
    list_filter = ['completado', 'fecha_inicio', 'test']
    search_fields = ['alumno__username', 'test__nombre']
    readonly_fields = ['alumno', 'test', 'fecha_inicio', 'fecha_fin', 'puntuacion', 'total_preguntas', 'respuestas_correctas']
    
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
    search_fields = ['intento__alumno__username', 'pregunta__titulo']
    readonly_fields = ['intento', 'pregunta', 'respuesta', 'es_correcta', 'fecha_respuesta']
    
    def pregunta_corta(self, obj):
        return obj.pregunta.titulo[:40] + '...' if len(obj.pregunta.titulo) > 40 else obj.pregunta.titulo
    pregunta_corta.short_description = 'Pregunta'
