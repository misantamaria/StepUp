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
            {"username": "paula_herrera", "first_name": "Paula", "last_name": "Herrera", "email": "paula.herrera@alumnos.upm.es", "perfil": "bajo"},
            {"username": "miguel_jimenez", "first_name": "Miguel", "last_name": "Jiménez", "email": "miguel.jimenez@alumnos.upm.es", "perfil": "riesgo"},
            {"username": "elena_morales", "first_name": "Elena", "last_name": "Morales", "email": "elena.morales@alumnos.upm.es", "perfil": "bajo"},
        ]
        
        # Alumnos Clase B (9 alumnos)
        alumnos_clase_b = [
            {"username": "roberto_silva", "first_name": "Roberto", "last_name": "Silva", "email": "roberto.silva@alumnos.upm.es", "perfil": "excelente_especial"},  # El especialmente bueno
            {"username": "maria_castro", "first_name": "María", "last_name": "Castro", "email": "maria.castro@alumnos.upm.es", "perfil": "bueno"},
            {"username": "pedro_vargas", "first_name": "Pedro", "last_name": "Vargas", "email": "pedro.vargas@alumnos.upm.es", "perfil": "bueno"},
            {"username": "carmen_ramos", "first_name": "Carmen", "last_name": "Ramos", "email": "carmen.ramos@alumnos.upm.es", "perfil": "bueno"},
            {"username": "alberto_ortega", "first_name": "Alberto", "last_name": "Ortega", "email": "alberto.ortega@alumnos.upm.es", "perfil": "regular"},
            {"username": "natalia_cruz", "first_name": "Natalia", "last_name": "Cruz", "email": "natalia.cruz@alumnos.upm.es", "perfil": "regular"},
            {"username": "diego_mendez", "first_name": "Diego", "last_name": "Méndez", "email": "diego.mendez@alumnos.upm.es", "perfil": "bajo"},
            {"username": "julia_vega", "first_name": "Julia", "last_name": "Vega", "email": "julia.vega@alumnos.upm.es", "perfil": "riesgo"},
            {"username": "sergio_blanco", "first_name": "Sergio", "last_name": "Blanco", "email": "sergio.blanco@alumnos.upm.es", "perfil": "bajo"},
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
        
        # Generar datos simulados de rendimiento (opcional para demo)
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
        """Genera algunos intentos de test simulados para demo (opcional)"""
        from boards.models import Test, IntentTest
        
        # Solo si existen tests en el sistema
        tests_disponibles = Test.objects.filter(activo=True, visible_alumnos=True)
        if not tests_disponibles.exists():
            self.stdout.write(self.style.WARNING("No hay tests disponibles para generar datos de demo"))
            return
        
        # Perfiles de rendimiento
        perfiles_rendimiento = {
            "excelente_especial": {"min": 85, "max": 98, "completados": 0.9},  # Roberto - especialmente bueno
            "excelente": {"min": 80, "max": 95, "completados": 0.8},  # Ana
            "bueno": {"min": 65, "max": 85, "completados": 0.7},
            "regular": {"min": 50, "max": 70, "completados": 0.6},
            "bajo": {"min": 35, "max": 55, "completados": 0.4},
            "riesgo": {"min": 20, "max": 40, "completados": 0.3},  # Los dos en riesgo
        }
        
        alumnos_con_perfil = [
            ("ana_garcia", "excelente"),
            ("carlos_ruiz", "bueno"),
            ("lucia_martin", "bueno"),
            ("david_lopez", "regular"),
            ("sara_gonzalez", "regular"),
            ("javier_torres", "regular"),
            ("paula_herrera", "bajo"),
            ("miguel_jimenez", "riesgo"),
            ("elena_morales", "bajo"),
            ("roberto_silva", "excelente_especial"),  # Especialmente bueno
            ("maria_castro", "bueno"),
            ("pedro_vargas", "bueno"),
            ("carmen_ramos", "bueno"),
            ("alberto_ortega", "regular"),
            ("natalia_cruz", "regular"),
            ("diego_mendez", "bajo"),
            ("julia_vega", "riesgo"),  # En riesgo
            ("sergio_blanco", "bajo"),
        ]
        
        self.stdout.write("\nGenerando datos de rendimiento demo...")
        
        # Tomar solo algunos tests para la demo
        tests_demo = list(tests_disponibles[:3])  # Primeros 3 tests
        
        for username, perfil in alumnos_con_perfil:
            try:
                user = User.objects.get(username=username)
                config = perfiles_rendimiento[perfil]
                
                # Determinar cuántos tests completará este alumno
                num_tests = int(len(tests_demo) * config["completados"])
                tests_a_completar = random.sample(tests_demo, min(num_tests, len(tests_demo)))
                
                for test in tests_a_completar:
                    # Verificar si ya existe un intento para este test
                    if IntentTest.objects.filter(alumno=user, test=test, completado=True).exists():
                        continue
                        
                    # Generar puntuación según el perfil
                    puntuacion = random.randint(config["min"], config["max"])
                    total_preguntas = test.preguntas.count() or 10  # Default 10 si no hay preguntas
                    respuestas_correctas = int((puntuacion / 100) * total_preguntas)
                    
                    # Crear intento
                    from django.utils import timezone
                    import datetime
                    
                    fecha_inicio = timezone.now() - datetime.timedelta(
                        days=random.randint(1, 30),
                        hours=random.randint(1, 23),
                        minutes=random.randint(1, 59)
                    )
                    
                    IntentTest.objects.create(
                        alumno=user,
                        test=test,
                        fecha_inicio=fecha_inicio,
                        fecha_fin=fecha_inicio + datetime.timedelta(minutes=random.randint(15, 45)),
                        completado=True,
                        puntuacion=puntuacion,
                        total_preguntas=total_preguntas,
                        respuestas_correctas=respuestas_correctas
                    )
                    
            except User.DoesNotExist:
                continue
        
        self.stdout.write("✓ Datos de rendimiento demo generados")