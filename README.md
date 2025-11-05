# StepUp Code

Repositorio GitHub para la aplicación [StepUP Code](https://www.youtube.com/watch?v=p-fRdRLUs44&feature=youtu.be), desarrollada dentro de un Proyecto de Innovación Educativa (PIE) para la realización de pruebas de tipo test en la asignatura Estructuras de Datos.

La aplicación tiene las siguientes herramientas:
- [Sistema de gestión de usuarios](https://github.com/misantamaria/StepUp/wiki/Gesti%C3%B3n-de-usuarios).
- Tests de prueba iniciales
- Panel de administración Django
- Base de datos inicial con MySQL

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
|── dump_PIE_ED.sql
|── schema.sql
└── README.md                     # Este archivo
```

## Tests de preguntas

Los archivos XML de preguntas se encuentran en `app/tests/preguntas/`:
- Formato compatible con Moodle XML
- Importables mediante comandos de gestión (implementación futura)
- Organizados por tema y dificultad

## Recursos adicionales

- **Corrector JUnit ED**: Herramientas para corrección automática de prácticas Java (`junit_ED/`)
- **Gestión**: Scripts SQL y herramientas de gestión (`Gestion/`)

## Licencia

Proyecto educativo - Universidad Politécnica de Madrid