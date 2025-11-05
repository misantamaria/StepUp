# StepUp Code

Repositorio GitHub para la aplicación [StepUP Code](https://www.youtube.com/watch?v=p-fRdRLUs44&feature=youtu.be), desarrollada dentro de un Proyecto de Innovación Educativa (PIE) para la realización de pruebas de tipo test en la asignatura Estructuras de Datos.

La aplicación tiene las siguientes herramientas:
- Sistema de gestión de usuarios
- Tests de prueba iniciales
- Panel de administración Django
- Base de datos inicial con MySQL

## Estructura del repositorio

```
StepUp/
├── app/                          #  StepUp - Estructuras de Datos (PRINCIPAL)
│   ├── stepup_config/            # Configuración Django
│   ├── boards/                   # App de tableros
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

## Configuración de Email

Ambas aplicaciones soportan envío real de emails para:
- Recuperación de contraseñas
- Notificaciones a nuevos usuarios
- Emails de bienvenida

### Configuración rápida (Gmail)

1. Genera una contraseña de aplicación: https://myaccount.google.com/apppasswords
2. Edita `.env`:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password-aqui
```

### Modo desarrollo (sin emails reales)
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## Gestión de usuarios

### Crear usuarios desde web
1. Entra como admin en http://127.0.0.1:8000/
2. Ve a "Crear Usuario"
3. Introduce username y email
4. Se enviará un email automático con instrucciones

### Crear usuarios desde CLI
```powershell
cd app
py manage.py initusers  # Crea usuarios predefinidos (admin, macu, alumno)
```

### Reset de contraseñas
URL: http://127.0.0.1:8000/accounts/password_reset/

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