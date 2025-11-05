"""
Comando para crear el Tema 1: Pilas con tests de diferentes niveles
Basado en las transparencias de ED.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from boards.models import Tema, Test, Pregunta, Respuesta


class Command(BaseCommand):
    help = 'Crea el Tema 1 (Pilas) con tests de nivel Fácil, Intermedio y Difícil'

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
        
        # Definición del tema
        tema_id = 'Tema 1 - Pilas'
        tema_descripcion = 'Pilas (Stacks): estructura LIFO, operaciones básicas y aplicaciones'
        
        # Preguntas organizadas por nivel de dificultad
        preguntas_por_nivel = {
            'Facil': [
                {
                    'enunciado': '¿Qué significa LIFO en el contexto de pilas?',
                    'dificultad': 'Facil',
                    'puntuacion': 10,
                    'respuestas': [
                        {'contenido': 'Last In, First Out (Último en entrar, primero en salir)', 'correcta': True},
                        {'contenido': 'Last In, Final Out (Último entrada, salida final)', 'correcta': False},
                        {'contenido': 'List In, First Out (Lista en entrada, primera salida)', 'correcta': False},
                        {'contenido': 'Linear Insert, Fast Output (Inserción lineal, salida rápida)', 'correcta': False},
                    ]
                },
                {
                    'enunciado': '¿Cuál es la operación que añade un elemento a una pila?',
                    'dificultad': 'Facil',
                    'puntuacion': 10,
                    'respuestas': [
                        {'contenido': 'push', 'correcta': True},
                        {'contenido': 'pop', 'correcta': False},
                        {'contenido': 'enqueue', 'correcta': False},
                        {'contenido': 'insert', 'correcta': False},
                    ]
                },
                {
                    'enunciado': '¿Cuál es la operación que elimina un elemento de una pila?',
                    'dificultad': 'Facil',
                    'puntuacion': 10,
                    'respuestas': [
                        {'contenido': 'pop', 'correcta': True},
                        {'contenido': 'push', 'correcta': False},
                        {'contenido': 'dequeue', 'correcta': False},
                        {'contenido': 'remove', 'correcta': False},
                    ]
                },
                {
                    'enunciado': '¿Desde dónde se insertan y extraen elementos en una pila?',
                    'dificultad': 'Facil',
                    'puntuacion': 10,
                    'respuestas': [
                        {'contenido': 'Desde el tope (top) de la pila', 'correcta': True},
                        {'contenido': 'Desde el fondo de la pila', 'correcta': False},
                        {'contenido': 'Desde cualquier posición', 'correcta': False},
                        {'contenido': 'Desde el medio de la pila', 'correcta': False},
                    ]
                },
                {
                    'enunciado': '¿Qué devuelve la operación peek en una pila?',
                    'dificultad': 'Facil',
                    'puntuacion': 10,
                    'respuestas': [
                        {'contenido': 'El elemento del tope sin eliminarlo', 'correcta': True},
                        {'contenido': 'El elemento del fondo de la pila', 'correcta': False},
                        {'contenido': 'El elemento del tope y lo elimina', 'correcta': False},
                        {'contenido': 'El tamaño de la pila', 'correcta': False},
                    ]
                },
            ],
            'Media': [
                {
                    'enunciado': '¿Cuál es la complejidad temporal de la operación push en una pila?',
                    'dificultad': 'Media',
                    'puntuacion': 15,
                    'respuestas': [
                        {'contenido': 'O(1) - Tiempo constante', 'correcta': True},
                        {'contenido': 'O(n) - Tiempo lineal', 'correcta': False},
                        {'contenido': 'O(log n) - Tiempo logarítmico', 'correcta': False},
                        {'contenido': 'O(n²) - Tiempo cuadrático', 'correcta': False},
                    ]
                },
                {
                    'enunciado': '¿Cuál de estas aplicaciones utiliza una pila?',
                    'dificultad': 'Media',
                    'puntuacion': 15,
                    'respuestas': [
                        {'contenido': 'Gestión de llamadas a funciones (call stack)', 'correcta': True},
                        {'contenido': 'Cola de impresión de documentos', 'correcta': False},
                        {'contenido': 'Búsqueda en amplitud (BFS)', 'correcta': False},
                        {'contenido': 'Planificación de procesos round-robin', 'correcta': False},
                    ]
                },
                {
                    'enunciado': 'Si realizamos: push(1), push(2), push(3), pop(), ¿qué elemento se extrae?',
                    'dificultad': 'Media',
                    'puntuacion': 15,
                    'respuestas': [
                        {'contenido': '3', 'correcta': True},
                        {'contenido': '1', 'correcta': False},
                        {'contenido': '2', 'correcta': False},
                        {'contenido': 'Ninguno, la pila está vacía', 'correcta': False},
                    ]
                },
                {
                    'enunciado': '¿Qué estructura de datos se puede usar para implementar una pila?',
                    'dificultad': 'Media',
                    'puntuacion': 15,
                    'respuestas': [
                        {'contenido': 'Array o lista enlazada', 'correcta': True},
                        {'contenido': 'Solo array', 'correcta': False},
                        {'contenido': 'Solo árbol binario', 'correcta': False},
                        {'contenido': 'Solo tabla hash', 'correcta': False},
                    ]
                },
                {
                    'enunciado': '¿Cuál es una ventaja de implementar una pila con lista enlazada sobre array?',
                    'dificultad': 'Media',
                    'puntuacion': 15,
                    'respuestas': [
                        {'contenido': 'No tiene límite de tamaño predefinido', 'correcta': True},
                        {'contenido': 'Acceso más rápido a elementos', 'correcta': False},
                        {'contenido': 'Usa menos memoria', 'correcta': False},
                        {'contenido': 'Operaciones más rápidas', 'correcta': False},
                    ]
                },
            ],
            'Dificil': [
                {
                    'enunciado': '¿Cómo se puede verificar si una expresión con paréntesis está balanceada usando una pila?',
                    'dificultad': 'Dificil',
                    'puntuacion': 20,
                    'respuestas': [
                        {'contenido': 'Apilando cada paréntesis de apertura y desapilando con cada cierre coincidente', 'correcta': True},
                        {'contenido': 'Contando el número de paréntesis de apertura y cierre', 'correcta': False},
                        {'contenido': 'Usando dos pilas, una para apertura y otra para cierre', 'correcta': False},
                        {'contenido': 'No se puede verificar con una pila', 'correcta': False},
                    ]
                },
                {
                    'enunciado': 'En la conversión de notación infija a postfija, ¿para qué se usa la pila?',
                    'dificultad': 'Dificil',
                    'puntuacion': 20,
                    'respuestas': [
                        {'contenido': 'Para almacenar operadores según su precedencia', 'correcta': True},
                        {'contenido': 'Para almacenar los operandos', 'correcta': False},
                        {'contenido': 'Para almacenar el resultado final', 'correcta': False},
                        {'contenido': 'Para contar los paréntesis', 'correcta': False},
                    ]
                },
                {
                    'enunciado': '¿Cuál es la complejidad espacial de implementar una pila con n elementos?',
                    'dificultad': 'Dificil',
                    'puntuacion': 20,
                    'respuestas': [
                        {'contenido': 'O(n) - Espacio lineal', 'correcta': True},
                        {'contenido': 'O(1) - Espacio constante', 'correcta': False},
                        {'contenido': 'O(log n) - Espacio logarítmico', 'correcta': False},
                        {'contenido': 'O(n²) - Espacio cuadrático', 'correcta': False},
                    ]
                },
                {
                    'enunciado': 'Si se implementa la función "undo" de un editor de texto con una pila, ¿qué almacenaría?',
                    'dificultad': 'Dificil',
                    'puntuacion': 20,
                    'respuestas': [
                        {'contenido': 'El historial de cambios o estados previos del documento', 'correcta': True},
                        {'contenido': 'Solo el último carácter escrito', 'correcta': False},
                        {'contenido': 'La posición del cursor', 'correcta': False},
                        {'contenido': 'El número de palabras del documento', 'correcta': False},
                    ]
                },
                {
                    'enunciado': '¿Cómo se puede implementar una cola usando dos pilas?',
                    'dificultad': 'Dificil',
                    'puntuacion': 20,
                    'respuestas': [
                        {'contenido': 'Una pila para enqueue y otra para dequeue, invirtiendo elementos cuando es necesario', 'correcta': True},
                        {'contenido': 'Usando ambas pilas de forma alterna', 'correcta': False},
                        {'contenido': 'No es posible implementar una cola con pilas', 'correcta': False},
                        {'contenido': 'Manteniendo ambas pilas con los mismos elementos', 'correcta': False},
                    ]
                },
            ],
        }
        
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('Creando Tema 1: Pilas con tests por niveles'))
        self.stdout.write(self.style.SUCCESS('='*70))
        
        tema_creado = False
        tests_creados = 0
        preguntas_creadas = 0
        
        with transaction.atomic():
            # Crear o obtener el tema
            tema, created = Tema.objects.get_or_create(tema_id=tema_id)
            if created:
                tema_creado = True
                self.stdout.write(self.style.SUCCESS(f'\n✓ Tema creado: {tema_id}'))
            else:
                self.stdout.write(self.style.WARNING(f'\n○ Tema ya existe: {tema_id}'))
            
            # Si se especifica recrear, eliminar preguntas existentes
            if recrear:
                preguntas_existentes = Pregunta.objects.filter(tema=tema_id)
                count = preguntas_existentes.count()
                if count > 0:
                    for pregunta in preguntas_existentes:
                        Respuesta.objects.filter(pregunta_id=pregunta.pregunta_id).delete()
                    preguntas_existentes.delete()
                    self.stdout.write(self.style.WARNING(f'  Eliminadas {count} preguntas existentes'))
            
            # Obtener el ID de la última pregunta para continuar la numeración
            ultima_pregunta = Pregunta.objects.order_by('-pregunta_id').first()
            siguiente_id = (ultima_pregunta.pregunta_id + 1) if ultima_pregunta else 1000
            
            # Crear tests y preguntas para cada nivel
            test_anterior = None
            
            for nivel, nombre_nivel in [('Facil', 'Fácil'), ('Media', 'Intermedio'), ('Dificil', 'Difícil')]:
                self.stdout.write(f'\n  📚 Nivel: {nombre_nivel}')
                
                preguntas_nivel = preguntas_por_nivel[nivel]
                ids_preguntas_nivel = []
                
                # Crear preguntas para este nivel
                for pregunta_info in preguntas_nivel:
                    pregunta = Pregunta.objects.create(
                        pregunta_id=siguiente_id,
                        tema=tema_id,
                        enunciado=pregunta_info['enunciado'],
                        dificultad=pregunta_info['dificultad'],
                        puntuacion=pregunta_info['puntuacion'],
                    )
                    ids_preguntas_nivel.append(siguiente_id)
                    
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
                    self.stdout.write(f'    + {pregunta_info["enunciado"][:60]}...')
                
                # Crear test para este nivel
                test_nombre = f"Test {tema_id} - {nombre_nivel}"
                test, test_created = Test.objects.get_or_create(
                    tema=tema,
                    nombre=test_nombre,
                    defaults={
                        'descripcion': f'Test de nivel {nombre_nivel.lower()} sobre Pilas',
                        'tiempo_limite': 15 if nivel == 'Facil' else (20 if nivel == 'Media' else 25),
                        'visible_alumnos': visible,
                        'activo': True,
                        'test_requisito': test_anterior,
                        'porcentaje_minimo': 70.0 if test_anterior else 0.0,
                    }
                )
                
                # Si el test ya existía, actualizar el requisito
                if not test_created and test_anterior:
                    test.test_requisito = test_anterior
                    test.porcentaje_minimo = 70.0
                    test.save()
                
                # Agregar las preguntas del nivel al test
                preguntas_test = Pregunta.objects.filter(pregunta_id__in=ids_preguntas_nivel)
                test.preguntas.set(preguntas_test)
                
                if test_created:
                    tests_creados += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Test creado: {test_nombre} ({len(ids_preguntas_nivel)} preguntas)'))
                else:
                    self.stdout.write(self.style.WARNING(f'  ○ Test actualizado: {test_nombre} ({len(ids_preguntas_nivel)} preguntas)'))
                
                if test_anterior:
                    self.stdout.write(f'    → Requisito: Superar "{test_anterior.nombre}" con 70%')
                else:
                    self.stdout.write(f'    → Sin requisitos previos (primer test)')
                
                # Guardar referencia para el siguiente nivel
                test_anterior = test
        
        # Resumen final
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('RESUMEN:'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Tema creado: {"Sí" if tema_creado else "Ya existía"}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Tests creados/actualizados: {tests_creados}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Preguntas creadas: {preguntas_creadas}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Niveles: Fácil (5) → Intermedio (5) → Difícil (5)'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Visibilidad: {"Visible para alumnos" if visible else "No visible"}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Requisitos: Cada nivel requiere 70% en el anterior'))
        self.stdout.write('='*70 + '\n')
