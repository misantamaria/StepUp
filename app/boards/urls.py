from django.urls import path
from . import views

app_name = 'boards'

urlpatterns = [
    # Ruta principal
    path('', views.home, name='home'),
    
    # Rutas para alumnos
    path('alumno/', views.dashboard_alumno, name='dashboard_alumno'),
    path('alumno/test/<int:test_id>/iniciar/', views.iniciar_test, name='iniciar_test'),
    path('alumno/intento/<int:intento_id>/', views.realizar_test, name='realizar_test'),
    path('alumno/resultado/<int:intento_id>/', views.resultado_test, name='resultado_test'),
    
    # Rutas para profesores
    path('profesor/', views.dashboard_profesor, name='dashboard_profesor'),
    path('profesor/alumno/<int:alumno_id>/estadisticas/', views.estadisticas_alumno, name='estadisticas_alumno'),
]
