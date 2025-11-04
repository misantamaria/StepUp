from django.core.management.base import BaseCommand
from boards.models import Tema, Test, Pregunta


class Command(BaseCommand):
    help = 'Crea un test automático para cada tema con todas sus preguntas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--visible',
            action='store_true',
            help='Marca los tests como visibles para los alumnos',
        )

    def handle(self, *args, **options):
        visible = options.get('visible', False)
        
        temas = Tema.objects.all()
        tests_creados = 0
        tests_actualizados = 0
        
        for tema in temas:
            # Verificar si ya existe un test para este tema
            test_nombre = f"Test {tema.tema_id}"
            test, created = Test.objects.get_or_create(
                tema=tema,
                nombre=test_nombre,
                defaults={
                    'descripcion': f'Test completo del tema {tema.tema_id} con todas las preguntas disponibles.',
                    'tiempo_limite': 30,
                    'visible_alumnos': visible,
                    'activo': True,
                }
            )
            
            # Agregar todas las preguntas del tema
            preguntas_tema = Pregunta.objects.filter(tema=tema.tema_id)
            count_preguntas = preguntas_tema.count()
            
            if count_preguntas > 0:
                test.preguntas.set(preguntas_tema)
                
                if created:
                    tests_creados += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Creado test para tema "{tema.tema_id}" con {count_preguntas} preguntas')
                    )
                else:
                    tests_actualizados += 1
                    self.stdout.write(
                        self.style.WARNING(f'○ Actualizado test para tema "{tema.tema_id}" con {count_preguntas} preguntas')
                    )
            else:
                if created:
                    test.delete()
                self.stdout.write(
                    self.style.ERROR(f'✗ No hay preguntas para el tema "{tema.tema_id}"')
                )
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'Resumen:'))
        self.stdout.write(self.style.SUCCESS(f'  - Tests creados: {tests_creados}'))
        self.stdout.write(self.style.WARNING(f'  - Tests actualizados: {tests_actualizados}'))
        self.stdout.write(self.style.SUCCESS(f'  - Visibilidad: {"Visible para alumnos" if visible else "No visible"}'))
