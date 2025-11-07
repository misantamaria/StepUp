from django.urls import path
from . import views
from . import views_bdd
from .views import profesor

app_name = 'boards'

urlpatterns = [
    # Ruta principal
    path('', views.home, name='home'),
    
    # Gestión de modo
    path('seleccionar-modo/', views.seleccionar_modo, name='seleccionar_modo'),
    path('cambiar-modo/', views.cambiar_modo, name='cambiar_modo'),
    path('restablecer-preferencia/', views.restablecer_preferencia_modo, name='restablecer_preferencia'),
    
    # Rutas para alumnos
    path('alumno/', views.dashboard_alumno, name='dashboard_alumno'),
    path('alumno/seleccionar-modo/', views.seleccionar_modo_alumno, name='seleccionar_modo_alumno'),
    path('alumno/examen/iniciar/', views.iniciar_examen, name='iniciar_examen'),
    path('alumno/examen/cambiar-modo/', views.cambiar_modo_examen, name='cambiar_modo_examen'),
    path('alumno/examen/<int:intento_id>/', views.realizar_examen, name='realizar_examen'),
    path('alumno/progreso/', views.mi_progreso, name='mi_progreso'),
    path('alumno/progreso/temas/', views.estadisticas_temas, name='estadisticas_temas'),
    path('alumno/progreso/historial/', views.historial_intentos, name='historial_intentos'),
    path('alumno/tema/<str:tema_id>/', views.detalle_tema, name='detalle_tema'),
    path('alumno/tema/<str:tema_id>/<str:nivel>/', views.tests_nivel, name='tests_nivel'),
    path('alumno/test/<int:test_id>/iniciar/', views.iniciar_test, name='iniciar_test'),
    path('alumno/intento/<int:intento_id>/', views.realizar_test, name='realizar_test'),
    path('alumno/resultado/<int:intento_id>/', views.resultado_test, name='resultado_test'),
    
    # Rutas para profesores
    path('profesor/', views.dashboard_profesor, name='dashboard_profesor'),
    path('profesor/alumno/<int:alumno_id>/estadisticas/', views.estadisticas_alumno, name='estadisticas_alumno'),
    path('profesor/test/<int:test_id>/toggle-field/', views.toggle_test_field, name='toggle_test_field'),
    path('profesor/tema/<str:tema_id>/toggle-field/', views.toggle_tema_field, name='toggle_tema_field'),
    path('profesor/test/<int:test_id>/detalles/', views.get_test_details, name='get_test_details'),
    path('profesor/test/<int:test_id>/eliminar/', views.delete_test, name='delete_test'),
    path('profesor/tema/<str:tema_id>/eliminar/', views.delete_tema, name='delete_tema'),
    path('profesor/pregunta/<int:pregunta_id>/respuestas/', profesor.obtener_respuestas_pregunta, name='obtener_respuestas_pregunta'),
    
    # Rutas para crear mediante modales
    path('profesor/tema/crear/', views.crear_tema_modal, name='crear_tema_modal'),
    path('profesor/test/crear/', views.crear_test_modal, name='crear_test_modal'),
    path('profesor/pregunta/crear/', views.crear_pregunta_modal, name='crear_pregunta_modal'),
    
    # Rutas para editar mediante modales
    path('profesor/tema/<str:tema_id>/detalles/', views.get_tema_details, name='get_tema_details'),
    path('profesor/tema/<str:tema_id>/actualizar/', views.update_tema, name='update_tema'),
    path('profesor/test/<int:test_id>/obtener/', views.get_test_data, name='get_test_data'),
    path('profesor/test/<int:test_id>/actualizar/', views.update_test, name='update_test'),
    path('profesor/pregunta/<int:pregunta_id>/obtener/', views.get_pregunta_data, name='get_pregunta_data'),
    path('profesor/pregunta/<int:pregunta_id>/actualizar/', views.update_pregunta, name='update_pregunta'),
    
    # Rutas para gestión de preguntas desde BDD
    path('profesor/preguntas/', views_bdd.listar_preguntas, name='listar_preguntas_bdd'),
    path('profesor/preguntas/crear/', views_bdd.crear_pregunta_view, name='crear_pregunta_bdd'),
    path('profesor/preguntas/<int:pregunta_id>/editar/', views_bdd.editar_pregunta_view, name='editar_pregunta_bdd'),
    path('profesor/preguntas/<int:pregunta_id>/eliminar/', views_bdd.eliminar_pregunta_view, name='eliminar_pregunta_bdd'),
    path('profesor/preguntas/<int:pregunta_id>/detalle/', views_bdd.ver_pregunta_detalle, name='detalle_pregunta_bdd'),
]
