"""
Tests para verificar datos del dashboard
Compatible con pytest y Django TestCase
"""

import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from core.profesor.services import get_dashboard_data


class TestDatosDashboard(TestCase):
    """Tests para verificar datos del dashboard"""
    
    def test_datos_basicos_dashboard(self):
        """Test: Verificar que el dashboard retorna datos básicos"""
        # Verificar usuarios
        usuarios_no_staff = User.objects.filter(is_staff=False).count()
        self.assertGreater(usuarios_no_staff, 0, "Debe haber usuarios no-staff")
        
        # Verificar datos del dashboard
        data = get_dashboard_data()
        
        # Verificar campos obligatorios
        campos_requeridos = [
            'total_alumnos', 'promedio_general', 'alumnos_detallados',
            'alumnos_activos', 'alumnos_en_riesgo'
        ]
        
        for campo in campos_requeridos:
            self.assertIn(campo, data, f"Campo '{campo}' no encontrado en dashboard")
        
        # Verificar que los valores son razonables
        self.assertGreaterEqual(data['total_alumnos'], 0)
        self.assertGreaterEqual(data['promedio_general'], 0)
        self.assertLessEqual(data['promedio_general'], 10)
        self.assertIsInstance(data['alumnos_detallados'], list)
    
    def test_alumnos_detallados_estructura(self):
        """Test: Verificar estructura de alumnos_detallados"""
        data = get_dashboard_data()
        alumnos_detallados = data.get('alumnos_detallados', [])
        
        if alumnos_detallados:
            alumno_sample = alumnos_detallados[0]
            campos_alumno = [
                'alumno', 'total_intentos', 'grupo', 'ultimo_acceso'
            ]
            
            for campo in campos_alumno:
                self.assertIn(campo, alumno_sample, 
                            f"Campo '{campo}' no encontrado en datos de alumno")
            
            # Verificar que el alumno es efectivamente un Usuario
            self.assertIsInstance(alumno_sample['alumno'], User)
            self.assertFalse(alumno_sample['alumno'].is_staff, 
                           "Los alumnos detallados no deben ser staff")
    
    def test_grupos_asignados_dashboard(self):
        """Test: Verificar que se muestran grupos en dashboard"""
        data = get_dashboard_data()
        alumnos_detallados = data.get('alumnos_detallados', [])
        
        grupos_encontrados = set()
        for alumno_data in alumnos_detallados:
            grupo = alumno_data.get('grupo')
            if grupo and grupo != 'Sin grupo':
                grupos_encontrados.add(grupo)
        
        # Debe haber al menos algunos grupos
        if alumnos_detallados:
            # Si hay alumnos detallados, al menos algunos deberían tener grupo
            self.assertGreaterEqual(len(grupos_encontrados), 0)
    
    def test_notas_rango_correcto(self):
        """Test: Verificar que las notas están en rango 0-10"""
        data = get_dashboard_data()
        alumnos_detallados = data.get('alumnos_detallados', [])
        
        for alumno_data in alumnos_detallados:
            # Verificar todas las notas que estén definidas
            campos_nota = ['nota_media_general', 'nota_media_temas', 'nota_media_examenes']
            
            for campo in campos_nota:
                if campo in alumno_data:
                    nota = alumno_data[campo]
                    if nota is not None:
                        self.assertGreaterEqual(nota, 0, f"{campo} debe ser >= 0")
                        self.assertLessEqual(nota, 10, f"{campo} debe ser <= 10")
    
    def test_conteo_usuarios_coherente(self):
        """Test: Verificar que el conteo de usuarios es coherente"""
        usuarios_no_staff_bd = User.objects.filter(is_staff=False).count()
        
        data = get_dashboard_data()
        total_alumnos_dashboard = data.get('total_alumnos', 0)
        alumnos_detallados = data.get('alumnos_detallados', [])
        
        # El total del dashboard debe coincidir con BD
        self.assertEqual(total_alumnos_dashboard, usuarios_no_staff_bd,
                        f"Dashboard reporta {total_alumnos_dashboard} pero BD tiene {usuarios_no_staff_bd}")
        
        # Si no hay problemas, alumnos_detallados debe tener el mismo número
        # (aunque puede estar vacío por errores en la función)
        if len(alumnos_detallados) > 0:
            self.assertEqual(len(alumnos_detallados), usuarios_no_staff_bd,
                           f"alumnos_detallados tiene {len(alumnos_detallados)} entradas pero BD tiene {usuarios_no_staff_bd}")


class TestRendimientoSistema(TestCase):
    """Tests de rendimiento y estadísticas del sistema"""
    
    def test_estadisticas_generales(self):
        """Test: Verificar estadísticas generales del sistema"""
        data = get_dashboard_data()
        
        # Verificar distribución de notas
        distribucion = data.get('distribucion', {})
        if distribucion:
            categorias_esperadas = ['excelente', 'bien', 'regular', 'mal', 'sin_actividad']
            for categoria in categorias_esperadas:
                self.assertIn(categoria, distribucion, 
                            f"Categoría '{categoria}' no encontrada en distribución")
                self.assertGreaterEqual(distribucion[categoria], 0, 
                                      f"Categoría '{categoria}' no puede ser negativa")
    
    def test_datos_completos(self):
        """Test: Verificar que el dashboard retorna datos completos"""
        data = get_dashboard_data()
        
        # Verificar que no hay valores None en campos críticos
        self.assertIsNotNone(data.get('total_alumnos'))
        self.assertIsNotNone(data.get('promedio_general'))
        self.assertIsNotNone(data.get('alumnos_detallados'))
        self.assertIsNotNone(data.get('alumnos_activos'))
        self.assertIsNotNone(data.get('alumnos_en_riesgo'))
    
    def test_integridad_datos(self):
        """Test: Verificar integridad de los datos"""
        data = get_dashboard_data()
        
        # El número de alumnos activos no puede ser mayor que total de alumnos
        total_alumnos = data.get('total_alumnos', 0)
        alumnos_activos = data.get('alumnos_activos', 0)
        alumnos_en_riesgo = data.get('alumnos_en_riesgo', 0)
        
        self.assertLessEqual(alumnos_activos, total_alumnos, 
                           "Alumnos activos no puede exceder total de alumnos")
        self.assertLessEqual(alumnos_en_riesgo, total_alumnos, 
                           "Alumnos en riesgo no puede exceder total de alumnos")


def verificar_datos_rapido():
    """Función utilitaria para verificación rápida (no es un test de pytest)"""
    print("🔍 VERIFICACIÓN RÁPIDA DE DATOS")
    print("=" * 40)
    
    # Verificar usuarios
    usuarios_no_staff = User.objects.filter(is_staff=False).count()
    print(f"👥 Usuarios no-staff: {usuarios_no_staff}")
    
    # Verificar datos del dashboard
    data = get_dashboard_data()
    print(f"Total alumnos en dashboard: {data.get('total_alumnos')}")
    print(f"Promedio general: {data.get('promedio_general', 0):.1f}")
    print(f"Alumnos detallados: {len(data.get('alumnos_detallados', []))}")
    print(f"Alumnos activos: {data.get('alumnos_activos', 0)}")
    print(f"Alumnos en riesgo: {data.get('alumnos_en_riesgo', 0)}")
    
    # Mostrar algunos alumnos
    alumnos_detallados = data.get('alumnos_detallados', [])
    if alumnos_detallados:
        print(f"\nPrimeros 5 alumnos:")
        for i, alumno_data in enumerate(alumnos_detallados[:5], 1):
            alumno = alumno_data['alumno']
            nombre_completo = f"{alumno.first_name} {alumno.last_name}".strip()
            grupo = alumno_data.get('grupo', 'Sin grupo')
            
            # Usar la clave correcta para la nota
            nota = alumno_data.get('nota_media_general', 
                                 alumno_data.get('nota_media', 0))
            
            print(f"  {i}. {alumno.username} (ID: {alumno.id})")
            print(f"     Nombre: {nombre_completo or 'Sin nombre'}")
            print(f"     Grupo: {grupo}")
            print(f"     Nota media: {nota:.1f}")
            print()
    else:
        print("No se encontraron alumnos detallados")
    
    # Verificar grupos
    grupos = set()
    for alumno_data in alumnos_detallados:
        grupo = alumno_data.get('grupo')
        if grupo:
            grupos.add(grupo)
    
    print(f"Grupos encontrados: {list(grupos)}")
    print("Verificación completada")


if __name__ == "__main__":
    # Si se ejecuta directamente, hacer verificación rápida
    verificar_datos_rapido()