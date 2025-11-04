from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import shutil


class Command(BaseCommand):
    help = "Copia el logo desde MEDIA_ROOT/logo.png a users/static/img/logo.png"

    def handle(self, *args, **options):
        source = Path(settings.MEDIA_ROOT) / 'logo.png'
        dest_dir = Path(settings.BASE_DIR) / 'users' / 'static' / 'img'
        dest = dest_dir / 'logo.png'

        if not source.exists():
            self.stderr.write(self.style.ERROR(f"No se encontró {source}. Coloca el archivo en esa ruta y vuelve a intentar."))
            return 1

        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        self.stdout.write(self.style.SUCCESS(f"Logo copiado a {dest}"))
        return 0
