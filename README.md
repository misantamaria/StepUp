# StepUp Code
<p align="center">
	<img src="media/logo.png" alt="Logotipo" width="|" />
</p>


Repositorio GitHub para la aplicación [StepUP Code](https://www.youtube.com/watch?v=p-fRdRLUs44&feature=youtu.be), desarrollada dentro de un Proyecto de Innovación Educativa (PIE) para la realización de pruebas de tipo test en la asignatura Estructuras de Datos.

La aplicación tiene las siguientes herramientas:
- [Sistema de gestión de usuarios](https://github.com/misantamaria/StepUp/wiki/Gesti%C3%B3n-de-usuarios).
- Tests de prueba iniciales
- Panel de administración Django
- Base de datos inicial con MySQL


## Requisitos
- Python 3.11+
- MySQL
- pip/venv
  
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

## Documentación
### Guías de presentación
- La [guía para alumnos](/docs/guiaAlumnos) contiene una descripción básica de la aplicación desde el punto de vista del estudiante.
- La [guía para docentes](/docs/guiaDocentes.pdf) contiene una descripción básica de la aplicación desde el punto de vista del profesor.

### Manuales de usuario
- El [manual para alumnos](/docs/manualAlumnos.pdf) describe las distintas pantallas y funcionalidades de la aplicación para los alumnos.
- El [manual para docentes](/docs/manualDocente.pdf) describe las distintas pantallas y funcionalidades de la aplicación para los docentes.