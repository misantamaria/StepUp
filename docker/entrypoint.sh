#!/usr/bin/env bash
set -e

# Entrypoint para contenedor Django
# Ejecuta migraciones, initusers (si existe), carga fixtures y collectstatic

# Move to app dir if exists
if [ -d "/app" ]; then
  cd /app || exit 1
fi

# Wait for database to be ready
if [ -n "$DB_HOST" ] && [ "$DB_HOST" != "localhost" ]; then
  echo "[entrypoint] Esperando a que la base de datos esté lista..."
  
  for i in {1..30}; do
    if python -c "
import pymysql
import os
try:
    conn = pymysql.connect(
        host=os.getenv('DB_HOST', 'db'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'root'),
        port=int(os.getenv('DB_PORT', '3306'))
    )
    conn.close()
    exit(0)
except Exception as e:
    exit(1)
" 2>/dev/null; then
      echo "[entrypoint] Base de datos lista!"
      break
    fi
    echo "[entrypoint] Esperando base de datos... intento $i/30"
    sleep 2
  done
fi

if [ -f manage.py ]; then
  echo "[entrypoint] manage.py encontrado, ejecutando tareas de inicialización..."

  # Apply migrations
  echo "[entrypoint] Ejecutando migrations..."
  python manage.py migrate --noinput || true

  # Run custom initusers command if available
  echo "[entrypoint] Ejecutando manage.py initusers..."
  python manage.py initusers || true

  # Load fixtures if a common fixture file exists
  if [ -f fixtures/initial_data.json ]; then
    echo "[entrypoint] Cargando fixtures/initial_data.json..."
    python manage.py loaddata fixtures/initial_data.json || true
  fi

  # Collect static
  echo "[entrypoint] Ejecutando collectstatic..."
  python manage.py collectstatic --noinput || true
else
  echo "[entrypoint] manage.py NO encontrado, saltando inicialización Django."
fi

# Execute the command provided as arguments (or default CMD from Dockerfile)
echo "[entrypoint] Ejecutando el comando: $@"
exec "$@"
