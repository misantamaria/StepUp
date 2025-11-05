"""
Comando para configurar los requisitos entre tests del Tema 1: Listas
Crea una progresión donde cada test requiere haber superado el anterior
"""
from django.core.management.base import BaseCommand
from boards.models import Test


class Command(BaseCommand):
    help = 'Configura los requisitos previos entre tests del Tema Listas'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('Configurando requisitos para tests de Listas'))
        self.stdout.write(self.style.SUCCESS('='*70))
        
        # Orden de progresión de tests
        orden_tests = [
            '1.1 Listas - Conceptos Básicos',
            '1.2 Listas - Implementación con Arrays',
            '1.3 Listas - Listas Enlazadas',
            '1.4 Listas - Pilas y Colas',
        ]
        
        tests_configurados = 0
        test_anterior = None
        
        for tema_id in orden_tests:
            try:
                # Buscar el test por nombre (que incluye el tema_id)
                test = Test.objects.get(nombre=f'Test {tema_id}')
                
                if test_anterior:
                    # Configurar que este test requiere el anterior
                    test.test_requisito = test_anterior
                    test.porcentaje_minimo = 70.0  # 70% mínimo para desbloquear el siguiente
                    test.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ "{test.nombre}" requiere superar "{test_anterior.nombre}" con 70%'
                        )
                    )
                    tests_configurados += 1
                else:
                    # El primer test no tiene requisitos
                    test.test_requisito = None
                    test.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ "{test.nombre}" - Sin requisitos (primer test)')
                    )
                
                test_anterior = test
                
            except Test.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'✗ No se encontró el test para tema: {tema_id}')
                )
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS(f'RESUMEN:'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Tests configurados con requisitos: {tests_configurados}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Porcentaje mínimo: 70%'))
        self.stdout.write('='*70 + '\n')
