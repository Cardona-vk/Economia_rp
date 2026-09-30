import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import get_db_cursor

def assign_test_item(player_id=1, item_name='Coche de Lujo', price=50000.00):
    try:
        with get_db_cursor(commit=True) as (cursor, _):
            sql = "INSERT INTO T_Item (id_jugador, nombre, precio, tiene_deuda) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (player_id, item_name, price, 0))
            print(f"Item '{item_name}' (${price}) asignado exitosamente al jugador {player_id}")
    except Exception as e:
        print(f"Error asignando ítem: {e}")

if __name__ == "__main__":
    assign_test_item()
