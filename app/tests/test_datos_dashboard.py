"""
Test rápido para verificar datos del dashboard
Ejecutar: python manage.py shell < tests/test_datos_dashboard.py
"""

from core.profesor.services import get_dashboard_data
from django.contrib.auth.models import User

print("🔍 VERIFICACIÓN RÁPIDA DE DATOS")
print("=" * 40)

# Verificar usuarios
usuarios_no_staff = User.objects.filter(is_staff=False).count()
print(f"👥 Usuarios no-staff: {usuarios_no_staff}")

# Verificar datos del dashboard
data = get_dashboard_data()
print(f"📊 Total alumnos en dashboard: {data.get('total_alumnos')}")
print(f"📈 Promedio general: {data.get('promedio_general', 0):.1f}")
print(f"👨‍🎓 Alumnos detallados: {len(data.get('alumnos_detallados', []))}")
print(f"🟢 Alumnos activos: {data.get('alumnos_activos', 0)}")
print(f"⚠️ Alumnos en riesgo: {data.get('alumnos_en_riesgo', 0)}")

# Mostrar algunos alumnos
alumnos_detallados = data.get('alumnos_detallados', [])
if alumnos_detallados:
    print(f"\n📋 Primeros 5 alumnos:")
    for i, alumno_data in enumerate(alumnos_detallados[:5], 1):
        alumno = alumno_data['alumno']
        nombre_completo = f"{alumno.first_name} {alumno.last_name}".strip()
        grupo = alumno_data.get('grupo', 'Sin grupo')
        nota = alumno_data.get('nota_media', 0)
        print(f"  {i}. {alumno.username} (ID: {alumno.id})")
        print(f"     📛 Nombre: {nombre_completo or 'Sin nombre'}")
        print(f"     🏷️ Grupo: {grupo}")
        print(f"     📝 Nota media: {nota:.1f}")
        print()
else:
    print("❌ No se encontraron alumnos detallados")

# Verificar grupos
grupos = set()
for alumno_data in alumnos_detallados:
    grupo = alumno_data.get('grupo')
    if grupo:
        grupos.add(grupo)

print(f"🏫 Grupos encontrados: {list(grupos)}")

print("✅ Verificación completada")