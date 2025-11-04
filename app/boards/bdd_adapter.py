"""
Adaptador para usar las tablas de la base de datos del proyecto en las vistas de Django
Las tablas específicas se definen en settings.py según la configuración de .env
"""
from django.db import connection
from typing import List, Dict, Any


def get_all_temas() -> List[str]:
    """Obtiene todos los temas disponibles"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT Tema_ID FROM Tema")
        return [row[0] for row in cursor.fetchall()]


def get_preguntas_por_tema(tema: str) -> List[Dict[str, Any]]:
    """Obtiene todas las preguntas de un tema específico con sus respuestas"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.Pregunta_ID, p.Enunciado, p.Dificultad, p.Puntuacion
            FROM Pregunta p
            INNER JOIN Contiene c ON p.Pregunta_ID = c.Pregunta_ID
            WHERE c.Tema_ID = %s
        """, [tema])
        
        preguntas = []
        for row in cursor.fetchall():
            pregunta = {
                'id': row[0],
                'enunciado': row[1],
                'dificultad': row[2],
                'puntuacion': row[3],
                'respuestas': []
            }
            
            # Obtener respuestas para esta pregunta
            cursor.execute("""
                SELECT Respuesta_ID, Contenido, Solucion
                FROM Respuesta
                WHERE Pregunta_ID = %s
                ORDER BY Respuesta_ID
            """, [pregunta['id']])
            
            for resp_row in cursor.fetchall():
                pregunta['respuestas'].append({
                    'id': resp_row[0],
                    'contenido': resp_row[1],
                    'es_correcta': resp_row[2] == 'Correcta'
                })
            
            preguntas.append(pregunta)
        
        return preguntas


def get_pregunta_con_respuestas(pregunta_id: int) -> Dict[str, Any]:
    """Obtiene una pregunta específica con todas sus respuestas"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Pregunta_ID, Tema, Enunciado, Dificultad, Puntuacion
            FROM Pregunta
            WHERE Pregunta_ID = %s
        """, [pregunta_id])
        
        row = cursor.fetchone()
        if not row:
            return None
        
        pregunta = {
            'id': row[0],
            'tema': row[1],
            'enunciado': row[2],
            'dificultad': row[3],
            'puntuacion': row[4],
            'respuestas': []
        }
        
        # Obtener respuestas
        cursor.execute("""
            SELECT Respuesta_ID, Contenido, Solucion
            FROM Respuesta
            WHERE Pregunta_ID = %s
            ORDER BY Respuesta_ID
        """, [pregunta_id])
        
        for resp_row in cursor.fetchall():
            pregunta['respuestas'].append({
                'id': resp_row[0],
                'contenido': resp_row[1],
                'es_correcta': resp_row[2] == 'Correcta'
            })
        
        return pregunta


def get_estadisticas_preguntas() -> Dict[str, Any]:
    """Obtiene estadísticas generales de preguntas"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM Pregunta")
        total_preguntas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT Tema) FROM Pregunta")
        total_temas = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT Dificultad, COUNT(*) 
            FROM Pregunta 
            GROUP BY Dificultad
        """)
        por_dificultad = {row[0]: row[1] for row in cursor.fetchall()}
        
        return {
            'total': total_preguntas,
            'total_temas': total_temas,
            'por_dificultad': por_dificultad
        }


def crear_pregunta(tema: str, enunciado: str, dificultad: str, puntuacion: int, respuestas: List[Dict]) -> int:
    """
    Crea una nueva pregunta con sus respuestas
    respuestas = [{'contenido': str, 'es_correcta': bool}, ...]
    """
    with connection.cursor() as cursor:
        # Obtener el siguiente ID
        cursor.execute("SELECT COALESCE(MAX(Pregunta_ID), 0) + 1 FROM Pregunta")
        pregunta_id = cursor.fetchone()[0]
        
        # Insertar pregunta
        cursor.execute("""
            INSERT INTO Pregunta (Pregunta_ID, Tema, Enunciado, Dificultad, Puntuacion)
            VALUES (%s, %s, %s, %s, %s)
        """, [pregunta_id, tema, enunciado, dificultad, puntuacion])
        
        # Insertar respuestas
        for idx, resp in enumerate(respuestas, 1):
            cursor.execute("""
                INSERT INTO Respuesta (Respuesta_ID, Pregunta_ID, Solucion, Contenido)
                VALUES (%s, %s, %s, %s)
            """, [
                idx,
                pregunta_id,
                'Correcta' if resp['es_correcta'] else 'Incorrecta',
                resp['contenido']
            ])
        
        # Relacionar con tema (crear tema si no existe)
        cursor.execute("INSERT IGNORE INTO Tema (Tema_ID) VALUES (%s)", [tema])
        cursor.execute("""
            INSERT INTO Contiene (Tema_ID, Pregunta_ID)
            VALUES (%s, %s)
        """, [tema, pregunta_id])
        
        return pregunta_id


def actualizar_pregunta(pregunta_id: int, enunciado: str = None, dificultad: str = None, puntuacion: int = None):
    """Actualiza los datos de una pregunta"""
    with connection.cursor() as cursor:
        updates = []
        params = []
        
        if enunciado is not None:
            updates.append("Enunciado = %s")
            params.append(enunciado)
        
        if dificultad is not None:
            updates.append("Dificultad = %s")
            params.append(dificultad)
        
        if puntuacion is not None:
            updates.append("Puntuacion = %s")
            params.append(puntuacion)
        
        if updates:
            params.append(pregunta_id)
            cursor.execute(f"""
                UPDATE Pregunta
                SET {', '.join(updates)}
                WHERE Pregunta_ID = %s
            """, params)


def eliminar_pregunta(pregunta_id: int):
    """Elimina una pregunta y sus respuestas"""
    with connection.cursor() as cursor:
        # Las respuestas se eliminan automáticamente por CASCADE
        cursor.execute("DELETE FROM Pregunta WHERE Pregunta_ID = %s", [pregunta_id])
