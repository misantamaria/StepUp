#!/bin/bash

# Script para verificar puntuaciones de tests usando Docker
# Uso: ./verificar_puntuaciones.sh

echo "🔍 VERIFICANDO PUNTUACIONES DE TESTS..."
echo "======================================"

# Ejecutar el test específico de puntuaciones
echo ""
echo "📋 Ejecutando verificaciones..."

# Asegurar que estamos en el directorio docker
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ejecutar solo el test de puntuaciones
docker compose exec web python -m pytest tests/test_puntuaciones_tests.py -v --no-header --tb=short

# Capturar el código de salida
exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✅ TODAS LAS VERIFICACIONES PASARON CORRECTAMENTE"
    echo ""
    echo "📊 Resultados:"
    echo "   - Todos los tests tienen puntuación máxima de 10 puntos ✓"
    echo "   - Todas las preguntas tienen respuestas correctas ✓"
    echo "   - Sistema de puntuaciones consistente ✓"
else
    echo "❌ SE ENCONTRARON PROBLEMAS EN LAS PUNTUACIONES"
    echo ""
    echo "🔧 Revisa los errores mostrados arriba y:"
    echo "   1. Corrige las preguntas sin respuestas correctas"
    echo "   2. Ajusta las puntuaciones para que cada test sume 10 puntos"
    echo "   3. Vuelve a ejecutar este script"
fi

echo ""
echo "📝 Para más detalles, ejecuta:"
echo "   docker compose exec web python -m pytest app/tests/test_puntuaciones_tests.py::TestPuntuacionMaxima::test_todos_los_tests_tienen_puntuacion_maxima_10 -v -s"

exit $exit_code