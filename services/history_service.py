from mysql.connector import Error
from core.database import get_db_cursor, ensure_scalar

def obtener_historial_jugador(id_jugador):
    """
    Retorna el historial de movimientos económicos y transacciones del jugador
    (tradeos P2P donde participó y cobros de salarios de jornadas laborales).
    """
    id_clean = ensure_scalar(id_jugador)
    if not id_clean:
        return None, "ID de jugador inválido"

    try:
        with get_db_cursor(dictionary=True) as (cursor, _):
            query = """
            SELECT t.id_transaccion, t.fecha_hora, t.tipo_transaccion, t.monto, t.estado_transaccion,
                   i.nombre AS nombre_item
            FROM T_Transaccion t
            LEFT JOIN T_Item i ON t.id_item_afectado = i.id_item
            LEFT JOIN T_Negociacion_Tradeo n ON t.id_negociacion = n.id_negociacion
            LEFT JOIN T_Jornada_Laboral j ON t.id_jornada = j.id_jornada
            WHERE (t.tipo_transaccion = 'TRADEO_P2P' AND (n.id_jugador_1 = %s OR n.id_jugador_2 = %s))
               OR (t.tipo_transaccion = 'PAGO_SALARIO' AND j.id_jugador = %s)
            ORDER BY t.fecha_hora DESC
            """
            cursor.execute(query, (id_clean, id_clean, id_clean))
            historial = cursor.fetchall()
            return historial, "Historial recuperado"
    except Error as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)
