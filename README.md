# StepUp Code

Repositorio GitHub para la aplicación [StepUP Code](https://www.youtube.com/watch?v=p-fRdRLUs44&feature=youtu.be), desarrollada dentro de un Proyecto de Innovación Educativa (PIE) para la realización de pruebas de tipo test en la asignatura Estructuras de Datos.

La aplicación tiene las siguientes herramientas:
- [Sistema de gestión de usuarios](https://github.com/misantamaria/StepUp/wiki/Gesti%C3%B3n-de-usuarios).
- Tests de prueba iniciales
- Panel de administración Django
- Base de datos inicial con MySQL


## Requisitos
- Python 3.11+
- MySQL (o SQLite)
- pip/venv
- Driver Python: este proyecto usa PyMySQL (ya incluido en `requirements.txt`). Si aparece `ModuleNotFoundError: No module named 'pymysql'`, ejecuta en el entorno virtual venv:

```powershell
    python -m pip install PyMySQL==1.1.1
```
  
## Estructura del repositorio

```
StepUp/
├── app/                          #  StepUp - Estructuras de Datos (PRINCIPAL)
│   ├── stepup_config/            # Configuración Django
│   ├── boards/                   # App de tableros (interfaces con información y controles, dashboards)
│   ├── users/                    # App de usuarios
│   ├── tests/preguntas/          # XMLs de preguntas
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   └── ...
├── docker/                          #  Docker para el lanzamiento en servidor
|   |── .env.example                # Configuración de ejemplo básica
|   |── Dockerfile
|   |── docker-compose.yml
|   |── entrypoint.sh 
├── media/                          #  Ficheros media para la aplicación web
|── dump_PIE_ED.sql
|── schema.sql
└── README.md                     # Este archivo
```