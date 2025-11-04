# Gestión de Base de Datos

## Archivos

- `schema.sql` - Esquema de la base de datos (versionado en git)
- `dump_*.sql` - Dumps con datos reales (NO versionados, solo local)

## Uso con Docker

Los archivos `.sql` en este directorio se cargan automáticamente al iniciar el contenedor MySQL.

## Crear un nuevo dump

Para crear un dump de tu base de datos local:

```bash
mysqldump -u root -p PIE_ED > Gestion/dump_PIE_ED.sql
```
