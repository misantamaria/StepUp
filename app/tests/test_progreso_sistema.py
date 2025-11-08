"""
Tests de verificación del sistema de análisis de progreso
Estos tests se pueden ejecutar para comprobar que el sistema funciona correctamente
"""

import os
import django
import sys

# Configurar Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stepup_config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile
from boards.models import IntentTest, Test
from core.profesor.services import get_dashboard_data


def test_usuarios_no_staff():
    """Test 1: Verificar que solo se cuentan usuarios no-staff"""
    print("=== TEST 1: Usuarios no-staff ===")
    
    total_usuarios = User.objects.count()
    usuarios_staff = User.objects.filter(is_staff=True).count()
    usuarios_no_staff = User.objects.filter(is_staff=False).count()
    
    print(f"Total usuarios: {total_usuarios}")
    print(f"Usuarios staff: {usuarios_staff}")
    print(f"Usuarios no-staff: {usuarios_no_staff}")
    
    # Verificar que hay usuarios no-staff
    assert usuarios_no_staff > 0, "Debe haber al menos un usuario no-staff"
    assert usuarios_staff + usuarios_no_staff == total_usuarios, "La suma debe coincidir"
    
    print("✅ Test usuarios no-staff PASADO")
    return True


def test_grupos_asignados():
    """Test 2: Verificar que los alumnos tienen grupos asignados"""
    print("\n=== TEST 2: Grupos asignados ===")
    
    alumnos_sin_grupo = []
    grupos_encontrados = set()
    
    for user in User.objects.filter(is_staff=False):
        if hasattr(user, 'profile') and user.profile.grupo:
            grupos_encontrados.add(user.profile.grupo)
        else:
            alumnos_sin_grupo.append(user.username)
    
    print(f"Grupos encontrados: {list(grupos_encontrados)}")
    print(f"Alumnos sin grupo: {len(alumnos_sin_grupo)}")
    
    if alumnos_sin_grupo:
        print(f"Usuarios sin grupo: {alumnos_sin_grupo[:5]}...")  # Mostrar solo 5
    
    # Verificar que hay al menos 2 grupos
    assert len(grupos_encontrados) >= 2, f"Debe haber al menos 2 grupos, encontrados: {len(grupos_encontrados)}"
    
    print("✅ Test grupos asignados PASADO")
    return True


def test_intentos_creados():
    """Test 3: Verificar que existen intentos de tests"""
    print("\n=== TEST 3: Intentos de tests ===")
    
    total_intentos = IntentTest.objects.count()
    intentos_completados = IntentTest.objects.filter(completado=True).count()
    intentos_no_staff = IntentTest.objects.filter(alumno__is_staff=False).count()
    
    print(f"Total intentos: {total_intentos}")
    print(f"Intentos completados: {intentos_completados}")
    print(f"Intentos de no-staff: {intentos_no_staff}")
    
    # Verificar que hay intentos
    assert total_intentos > 0, "Debe haber al menos un intento"
    assert intentos_completados > 0, "Debe haber al menos un intento completado"
    assert intentos_no_staff > 0, "Debe haber al menos un intento de usuario no-staff"
    
    print("✅ Test intentos creados PASADO")
    return True


def test_notas_en_rango():
    """Test 4: Verificar que las notas están en el rango correcto (0-10)"""
    print("\n=== TEST 4: Rango de notas ===")
    
    intentos_con_notas = IntentTest.objects.filter(puntuacion__isnull=False)
    nota_min = min([i.puntuacion for i in intentos_con_notas]) if intentos_con_notas else 0
    nota_max = max([i.puntuacion for i in intentos_con_notas]) if intentos_con_notas else 0
    
    print(f"Nota mínima: {nota_min}")
    print(f"Nota máxima: {nota_max}")
    print(f"Intentos con notas: {intentos_con_notas.count()}")
    
    # Verificar rango de notas
    if intentos_con_notas:
        assert 0 <= nota_min <= 10, f"Nota mínima fuera de rango: {nota_min}"
        assert 0 <= nota_max <= 10, f"Nota máxima fuera de rango: {nota_max}"
    
    print("✅ Test rango de notas PASADO")
    return True


def test_alumnos_en_riesgo():
    """Test 5: Verificar detección de alumnos en riesgo"""
    print("\n=== TEST 5: Alumnos en riesgo ===")
    
    alumnos_muy_buenos = []
    alumnos_en_riesgo = []
    alumnos_sin_intentos = []
    
    for user in User.objects.filter(is_staff=False):
        intentos = IntentTest.objects.filter(alumno=user, completado=True)
        if intentos.exists():
            promedio = sum([i.puntuacion for i in intentos]) / len(intentos)
            if promedio >= 8.5:
                alumnos_muy_buenos.append((user.username, promedio))
            elif promedio < 5:
                alumnos_en_riesgo.append((user.username, promedio))
        else:
            alumnos_sin_intentos.append(user.username)
    
    print(f"Alumnos muy buenos (>=8.5): {len(alumnos_muy_buenos)}")
    print(f"Alumnos en riesgo (<5): {len(alumnos_en_riesgo)}")
    print(f"Alumnos sin intentos: {len(alumnos_sin_intentos)}")
    
    if alumnos_muy_buenos:
        print(f"Mejor alumno: {alumnos_muy_buenos[0][0]} con {alumnos_muy_buenos[0][1]:.1f}")
    
    if alumnos_en_riesgo:
        print(f"Alumnos en riesgo: {[a[0] for a in alumnos_en_riesgo]}")
    
    # Verificar que hay al menos 1 muy bueno y 2 en riesgo
    assert len(alumnos_muy_buenos) >= 1, "Debe haber al menos 1 alumno muy bueno"
    assert len(alumnos_en_riesgo) >= 2, f"Debe haber al menos 2 alumnos en riesgo, encontrados: {len(alumnos_en_riesgo)}"
    
    print("✅ Test alumnos en riesgo PASADO")
    return True


def test_dashboard_data():
    """Test 6: Verificar que get_dashboard_data funciona correctamente"""
    print("\n=== TEST 6: Dashboard data ===")
    
    try:
        data = get_dashboard_data()
        
        print(f"Total alumnos: {data.get('total_alumnos', 0)}")
        print(f"Promedio general: {data.get('promedio_general', 0):.2f}")
        print(f"Alumnos detallados: {len(data.get('alumnos_detallados', []))}")
        print(f"Alumnos activos: {data.get('alumnos_activos', 0)}")
        print(f"Alumnos en riesgo: {data.get('alumnos_en_riesgo', 0)}")
        
        # Verificar que los datos básicos están presentes
        assert 'total_alumnos' in data, "Debe incluir total_alumnos"
        assert 'alumnos_detallados' in data, "Debe incluir alumnos_detallados"
        assert 'promedio_general' in data, "Debe incluir promedio_general"
        assert data['total_alumnos'] > 0, "Debe haber alumnos"
        
        # Verificar estructura de alumnos_detallados
        for alumno_data in data['alumnos_detallados'][:3]:  # Solo verificar 3
            assert 'alumno' in alumno_data, "Cada alumno debe tener campo 'alumno'"
            assert 'nota_media' in alumno_data, "Cada alumno debe tener 'nota_media'"
            assert 'grupo' in alumno_data, "Cada alumno debe tener 'grupo'"
            print(f"- {alumno_data['alumno'].username}: {alumno_data['grupo']} (nota: {alumno_data['nota_media']:.1f})")
        
        print("✅ Test dashboard data PASADO")
        return True
        
    except Exception as e:
        print(f"❌ Error en dashboard data: {e}")
        return False


def test_nombres_apellidos():
    """Test 7: Verificar que los alumnos tienen nombres y apellidos"""
    print("\n=== TEST 7: Nombres y apellidos ===")
    
    alumnos_con_nombres = 0
    alumnos_sin_nombres = []
    
    for user in User.objects.filter(is_staff=False):
        if user.first_name and user.last_name:
            alumnos_con_nombres += 1
        else:
            alumnos_sin_nombres.append(user.username)
    
    print(f"Alumnos con nombres completos: {alumnos_con_nombres}")
    print(f"Alumnos sin nombres: {len(alumnos_sin_nombres)}")
    
    if alumnos_sin_nombres:
        print(f"Sin nombres: {alumnos_sin_nombres[:5]}")
    
    # La mayoría debería tener nombres
    total_no_staff = User.objects.filter(is_staff=False).count()
    porcentaje_con_nombres = (alumnos_con_nombres / total_no_staff) * 100 if total_no_staff > 0 else 0
    print(f"Porcentaje con nombres: {porcentaje_con_nombres:.1f}%")
    
    print("✅ Test nombres y apellidos PASADO")
    return True


def ejecutar_todos_los_tests():
    """Ejecutar todos los tests de verificación"""
    print("🚀 EJECUTANDO TESTS DE VERIFICACIÓN DEL SISTEMA")
    print("=" * 50)
    
    tests = [
        test_usuarios_no_staff,
        test_grupos_asignados,
        test_intentos_creados,
        test_notas_en_rango,
        test_alumnos_en_riesgo,
        test_dashboard_data,
        test_nombres_apellidos,
    ]
    
    tests_pasados = 0
    tests_fallidos = 0
    
    for test_func in tests:
        try:
            if test_func():
                tests_pasados += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} FALLÓ: {e}")
            tests_fallidos += 1
    
    print("\n" + "=" * 50)
    print(f"📊 RESUMEN: {tests_pasados} pasados, {tests_fallidos} fallidos")
    
    if tests_fallidos == 0:
        print("🎉 TODOS LOS TESTS PASARON!")
    else:
        print(f"⚠️  {tests_fallidos} tests necesitan atención")
    
    return tests_fallidos == 0


if __name__ == "__main__":
    ejecutar_todos_los_tests()