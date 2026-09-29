import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'economy_rp')
        )
        return connection
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

def backfill_history():
    conn = get_db_connection()
    if not conn: return
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT id_negociacion, id_jugador_1, id_jugador_2, monto_j1, monto_j도_j2
        FROM T_Negociacion_Tradeo
        WHERE estado = 'COMPLETADO'
        AND id_negociacion NOT IN (SELECT id_negociacion FROM T_Transaccion WHERE tipo_transaccion = 'TRADEO_P2P')
        """
        cursor.execute(query)
        completed_trades = cursor.fetchall()

        for trade in completed_trades:
            monto_total = float(trade['monto_j1'] or 0) + float(trade['monto_j2'] or 0)
            insert_sql = "INSERT INTO T_Transaccion (id_negociacion, tipo_transaccion, estado_transaccion, monto) VALUES (%s, 'TRADEO_P2P', 'COMPLETADA', %s)"
            cursor.execute(insert_sql, (trade['id_negociacion'], monto_total))

        conn.commit()
        print(f"Historial retroactivo creado para {len(completed_trades)} tradeos.")
    except Error as e:
        print(f"Error en backfill: {e}")
        conn.rollback()
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    backfill_history()
