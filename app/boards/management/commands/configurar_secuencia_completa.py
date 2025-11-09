"""
Comando para configurar la secuencia completa de temas y tests.
Establece los permisos y configuraciones necesarias para que el sistema funcione correctamente.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from boards.models import Tema, Test


class Command(BaseCommand):
    help = "Configura la secuencia completa de temas y tests con permisos correctos"

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Resetear todas las configuraciones antes de aplicar las nuevas',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(self.style.SUCCESS('CONFIGURANDO SECUENCIA COMPLETA DE TEMAS Y TESTS'))
        self.stdout.write(self.style.SUCCESS('='*80))

        reset = options.get('reset', False)
        if reset:
            self.stdout.write(self.style.WARNING('🔄 Reseteando configuraciones...'))

        with transaction.atomic():
            # 1. CONFIGURAR TEMAS
            self._configurar_temas(reset)
            
            # 2. CONFIGURAR TESTS
            self._configurar_tests(reset)
            
            # 3. VERIFICAR CONFIGURACIÓN
            self._verificar_configuracion()

        self.stdout.write(self.style.SUCCESS('\n✅ Configuración completada exitosamente!'))
        self.stdout.write(self.style.SUCCESS('='*80))

    def _configurar_temas(self, reset):
        """Configura los permisos de los temas"""
        self.stdout.write(self.style.SUCCESS('\n📁 CONFIGURANDO TEMAS'))
        self.stdout.write('-' * 40)
        
        # Configuración de temas: {tema_id: configuración}
        config_temas = {
            'Tema 1 - Conceptos básicos': {
                'visible_alumnos': True,
                'disponible_alumno': True,
                'visible_profesor': True,
                'disponible_profesor': True,
                'activo': True
            },
            'Tema 2 - Pilas y colas': {
                'visible_alumnos': True,
                'disponible_alumno': True,
                'visible_profesor': True,
                'disponible_profesor': True,
                'activo': True
            },
            'Tema 3 - Listas': {
                'visible_alumnos': True,
                'disponible_alumno': True,
                'visible_profesor': True,
                'disponible_profesor': True,
                'activo': True
            },
            'Exámenes': {
                'visible_alumnos': False,
                'disponible_alumno': False,
                'visible_profesor': True,
                'disponible_profesor': True,
                'activo': True
            }
        }
        
        temas_configurados = 0
        for tema_id, config in config_temas.items():
            try:
                tema = Tema.objects.get(tema_id=tema_id)
                
                # Solo actualizar si hay cambios o si se solicitó reset
                if reset or any(getattr(tema, k) != v for k, v in config.items()):
                    for campo, valor in config.items():
                        setattr(tema, campo, valor)
                    tema.save()
                    temas_configurados += 1
                    self.stdout.write(f'  ✓ {tema_id} - Configurado')
                else:
                    self.stdout.write(f'  ○ {tema_id} - Ya configurado correctamente')
                    
            except Tema.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ⚠️ {tema_id} - No encontrado'))
        
        self.stdout.write(f'\n📊 Temas configurados: {temas_configurados}')

    def _configurar_tests(self, reset):
        """Configura los permisos y requisitos de los tests"""
        self.stdout.write(self.style.SUCCESS('\n📝 CONFIGURANDO TESTS'))
        self.stdout.write('-' * 40)
        
        # Configuración por tema
        tema_configs = {
            'Tema 1 - Conceptos básicos': self._config_tema1,
            'Tema 2 - Pilas y colas': self._config_tema2,
            'Tema 3 - Listas': self._config_tema3,
            'Exámenes': self._config_examenes
        }
        
        tests_configurados = 0
        for tema_id, config_func in tema_configs.items():
            try:
                tema = Tema.objects.get(tema_id=tema_id)
                tests = Test.objects.filter(tema=tema, activo=True)
                
                self.stdout.write(f'\n  🎯 {tema_id} ({tests.count()} tests)')
                tests_tema = config_func(tests, reset)
                tests_configurados += tests_tema
                
            except Tema.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ⚠️ {tema_id} - Tema no encontrado'))
        
        self.stdout.write(f'\n📊 Tests configurados: {tests_configurados}')

    def _config_tema1(self, tests, reset):
        """Configuración específica para Tema 1 - Conceptos básicos"""
        # Configuración: tests visibles para alumnos de forma progresiva
        tests_visibles = [
            'Test 1.1 - Introducción a Algoritmos',
            'Test 1.2 - Estructuras de Datos Básicas', 
            'Test 1.3 - Notación y Complejidad Básica'
        ]
        
        config_default = {
            'visible_alumnos': False,
            'disponible_alumno': True,
            'visible_profesor': True,
            'disponible_profesor': True,
            'porcentaje_minimo': 70.0
        }
        
        configurados = 0
        for test in tests:
            config = config_default.copy()
            
            # Tests iniciales visibles para alumnos
            if test.nombre in tests_visibles:
                config['visible_alumnos'] = True
            
            # El primer test puede tener % mínimo menor
            if 'Test 1.1' in test.nombre:
                config['porcentaje_minimo'] = 50.0
            
            if self._aplicar_config_test(test, config, reset):
                configurados += 1
        
        return configurados

    def _config_tema2(self, tests, reset):
        """Configuración específica para Tema 2 - Pilas y colas"""
        config_default = {
            'visible_alumnos': True,
            'disponible_alumno': True,
            'visible_profesor': True,
            'disponible_profesor': True,
            'porcentaje_minimo': 70.0
        }
        
        configurados = 0
        for test in tests:
            if self._aplicar_config_test(test, config_default, reset):
                configurados += 1
        
        return configurados

    def _config_tema3(self, tests, reset):
        """Configuración específica para Tema 3 - Listas"""
        config_default = {
            'visible_alumnos': True,
            'disponible_alumno': True,
            'visible_profesor': True,
            'disponible_profesor': True,
            'porcentaje_minimo': 70.0
        }
        
        configurados = 0
        for test in tests:
            if self._aplicar_config_test(test, config_default, reset):
                configurados += 1
        
        return configurados

    def _config_examenes(self, tests, reset):
        """Configuración específica para tema Exámenes"""
        config_default = {
            'visible_alumnos': False,  # Solo para modo examen
            'disponible_alumno': False,
            'visible_profesor': True,
            'disponible_profesor': True,
            'porcentaje_minimo': 70.0
        }
        
        configurados = 0
        for test in tests:
            if self._aplicar_config_test(test, config_default, reset):
                configurados += 1
        
        return configurados

    def _aplicar_config_test(self, test, config, reset):
        """Aplica configuración a un test específico"""
        # Solo actualizar si hay cambios o si se solicitó reset
        if reset or any(getattr(test, k) != v for k, v in config.items()):
            for campo, valor in config.items():
                setattr(test, campo, valor)
            test.save()
            self.stdout.write(f'    ✓ {test.nombre}')
            return True
        else:
            self.stdout.write(f'    ○ {test.nombre}')
            return False

    def _verificar_configuracion(self):
        """Verifica que la configuración se aplicó correctamente"""
        self.stdout.write(self.style.SUCCESS('\n🔍 VERIFICANDO CONFIGURACIÓN'))
        self.stdout.write('-' * 40)
        
        # Verificar temas
        temas_activos = Tema.objects.filter(activo=True).exclude(tema_id='Exámenes')
        temas_examenes = Tema.objects.filter(tema_id='Exámenes')
        
        self.stdout.write(f'📁 Temas normales activos: {temas_activos.count()}')
        self.stdout.write(f'📁 Tema Exámenes configurado: {temas_examenes.exists()}')
        
        # Verificar tests por tema
        for tema in temas_activos:
            tests_visibles = Test.objects.filter(
                tema=tema, 
                activo=True, 
                visible_alumnos=True,
                disponible_alumno=True
            ).count()
            total_tests = Test.objects.filter(tema=tema, activo=True).count()
            
            self.stdout.write(f'  📝 {tema.tema_id}: {tests_visibles}/{total_tests} tests visibles')
        
        self.stdout.write('\n✅ Verificación completada')