import sys
import os
import bcrypt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import get_db_cursor

def reseed():
    print("Iniciando reconstrucción limpia de la base de datos...")
    
    # 1. Hashear contraseñas
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw('21492477'.encode('utf-8'), salt).decode('utf-8')

    with get_db_cursor(commit=True) as (cursor, _):
        # Desactivar FK checks para limpieza rápida
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for tbl in ['T_Detalle_Transaccion', 'T_Transaccion', 'T_Negociacion_Tradeo', 'T_Jornada_Laboral', 'T_Item', 'T_Cuenta', 'T_Empleo', 'T_Jugador', 'T_Servidor']:
            try:
                cursor.execute(f"TRUNCATE TABLE {tbl}")
            except Exception:
                pass
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # 1. Servidor
        cursor.execute("""
            INSERT INTO T_Servidor (id_servidor, nombre, porcentaje_comision, limite_bienes_por_jugador, tiempo_enfriamiento_min)
            VALUES (1, 'Servidor Principal RP', 5.00, 100, 15)
        """)

        # 2. Cuenta de Sistema (Tesorería)
        cursor.execute("""
            INSERT INTO T_Cuenta (id_cuenta, id_jugador, id_servidor, tipo_cuenta, saldo_inicial, saldo_disponible)
            VALUES (1, NULL, 1, 'SISTEMA', 10000000.00, 10000000.00)
        """)

        # 3. Jugadores (Cardona222 y Cardona)
        cursor.execute("""
            INSERT INTO T_Jugador (id_jugador, id_servidor, nombre_usuario, correo, contrasena_hash, estado)
            VALUES 
            (1, 1, 'Cardona222', 'cardona222@economy.rp', %s, 'ACTIVO'),
            (2, 1, 'Cardona', 'cardona@economy.rp', %s, 'ACTIVO')
        """, (pw_hash, pw_hash))

        # 4. Cuentas Personales
        cursor.execute("""
            INSERT INTO T_Cuenta (id_cuenta, id_jugador, id_servidor, tipo_cuenta, saldo_inicial, saldo_disponible)
            VALUES
            (2, 1, 1, 'PERSONAL', 100000.00, 100000.00),
            (3, 2, 1, 'PERSONAL', 100000.00, 100000.00)
        """)

        # 5. Empleos
        cursor.execute("""
            INSERT INTO T_Empleo (id_empleo, id_servidor, nombre_empleo, tarifa_base)
            VALUES
            (1, 1, 'Mecánico de Los Santos Custom', 250.00),
            (2, 1, 'Transportista de Mercancías', 180.00),
            (3, 1, 'Minero de Cantera Davis Quartz', 220.00),
            (4, 1, 'Comerciante Concesionario', 300.00)
        """)

        # 6. Bienes e Inventario de Cardona222 (ID 1)
        cursor.execute("""
            INSERT INTO T_Item (id_jugador, nombre, precio, tiene_deuda, antiguedad_dias)
            VALUES
            (1, 'Coche Deportivo', 50000.00, FALSE, 0),
            (1, 'Reloj de Lujo', 5000.00, FALSE, 0),
            (1, 'Kit de Reparación', 150.00, FALSE, 0),
            (1, 'Maletín Blindado', 8500.00, FALSE, 0)
        """)

        # 7. Bienes e Inventario de Cardona (ID 2)
        cursor.execute("""
            INSERT INTO T_Item (id_jugador, nombre, precio, tiene_deuda, antiguedad_dias)
            VALUES
            (2, 'Casa de Campo', 150000.00, FALSE, 0),
            (2, 'Moto de Carreras', 28000.00, FALSE, 0),
            (2, 'Laptop Cyber-Tech', 3500.00, FALSE, 0)
        """)

    print("Base de datos re-inicializada exitosamente con datos limpios.")

if __name__ == "__main__":
    reseed()
