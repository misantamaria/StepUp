"""
Comando para crear la estructura completa de temas según el índice de ED
Crea 6 temas con 3 tests por nivel (Fácil, Intermedio, Difícil)
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from boards.models import Tema, Test, Pregunta, Respuesta


class Command(BaseCommand):
    help = 'Crea la estructura completa de 6 temas con tests por niveles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Limpia todos los temas y tests existentes antes de crear',
        )

    def handle(self, *args, **options):
        limpiar = options.get('limpiar', False)
        
        if limpiar:
            self.stdout.write(self.style.WARNING('🗑️  Limpiando temas y tests existentes...'))
            with transaction.atomic():
                # Eliminar en orden para evitar problemas de FK
                Test.objects.all().delete()
                Pregunta.objects.all().delete()
                Tema.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Limpieza completada\n'))
        
        # Definición de los 6 temas según el índice
        temas_info = [
            {
                'id': 'Tema 1 - Conceptos básicos',
                'descripcion': 'Fundamentos de estructuras de datos y algoritmos',
                'visible': True,
            },
            {
                'id': 'Tema 2 - Pilas y colas',
                'descripcion': 'Estructuras LIFO (Pilas) y FIFO (Colas)',
                'visible': True,
            },
            {
                'id': 'Tema 3 - Listas',
                'descripcion': 'Listas: arrays, listas enlazadas y variantes',
                'visible': True,
            },
            {
                'id': 'Tema 4 - Árboles',
                'descripcion': 'Estructuras jerárquicas: árboles binarios, AVL, B-trees',
                'visible': False,
            },
            {
                'id': 'Tema 5 - Grafos',
                'descripcion': 'Grafos dirigidos y no dirigidos, algoritmos de recorrido',
                'visible': False,
            },
            {
                'id': 'Tema 6 - Tablas Hash',
                'descripcion': 'Tablas hash, funciones de dispersión y resolución de colisiones',
                'visible': False,
            },
        ]
        
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('Creando estructura de 6 temas'))
        self.stdout.write(self.style.SUCCESS('='*70))
        
        temas_creados = 0
        
        with transaction.atomic():
            for tema_info in temas_info:
                tema, created = Tema.objects.get_or_create(tema_id=tema_info['id'])
                if created:
                    temas_creados += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'\n✓ {tema_info["id"]}') +
                        f' {"[VISIBLE]" if tema_info["visible"] else "[BLOQUEADO 🔒]"}'
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'\n○ {tema_info["id"]} (ya existe)')
                    )
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('RESUMEN:'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Temas creados: {temas_creados}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Temas visibles: 3 (Conceptos, Pilas/Colas, Listas)'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Temas bloqueados: 3 (Árboles, Grafos, Hash)'))
        self.stdout.write('='*70 + '\n')
        
        self.stdout.write(self.style.WARNING('\n⚠️  Siguiente paso: Ejecutar comandos individuales para crear tests:'))
        self.stdout.write('  - python manage.py crear_tests_tema1_conceptos --visible')
        self.stdout.write('  - python manage.py crear_tests_tema2_pilas_colas --visible')
        self.stdout.write('  - python manage.py crear_tests_tema3_listas --visible')
