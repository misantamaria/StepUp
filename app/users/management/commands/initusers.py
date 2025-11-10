from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
import os


class Command(BaseCommand):
    help = "Crea usuarios y configura permisos para StepUp: alumno, profesor, profesor_ayudante, admin"

    def handle(self, *args, **options):
        from boards.models import Pregunta, Test, IntentTest, RespuestaAlumno
        
        # Crear grupos si no existen
        grupo_alumnos, _ = Group.objects.get_or_create(name='Alumnos')
        grupo_profesores, _ = Group.objects.get_or_create(name='Profesores')
        grupo_profesores_ayudantes, _ = Group.objects.get_or_create(name='Profesores Ayudantes')
        
        # Configurar permisos de grupos
        self._configurar_permisos_grupos(grupo_alumnos, grupo_profesores, grupo_profesores_ayudantes)
        
        # 1. ALUMNO - Usuario regular que hace tests
        alumno_username = "alumno"
        alumno_password = "alumno"
        alumno_email = os.getenv('ALUMNO_EMAIL', 'alumno@alumnos.upm.es')
        
        if User.objects.filter(username=alumno_username).exists():
            alumno = User.objects.get(username=alumno_username)
            alumno.email = alumno_email
            alumno.is_staff = False
            alumno.is_superuser = False
            alumno.set_password(alumno_password)
            alumno.save()
            self.stdout.write(self.style.WARNING(f"Usuario '{alumno_username}' actualizado"))
        else:
            alumno = User.objects.create_user(
                username=alumno_username, 
                password=alumno_password, 
                email=alumno_email
            )
            self.stdout.write(self.style.SUCCESS(f"Usuario '{alumno_username}' creado"))
        
        alumno.groups.clear()
        alumno.groups.add(grupo_alumnos)
        
        # 2. PROFESOR - Puede gestionar preguntas y ver resultados
        profesor_username = "profesor"
        profesor_password = "profesor"
        profesor_email = os.getenv('PROFESOR_EMAIL', 'profesor@upm.es')
        
        if User.objects.filter(username=profesor_username).exists():
            profesor = User.objects.get(username=profesor_username)
            profesor.email = profesor_email
            profesor.is_staff = True  # Puede acceder al admin
            profesor.is_superuser = False
            profesor.set_password(profesor_password)
            profesor.save()
            self.stdout.write(self.style.WARNING(f"Usuario '{profesor_username}' actualizado"))
        else:
            profesor = User.objects.create_user(
                username=profesor_username, 
                password=profesor_password, 
                email=profesor_email,
                is_staff=True  # Puede acceder al admin
            )
            self.stdout.write(self.style.SUCCESS(f"Usuario '{profesor_username}' creado"))
        
        profesor.groups.clear()
        profesor.groups.add(grupo_profesores)
        
        # 3. PROFESOR AYUDANTE - Puede crear preguntas pero no eliminar
        ayudante_username = "profesor_ayudante"
        ayudante_password = "ayudante"
        ayudante_email = "ayudante@upm.es"
        
        if User.objects.filter(username=ayudante_username).exists():
            ayudante = User.objects.get(username=ayudante_username)
            ayudante.email = ayudante_email
            ayudante.is_staff = True
            ayudante.is_superuser = False
            ayudante.set_password(ayudante_password)
            ayudante.save()
            self.stdout.write(self.style.WARNING(f"Usuario '{ayudante_username}' actualizado"))
        else:
            ayudante = User.objects.create_user(
                username=ayudante_username,
                password=ayudante_password,
                email=ayudante_email,
                is_staff=True
            )
            self.stdout.write(self.style.SUCCESS(f"Usuario '{ayudante_username}' creado"))
        
        ayudante.groups.clear()
        ayudante.groups.add(grupo_profesores_ayudantes)
        
        # 4. ADMIN - Administrador del sistema
        admin_username = "admin"
        admin_password = "admin"
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@upm.es')
        
        if User.objects.filter(username=admin_username).exists():
            admin = User.objects.get(username=admin_username)
            admin.email = admin_email
            admin.is_superuser = True
            admin.is_staff = True
            admin.set_password(admin_password)
            admin.save()
            self.stdout.write(self.style.WARNING(f"Usuario '{admin_username}' actualizado"))
        else:
            admin = User.objects.create_superuser(
                username=admin_username, 
                password=admin_password, 
                email=admin_email
            )
            self.stdout.write(self.style.SUCCESS(f"Superusuario '{admin_username}' creado"))
        
        # Mostrar resumen
        self.stdout.write(self.style.HTTP_INFO("\n--- Usuarios configurados ---"))
        self.stdout.write(self.style.SUCCESS(f"✓ alumno/alumno             - Alumno (hace tests, sin acceso admin)"))
        self.stdout.write(self.style.SUCCESS(f"✓ profesor/profesor         - Profesor (crea/edita/elimina preguntas y tests)"))
        self.stdout.write(self.style.SUCCESS(f"✓ profesor_ayudante/ayudante - Profesor Ayudante (crea/edita preguntas, NO elimina)"))
        self.stdout.write(self.style.SUCCESS(f"✓ admin/admin               - Administrador (gestiona todo)"))
    
    def _configurar_permisos_grupos(self, grupo_alumnos, grupo_profesores, grupo_profesores_ayudantes):
        """Configura los permisos específicos para cada grupo"""
        from boards.models import Pregunta, Test, IntentTest, RespuestaAlumno
        
        # Limpiar permisos anteriores
        grupo_alumnos.permissions.clear()
        grupo_profesores.permissions.clear()
        grupo_profesores_ayudantes.permissions.clear()
        
        # ContentTypes de los modelos
        ct_pregunta = ContentType.objects.get_for_model(Pregunta)
        ct_test = ContentType.objects.get_for_model(Test)
        ct_intenttest = ContentType.objects.get_for_model(IntentTest)
        ct_respuesta = ContentType.objects.get_for_model(RespuestaAlumno)
        
        # === ALUMNOS: Solo pueden ver sus propios intentos y respuestas (controlado por vistas) ===
        # No necesitan permisos de modelo en el admin porque no acceden
        
        # === PROFESORES: Control total sobre preguntas y tests ===
        permisos_profesor = Permission.objects.filter(
            content_type__in=[ct_pregunta, ct_test, ct_intenttest, ct_respuesta]
        )
        grupo_profesores.permissions.set(permisos_profesor)
        
        # === PROFESORES AYUDANTES: Pueden crear y editar, pero NO eliminar ===
        permisos_ayudante = Permission.objects.filter(
            content_type__in=[ct_pregunta, ct_test, ct_intenttest, ct_respuesta],
            codename__in=[
                # Pregunta
                'add_pregunta', 'change_pregunta', 'view_pregunta',
                # Test
                'add_test', 'change_test', 'view_test',
                # IntentTest (solo lectura)
                'view_intenttest',
                # RespuestaAlumno (solo lectura)
                'view_respuestaalumno',
            ]
        )
        grupo_profesores_ayudantes.permissions.set(permisos_ayudante)
        
        self.stdout.write(self.style.SUCCESS("\n✓ Permisos de grupos configurados:"))
        self.stdout.write(f"  - Alumnos: Sin permisos de admin")
        self.stdout.write(f"  - Profesores: {grupo_profesores.permissions.count()} permisos (todos)")
        self.stdout.write(f"  - Profesores Ayudantes: {grupo_profesores_ayudantes.permissions.count()} permisos (add/change, sin delete)")

