from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Question(models.Model):
    """Modelo para preguntas de test"""
    TIPO_CHOICES = [
        ('multiple', 'Opción Múltiple'),
        ('verdadero_falso', 'Verdadero/Falso'),
        ('texto', 'Texto Corto'),
    ]
    
    DIFICULTAD_CHOICES = [
        ('facil', 'Fácil'),
        ('media', 'Media'),
        ('dificil', 'Difícil'),
    ]
    
    titulo = models.CharField(max_length=500, help_text="Enunciado de la pregunta")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='multiple')
    dificultad = models.CharField(max_length=10, choices=DIFICULTAD_CHOICES, default='media')
    tema = models.CharField(max_length=100, blank=True, help_text="Tema o categoría")
    
    # Opciones para preguntas de opción múltiple
    opcion_a = models.CharField(max_length=300, blank=True)
    opcion_b = models.CharField(max_length=300, blank=True)
    opcion_c = models.CharField(max_length=300, blank=True)
    opcion_d = models.CharField(max_length=300, blank=True)
    
    respuesta_correcta = models.CharField(max_length=300, help_text="Respuesta correcta o letra (A, B, C, D)")
    explicacion = models.TextField(blank=True, help_text="Explicación de la respuesta")
    
    activa = models.BooleanField(default=True)
    creada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='preguntas_creadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'
    
    def __str__(self):
        return f"{self.titulo[:50]}..."


class Test(models.Model):
    """Un test es una colección de preguntas"""
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    preguntas = models.ManyToManyField(Question, related_name='tests')
    tiempo_limite = models.IntegerField(help_text="Tiempo en minutos", default=30)
    
    activo = models.BooleanField(default=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Test'
        verbose_name_plural = 'Tests'
    
    def __str__(self):
        return self.nombre
    
    def total_preguntas(self):
        return self.preguntas.count()


class IntentTest(models.Model):
    """Registro de un intento de test por parte de un alumno"""
    alumno = models.ForeignKey(User, on_delete=models.CASCADE, related_name='intentos_test')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='intentos')
    
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    completado = models.BooleanField(default=False)
    
    puntuacion = models.FloatField(default=0.0)
    total_preguntas = models.IntegerField(default=0)
    respuestas_correctas = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = 'Intento de Test'
        verbose_name_plural = 'Intentos de Tests'
    
    def __str__(self):
        return f"{self.alumno.username} - {self.test.nombre} ({self.fecha_inicio.strftime('%d/%m/%Y %H:%M')})"
    
    def calcular_puntuacion(self):
        """Calcula la puntuación basada en respuestas correctas"""
        if self.total_preguntas > 0:
            self.puntuacion = (self.respuestas_correctas / self.total_preguntas) * 100
        else:
            self.puntuacion = 0
        self.save()


class RespuestaAlumno(models.Model):
    """Respuesta de un alumno a una pregunta específica"""
    intento = models.ForeignKey(IntentTest, on_delete=models.CASCADE, related_name='respuestas')
    pregunta = models.ForeignKey(Question, on_delete=models.CASCADE)
    respuesta = models.CharField(max_length=300)
    es_correcta = models.BooleanField(default=False)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['fecha_respuesta']
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'
    
    def __str__(self):
        return f"{self.pregunta.titulo[:30]} - {'✓' if self.es_correcta else '✗'}"
