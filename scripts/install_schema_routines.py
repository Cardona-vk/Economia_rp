import sys
import os
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import get_db_cursor

def install_routines():
    print("Instalando Triggers, Stored Procedures y Events de schema.sql...")

    with open('sql/schema.sql', 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract delimiter block
    delimiter_match = re.search(r'DELIMITER //(.*?)DELIMITER ;', content, re.DOTALL)
    if not delimiter_match:
        print("No se encontró bloque DELIMITER.")
        return

    routines_block = delimiter_match.group(1)
    # Split by //
    statements = [s.strip() for s in routines_block.split('//') if s.strip()]

    with get_db_cursor(commit=True) as (cursor, _):
        for stmt in statements:
            # Clean comments or SET GLOBAL
            cleaned = stmt.strip()
            if cleaned:
                # Extract routine name
                first_line = cleaned.split('\n')[0]
                try:
                    cursor.execute(cleaned)
                    print(f" -> OK: {first_line[:60]}...")
                except Exception as e:
                    print(f" -> Error ejecutando: {first_line[:60]} -> {e}")

    print("Instalación de rutinas completada.")

if __name__ == "__main__":
    install_routines()
