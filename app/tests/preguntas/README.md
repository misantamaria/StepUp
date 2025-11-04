# Preguntas XML para tests de Estructuras de Datos

Este directorio contiene los archivos XML de preguntas exportados desde Moodle.

## Archivos disponibles

- `preguntas-Test PIE - Step-Up-Por defecto en Test PIE - Step-Up-20251001-1749.xml`: Banco de preguntas completo
- Archivos `.txt`: Versiones de texto para revisión

## Formato

Los archivos XML siguen el formato de exportación de Moodle y pueden ser:
- Importados a Moodle directamente
- Procesados por comandos de gestión de Django (próximamente)
- Utilizados para generar tests aleatorios

## Uso futuro

```python
# Comando para importar preguntas (implementación futura)
python manage.py import_questions tests/preguntas/archivo.xml
```
