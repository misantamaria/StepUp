from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Test, Pregunta, Tema

"""
Pruebas para validar que la suma de valores de las preguntas asociadas a un Test
no exceda el máximo permitido (debe lanzar ValidationError cuando supere 10).
"""


class TestPreguntasSumValidation(TestCase):
    def setUp(self):
        # Crear usuario profesor mínimo necesario
        self.profesor = User.objects.create_user(username='prof', password='pwd123')
        # Crear tema (campos asumidos similares a los del proyecto)
        self.tema = Tema.objects.create(
            tema_id='tema_test',
            visible_alumnos=True,
            disponible_alumno=True,
            visible_profesor=True,
            disponible_profesor=True,
            activo=True
        )
        # Crear Test al que se asociarán las preguntas
        self.test = Test.objects.create(
            nombre='Test Suma Valores',
            descripcion='Test para validar suma de valores de preguntas',
            tema=self.tema,
            nivel='Facil',
            tiempo_limite=10,
            visible_alumnos=True,
            disponible_alumno=True,
            creado_por=self.profesor
        )

    def test_sum_preguntas_above_limit_raises_validation_error(self):
        """
        Crear dos preguntas cuyo valor suma más de 10 y verificar que al validar
        el Test se lanza ValidationError (validación definida en el modelo).
        """
        # Crear preguntas asociadas cuyo valor total será 12 (6 + 6)
        Pregunta.objects.create(test=self.test, texto='Pregunta 1', valor=6)
        Pregunta.objects.create(test=self.test, texto='Pregunta 2', valor=6)

        # Al validar el Test debe producirse un ValidationError por superar el límite
        with self.assertRaises(ValidationError):
            # full_clean() debe disparar la validación definida en el modelo Test
            self.test.full_clean()