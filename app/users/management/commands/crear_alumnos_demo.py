from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from users.models import UserProfile
import random


class Command(BaseCommand):
    help = "Crea 18 alumnos distribuidos en 2 clases con perfiles de rendimiento realistas"

    def handle(self, *args, **options):
        # Obtener el grupo de alumnos
        try:
            grupo_alumnos = Group.objects.get(name='Alumnos')
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR("Error: El grupo 'Alumnos' no existe. Ejecuta primero 'python manage.py initusers'"))
            return

        # Definir las dos clases
        clase_a = "Clase A"
        clase_b = "Clase B"
        
        # Alumnos Clase A (9 alumnos)
        alumnos_clase_a = [
            {"username": "ana_garcia", "first_name": "Ana", "last_name": "García", "email": "ana.garcia@alumnos.upm.es", "perfil": "excelente"},
            {"username": "carlos_ruiz", "first_name": "Carlos", "last_name": "Ruiz", "email": "carlos.ruiz@alumnos.upm.es", "perfil": "bueno"},
            {"username": "lucia_martin", "first_name": "Lucía", "last_name": "Martín", "email": "lucia.martin@alumnos.upm.es", "perfil": "bueno"},
            {"username": "david_lopez", "first_name": "David", "last_name": "López", "email": "david.lopez@alumnos.upm.es", "perfil": "regular"},
            {"username": "sara_gonzalez", "first_name": "Sara", "last_name": "González", "email": "sara.gonzalez@alumnos.upm.es", "perfil": "regular"},
            {"username": "javier_torres", "first_name": "Javier", "last_name": "Torres", "email": "javier.torres@alumnos.upm.es", "perfil": "regular"},
            {"username": "paula_herrera", "first_name": "Paula", "last_name": "Herrera", "email": "paula.herrera@alumnos.upm.es", "perfil": "regular"},
            {"username": "miguel_jimenez", "first_name": "Miguel", "last_name": "Jiménez", "email": "miguel.jimenez@alumnos.upm.es", "perfil": "bajo"},
            {"username": "elena_morales", "first_name": "Elena", "last_name": "Morales", "email": "elena.morales@alumnos.upm.es", "perfil": "riesgo"},
        ]
        
        # Alumnos Clase B (9 alumnos)
        alumnos_clase_b = [
            {"username": "roberto_silva", "first_name": "Roberto", "last_name": "Silva", "email": "roberto.silva@alumnos.upm.es", "perfil": "excelente_especial"},  # El especialmente bueno
            {"username": "maria_castro", "first_name": "María", "last_name": "Castro", "email": "maria.castro@alumnos.upm.es", "perfil": "bueno"},
            {"username": "pedro_vargas", "first_name": "Pedro", "last_name": "Vargas", "email": "pedro.vargas@alumnos.upm.es", "perfil": "bueno"},
            {"username": "carmen_ramos", "first_name": "Carmen", "last_name": "Ramos", "email": "carmen.ramos@alumnos.upm.es", "perfil": "bueno"},
            {"username": "alberto_ortega", "first_name": "Alberto", "last_name": "Ortega", "email": "alberto.ortega@alumnos.upm.es", "perfil": "regular"},
            {"username": "natalia_cruz", "first_name": "Natalia", "last_name": "Cruz", "email": "natalia.cruz@alumnos.upm.es", "perfil": "regular"},
            {"username": "diego_mendez", "first_name": "Diego", "last_name": "Méndez", "email": "diego.mendez@alumnos.upm.es", "perfil": "regular"},
            {"username": "julia_vega", "first_name": "Julia", "last_name": "Vega", "email": "julia.vega@alumnos.upm.es", "perfil": "bajo"},
            {"username": "sergio_blanco", "first_name": "Sergio", "last_name": "Blanco", "email": "sergio.blanco@alumnos.upm.es", "perfil": "riesgo"},
        ]
        
        # Crear alumnos
        alumnos_creados = 0
        alumnos_actualizados = 0
        
        for clase_nombre, alumnos in [(clase_a, alumnos_clase_a), (clase_b, alumnos_clase_b)]:
            for alumno_data in alumnos:
                username = alumno_data["username"]
                
                # Crear o actualizar usuario
                if User.objects.filter(username=username).exists():
                    user = User.objects.get(username=username)
                    user.first_name = alumno_data["first_name"]
                    user.last_name = alumno_data["last_name"]
                    user.email = alumno_data["email"]
                    user.is_staff = False
                    user.is_superuser = False
                    user.set_password("alumno123")  # Contraseña estándar para todos
                    user.save()
                    alumnos_actualizados += 1
                    action = "actualizado"
                else:
                    user = User.objects.create_user(
                        username=username,
                        password="alumno123",
                        email=alumno_data["email"],
                        first_name=alumno_data["first_name"],
                        last_name=alumno_data["last_name"],
                        is_staff=False
                    )
                    alumnos_creados += 1
                    action = "creado"
                
                # Asignar al grupo de alumnos
                user.groups.clear()
                user.groups.add(grupo_alumnos)
                
                # Crear o actualizar perfil
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.grupo = clase_nombre
                profile.save()
                
                self.stdout.write(f"  {action}: {user.first_name} {user.last_name} ({username}) - {clase_nombre} - Perfil: {alumno_data['perfil']}")
        
        # Crear tests y temas básicos si no existen
        self._crear_tests_basicos()
        
        # Generar datos simulados de rendimiento con fechas recientes
        self._generar_datos_rendimiento()
        
        # Resumen
        self.stdout.write(self.style.SUCCESS(f"\n=== RESUMEN ==="))
        self.stdout.write(f"Alumnos creados: {alumnos_creados}")
        self.stdout.write(f"Alumnos actualizados: {alumnos_actualizados}")
        self.stdout.write(f"Total procesados: {alumnos_creados + alumnos_actualizados}")
        
        # Mostrar distribución por clases
        clase_a_count = UserProfile.objects.filter(grupo=clase_a).count()
        clase_b_count = UserProfile.objects.filter(grupo=clase_b).count()
        
        self.stdout.write(f"\nDistribución por clases:")
        self.stdout.write(f"  {clase_a}: {clase_a_count} alumnos")
        self.stdout.write(f"  {clase_b}: {clase_b_count} alumnos")
        
        self.stdout.write(self.style.SUCCESS(f"\n✓ Configuración de alumnos demo completada"))
        self.stdout.write(self.style.HTTP_INFO("Contraseña para todos los alumnos: alumno123"))

    def _generar_datos_rendimiento(self):
        """Genera algunos intentos de test simulados para demo con fechas recientes"""
        from boards.models import Test, IntentTest
        from django.utils import timezone
        from django.contrib.auth.models import User
        import datetime
        
        # Solo si existen tests en el sistema
        tests_disponibles = Test.objects.filter(activo=True, visible_alumnos=True)
        if not tests_disponibles.exists():
            self.stdout.write(self.style.WARNING("No hay tests disponibles para generar datos de demo"))
            return
        
        # Perfiles de rendimiento (ajustados para promedio ~6.8) - puntuaciones sobre 10
        perfiles_rendimiento = {
            "excelente_especial": {"min": 8.8, "max": 9.8, "completados": 0.9},  # Roberto - especialmente bueno
            "excelente": {"min": 8.0, "max": 9.5, "completados": 0.8},  # Ana
            "bueno": {"min": 6.8, "max": 8.5, "completados": 0.75},  # Mejorado
            "regular": {"min": 5.5, "max": 7.0, "completados": 0.65},  # Mejorado
            "bajo": {"min": 4.5, "max": 6.0, "completados": 0.5},  # Mejorado - ya no están en riesgo crítico
            "riesgo": {"min": 3.0, "max": 4.5, "completados": 0.35},  # Solo 2 alumnos en riesgo real
        }
        
        alumnos_con_perfil = [
            ("ana_garcia", "excelente"),
            ("carlos_ruiz", "bueno"),
            ("lucia_martin", "bueno"),
            ("david_lopez", "regular"),
            ("sara_gonzalez", "regular"),
            ("javier_torres", "regular"),
            ("paula_herrera", "regular"),  # Mejorado de bajo a regular
            ("miguel_jimenez", "bajo"),  # Mejorado de riesgo a bajo
            ("elena_morales", "riesgo"),  # Sigue en riesgo
            ("roberto_silva", "excelente_especial"),  # Especialmente bueno
            ("maria_castro", "bueno"),
            ("pedro_vargas", "bueno"),
            ("carmen_ramos", "bueno"),
            ("alberto_ortega", "regular"),
            ("natalia_cruz", "regular"),
            ("diego_mendez", "regular"),  # Mejorado de bajo a regular
            ("julia_vega", "bajo"),  # Mejorado de riesgo a bajo
            ("sergio_blanco", "riesgo"),  # Sigue en riesgo
        ]
        
        self.stdout.write("\nGenerando datos de rendimiento demo con actividad reciente...")
        
        # Obtener tests visibles para los alumnos
        tests_tema1 = Test.objects.filter(tema__tema_id='Tema 1 - Conceptos básicos', visible_alumnos=True, activo=True)
        examenes = Test.objects.filter(tema__tema_id='Exámenes', visible_alumnos=True, disponible_alumno=True, activo=True)
        todos_tests = list(tests_tema1) + list(examenes)
        
        if not todos_tests:
            self.stdout.write(self.style.WARNING("No hay tests visibles disponibles"))
            return
            
        # Limpiar intentos anteriores del demo
        IntentTest.objects.filter(alumno__username__in=[u[0] for u in alumnos_con_perfil]).delete()
        
        ahora = timezone.now()
        
        for username, perfil in alumnos_con_perfil:
            try:
                user = User.objects.get(username=username)
                config = perfiles_rendimiento[perfil]
                
                # Cada alumno tendrá entre 2 y 5 intentos en la última semana
                num_intentos = random.randint(2, 5)
                tests_seleccionados = random.sample(todos_tests, min(num_intentos, len(todos_tests)))
                
                for i, test in enumerate(tests_seleccionados):
                    # Verificar si ya existe un intento para este test
                    if IntentTest.objects.filter(alumno=user, test=test).exists():
                        continue
                    
                    # Generar puntuación según el perfil (sobre 10)
                    puntuacion = round(random.uniform(config["min"], config["max"]), 2)
                    total_preguntas = max(test.preguntas.count(), 3)  # Mínimo 3 preguntas
                    respuestas_correctas = int((puntuacion / 10) * total_preguntas)
                    
                    # Generar fecha en la última semana (más actividad reciente)
                    dias_atras = random.randint(0, 6)  # Últimos 7 días
                    horas_atras = random.randint(1, 23)
                    minutos_atras = random.randint(1, 59)
                    
                    fecha_inicio = ahora - datetime.timedelta(
                        days=dias_atras,
                        hours=horas_atras,
                        minutes=minutos_atras
                    )
                    
                    duracion = random.randint(10, min(test.tiempo_limite, 45))  # Duración realista
                    fecha_fin = fecha_inicio + datetime.timedelta(minutes=duracion)
                    
                    # Crear intento
                    IntentTest.objects.create(
                        alumno=user,
                        test=test,
                        fecha_inicio=fecha_inicio,
                        fecha_fin=fecha_fin,
                        completado=True,
                        puntuacion=puntuacion,
                        total_preguntas=total_preguntas,
                        respuestas_correctas=respuestas_correctas,
                        es_examen=test.es_aleatorio
                    )
                    
            except User.DoesNotExist:
                continue
        
        # Mostrar resumen de actividad generada
        total_intentos = IntentTest.objects.filter(
            alumno__username__in=[u[0] for u in alumnos_con_perfil],
            completado=True
        ).count()
        
        # Intentos en la última semana
        hace_7_dias = ahora - datetime.timedelta(days=7)
        intentos_semana = IntentTest.objects.filter(
            alumno__username__in=[u[0] for u in alumnos_con_perfil],
            fecha_inicio__gte=hace_7_dias,
            completado=True
        ).count()
        
        self.stdout.write(f"✓ {total_intentos} intentos generados ({intentos_semana} en la última semana)")
        self.stdout.write("✓ Datos de rendimiento demo generados")

    def _crear_tests_basicos(self):
        """Crea tests básicos y examenes aleatorios"""
        from boards.models import Test, Tema, Pregunta
        from django.utils import timezone
        from django.contrib.auth.models import User
        
        # Limpiar tema duplicado
        tema_pilas_duplicado = Tema.objects.filter(tema_id='Tema 1 - Pilas').first()
        if tema_pilas_duplicado:
            self.stdout.write("🗑️ Eliminando tema duplicado 'Tema 1 - Pilas'...")
            tema_pilas_duplicado.delete()
        
        # Obtener temas principales
        try:
            tema1 = Tema.objects.get(tema_id='Tema 1 - Conceptos básicos')
            tema2 = Tema.objects.get(tema_id='Tema 2 - Pilas y colas')
            tema3 = Tema.objects.get(tema_id='Tema 3 - Listas')
        except Tema.DoesNotExist:
            self.stdout.write(self.style.ERROR("Error: Los temas no existen. Ejecuta primero 'crear_estructura_completa'"))
            return
        
        # Crear tests básicos para temas 2 y 3 si no existen
        self._crear_tests_tema2(tema2)
        self._crear_tests_tema3(tema3)
        
        # Crear tema especial para exámenes
        tema_examenes, created = Tema.objects.get_or_create(
            tema_id='Exámenes',
            defaults={
                'visible_alumnos': True,
                'disponible_alumno': True,
                'activo': True
            }
        )
        if created:
            self.stdout.write("✓ Tema 'Exámenes' creado")
        
        # Crear exámenes aleatorios
        self._crear_examenes_aleatorios(tema_examenes)
        
        self.stdout.write("✓ Tests básicos y exámenes creados")
        
    def _crear_tests_tema2(self, tema):
        """Crea tests básicos para el Tema 2 - Pilas y colas"""
        from boards.models import Test, Pregunta
        
        tests_info = [
            {
                'nombre': 'Test 2.1 - Pilas básicas',
                'nivel': 'Facil',
                'tiempo': 15,
                'preguntas': [
                    {'enunciado': '¿Qué significa LIFO en el contexto de pilas?', 'dificultad': 'Facil', 'puntuacion': 10},
                    {'enunciado': '¿Cuál es la operación que añade un elemento a una pila?', 'dificultad': 'Facil', 'puntuacion': 10},
                ]
            },
            {
                'nombre': 'Test 2.2 - Colas básicas', 
                'nivel': 'Facil',
                'tiempo': 15,
                'preguntas': [
                    {'enunciado': '¿Qué significa FIFO en el contexto de colas?', 'dificultad': 'Facil', 'puntuacion': 10},
                    {'enunciado': '¿Cuál es la operación que añade un elemento a una cola?', 'dificultad': 'Facil', 'puntuacion': 10},
                ]
            },
            {
                'nombre': 'Test 2.3 - Pilas y colas intermedias',
                'nivel': 'Media', 
                'tiempo': 20,
                'preguntas': [
                    {'enunciado': '¿Cuál es la complejidad temporal de push en una pila?', 'dificultad': 'Media', 'puntuacion': 15},
                    {'enunciado': '¿Cómo implementar una cola con dos pilas?', 'dificultad': 'Media', 'puntuacion': 15},
                ]
            }
        ]
        
        for test_info in tests_info:
            test, created = Test.objects.get_or_create(
                nombre=test_info['nombre'],
                tema=tema,
                defaults={
                    'nivel': test_info['nivel'],
                    'tiempo_limite': test_info['tiempo'],
                    'visible_alumnos': False,  # No visible hasta completar tema 1
                    'disponible_alumno': False,
                    'activo': True
                }
            )
            
            if created:
                self.stdout.write(f"  ✓ {test_info['nombre']} creado")
                # Crear preguntas básicas
                for i, pregunta_info in enumerate(test_info['preguntas']):
                    Pregunta.objects.get_or_create(
                        pregunta_id=f"{test.id}{i+1:03d}",
                        defaults={
                            'tema': tema.tema_id,
                            'enunciado': pregunta_info['enunciado'],
                            'dificultad': pregunta_info['dificultad'],
                            'puntuacion': pregunta_info['puntuacion']
                        }
                    )

    def _crear_tests_tema3(self, tema):
        """Crea tests básicos para el Tema 3 - Listas"""
        from boards.models import Test, Pregunta
        
        tests_info = [
            {
                'nombre': 'Test 3.1 - Arrays básicos',
                'nivel': 'Facil',
                'tiempo': 15, 
                'preguntas': [
                    {'enunciado': '¿Qué es un array o arreglo?', 'dificultad': 'Facil', 'puntuacion': 10},
                    {'enunciado': '¿Cuál es la complejidad de acceso a un elemento en un array?', 'dificultad': 'Facil', 'puntuacion': 10},
                ]
            },
            {
                'nombre': 'Test 3.2 - Listas enlazadas',
                'nivel': 'Facil', 
                'tiempo': 15,
                'preguntas': [
                    {'enunciado': '¿Qué es una lista enlazada?', 'dificultad': 'Facil', 'puntuacion': 10},
                    {'enunciado': '¿Cuál es la ventaja principal de las listas enlazadas sobre los arrays?', 'dificultad': 'Facil', 'puntuacion': 10},
                ]
            },
            {
                'nombre': 'Test 3.3 - Listas avanzadas',
                'nivel': 'Media',
                'tiempo': 20,
                'preguntas': [
                    {'enunciado': '¿Qué es una lista doblemente enlazada?', 'dificultad': 'Media', 'puntuacion': 15},
                    {'enunciado': '¿Cuándo usar arrays vs listas enlazadas?', 'dificultad': 'Media', 'puntuacion': 15},
                ]
            }
        ]
        
        for test_info in tests_info:
            test, created = Test.objects.get_or_create(
                nombre=test_info['nombre'],
                tema=tema,
                defaults={
                    'nivel': test_info['nivel'],
                    'tiempo_limite': test_info['tiempo'],
                    'visible_alumnos': False,  # No visible hasta completar tema anterior
                    'disponible_alumno': False,
                    'activo': True
                }
            )
            
            if created:
                self.stdout.write(f"  ✓ {test_info['nombre']} creado")
                # Crear preguntas básicas
                for i, pregunta_info in enumerate(test_info['preguntas']):
                    Pregunta.objects.get_or_create(
                        pregunta_id=f"{test.id}{i+1:03d}",
                        defaults={
                            'tema': tema.tema_id,
                            'enunciado': pregunta_info['enunciado'],
                            'dificultad': pregunta_info['dificultad'],
                            'puntuacion': pregunta_info['puntuacion']
                        }
                    )

    def _crear_examenes_aleatorios(self, tema_examenes):
        """Crea exámenes aleatorios con preguntas de múltiples temas"""
        from boards.models import Test
        
        examenes_info = [
            {
                'nombre': 'Examen Parcial 1',
                'descripcion': 'Examen parcial de los 3 primeros temas',
                'tiempo': 60,
                'visible': True,
                'disponible': True,
                'configuracion': {
                    'Tema 1 - Conceptos básicos': 6,
                    'Tema 2 - Pilas y colas': 4,
                    'Tema 3 - Listas': 4,
                }
            },
            {
                'nombre': 'Examen Final',
                'descripcion': 'Examen final de todos los temas',
                'tiempo': 90,
                'visible': True,
                'disponible': False,  # Se desbloqueará después
                'configuracion': {
                    'Tema 1 - Conceptos básicos': 8,
                    'Tema 2 - Pilas y colas': 6,
                    'Tema 3 - Listas': 6,
                }
            }
        ]
        
        for examen_info in examenes_info:
            examen, created = Test.objects.get_or_create(
                nombre=examen_info['nombre'],
                tema=tema_examenes,
                defaults={
                    'descripcion': examen_info['descripcion'],
                    'tiempo_limite': examen_info['tiempo'],
                    'es_aleatorio': True,
                    'configuracion_aleatoria': examen_info['configuracion'],
                    'visible_alumnos': examen_info['visible'],
                    'disponible_alumno': examen_info['disponible'],
                    'activo': True,
                    'nivel': 'Media'  # Nivel intermedio para exámenes
                }
            )
            
            if created:
                self.stdout.write(f"  ✓ {examen_info['nombre']} - {'Disponible' if examen_info['disponible'] else 'Bloqueado'}")
                
        self.stdout.write("✓ Exámenes aleatorios creados")