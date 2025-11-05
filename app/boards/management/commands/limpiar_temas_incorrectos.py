"""
Comando para limpiar los temas creados incorrectamente
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from boards.models import Tema, Pregunta, Respuesta


class Command(BaseCommand):
    help = 'Elimina los temas incorrectos creados anteriormente'

    def handle(self, *args, **options):
        temas_borrar = [
            '1.1 Listas - Conceptos Básicos',
            '1.2 Listas - Implementación con Arrays',
            '1.3 Listas - Listas Enlazadas',
            '1.4 Listas - Pilas y Colas',
        ]
        
        self.stdout.write('Eliminando temas incorrectos...')
        
        with transaction.atomic():
            for tema_id in temas_borrar:
                # Eliminar preguntas del tema
                preguntas = Pregunta.objects.filter(tema=tema_id)
                count_preguntas = preguntas.count()
                
                if count_preguntas > 0:
                    # Eliminar respuestas
                    for pregunta in preguntas:
                        Respuesta.objects.filter(pregunta_id=pregunta.pregunta_id).delete()
                    
                    # Eliminar preguntas
                    preguntas.delete()
                
                # Eliminar tema
                tema = Tema.objects.filter(tema_id=tema_id)
                if tema.exists():
                    tema.delete()
                    self.stdout.write(self.style.SUCCESS(f'✓ Eliminado: {tema_id} ({count_preguntas} preguntas)'))
        
        self.stdout.write(self.style.SUCCESS('\n¡Limpieza completada!'))
