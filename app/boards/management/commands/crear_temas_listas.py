"""
Comando para crear temas y preguntas básicas del Tema 1: Listas
Basado en las transparencias de ED.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from boards.models import Tema, Test, Pregunta, Respuesta


class Command(BaseCommand):
    help = 'Crea el Tema 1 (Listas) con sus subtemas y preguntas básicas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--visible',
            action='store_true',
            help='Marca los tests como visibles para los alumnos',
        )
        parser.add_argument(
            '--recrear',
            action='store_true',
            help='Elimina y recrea todas las preguntas del tema',
        )

    def handle(self, *args, **options):
        visible = options.get('visible', False)
        recrear = options.get('recrear', False)
        
        # Definición de temas según las transparencias
        temas_data = [
            {
                'id': 'Tema 2 - Listas',
                'descripcion': 'Listas: definición, operaciones básicas, implementaciones con arrays y listas enlazadas',
            },
        ]
        
        # Preguntas para el Tema 2 - Listas
        preguntas_data = {
            'Tema 2 - Listas': [
                # Conceptos básicos
                {
                    'enunciado': '¿Qué es una lista en estructuras de datos?',
                    'dificultad': 'Facil',
                    'puntuacion': 10,
                    'respuestas': [
                        {'contenido': 'Una colección ordenada de elementos del mismo tipo', 'correcta': True},
                        {'contenido': 'Una estructura que solo permite acceso al primer elemento', 'correcta': False},
                        {'contenido': 'Una tabla hash con claves numéricas', 'correcta': False},
                        {'contenido': 'Un árbol binario sin jerarquía', 'correcta': False},
                    ]
                },
                {
                    'enunciado': '¿Cuál es la característica principal de una lista?',
                    'dificultad': 'Facil',
                    'puntuacion': 10,
                    'respuestas': [
                        {'contenido': 'Mantiene el orden de inserción de los elementos', 'correcta': True},
                        {'contenido': 'Los elementos están ordenados alfabéticamente', 'correcta': False},
                        {'contenido': 'Solo puede contener números', 'correcta': False},
                        {'contenido': 'Tiene un tamaño fijo e inmutable', 'correcta': False},
                    ]
                },
                {
                    'enunciado': '¿Qué operaciones básicas se pueden realizar en una lista?',
                    'dificultad': 'Media',
                    'puntuacion': 15,
                    'respuestas': [
                        {'contenido': 'Insertar, eliminar, buscar y recorrer', 'correcta': True},
                        {'contenido': 'Solo insertar y eliminar', 'correcta': False},
                        {'contenido': 'Únicamente buscar elementos', 'correcta': False},
                        {'contenido': 'Ordenar y descomprimir', 'correcta': False},
                    ]
                },
                # Implementación con Arrays
                {
                    'enunciado': '¿Cuál es la principal ventaja de implementar listas con arrays?',
                    'dificultad': 'Media',
                    'puntuacion': 15,
                    'respuestas': [
                        {'contenido': 'Acceso directo a cualquier elemento en tiempo O(1)', 'correcta': True},
                        {'contenido': 'Inserción rápida al inicio', 'correcta': False},
                        {'contenido': 'Tamaño dinámico sin límites', 'correcta': False},
                        {'contenido': 'Menor uso de memoria', 'correcta': False},
                    ]
                },
                {
                    'enunciado': '¿Cuál es la principal desventaja de usar arrays para implementar listas?',
                    'dificultad': 'Media',
                    'puntuacion': 15,
                    'respuestas': [
                        {'contenido': 'Tamaño fijo que requiere redimensionamiento', 'correcta': True},
                        {'contenido': 'No se pueden almacenar números', 'correcta': False},
                        {'contenido': 'Acceso lento a los elementos', 'correcta': False},
                        {'contenido': 'No permiten eliminar elementos', 'correcta': False},
                    ]
                },
                {
                    'enunciado': '¿Qué complejidad temporal tiene insertar un elemento al final de un array (sin redimensionar)?',
                    'dificultad': 'Dificil',
                    'puntuacion': 20,
                    'respuestas': [
                        {'contenido': 'O(1) - Tiempo constante', 'correcta': True},
                        {'contenido': 'O(n) - Tiempo lineal', 'correcta': False},
                        {'contenido': 'O(log n) - Tiempo logarítmico', 'correcta': False},
                        {'contenido': 'O(n²) - Tiempo cuadrático', 'correcta': False},
                    ]
                },
                # Listas Enlazadas
                {
                    'enunciado': '¿Qué es un nodo en una lista enlazada?',
                    'dificultad': 'Facil',
                    'puntuacion': 10,
                    'respuestas': [
                        {'contenido': 'Una estructura que contiene un dato y una referencia al siguiente nodo', 'correcta': True},
                        {'contenido': 'El primer elemento de la lista', 'correcta': False},
                        {'contenido': 'Un índice que apunta a una posición del array', 'correcta': False},
                        {'contenido': 'Una función para recorrer la lista', 'correcta': False},
                    ]
                },
                {
                    'enunciado': '¿Cuál es la ventaja principal de las listas enlazadas sobre los arrays?',
                    'dificultad': 'Media',
                    'puntuacion': 15,
                    'respuestas': [
                        {'contenido': 'Inserción y eliminación eficiente sin mover elementos', 'correcta': True},
                        {'contenido': 'Acceso directo a cualquier posición', 'correcta': False},
                        {'contenido': 'Menor uso de memoria', 'correcta': False},
                        {'contenido': 'Búsqueda más rápida de elementos', 'correcta': False},
                    ]
                },
                {
                    'enunciado': '¿Qué diferencia hay entre una lista enlazada simple y una doble?',
                    'dificultad': 'Media',
                    'puntuacion': 15,
                    'respuestas': [
                        {'contenido': 'La doble tiene referencias al nodo anterior y siguiente', 'correcta': True},
                        {'contenido': 'La doble tiene el doble de capacidad', 'correcta': False},
                        {'contenido': 'La simple no puede eliminar elementos', 'correcta': False},
                        {'contenido': 'La doble usa arrays internamente', 'correcta': False},
                    ]
                },
                {
                    'enunciado': '¿Qué complejidad tiene buscar un elemento en una lista enlazada?',
                    'dificultad': 'Dificil',
                    'puntuacion': 20,
                    'respuestas': [
                        {'contenido': 'O(n) - Debe recorrer la lista secuencialmente', 'correcta': True},
                        {'contenido': 'O(1) - Acceso directo', 'correcta': False},
                        {'contenido': 'O(log n) - Búsqueda binaria', 'correcta': False},
                        {'contenido': 'O(n²) - Recorrido doble', 'correcta': False},
                    ]
                },
            ],
        }
        
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('Creando Tema 2: Listas con preguntas básicas'))
        self.stdout.write(self.style.SUCCESS('='*70))
        
        temas_creados = 0
        tests_creados = 0
        preguntas_creadas = 0
        
        with transaction.atomic():
            for tema_info in temas_data:
                tema_id = tema_info['id']
                
                # Crear o obtener el tema
                tema, created = Tema.objects.get_or_create(tema_id=tema_id)
                if created:
                    temas_creados += 1
                    self.stdout.write(self.style.SUCCESS(f'\n✓ Tema creado: {tema_id}'))
                else:
                    self.stdout.write(self.style.WARNING(f'\n○ Tema ya existe: {tema_id}'))
                
                # Si se especifica recrear, eliminar preguntas existentes
                if recrear:
                    preguntas_existentes = Pregunta.objects.filter(tema=tema_id)
                    count = preguntas_existentes.count()
                    if count > 0:
                        # Primero eliminar las respuestas asociadas
                        for pregunta in preguntas_existentes:
                            Respuesta.objects.filter(pregunta_id=pregunta.pregunta_id).delete()
                        preguntas_existentes.delete()
                        self.stdout.write(self.style.WARNING(f'  Eliminadas {count} preguntas existentes'))
                
                # Obtener el ID de la última pregunta para continuar la numeración
                ultima_pregunta = Pregunta.objects.order_by('-pregunta_id').first()
                siguiente_id = (ultima_pregunta.pregunta_id + 1) if ultima_pregunta else 1
                
                # Crear preguntas para este tema
                preguntas_tema = preguntas_data.get(tema_id, [])
                for pregunta_info in preguntas_tema:
                    # Crear la pregunta
                    pregunta = Pregunta.objects.create(
                        pregunta_id=siguiente_id,
                        tema=tema_id,
                        enunciado=pregunta_info['enunciado'],
                        dificultad=pregunta_info['dificultad'],
                        puntuacion=pregunta_info['puntuacion'],
                    )
                    
                    # Crear las respuestas
                    respuesta_id = 1
                    for respuesta_info in pregunta_info['respuestas']:
                        Respuesta.objects.create(
                            respuesta_id=f"{siguiente_id}_{respuesta_id}",
                            pregunta_id=siguiente_id,
                            contenido=respuesta_info['contenido'],
                            solucion='Correcta' if respuesta_info['correcta'] else 'Incorrecta',
                        )
                        respuesta_id += 1
                    
                    preguntas_creadas += 1
                    siguiente_id += 1
                    self.stdout.write(f'    + Pregunta: {pregunta_info["enunciado"][:60]}...')
                
                # Crear test para este tema
                test_nombre = f"Test {tema_id}"
                test, test_created = Test.objects.get_or_create(
                    tema=tema,
                    nombre=test_nombre,
                    defaults={
                        'descripcion': tema_info['descripcion'],
                        'tiempo_limite': 20,
                        'visible_alumnos': visible,
                        'activo': True,
                    }
                )
                
                # Agregar todas las preguntas del tema al test
                preguntas_tema = Pregunta.objects.filter(tema=tema_id)
                test.preguntas.set(preguntas_tema)
                
                if test_created:
                    tests_creados += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Test creado con {preguntas_tema.count()} preguntas'))
                else:
                    self.stdout.write(self.style.WARNING(f'  ○ Test actualizado con {preguntas_tema.count()} preguntas'))
        
        # Resumen final
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('RESUMEN:'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Temas creados: {temas_creados}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Tests creados: {tests_creados}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Preguntas creadas: {preguntas_creadas}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Visibilidad: {"Visible para alumnos" if visible else "No visible (usar --visible para hacerlos visibles)"}'))
        self.stdout.write('='*70 + '\n')
