#!/usr/bin/env python
"""
Script para normalizar todas las puntuaciones a escala de 0-10.
Este script corrige las puntuaciones que fueron guardadas en escala de 0-100
y las convierte a escala de 0-10.
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stepup_config.settings')
django.setup()

from boards.models import IntentTest
from django.db import transaction


def normalizar_notas():
    """
    Normaliza todas las puntuaciones de intentos de test a escala de 0-10.
    Las puntuaciones > 10 se escalan dividiendo entre 10.
    """
    print("🔍 Buscando puntuaciones que necesitan normalización...")
    
    # Buscar todos los intentos con puntuación > 10
    intentos_incorrectos = IntentTest.objects.filter(puntuacion__gt=10)
    total = intentos_incorrectos.count()
    
    if total == 0:
        print("✅ No se encontraron puntuaciones que necesiten corrección.")
        return
    
    print(f"⚠️  Encontrados {total} intentos con puntuación > 10")
    print("\nEjemplos de notas incorrectas:")
    for intento in intentos_incorrectos[:10]:
        print(f"  - {intento.alumno.username}: {intento.test.nombre} → {intento.puntuacion:.2f}")
    
    respuesta = input(f"\n¿Deseas normalizar estas {total} puntuaciones? (s/n): ")
    
    if respuesta.lower() != 's':
        print("❌ Operación cancelada.")
        return
    
    print("\n🔄 Normalizando puntuaciones...")
    
    corregidos = 0
    with transaction.atomic():
        for intento in intentos_incorrectos:
            puntuacion_anterior = intento.puntuacion
            
            # Normalizar: dividir entre 10 para pasar de escala 0-100 a 0-10
            intento.puntuacion = puntuacion_anterior / 10
            
            # Asegurar que no exceda 10
            if intento.puntuacion > 10:
                intento.puntuacion = 10
            
            intento.save(update_fields=['puntuacion'])
            corregidos += 1
            
            if corregidos <= 10:  # Mostrar solo los primeros 10
                print(f"  ✓ {intento.alumno.username}: {intento.test.nombre}")
                print(f"    {puntuacion_anterior:.2f} → {intento.puntuacion:.2f}")
    
    print(f"\n✅ Se normalizaron {corregidos} puntuaciones correctamente.")
    
    # Verificar que no queden puntuaciones > 10
    verificacion = IntentTest.objects.filter(puntuacion__gt=10).count()
    if verificacion > 0:
        print(f"⚠️  Aún quedan {verificacion} puntuaciones > 10. Revisar manualmente.")
    else:
        print("✅ Todas las puntuaciones están ahora en escala de 0-10.")


def verificar_notas():
    """Muestra estadísticas de las puntuaciones actuales"""
    print("\n📊 Estadísticas de puntuaciones:")
    
    total_intentos = IntentTest.objects.filter(completado=True).count()
    print(f"\nTotal de intentos completados: {total_intentos}")
    
    # Contar por rangos
    rangos = [
        ("0-2", 0, 2),
        ("2-4", 2, 4),
        ("4-6", 4, 6),
        ("6-8", 6, 8),
        ("8-10", 8, 10),
        (">10 (INCORRECTAS)", 10, 1000),
    ]
    
    print("\nDistribución de notas:")
    for nombre, minimo, maximo in rangos:
        count = IntentTest.objects.filter(
            completado=True,
            puntuacion__gte=minimo,
            puntuacion__lt=maximo
        ).count()
        porcentaje = (count / total_intentos * 100) if total_intentos > 0 else 0
        print(f"  {nombre}: {count} ({porcentaje:.1f}%)")
    
    # Mostrar máximo y mínimo
    from django.db.models import Max, Min, Avg
    stats = IntentTest.objects.filter(completado=True).aggregate(
        max=Max('puntuacion'),
        min=Min('puntuacion'),
        avg=Avg('puntuacion')
    )
    
    print(f"\n📈 Estadísticas:")
    print(f"  Nota máxima: {stats['max']:.2f}")
    print(f"  Nota mínima: {stats['min']:.2f}")
    print(f"  Nota media: {stats['avg']:.2f}")


if __name__ == '__main__':
    print("=" * 60)
    print("  NORMALIZACIÓN DE NOTAS A ESCALA 0-10")
    print("=" * 60)
    
    # Primero verificar el estado actual
    verificar_notas()
    
    print("\n" + "=" * 60)
    
    # Luego normalizar
    normalizar_notas()
    
    # Verificar resultado final
    print("\n" + "=" * 60)
    print("  VERIFICACIÓN FINAL")
    print("=" * 60)
    verificar_notas()
