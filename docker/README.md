Docker/Compose para la aplicación Django

Cómo funciona
- Lee variables desde `../app/.env` (asegúrate de que `DJANGO_PORT` esté definido allí).
- Construye la imagen desde la raíz del repositorio usando `docker/Dockerfile`.
- Monta la carpeta `app/` dentro del contenedor en `/app`.

Pasos rápidos
1. Desde la carpeta `docker/` corre:

```bash
docker compose up --build
```

2. Abre en el navegador `http://localhost:<DJANGO_PORT>` (valor tomado de `app/.env`).

Notas
- Si no existe `app/requirements.txt`, el Dockerfile instalará `Django` y `gunicorn` por defecto.
- Si tu WSGI module no es `project.wsgi:application`, exporta la variable `DJANGO_WSGI_MODULE` en `app/.env` con el path correcto (por ejemplo `myproject.wsgi:application`).
- El Dockerfile intentará correr `collectstatic` si `manage.py` existe; si no, ignorará ese paso.
