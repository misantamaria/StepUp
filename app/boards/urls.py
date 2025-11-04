from django.urls import path
from . import views
from . import views_bdd

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
    path('alumno/test/<int:test_id>/iniciar/', views.iniciar_test, name='iniciar_test'),
    path('alumno/intento/<int:intento_id>/', views.realizar_test, name='realizar_test'),
    path('alumno/resultado/<int:intento_id>/', views.resultado_test, name='resultado_test'),
    
    # Rutas para profesores
    path('profesor/', views.dashboard_profesor, name='dashboard_profesor'),
    path('profesor/alumno/<int:alumno_id>/estadisticas/', views.estadisticas_alumno, name='estadisticas_alumno'),
    
    # Rutas para gestión de preguntas desde BDD
    path('profesor/preguntas/', views_bdd.listar_preguntas, name='listar_preguntas_bdd'),
    path('profesor/preguntas/crear/', views_bdd.crear_pregunta_view, name='crear_pregunta_bdd'),
    path('profesor/preguntas/<int:pregunta_id>/editar/', views_bdd.editar_pregunta_view, name='editar_pregunta_bdd'),
    path('profesor/preguntas/<int:pregunta_id>/eliminar/', views_bdd.eliminar_pregunta_view, name='eliminar_pregunta_bdd'),
    path('profesor/preguntas/<int:pregunta_id>/detalle/', views_bdd.ver_pregunta_detalle, name='detalle_pregunta_bdd'),
]
