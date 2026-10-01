from mysql.connector import Error
from core.database import get_db_cursor, ensure_scalar
from services.trade_service import _get_items_details

def obtener_historial_jugador(id_jugador):
    """
    Retorna el historial enriquecido de movimientos económicos y transacciones del jugador
    (tradeos P2P con desglose bilateral de ítems, participantes, montos y comisión impuesta).
    """
    id_clean = ensure_scalar(id_jugador)
    if not id_clean:
        return None, "ID de jugador inválido"

    try:
        with get_db_cursor(dictionary=True) as (cursor, _):
            query = """
            SELECT 
                t.id_transaccion, t.fecha_hora, t.tipo_transaccion, t.monto, t.estado_transaccion,
                t.id_negociacion, t.id_jornada,
                n.id_jugador_1, n.id_jugador_2,
                j1.nombre_usuario AS usuario_j1,
                j2.nombre_usuario AS usuario_j2,
                n.monto_j1, n.monto_j2,
                n.items_j1_ids, n.items_j2_ids,
                n.id_item_j1, n.id_item_j2,
                j.horas_trabajadas, j.monto_pagado,
                emp.nombre_empleo
            FROM transacciones t
            LEFT JOIN negociaciones_tradeos n ON t.id_negociacion = n.id_negociacion
            LEFT JOIN jugadores j1 ON n.id_jugador_1 = j1.id_jugador
            LEFT JOIN jugadores j2 ON n.id_jugador_2 = j2.id_jugador
            LEFT JOIN jornadas_laborales j ON t.id_jornada = j.id_jornada
            LEFT JOIN empleos emp ON j.id_empleo = emp.id_empleo
            WHERE (t.tipo_transaccion = 'TRADEO_P2P' AND (n.id_jugador_1 = %s OR n.id_jugador_2 = %s))
               OR (t.tipo_transaccion = 'PAGO_SALARIO' AND j.id_jugador = %s)
            ORDER BY t.fecha_hora DESC
            """
            cursor.execute(query, (id_clean, id_clean, id_clean))
            historial = cursor.fetchall()
            
            cursor.execute("SELECT porcentaje_comision FROM servidores LIMIT 1")
            srv = cursor.fetchone()
            pct_comision = float(srv['porcentaje_comision']) if srv else 5.0

            for mov in historial:
                if mov['tipo_transaccion'] == 'TRADEO_P2P':
                    ids_j1 = mov.get('items_j1_ids') or mov.get('id_item_j1')
                    ids_j2 = mov.get('items_j2_ids') or mov.get('id_item_j2')
                    mov['items_j1_details'] = _get_items_details(ids_j1, cursor=cursor)
                    mov['items_j2_details'] = _get_items_details(ids_j2, cursor=cursor)
                    
                    monto_j1 = float(mov.get('monto_j1') or 0.0)
                    monto_j2 = float(mov.get('monto_j2') or 0.0)
                    total_dinero = monto_j1 + monto_j2
                    comision_total = round(total_dinero * (pct_comision / 100.0), 2)
                    mov['comision_total'] = comision_total
                    mov['porcentaje_comision'] = pct_comision

            return historial, "Historial recuperado"
    except Error as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)
