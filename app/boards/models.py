from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Tema(models.Model):
    """Mapea a la tabla Tema de PIE_ED"""
    tema_id = models.CharField(max_length=100, primary_key=True, db_column='Tema_ID')
    
    # Control de visibilidad y disponibilidad
    # VISIBLE = Aparece en la interfaz
    # DISPONIBLE = Se puede acceder (hacer tests)
    # Un tema se muestra solo si está VISIBLE Y DISPONIBLE
    visible_alumnos = models.BooleanField(default=True, help_text="¿Visible para los alumnos?")
    visible_profesor = models.BooleanField(default=True, help_text="¿Visible para el profesor en modo alumno?")
    disponible_alumno = models.BooleanField(default=True, help_text="¿Disponible para alumnos?")
    disponible_profesor = models.BooleanField(default=True, help_text="¿Disponible para profesor?")
    activo = models.BooleanField(default=True, help_text="¿Tema activo en el sistema?")
    
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
    
    def get_respuestas(self):
        """Obtiene las respuestas de esta pregunta"""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT Respuesta_ID, Contenido, Solucion FROM Respuesta WHERE Pregunta_ID = %s ORDER BY Respuesta_ID',
                [self.pregunta_id]
            )
            respuestas = []
            for row in cursor.fetchall():
                respuestas.append({
                    'id': row[0],
                    'contenido': row[1],
                    'es_correcta': row[2] == 'Correcta'
                })
            return respuestas


class Respuesta(models.Model):
    """Mapea a la tabla Respuesta de PIE_ED"""
    SOLUCION_CHOICES = [
        ('Correcta', 'Correcta'),
        ('Incorrecta', 'Incorrecta'),
    ]
    
    respuesta_id = models.IntegerField(db_column='Respuesta_ID', primary_key=True)
    pregunta_id = models.IntegerField(db_column='Pregunta_ID')
    solucion = models.CharField(max_length=20, choices=SOLUCION_CHOICES, db_column='Solucion')
    contenido = models.TextField(db_column='Contenido')
    
    class Meta:
        db_table = 'Respuesta'
        managed = False  # NO gestionar, tabla externa PIE_ED
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'
    
    def __str__(self):
        return f"{self.contenido[:30]} - {self.solucion}"


class Test(models.Model):
    """Un test es una colección de preguntas"""
    NIVEL_CHOICES = [
        ('Facil', 'Fácil'),
        ('Media', 'Intermedio'),
        ('Dificil', 'Difícil'),
    ]
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, related_name='tests', null=True, blank=True, db_column='tema_id')
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES, default='Facil', help_text="Nivel de dificultad del test")
    preguntas = models.ManyToManyField(Pregunta, related_name='tests', blank=True)
    tiempo_limite = models.IntegerField(help_text="Tiempo en minutos", default=30)
    
    # Visibilidad: controla si el test aparece en la interfaz
    visible_alumnos = models.BooleanField(default=False, help_text="¿Visible para los alumnos?")
    visible_profesor = models.BooleanField(default=True, help_text="¿Visible para el profesor en modo alumno? (para pruebas)")
    
    # Disponibilidad: controla si el test está activo/disponible
    disponible_alumno = models.BooleanField(default=True, help_text="¿Disponible para alumnos? (debe estar visible también)")
    disponible_profesor = models.BooleanField(default=True, help_text="¿Disponible para profesor? (debe estar visible también)")
    
    activo = models.BooleanField(default=True)
    test_requisito = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                       related_name='tests_desbloqueados',
                                       help_text="Test que debe superarse antes de poder hacer este")
    porcentaje_minimo = models.FloatField(default=70.0, help_text="Porcentaje mínimo requerido en el test requisito")
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['tema', '-fecha_creacion']
        verbose_name = 'Test'
        verbose_name_plural = 'Tests'
    
    def __str__(self):
        tema_str = "{} - ".format(str(self.tema.tema_id)) if self.tema else ""
        return "{}{}".format(tema_str, self.nombre)
    
    def total_preguntas(self):
        return self.preguntas.count()
    
    def agregar_preguntas_tema(self):
        """Agrega automáticamente todas las preguntas del tema al test"""
        if self.tema:
            preguntas_tema = Pregunta.objects.filter(tema=self.tema.tema_id)
            self.preguntas.set(preguntas_tema)
            return preguntas_tema.count()
        return 0
    
    def alumno_cumple_requisitos(self, alumno):
        """
        Verifica si el alumno cumple con los requisitos para acceder a este test.
        Para tests de nivel Intermedio/Difícil, debe haber superado TODOS los tests
        del nivel anterior del mismo tema.
        """
        # Si es nivel Fácil, siempre puede acceder (si está visible)
        if self.nivel == 'Facil':
            return True
        
        # Si no tiene tema asignado, usar lógica simple de test_requisito
        if not self.tema:
            if not self.test_requisito:
                return True
            mejor_intento = IntentTest.objects.filter(
                alumno=alumno,
                test=self.test_requisito,
                completado=True
            ).order_by('-puntuacion').first()
            
            if not mejor_intento:
                return False
            return mejor_intento.puntuacion >= self.porcentaje_minimo
        
        # Determinar el nivel anterior requerido
        nivel_requerido = 'Facil' if self.nivel == 'Media' else 'Media'
        
        # Obtener TODOS los tests del nivel anterior del mismo tema
        tests_nivel_anterior = Test.objects.filter(
            tema=self.tema,
            nivel=nivel_requerido,
            activo=True
        )
        
        # Si no hay tests del nivel anterior, puede acceder
        if not tests_nivel_anterior.exists():
            return True
        
        # Verificar que haya superado TODOS los tests del nivel anterior
        for test_previo in tests_nivel_anterior:
            mejor_intento = IntentTest.objects.filter(
                alumno=alumno,
                test=test_previo,
                completado=True
            ).order_by('-puntuacion').first()
            
            # Si no ha completado este test del nivel anterior, no puede avanzar
            if not mejor_intento:
                return False
            
            # Si no superó el porcentaje mínimo (70%), no puede avanzar
            if mejor_intento.puntuacion < self.porcentaje_minimo:
                return False
        
        # Ha superado TODOS los tests del nivel anterior
        return True


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
    
    # Campo para identificar si es un examen aleatorio
    es_examen = models.BooleanField(default=False, help_text="¿Es un examen con preguntas aleatorias?")
    
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
    confirmada = models.BooleanField(default=False)  # Si el alumno confirmó la respuesta en tests por tema
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
        porcentaje = int(self.porcentaje_completado)
        return "{} - {} ({}%)".format(
            self.alumno.username,
            str(self.tema.tema_id),
            porcentaje
        )
    
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

