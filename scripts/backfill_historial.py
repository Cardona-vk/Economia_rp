import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import get_db_cursor
from mysql.connector import Error

def backfill_history():
    try:
        with get_db_cursor(commit=True, dictionary=True) as (cursor, _):
            query = """
            SELECT id_negociacion, id_jugador_1, id_jugador_2, monto_j1, monto_j2
            FROM T_Negociacion_Tradeo
            WHERE estado = 'COMPLETADO'
            AND id_negociacion NOT IN (SELECT id_negociacion FROM T_Transaccion WHERE tipo_transaccion = 'TRADEO_P2P')
            """
            cursor.execute(query)
            completed_trades = cursor.fetchall()

            for trade in completed_trades:
                monto_total = float(trade['monto_j1'] or 0) + float(trade['monto_j2'] or 0)
                insert_sql = """
                INSERT INTO T_Transaccion (id_negociacion, tipo_transaccion, estado_transaccion, monto) 
                VALUES (%s, 'TRADEO_P2P', 'COMPLETADA', %s)
                """
                cursor.execute(insert_sql, (trade['id_negociacion'], monto_total))

            print(f"Historial retroactivo creado para {len(completed_trades)} tradeos.")
    except Error as e:
        print(f"Error en backfill: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    backfill_history()
