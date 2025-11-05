"""
Comando para crear N tests por nivel (Facil/Media/Dificil) para un tema dado.
Usa las preguntas existentes del tema y las distribuye en los tests (con reutilización si hace falta).
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from boards.models import Tema, Test, Pregunta


class Command(BaseCommand):
    help = 'Crea varios tests por nivel para un tema usando preguntas existentes'

    def add_arguments(self, parser):
        parser.add_argument('--tema', required=True, help='ID del tema (ej: "Tema 2 - Pilas y colas")')
        parser.add_argument('--por_nivel', type=int, default=3, help='Número de tests a crear por nivel')
        parser.add_argument('--preguntas_por_test', type=int, default=3, help='Número de preguntas por test')
        parser.add_argument('--visible_facil', action='store_true', help='Marcar tests fáciles como visibles (si no se pasa, también se marcarán visibles)')

    def handle(self, *args, **options):
        tema_id = options['tema']
        por_nivel = options['por_nivel']
        preguntas_por_test = options['preguntas_por_test']
        # visible_facil flag kept for API parity; we'll mark fáciles visibles regardless

        try:
            tema = Tema.objects.get(tema_id=tema_id)
        except Tema.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'✗ Tema no encontrado: {tema_id}'))
            return

        preguntas = list(Pregunta.objects.filter(tema=tema.tema_id))
        if not preguntas:
            self.stdout.write(self.style.ERROR(f'✗ No hay preguntas para el tema {tema_id}'))
            return

        niveles = [
            ('Facil', 'Fácil', 12),
            ('Media', 'Intermedio', 18),
            ('Dificil', 'Difícil', 25),
        ]

        creado = 0
        actualizados = 0

        with transaction.atomic():
            total_preguntas = len(preguntas)
            idx = 0

            for nivel_key, nivel_label, tiempo in niveles:
                for i in range(1, por_nivel + 1):
                    nombre = f"{tema.tema_id} - {nivel_label} #{i}"

                    defaults = {
                        'descripcion': f'Test {nivel_label} #{i} para {tema.tema_id}',
                        'tiempo_limite': tiempo,
                        'visible_alumnos': True if nivel_key == 'Facil' else False,
                        'activo': True,
                    }

                    test, created_flag = Test.objects.get_or_create(
                        tema=tema,
                        nombre=nombre,
                        defaults=defaults
                    )

                    # Seleccionar preguntas por ventana circular
                    selected_ids = []
                    for p in range(preguntas_por_test):
                        pregunta_obj = preguntas[(idx + p) % total_preguntas]
                        selected_ids.append(pregunta_obj.pregunta_id)

                    idx = (idx + preguntas_por_test) % total_preguntas

                    # Asignar preguntas
                    test.preguntas.set(Pregunta.objects.filter(pregunta_id__in=selected_ids))

                    # Asegurarse de nivel y visibilidad
                    if getattr(test, 'nivel', None) != nivel_key:
                        test.nivel = nivel_key
                    test.visible_alumnos = defaults['visible_alumnos']
                    test.save()

                    if created_flag:
                        creado += 1
                        self.stdout.write(self.style.SUCCESS(f'✓ Creado: {nombre} ({len(selected_ids)} preguntas)'))
                    else:
                        actualizados += 1
                        self.stdout.write(self.style.WARNING(f'○ Actualizado: {nombre} (preguntas reasignadas)'))

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Resumen:'))
        self.stdout.write(self.style.SUCCESS(f'  Tests creados: {creado}'))
        self.stdout.write(self.style.SUCCESS(f'  Tests actualizados: {actualizados}'))
        self.stdout.write(self.style.SUCCESS(f'  Preguntas usadas por test: {preguntas_por_test} (reutilización si es necesario)'))
        self.stdout.write('='*60 + '\n')}
