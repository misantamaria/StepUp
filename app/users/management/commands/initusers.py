from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
import os


class Command(BaseCommand):
    help = "Crea los 3 usuarios básicos para StepUp: alumno, profesor, admin"

    def handle(self, *args, **options):
        # Crear grupos si no existen
        grupo_alumnos, _ = Group.objects.get_or_create(name='Alumnos')
        grupo_profesores, _ = Group.objects.get_or_create(name='Profesores')
        
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
        
        # 3. ADMIN - Administrador del sistema
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
        self.stdout.write(self.style.SUCCESS(f"✓ alumno/alumno   - Alumno (hace tests)"))
        self.stdout.write(self.style.SUCCESS(f"✓ profesor/profesor - Profesor (gestiona preguntas y ve estadísticas)"))
        self.stdout.write(self.style.SUCCESS(f"✓ admin/admin     - Administrador (gestiona usuarios)"))
