from core.database import get_db_cursor

def crear_notificacion(id_jugador: int, titulo: str, mensaje: str, tipo: str = 'ADMIN'):
    """
    Registra una nueva notificación en la base de datos para un jugador específico.
    """
    try:
        with get_db_cursor(commit=True) as (cursor, _):
            cursor.execute("""
                INSERT INTO T_Notificacion (id_jugador, titulo, mensaje, tipo, leido)
                VALUES (%s, %s, %s, %s, FALSE)
            """, (id_jugador, titulo, mensaje, tipo))
            return True, "Notificación registrada"
    except Exception as e:
        return False, f"Error al registrar notificación: {str(e)}"

def obtener_notificaciones_no_leidas(id_jugador: int):
    """
    Obtiene todas las notificaciones pendientes no leídas de un jugador.
    """
    try:
        with get_db_cursor(dictionary=True, commit=False) as (cursor, _):
            cursor.execute("""
                SELECT id_notificacion, id_jugador, titulo, mensaje, tipo, fecha_creacion
                FROM T_Notificacion
                WHERE id_jugador = %s AND leido = FALSE
                ORDER BY id_notificacion ASC
            """, (id_jugador,))
            rows = cursor.fetchall()
            return rows, "OK"
    except Exception as e:
        return [], f"Error al consultar notificaciones: {str(e)}"


def marcar_como_leidas(id_jugador: int, ids_notificaciones=None):
    """
    Marca las notificaciones especificadas (o todas las del jugador) como leídas.
    """
    try:
        with get_db_cursor(commit=True) as (cursor, _):
            if ids_notificaciones:
                format_strings = ','.join(['%s'] * len(ids_notificaciones))
                cursor.execute(f"""
                    UPDATE T_Notificacion
                    SET leido = TRUE
                    WHERE id_jugador = %s AND id_notificacion IN ({format_strings})
                """, [id_jugador] + list(ids_notificaciones))
            else:
                cursor.execute("""
                    UPDATE T_Notificacion
                    SET leido = TRUE
                    WHERE id_jugador = %s AND leido = FALSE
                """, (id_jugador,))
            return True, "Notificaciones marcadas como leídas"
    except Exception as e:
        return False, f"Error al marcar notificaciones: {str(e)}"
