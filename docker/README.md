# Docker

Esta carpeta contiene un docker para la configuración y uso de la aplicación en un servidor (testeado en Ubuntu 22.04).

El docker
- Lee la configuración desde las variables en `../app/.env`.
  - Para su uso deberás copiar `.env.example` y modificar los valores para ajustarlos a tu caso particular.
- Construye la imagen desde la raíz del repositorio usando `docker/Dockerfile`.
- Monta la carpeta `app/` dentro del contenedor en `/app`.

Tras la configuración, se puede usar el docker con:
1. Desde la carpeta `docker/` corre:
```bash
cd /home/user/StepUP/docker
docker compose up --build
```
2. Abre en el navegador `<opción en ALLOWED_HOSTS>:<DJANGO_PORT>` (valor tomado de `app/.env`).

Notas
- Si no existe `app/requirements.txt`, el Dockerfile instalará `Django` y `gunicorn` por defecto.
- Si tu WSGI module no es `project.wsgi:application`, exporta la variable `DJANGO_WSGI_MODULE` en `app/.env` con el path correcto (por ejemplo `myproject.wsgi:application`).
- El Dockerfile intentará correr `collectstatic` si `manage.py` existe; si no, ignorará ese paso.
- Para actualizar la web sin recompilar el docker, usar docker restart docker-web-1.
