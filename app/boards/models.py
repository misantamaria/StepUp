from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Tema(models.Model):
    """Mapea a la tabla Tema de PIE_ED"""
    tema_id = models.CharField(max_length=100, primary_key=True, db_column='Tema_ID')
    
    class Meta:
        db_table = 'Tema'
        managed = True  # Django SÍ gestiona esta tabla
        verbose_name = 'Tema'
        verbose_name_plural = 'Temas'
    
    def __str__(self):
        return self.tema_id


class Pregunta(models.Model):
    """Mapea a la tabla Pregunta de PIE_ED"""
    DIFICULTAD_CHOICES = [
        ('Facil', 'Fácil'),
        ('Media', 'Media'),
        ('Dificil', 'Difícil'),
    ]
    
    pregunta_id = models.IntegerField(primary_key=True, db_column='Pregunta_ID')
    tema = models.CharField(max_length=100, db_column='Tema')
    enunciado = models.TextField(db_column='Enunciado')
    dificultad = models.CharField(max_length=20, choices=DIFICULTAD_CHOICES, db_column='Dificultad')
    puntuacion = models.IntegerField(db_column='Puntuacion')
    
    class Meta:
        db_table = 'Pregunta'
        managed = True  # Django SÍ gestiona esta tabla
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'
    
    def __str__(self):
        return f"{self.enunciado[:50]}..."


class Respuesta(models.Model):
    """Mapea a la tabla Respuesta de PIE_ED"""
    SOLUCION_CHOICES = [
        ('Correcta', 'Correcta'),
        ('Incorrecta', 'Incorrecta'),
    ]
    
    respuesta_id = models.IntegerField(db_column='Respuesta_ID')
    pregunta_id = models.IntegerField(db_column='Pregunta_ID')
    solucion = models.CharField(max_length=20, choices=SOLUCION_CHOICES, db_column='Solucion')
    contenido = models.TextField(db_column='Contenido')
    
    class Meta:
        db_table = 'Respuesta'
        managed = True  # Django SÍ gestiona esta tabla
        unique_together = (('respuesta_id', 'pregunta_id'),)
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'
    
    def __str__(self):
        return f"{self.contenido[:30]} - {self.solucion}"


# Modelos antiguos de Django - mantener por compatibilidad o migrar después
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
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, related_name='tests', null=True, blank=True, db_column='tema_id')
    preguntas = models.ManyToManyField(Pregunta, related_name='tests', blank=True)
    tiempo_limite = models.IntegerField(help_text="Tiempo en minutos", default=30)
    
    visible_alumnos = models.BooleanField(default=False, help_text="¿Visible para los alumnos?")
    activo = models.BooleanField(default=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['tema', '-fecha_creacion']
        verbose_name = 'Test'
        verbose_name_plural = 'Tests'
    
    def __str__(self):
        tema_str = f"{self.tema.tema_id} - " if self.tema else ""
        return f"{tema_str}{self.nombre}"
    
    def total_preguntas(self):
        return self.preguntas.count()
    
    def agregar_preguntas_tema(self):
        """Agrega automáticamente todas las preguntas del tema al test"""
        if self.tema:
            preguntas_tema = Pregunta.objects.filter(tema=self.tema.tema_id)
            self.preguntas.set(preguntas_tema)
            return preguntas_tema.count()
        return 0


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
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, db_column='pregunta_id')
    respuesta = models.CharField(max_length=300)
    es_correcta = models.BooleanField(default=False)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['fecha_respuesta']
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'
    
    def __str__(self):
        return f"{self.pregunta.enunciado[:30]} - {'✓' if self.es_correcta else '✗'}"


class ProgresoTema(models.Model):
    """Registro del progreso de un alumno en un tema específico"""
    alumno = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progresos_temas')
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, related_name='progresos')
    
    total_preguntas = models.IntegerField(default=0)
    preguntas_respondidas = models.IntegerField(default=0)
    preguntas_correctas = models.IntegerField(default=0)
    
    porcentaje_completado = models.FloatField(default=0.0)
    porcentaje_aciertos = models.FloatField(default=0.0)
    
    completado = models.BooleanField(default=False)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_ultima_actividad = models.DateTimeField(auto_now=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = (('alumno', 'tema'),)
        ordering = ['alumno', 'tema']
        verbose_name = 'Progreso de Tema'
        verbose_name_plural = 'Progresos de Temas'
    
    def __str__(self):
        return f"{self.alumno.username} - {self.tema.tema_id} ({self.porcentaje_completado:.0f}%)"
    
    def actualizar_progreso(self):
        """Actualiza el progreso del alumno en este tema"""
        # Obtener todos los intentos del alumno en tests de este tema
        intentos = IntentTest.objects.filter(
            alumno=self.alumno,
            test__tema=self.tema,
            completado=True
        )
        
        if not intentos.exists():
            return
        
        # Contar todas las preguntas únicas respondidas
        respuestas = RespuestaAlumno.objects.filter(
            intento__in=intentos
        ).values('pregunta').distinct()
        
        self.total_preguntas = Pregunta.objects.filter(tema=self.tema.tema_id).count()
        self.preguntas_respondidas = respuestas.count()
        
        # Contar correctas
        correctas = RespuestaAlumno.objects.filter(
            intento__in=intentos,
            es_correcta=True
        ).values('pregunta').distinct().count()
        
        self.preguntas_correctas = correctas
        
        # Calcular porcentajes
        if self.total_preguntas > 0:
            self.porcentaje_completado = (self.preguntas_respondidas / self.total_preguntas) * 100
        
        if self.preguntas_respondidas > 0:
            self.porcentaje_aciertos = (self.preguntas_correctas / self.preguntas_respondidas) * 100
        
        # Marcar como completado si respondió todas las preguntas
        if self.porcentaje_completado >= 100 and not self.completado:
            self.completado = True
            self.fecha_completado = timezone.now()
        
        self.save()

