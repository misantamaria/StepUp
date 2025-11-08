"""
Comando para crear el Tema 1: Conceptos Básicos con 9 tests (3 por nivel)
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from boards.models import Tema, Test, Pregunta, Respuesta


class Command(BaseCommand):
    help = 'Crea el Tema 1 (Conceptos Básicos) con 9 tests divididos en 3 niveles'

    def add_arguments(self, parser):
        parser.add_argument('--visible', action='store_true', help='Marca los tests como visibles')

    def handle(self, *args, **options):
        visible = options.get('visible', False)
        tema_id = 'Tema 1 - Conceptos básicos'
        
        # Definición de preguntas por test
        tests_data = {
            # NIVEL FÁCIL - 3 tests
            'Test 1.1 - Introducción a Algoritmos': {
                'nivel': 'Facil',
                'tiempo': 10,
                'orden': 1,
                'preguntas': [
                    {
                        'enunciado': '¿Qué es un algoritmo?',
                        'dificultad': 'Facil',
                        'puntuacion': 10,
                        'respuestas': [
                            {'contenido': 'Una secuencia finita de pasos para resolver un problema', 'correcta': True},
                            {'contenido': 'Un programa escrito en lenguaje de programación', 'correcta': False},
                            {'contenido': 'Una base de datos', 'correcta': False},
                            {'contenido': 'Un tipo de computadora', 'correcta': False},
                        ]
                    },
                    {
                        'enunciado': '¿Cuál es una característica esencial de un algoritmo?',
                        'dificultad': 'Facil',
                        'puntuacion': 10,
                        'respuestas': [
                            {'contenido': 'Debe ser finito y terminar en algún momento', 'correcta': True},
                            {'contenido': 'Debe ser infinito', 'correcta': False},
                            {'contenido': 'Debe usar solo números', 'correcta': False},
                            {'contenido': 'Debe estar en inglés', 'correcta': False},
                        ]
                    },
                    {
                        'enunciado': '¿Qué significa que un algoritmo sea "determinista"?',
                        'dificultad': 'Facil',
                        'puntuacion': 10,
                        'respuestas': [
                            {'contenido': 'Que con la misma entrada siempre produce la misma salida', 'correcta': True},
                            {'contenido': 'Que puede dar diferentes resultados', 'correcta': False},
                            {'contenido': 'Que es muy lento', 'correcta': False},
                            {'contenido': 'Que no funciona correctamente', 'correcta': False},
                        ]
                    },
                ]
            },
            'Test 1.2 - Estructuras de Datos Básicas': {
                'nivel': 'Facil',
                'tiempo': 10,
                'orden': 2,
                'preguntas': [
                    {
                        'enunciado': '¿Qué es una estructura de datos?',
                        'dificultad': 'Facil',
                        'puntuacion': 10,
                        'respuestas': [
                            {'contenido': 'Una forma de organizar y almacenar datos', 'correcta': True},
                            {'contenido': 'Un tipo de algoritmo', 'correcta': False},
                            {'contenido': 'Un lenguaje de programación', 'correcta': False},
                            {'contenido': 'Un sistema operativo', 'correcta': False},
                        ]
                    },
                    {
                        'enunciado': '¿Cuál de estas es una estructura de datos?',
                        'dificultad': 'Facil',
                        'puntuacion': 10,
                        'respuestas': [
                            {'contenido': 'Array (arreglo)', 'correcta': True},
                            {'contenido': 'For loop', 'correcta': False},
                            {'contenido': 'If-else', 'correcta': False},
                            {'contenido': 'Print', 'correcta': False},
                        ]
                    },
                    {
                        'enunciado': '¿Qué es un tipo de dato primitivo?',
                        'dificultad': 'Facil',
                        'puntuacion': 10,
                        'respuestas': [
                            {'contenido': 'Un tipo básico provisto por el lenguaje (int, char, bool, etc.)', 'correcta': True},
                            {'contenido': 'Una estructura compleja creada por el programador', 'correcta': False},
                            {'contenido': 'Un archivo de texto', 'correcta': False},
                            {'contenido': 'Una función matemática', 'correcta': False},
                        ]
                    },
                ]
            },
            'Test 1.3 - Notación y Complejidad Básica': {
                'nivel': 'Facil',
                'tiempo': 10,
                'orden': 3,
                'preguntas': [
                    {
                        'enunciado': '¿Qué mide la complejidad temporal de un algoritmo?',
                        'dificultad': 'Facil',
                        'puntuacion': 10,
                        'respuestas': [
                            {'contenido': 'El tiempo que tarda en ejecutarse en función del tamaño de entrada', 'correcta': True},
                            {'contenido': 'El tamaño del código fuente', 'correcta': False},
                            {'contenido': 'El número de líneas de código', 'correcta': False},
                            {'contenido': 'La cantidad de memoria RAM', 'correcta': False},
                        ]
                    },
                    {
                        'enunciado': '¿Qué significa O(1) en complejidad?',
                        'dificultad': 'Facil',
                        'puntuacion': 10,
                        'respuestas': [
                            {'contenido': 'Tiempo constante, independiente del tamaño de entrada', 'correcta': True},
                            {'contenido': 'Solo funciona con 1 elemento', 'correcta': False},
                            {'contenido': 'Tarda exactamente 1 segundo', 'correcta': False},
                            {'contenido': 'Es muy lento', 'correcta': False},
                        ]
                    },
                    {
                        'enunciado': '¿Qué es mejor en términos de eficiencia?',
                        'dificultad': 'Facil',
                        'puntuacion': 10,
                        'respuestas': [
                            {'contenido': 'O(1) es mejor que O(n)', 'correcta': True},
                            {'contenido': 'O(n) es mejor que O(1)', 'correcta': False},
                            {'contenido': 'Son equivalentes', 'correcta': False},
                            {'contenido': 'No se pueden comparar', 'correcta': False},
                        ]
                    },
                ]
            },
            # NIVEL INTERMEDIO - 3 tests
            'Test 1.4 - Análisis de Algoritmos': {
                'nivel': 'Media',
                'tiempo': 15,
                'orden': 4,
                'preguntas': [
                    {
                        'enunciado': '¿Cuál es la complejidad de buscar un elemento en un array no ordenado?',
                        'dificultad': 'Media',
                        'puntuacion': 15,
                        'respuestas': [
                            {'contenido': 'O(n) - debe revisar cada elemento en el peor caso', 'correcta': True},
                            {'contenido': 'O(1) - acceso inmediato', 'correcta': False},
                            {'contenido': 'O(log n) - búsqueda logarítmica', 'correcta': False},
                            {'contenido': 'O(n²) - dos bucles anidados', 'correcta': False},
                        ]
                    },
                    {
                        'enunciado': 'Si un algoritmo tiene dos bucles anidados que recorren n elementos, ¿cuál es su complejidad?',
                        'dificultad': 'Media',
                        'puntuacion': 15,
                        'respuestas': [
                            {'contenido': 'O(n²)', 'correcta': True},
                            {'contenido': 'O(n)', 'correcta': False},
                            {'contenido': 'O(2n)', 'correcta': False},
                            {'contenido': 'O(log n)', 'correcta': False},
                        ]
                    },
                    {
                        'enunciado': '¿Qué notación describe el mejor caso de un algoritmo?',
                        'dificultad': 'Media',
                        'puntuacion': 15,
                        'respuestas': [
                            {'contenido': 'Omega (Ω)', 'correcta': True},
                            {'contenido': 'O grande (O)', 'correcta': False},
                            {'contenido': 'Theta (Θ)', 'correcta': False},
                            {'contenido': 'Pi (π)', 'correcta': False},
                        ]
                    },
                ]
            },
            'Test 1.5 - Recursividad': {
                'nivel': 'Media',
                'tiempo': 15,
                'orden': 5,
                'preguntas': [
                    {
                        'enunciado': '¿Qué es la recursividad?',
                        'dificultad': 'Media',
                        'puntuacion': 15,
                        'respuestas': [
                            {'contenido': 'Cuando una función se llama a sí misma', 'correcta': True},
                            {'contenido': 'Cuando se usan bucles', 'correcta': False},
                            {'contenido': 'Cuando hay muchas funciones', 'correcta': False},
                            {'contenido': 'Cuando se repite código', 'correcta': False},
                        ]
                    },
                    {
                        'enunciado': '¿Qué es esencial en una función recursiva para evitar bucles infinitos?',
                        'dificultad': 'Media',
                        'puntuacion': 15,
                        'respuestas': [
                            {'contenido': 'Un caso base que detenga la recursión', 'correcta': True},
                            {'contenido': 'Usar variables globales', 'correcta': False},
                            {'contenido': 'Tener muchos parámetros', 'correcta': False},
                            {'contenido': 'Usar solo números enteros', 'correcta': False},
                        ]
                    },
                    {
                        'enunciado': '¿Cuál es una ventaja de la recursividad?',
                        'dificultad': 'Media',
                        'puntuacion': 15,
                        'respuestas': [
                            {'contenido': 'Código más elegante y fácil de entender para problemas naturalmente recursivos', 'correcta': True},
                            {'contenido': 'Siempre es más rápida que iteración', 'correcta': False},
                            {'contenido': 'Usa menos memoria', 'correcta': False},
                            {'contenido': 'No necesita caso base', 'correcta': False},
                        ]
                    },
                ]
            },
            'Test 1.6 - Ordenamiento Básico': {
                'nivel': 'Media',
                'tiempo': 15,
                'orden': 6,
                'preguntas': [
                    {
                        'enunciado': '¿Cuál es la idea básica del algoritmo de ordenamiento por burbuja (bubble sort)?',
                        'dificultad': 'Media',
                        'puntuacion': 15,
                        'respuestas': [
                            {'contenido': 'Comparar elementos adyacentes e intercambiarlos si están en orden incorrecto', 'correcta': True},
                            {'contenido': 'Dividir el array en mitades recursivamente', 'correcta': False},
                            {'contenido': 'Buscar el mínimo en cada iteración', 'correcta': False},
                            {'contenido': 'Insertar elementos en posiciones ordenadas', 'correcta': False},
                        ]
                    },
                    {
                        'enunciado': '¿Cuál es la complejidad temporal promedio de Bubble Sort?',
                        'dificultad': 'Media',
                        'puntuacion': 15,
                        'respuestas': [
                            {'contenido': 'O(n²)', 'correcta': True},
                            {'contenido': 'O(n log n)', 'correcta': False},
                            {'contenido': 'O(n)', 'correcta': False},
                            {'contenido': 'O(1)', 'correcta': False},
                        ]
                    },
                    {
                        'enunciado': '¿Qué algoritmo de ordenamiento es generalmente más eficiente?',
                        'dificultad': 'Media',
                        'puntuacion': 15,
                        'respuestas': [
                            {'contenido': 'Quick Sort o Merge Sort', 'correcta': True},
                            {'contenido': 'Bubble Sort', 'correcta': False},
                            {'contenido': 'Selection Sort', 'correcta': False},
                            {'contenido': 'Insertion Sort', 'correcta': False},
                        ]
                    },
                ]
            },
            # NIVEL DIFÍCIL - 3 tests
            'Test 1.7 - Complejidad Avanzada': {
                'nivel': 'Dificil',
                'tiempo': 20,
                'orden': 7,
                'preguntas': [
                    {
                        'enunciado': '¿Cuál es la complejidad de la búsqueda binaria?',
                        'dificultad': 'Dificil',
                        'puntuacion': 20,
                        'respuestas': [
                            {'contenido': 'O(log n)', 'correcta': True},
                            {'contenido': 'O(n)', 'correcta': False},
                            {'contenido': 'O(n²)', 'correcta': False},
                            {'contenido': 'O(1)', 'correcta': False},
                        ]
                    },
                    {
                        'enunciado': '¿Qué requisito debe cumplir un array para aplicar búsqueda binaria?',
                        'dificultad': 'Dificil',
                        'puntuacion': 20,
                        'respuestas': [
                            {'contenido': 'Debe estar ordenado', 'correcta': True},
                            {'contenido': 'Debe tener tamaño par', 'correcta': False},
                            {'contenido': 'Debe contener solo números', 'correcta': False},
                            {'contenido': 'No debe tener duplicados', 'correcta': False},
                        ]
                    },
                    {
                        'enunciado': 'En el análisis de complejidad, ¿qué significa la notación Θ (Theta)?',
                        'dificultad': 'Dificil',
                        'puntuacion': 20,
                        'respuestas': [
                            {'contenido': 'Cota ajustada (tight bound): el algoritmo crece exactamente a esa tasa', 'correcta': True},
                            {'contenido': 'Solo el peor caso', 'correcta': False},
                            {'contenido': 'Solo el mejor caso', 'correcta': False},
                            {'contenido': 'Complejidad espacial únicamente', 'correcta': False},
                        ]
                    },
                ]
            },
            'Test 1.8 - Divide y Vencerás': {
                'nivel': 'Dificil',
                'tiempo': 20,
                'orden': 8,
                'preguntas': [
                    {
                        'enunciado': '¿Qué es la técnica "Divide y Vencerás"?',
                        'dificultad': 'Dificil',
                        'puntuacion': 20,
                        'respuestas': [
                            {'contenido': 'Dividir el problema en subproblemas, resolverlos y combinar las soluciones', 'correcta': True},
                            {'contenido': 'Usar muchas variables globales', 'correcta': False},
                            {'contenido': 'Probar todas las soluciones posibles', 'correcta': False},
                            {'contenido': 'Usar solo bucles for', 'correcta': False},
                        ]
                    },
                    {
                        'enunciado': '¿Cuál de estos algoritmos usa "Divide y Vencerás"?',
                        'dificultad': 'Dificil',
                        'puntuacion': 20,
                        'respuestas': [
                            {'contenido': 'Merge Sort', 'correcta': True},
                            {'contenido': 'Bubble Sort', 'correcta': False},
                            {'contenido': 'Selection Sort', 'correcta': False},
                            {'contenido': 'Insertion Sort', 'correcta': False},
                        ]
                    },
                    {
                        'enunciado': '¿Cuál es la complejidad temporal de Merge Sort?',
                        'dificultad': 'Dificil',
                        'puntuacion': 20,
                        'respuestas': [
                            {'contenido': 'O(n log n)', 'correcta': True},
                            {'contenido': 'O(n²)', 'correcta': False},
                            {'contenido': 'O(n)', 'correcta': False},
                            {'contenido': 'O(log n)', 'correcta': False},
                        ]
                    },
                ]
            },
            'Test 1.9 - Programación Dinámica': {
                'nivel': 'Dificil',
                'tiempo': 20,
                'orden': 9,
                'preguntas': [
                    {
                        'enunciado': '¿Qué es la programación dinámica?',
                        'dificultad': 'Dificil',
                        'puntuacion': 20,
                        'respuestas': [
                            {'contenido': 'Técnica que resuelve problemas almacenando resultados de subproblemas para evitar recálculos', 'correcta': True},
                            {'contenido': 'Programar en varios lenguajes a la vez', 'correcta': False},
                            {'contenido': 'Usar solo variables dinámicas', 'correcta': False},
                            {'contenido': 'Programar sin planificar', 'correcta': False},
                        ]
                    },
                    {
                        'enunciado': '¿Cuál es un ejemplo clásico de programación dinámica?',
                        'dificultad': 'Dificil',
                        'puntuacion': 20,
                        'respuestas': [
                            {'contenido': 'Cálculo de números de Fibonacci con memoización', 'correcta': True},
                            {'contenido': 'Bubble Sort', 'correcta': False},
                            {'contenido': 'Búsqueda lineal', 'correcta': False},
                            {'contenido': 'Imprimir un array', 'correcta': False},
                        ]
                    },
                    {
                        'enunciado': '¿Qué ventaja ofrece la memoización en programación dinámica?',
                        'dificultad': 'Dificil',
                        'puntuacion': 20,
                        'respuestas': [
                            {'contenido': 'Reduce la complejidad temporal evitando cálculos repetidos', 'correcta': True},
                            {'contenido': 'Usa menos variables', 'correcta': False},
                            {'contenido': 'Hace el código más largo', 'correcta': False},
                            {'contenido': 'Elimina todos los bucles', 'correcta': False},
                        ]
                    },
                ]
            },
        }
        
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS(f'Creando {tema_id} - 9 tests (3 por nivel)'))
        self.stdout.write(self.style.SUCCESS('='*70))
        
        with transaction.atomic():
            tema = Tema.objects.get(tema_id=tema_id)
            
            ultima_pregunta = Pregunta.objects.order_by('-pregunta_id').first()
            siguiente_id = (ultima_pregunta.pregunta_id + 1) if ultima_pregunta else 1
            
            tests_creados = 0
            preguntas_creadas = 0
            test_previo_nivel = None
            nivel_actual = None
            
            for test_nombre, test_info in tests_data.items():
                nivel = test_info['nivel']
                
                # Si cambiamos de nivel, resetear el test previo
                if nivel != nivel_actual:
                    test_previo_nivel = None
                    nivel_actual = nivel
                    nombre_nivel = {'Facil': 'FÁCIL', 'Media': 'INTERMEDIO', 'Dificil': 'DIFÍCIL'}[nivel]
                    self.stdout.write(f'\nNivel {nombre_nivel}:')
                
                # Crear preguntas
                ids_preguntas = []
                for preg_data in test_info['preguntas']:
                    pregunta = Pregunta.objects.create(
                        pregunta_id=siguiente_id,
                        tema=tema_id,
                        enunciado=preg_data['enunciado'],
                        dificultad=preg_data['dificultad'],
                        puntuacion=preg_data['puntuacion'],
                    )
                    ids_preguntas.append(siguiente_id)
                    
                    resp_id = 1
                    for resp_data in preg_data['respuestas']:
                        Respuesta.objects.create(
                            respuesta_id=f"{siguiente_id}_{resp_id}",
                            pregunta_id=siguiente_id,
                            contenido=resp_data['contenido'],
                            solucion='Correcta' if resp_data['correcta'] else 'Incorrecta',
                        )
                        resp_id += 1
                    
                    preguntas_creadas += 1
                    siguiente_id += 1
                
                # Crear test
                test, created = Test.objects.get_or_create(
                    tema=tema,
                    nombre=test_nombre,
                    defaults={
                        'descripcion': f'Test {test_info["orden"]} de nivel {nivel.lower()}',
                        'tiempo_limite': test_info['tiempo'],
                        'visible_alumnos': visible and nivel == 'Facil',  # Solo tests fáciles visibles
                        'activo': True,
                        'test_requisito': test_previo_nivel,
                        'porcentaje_minimo': 70.0 if test_previo_nivel else 0.0,
                    }
                )
                
                test.preguntas.set(Pregunta.objects.filter(pregunta_id__in=ids_preguntas))
                
                if created:
                    tests_creados += 1
                    req_text = f' → Requiere: {test_previo_nivel.nombre[:40]}...' if test_previo_nivel else ' → Sin requisitos'
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {test_nombre}') + req_text)
                
                test_previo_nivel = test
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('RESUMEN:'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Tests creados: {tests_creados}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Preguntas creadas: {preguntas_creadas}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Visibles inicialmente: Solo 3 tests fáciles'))
        self.stdout.write('='*70 + '\n')
