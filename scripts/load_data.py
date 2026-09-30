import sys
import os

# Permitir importación desde la raíz del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import get_db_cursor
from mysql.connector import Error

def load_test_data():
    print("--- Iniciando Carga de Datos de Prueba ---")
    try:
        with get_db_cursor(commit=True) as (cursor, _):
            # 1. Definir jugadores y sus saldos
            jugadores = [1, 2]
            saldo_inicial = 50000.00

            for jid in jugadores:
                print(f"Asignando saldo a Jugador ID {jid}...")
                cursor.execute("""
                    INSERT INTO T_Cuenta (id_jugador, id_servidor, tipo_cuenta, saldo_inicial, saldo_disponible)
                    SELECT id_jugador, id_servidor, 'PERSONAL', %s, %s
                    FROM T_Jugador WHERE id_jugador = %s
                    ON DUPLICATE KEY UPDATE saldo_disponible = %s
                """, (saldo_inicial, saldo_inicial, jid, saldo_inicial))

            # 2. Definir Items de prueba
            items_j1 = [
                ('Coche Deportivo', 50000.00, 1),
                ('Reloj de Lujo', 5000.00, 1),
                ('Kit de Reparación', 150.00, 3)
            ]

            for nombre, precio, cant in items_j1:
                for _ in range(cant):
                    cursor.execute("INSERT INTO T_Item (id_jugador, nombre, precio, tiene_deuda) VALUES (%s, %s, %s, FALSE)", (1, nombre, precio))

            print("\nDatos inyectados exitosamente.")
    except Error as e:
        print(f"Error durante la carga de datos: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    load_test_data()
