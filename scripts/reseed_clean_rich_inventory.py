import sys
import os
import bcrypt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import get_db_cursor

def reseed_clean_rich():
    print("--- 1. Homologación y Limpieza de Base de Datos ---")
    
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw('21492477'.encode('utf-8'), salt).decode('utf-8')

    with get_db_cursor(commit=True) as (cursor, _):
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for tbl in ['T_Detalle_Transaccion', 'T_Transaccion', 'T_Negociacion_Tradeo', 'T_Jornada_Laboral', 'T_Item', 'T_Cuenta', 'T_Empleo', 'T_Jugador', 'T_Servidor']:
            try:
                cursor.execute(f"TRUNCATE TABLE {tbl}")
            except Exception as e:
                print(f"Truncate {tbl}: {e}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # 1. Configuración del Servidor
        cursor.execute("""
            INSERT INTO T_Servidor (id_servidor, nombre, porcentaje_comision, limite_bienes_por_jugador, tiempo_enfriamiento_min)
            VALUES (1, 'Servidor Principal RP Los Santos', 5.00, 100, 15)
        """)

        # 2. Cuenta Central del Sistema / Tesorería (ID: 1)
        cursor.execute("""
            INSERT INTO T_Cuenta (id_cuenta, id_jugador, id_servidor, tipo_cuenta, saldo_inicial, saldo_disponible)
            VALUES (1, NULL, 1, 'SISTEMA', 10000000.00, 10000000.00)
        """)

        # 3. Operadores
        cursor.execute("""
            INSERT INTO T_Jugador (id_jugador, id_servidor, nombre_usuario, correo, contrasena_hash, estado, es_admin)
            VALUES 
            (1, 1, 'Cardona222', 'cardona222@economy.rp', %s, 'ACTIVO', TRUE),
            (2, 1, 'Cardona', 'cardona@economy.rp', %s, 'ACTIVO', FALSE)
        """, (pw_hash, pw_hash))

        # 4. Cuentas Personales
        cursor.execute("""
            INSERT INTO T_Cuenta (id_cuenta, id_jugador, id_servidor, tipo_cuenta, saldo_inicial, saldo_disponible)
            VALUES
            (2, 1, 1, 'PERSONAL', 150000.00, 150000.00),
            (3, 2, 1, 'PERSONAL', 120000.00, 120000.00)
        """)

        # 5. Empleos y Tarifas
        cursor.execute("""
            INSERT INTO T_Empleo (id_empleo, id_servidor, nombre_empleo, tarifa_base)
            VALUES
            (1, 1, 'Mecánico de Los Santos Custom', 250.00),
            (2, 1, 'Transportista de Mercancías', 180.00),
            (3, 1, 'Minero de Cantera Davis Quartz', 220.00),
            (4, 1, 'Comerciante Concesionario', 300.00)
        """)

        # 6. Catálogo Diverso de Bienes para Cardona222 (ID 1)
        items_cardona222 = [
            ('Coche Deportivo Pagani Zonda', 85000.00, 0),
            ('Reloj de Lujo Rolex Submariner', 14500.00, 0),
            ('Maletín de Dinero Táctico', 25000.00, 0),
            ('Laptop Cyber-Tech Neural', 4800.00, 0),
            ('Lingote de Oro 24K', 32000.00, 0),
            ('Rifle de Asalto AK Táctico', 18000.00, 0),
            ('Microchip Criptográfico Quantum', 9200.00, 0),
            ('Botiquín Médico Avanzado', 850.00, 0),
            ('Llave de Acceso Penthouse', 45000.00, 0),
            ('Pistola Glock Custom 9mm', 3200.00, 0),
            ('Vehículo Blindado Insurgent', 110000.00, 0),
            ('Cuchillo de Combate Militar', 650.00, 0)
        ]

        for nombre, precio, deuda in items_cardona222:
            cursor.execute("""
                INSERT INTO T_Item (id_jugador, nombre, precio, tiene_deuda, antiguedad_dias)
                VALUES (1, %s, %s, %s, 0)
            """, (nombre, precio, deuda))

        # 7. Catálogo Diverso de Bienes para Cardona (ID 2)
        items_cardona = [
            ('Casa de Campo en Vinewood Hills', 220000.00, 0),
            ('Moto de Carreras Ducati Panigale', 34000.00, 0),
            ('Diamante Puro Tallado', 42000.00, 0),
            ('Maletín de Dinero Táctico', 25000.00, 0),
            ('Coche Deportivo Ferrari F8', 95000.00, 0),
            ('Reloj de Lujo Patek Philippe', 18500.00, 0),
            ('Laptop Cyber-Tech Neural', 4800.00, 0),
            ('Lingote de Oro 24K', 32000.00, 0),
            ('Pistola Glock Custom 9mm', 3200.00, 0),
            ('Botiquín Médico Avanzado', 850.00, 0),
            ('Rifle de Francotirador Especial', 24000.00, 0),
            ('Llave de Acceso Bóveda Subterránea', 60000.00, 0)
        ]

        for nombre, precio, deuda in items_cardona:
            cursor.execute("""
                INSERT INTO T_Item (id_jugador, nombre, precio, tiene_deuda, antiguedad_dias)
                VALUES (2, %s, %s, %s, 0)
            """, (nombre, precio, deuda))

    print("Base de datos completamente homologada, limpia y con catálogo enriquecido.")

if __name__ == "__main__":
    reseed_clean_rich()

