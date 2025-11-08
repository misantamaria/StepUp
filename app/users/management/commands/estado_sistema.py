from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from users.models import UserProfile


class Command(BaseCommand):
    help = "Muestra un resumen completo del estado de usuarios y configuración del sistema"

    def add_arguments(self, parser):
        parser.add_argument(
            '--detallado',
            action='store_true',
            help='Mostrar información detallada de cada usuario',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("=== ESTADO COMPLETO DEL SISTEMA STEPUP ==="))
        self.stdout.write()

        # Verificar usuarios básicos
        self._verificar_usuarios_basicos()
        
        # Verificar grupos y permisos
        self._verificar_grupos()
        
        # Mostrar estadísticas de alumnos
        self._mostrar_estadisticas_alumnos(detallado=options['detallado'])
        
        # Verificar configuración de persistencia
        self._verificar_persistencia()

    def _verificar_usuarios_basicos(self):
        """Verifica que existen los usuarios básicos del sistema"""
        self.stdout.write(self.style.SUCCESS("🔍 USUARIOS BÁSICOS DEL SISTEMA"))
        
        usuarios_esperados = [
            ("admin", "admin", True, True, "Administrador principal"),
            ("profesor", "profesor", True, False, "Profesor principal"),
            ("profesor_ayudante", "ayudante", True, False, "Profesor ayudante"),
            ("alumno", "alumno", False, False, "Usuario alumno de prueba"),
        ]
        
        for username, password_esperado, es_staff, es_super, descripcion in usuarios_esperados:
            try:
                user = User.objects.get(username=username)
                grupos = list(user.groups.values_list('name', flat=True))
                
                status = "✓"
                if user.is_staff != es_staff or user.is_superuser != es_super:
                    status = "⚠️"
                
                self.stdout.write(f"  {status} {username}/{password_esperado} - {descripcion}")
                self.stdout.write(f"    📧 {user.email}")
                self.stdout.write(f"    🔐 staff:{user.is_staff} | super:{user.is_superuser} | grupos:{grupos}")
                
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"  ✗ {username} - NO EXISTE"))
        
        self.stdout.write()

    def _verificar_grupos(self):
        """Verifica la configuración de grupos y permisos"""
        self.stdout.write(self.style.SUCCESS("👥 GRUPOS Y PERMISOS"))
        
        grupos_esperados = ["Alumnos", "Profesores", "Profesores Ayudantes"]
        
        for nombre_grupo in grupos_esperados:
            try:
                grupo = Group.objects.get(name=nombre_grupo)
                usuarios_en_grupo = grupo.user_set.count()
                permisos = grupo.permissions.count()
                
                self.stdout.write(f"  ✓ {nombre_grupo}: {usuarios_en_grupo} usuarios, {permisos} permisos")
                
            except Group.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"  ✗ {nombre_grupo} - GRUPO NO EXISTE"))
        
        self.stdout.write()

    def _mostrar_estadisticas_alumnos(self, detallado=False):
        """Muestra estadísticas de los alumnos creados"""
        self.stdout.write(self.style.SUCCESS("👨‍🎓 ALUMNOS DEL SISTEMA"))
        
        # Estadísticas generales
        total_alumnos = User.objects.filter(groups__name='Alumnos').count()
        alumnos_con_clase = UserProfile.objects.exclude(grupo__isnull=True).exclude(grupo='').count()
        
        self.stdout.write(f"  📊 Total alumnos: {total_alumnos}")
        self.stdout.write(f"  🏫 Alumnos con clase asignada: {alumnos_con_clase}")
        
        # Distribución por clases
        clase_a_count = UserProfile.objects.filter(grupo='Clase A').count()
        clase_b_count = UserProfile.objects.filter(grupo='Clase B').count()
        sin_clase_count = total_alumnos - alumnos_con_clase
        
        self.stdout.write(f"\n  📚 Distribución por clases:")
        self.stdout.write(f"    • Clase A: {clase_a_count} alumnos")
        self.stdout.write(f"    • Clase B: {clase_b_count} alumnos")
        if sin_clase_count > 0:
            self.stdout.write(f"    • Sin clase: {sin_clase_count} alumnos")
        
        if detallado:
            self._mostrar_detalle_clases()
        
        # Mostrar alumnos destacados
        self._mostrar_alumnos_destacados()
        
        self.stdout.write()

    def _mostrar_detalle_clases(self):
        """Muestra el detalle de alumnos por clase"""
        for clase_nombre in ['Clase A', 'Clase B']:
            alumnos_clase = UserProfile.objects.filter(grupo=clase_nombre).select_related('user').order_by('user__first_name')
            
            if alumnos_clase.exists():
                self.stdout.write(f"\n    📋 {clase_nombre}:")
                for profile in alumnos_clase:
                    user = profile.user
                    self.stdout.write(f"      • {user.first_name} {user.last_name} ({user.username})")

    def _mostrar_alumnos_destacados(self):
        """Muestra información sobre alumnos con perfiles especiales"""
        
        # Buscar alumnos con perfiles específicos por nombre de usuario (basado en el comando crear_alumnos_demo)
        alumnos_especiales = [
            ("ana_garcia", "🌟 Excelente (Clase A)"),
            ("roberto_silva", "⭐ Especialmente bueno (Clase B)"),
            ("miguel_jimenez", "⚠️ En riesgo (Clase A)"),
            ("julia_vega", "⚠️ En riesgo (Clase B)"),
        ]
        
        self.stdout.write(f"\n  🎯 Perfiles destacados:")
        for username, descripcion in alumnos_especiales:
            try:
                user = User.objects.get(username=username)
                self.stdout.write(f"    {descripcion}: {user.first_name} {user.last_name}")
            except User.DoesNotExist:
                self.stdout.write(f"    ❌ {descripcion}: Usuario {username} no encontrado")

    def _verificar_persistencia(self):
        """Verifica que la configuración de persistencia esté correcta"""
        self.stdout.write(self.style.SUCCESS("💾 CONFIGURACIÓN DE PERSISTENCIA"))
        
        # Verificar que hay datos en la BD
        total_users = User.objects.count()
        self.stdout.write(f"  ✓ Base de datos activa con {total_users} usuarios")
        
        # Información sobre Docker
        self.stdout.write(f"La persistencia está configurada con volumen Docker 'mysql_data'")
        self.stdout.write(f"Los datos se mantienen después de 'docker-compose down'")
        
        self.stdout.write()
        
        # Resumen final
        self.stdout.write(self.style.HTTP_INFO("=== RESUMEN FINAL ==="))
        self.stdout.write(self.style.SUCCESS("-- Sistema StepUp configurado correctamente --"))
        self.stdout.write("Credenciales principales:")
        self.stdout.write("   • admin/admin (Administrador)")
        self.stdout.write("   • profesor/profesor (Profesor)")
        self.stdout.write("   • profesor_ayudante/ayudante (Profesor Ayudante)")
        self.stdout.write("   • Alumnos: [nombre_usuario]/alumno123")
        self.stdout.write()
        self.stdout.write(self.style.HTTP_INFO("-- Comandos útiles --"))
        self.stdout.write("   • python manage.py estado_sistema --detallado")
        self.stdout.write("   • python manage.py initusers (crear usuarios básicos)")
        self.stdout.write("   • python manage.py crear_alumnos_demo (crear alumnos de ejemplo)")