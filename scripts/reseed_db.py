import sys
import os
import bcrypt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import get_db_cursor

def reseed():
    print("Iniciando reconstrucción limpia de la base de datos (Tablas en plural y preservando Admin Cardona222)...")
    
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw('21492477'.encode('utf-8'), salt).decode('utf-8')

    with get_db_cursor(commit=True) as (cursor, _):
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        all_tables = [
            'T_Detalle_Transaccion', 'T_Transaccion', 'T_Negociacion_Tradeo', 
            'T_Jornada_Laboral', 'T_Item', 'T_Cuenta', 'T_Empleo', 'T_Jugador', 
            'T_Servidor', 'T_Notificacion', 't_notificacion',
            'detalles_transacciones', 'transacciones', 'negociaciones_tradeos',
            'jornadas_laborales', 'items', 'cuentas', 'empleos', 'jugadores',
            'servidores', 'notificaciones'
        ]
        for tbl in all_tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {tbl}")
            except Exception:
                pass
        
        # 1. Servidores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS servidores (
              id_servidor INT AUTO_INCREMENT PRIMARY KEY,
              nombre VARCHAR(100) NOT NULL,
              porcentaje_comision DECIMAL(5,2) NOT NULL DEFAULT 5.00,
              limite_bienes_por_jugador INT NOT NULL DEFAULT 100,
              tiempo_enfriamiento_min INT NOT NULL DEFAULT 15
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 2. Jugadores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jugadores (
              id_jugador INT AUTO_INCREMENT PRIMARY KEY,
              id_servidor INT NOT NULL,
              nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
              correo VARCHAR(150) NOT NULL UNIQUE,
              contrasena_hash VARCHAR(255) NOT NULL,
              fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
              estado VARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
              es_admin BOOLEAN NOT NULL DEFAULT FALSE,
              CONSTRAINT fk_jugador_servidor FOREIGN KEY (id_servidor) REFERENCES servidores(id_servidor),
              CONSTRAINT chk_jugador_estado CHECK (estado IN ('ACTIVO','BANCARROTA','SUSPENDIDO'))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 3. Cuentas (1:N, sin unique en id_jugador)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cuentas (
              id_cuenta INT AUTO_INCREMENT PRIMARY KEY,
              id_jugador INT NULL,
              id_servidor INT NULL,
              tipo_cuenta VARCHAR(30) NOT NULL DEFAULT 'PERSONAL',
              saldo_inicial DECIMAL(12,2) NOT NULL DEFAULT 0.00,
              saldo_disponible DECIMAL(12,2) NOT NULL DEFAULT 0.00,
              CONSTRAINT fk_cuenta_jugador FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador) ON DELETE CASCADE,
              CONSTRAINT fk_cuenta_servidor FOREIGN KEY (id_servidor) REFERENCES servidores(id_servidor),
              CONSTRAINT chk_cuenta_tipo CHECK (tipo_cuenta IN ('PERSONAL','AHORROS','CORPORATIVA','SISTEMA'))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 4. Empleos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS empleos (
              id_empleo INT AUTO_INCREMENT PRIMARY KEY,
              id_servidor INT NOT NULL,
              nombre_empleo VARCHAR(100) NOT NULL,
              tarifa_base DECIMAL(10,2) NOT NULL,
              CONSTRAINT fk_empleo_servidor FOREIGN KEY (id_servidor) REFERENCES servidores(id_servidor)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 5. Items (custodia y concesionario)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
              id_item INT AUTO_INCREMENT PRIMARY KEY,
              id_jugador INT NULL,
              nombre VARCHAR(100) NOT NULL,
              precio DECIMAL(12,2) NOT NULL,
              fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
              tiene_deuda BOOLEAN NOT NULL DEFAULT FALSE,
              antiguedad_dias INT NOT NULL DEFAULT 0,
              estado_custodia VARCHAR(30) NOT NULL DEFAULT 'PERSONAL',
              tipo_propietario VARCHAR(30) NOT NULL DEFAULT 'JUGADOR',
              CONSTRAINT fk_item_jugador FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador) ON DELETE SET NULL,
              CONSTRAINT chk_item_custodia CHECK (estado_custodia IN ('PERSONAL','CONCESIONARIO','EN_TRADEO','EMBARGADO')),
              CONSTRAINT chk_item_propietario CHECK (tipo_propietario IN ('JUGADOR','CONCESIONARIO','SISTEMA'))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 6. Jornadas Laborales
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jornadas_laborales (
              id_jornada INT AUTO_INCREMENT PRIMARY KEY,
              id_jugador INT NOT NULL,
              id_empleo INT NOT NULL,
              horas_trabajadas DECIMAL(6,2) NOT NULL,
              fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
              monto_pagado DECIMAL(10,2) NOT NULL DEFAULT 0.00,
              CONSTRAINT fk_jornada_jugador FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador) ON DELETE CASCADE,
              CONSTRAINT fk_jornada_empleo FOREIGN KEY (id_empleo) REFERENCES empleos(id_empleo)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 7. Negociaciones Tradeos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS negociaciones_tradeos (
              id_negociacion INT AUTO_INCREMENT PRIMARY KEY,
              id_jugador_1 INT NOT NULL,
              id_jugador_2 INT NOT NULL,
              id_item_j1 INT NULL,
              id_item_j2 INT NULL,
              items_j1_ids VARCHAR(255) NULL,
              items_j2_ids VARCHAR(255) NULL,
              monto_j1 DECIMAL(12,2) NOT NULL DEFAULT 0.00,
              monto_j2 DECIMAL(12,2) NOT NULL DEFAULT 0.00,
              confirmacion_j1 BOOLEAN NOT NULL DEFAULT FALSE,
              confirmacion_j2 BOOLEAN NOT NULL DEFAULT FALSE,
              estado VARCHAR(50) NOT NULL DEFAULT 'PENDIENTE',
              fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
              fecha_expiracion DATETIME NOT NULL,
              CONSTRAINT fk_negociacion_jugador1 FOREIGN KEY (id_jugador_1) REFERENCES jugadores(id_jugador) ON DELETE CASCADE,
              CONSTRAINT fk_negociacion_jugador2 FOREIGN KEY (id_jugador_2) REFERENCES jugadores(id_jugador) ON DELETE CASCADE,
              CONSTRAINT fk_negociacion_item_j1 FOREIGN KEY (id_item_j1) REFERENCES items(id_item) ON DELETE SET NULL,
              CONSTRAINT fk_negociacion_item_j2 FOREIGN KEY (id_item_j2) REFERENCES items(id_item) ON DELETE SET NULL,
              CONSTRAINT chk_negociacion_estado CHECK (estado IN ('PENDIENTE','ACEPTADO','EN_PROCESO','ESPERANDO_CONFIRMACION_FINAL','CONFIRMADO','COMPLETADO','CANCELADO','EXPIRADO'))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 8. Transacciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transacciones (
              id_transaccion INT AUTO_INCREMENT PRIMARY KEY,
              id_item_afectado INT NULL,
              id_negociacion INT NULL,
              id_jornada INT NULL,
              tipo_transaccion VARCHAR(50) NOT NULL,
              estado_transaccion VARCHAR(30) NOT NULL DEFAULT 'COMPLETADA',
              monto DECIMAL(12,2) NOT NULL,
              fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
              CONSTRAINT fk_transaccion_item FOREIGN KEY (id_item_afectado) REFERENCES items(id_item) ON DELETE SET NULL,
              CONSTRAINT fk_transaccion_negociacion FOREIGN KEY (id_negociacion) REFERENCES negociaciones_tradeos(id_negociacion) ON DELETE SET NULL,
              CONSTRAINT fk_transaccion_jornada FOREIGN KEY (id_jornada) REFERENCES jornadas_laborales(id_jornada) ON DELETE SET NULL,
              CONSTRAINT chk_transaccion_tipo CHECK (tipo_transaccion IN ('PAGO_SALARIO','TRADEO_P2P','COMPRA_COMERCIANTE','TRANSFERENCIA_DIRECTA','AJUSTE_ADMIN')),
              CONSTRAINT chk_transaccion_estado CHECK (estado_transaccion IN ('COMPLETADA','CANCELADA','REVERTIDA'))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 9. Detalles Transacciones (Partida Doble)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalles_transacciones (
              id_detalle INT AUTO_INCREMENT PRIMARY KEY,
              id_transaccion INT NOT NULL,
              cuenta_origen INT NOT NULL,
              cuenta_destino INT NOT NULL,
              tipo_movimiento VARCHAR(20) NOT NULL,
              monto_detalle DECIMAL(12,2) NOT NULL,
              concepto VARCHAR(100),
              CONSTRAINT fk_detalle_transaccion FOREIGN KEY (id_transaccion) REFERENCES transacciones(id_transaccion) ON DELETE CASCADE,
              CONSTRAINT fk_detalle_origen FOREIGN KEY (cuenta_origen) REFERENCES cuentas(id_cuenta),
              CONSTRAINT fk_detalle_destino FOREIGN KEY (cuenta_destino) REFERENCES cuentas(id_cuenta),
              CONSTRAINT chk_detalle_tipo CHECK (tipo_movimiento IN ('DEBITO','CREDITO'))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # 10. Notificaciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notificaciones (
              id_notificacion INT AUTO_INCREMENT PRIMARY KEY,
              id_jugador INT NOT NULL,
              titulo VARCHAR(100) NOT NULL,
              mensaje TEXT NOT NULL,
              tipo VARCHAR(20) NOT NULL DEFAULT 'ADMIN',
              leido BOOLEAN NOT NULL DEFAULT FALSE,
              fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
              CONSTRAINT fk_notificacion_jugador FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Índices de alto rendimiento
        try:
            cursor.execute("CREATE INDEX idx_trade_j1_j2_estado ON negociaciones_tradeos(id_jugador_1, id_jugador_2, estado)")
            cursor.execute("CREATE INDEX idx_trade_j2_estado ON negociaciones_tradeos(id_jugador_2, estado)")
            cursor.execute("CREATE INDEX idx_notif_jugador_leido ON notificaciones(id_jugador, leido)")
            cursor.execute("CREATE INDEX idx_trans_item ON transacciones(id_item_afectado)")
        except Exception:
            pass

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # --- SEED INICIAL (ADMIN CARDONA222 + TESORERÍA + EMPLEOS) ---
        # 1. Servidor Principal
        cursor.execute("""
            INSERT INTO servidores (id_servidor, nombre, porcentaje_comision, limite_bienes_por_jugador, tiempo_enfriamiento_min)
            VALUES (1, 'Servidor Principal RP', 5.00, 100, 15)
        """)

        # 2. Cuenta de Sistema (Tesorería Central)
        cursor.execute("""
            INSERT INTO cuentas (id_cuenta, id_jugador, id_servidor, tipo_cuenta, saldo_inicial, saldo_disponible)
            VALUES (1, NULL, 1, 'SISTEMA', 10000000.00, 10000000.00)
        """)

        # 3. Usuario Administrador Único: Cardona222
        cursor.execute("""
            INSERT INTO jugadores (id_jugador, id_servidor, nombre_usuario, correo, contrasena_hash, estado, es_admin)
            VALUES (1, 1, 'Cardona222', 'cardona222@economy.rp', %s, 'ACTIVO', TRUE)
        """, (pw_hash,))

        # 4. Cuenta Bancaria Personal de Cardona222
        cursor.execute("""
            INSERT INTO cuentas (id_cuenta, id_jugador, id_servidor, tipo_cuenta, saldo_inicial, saldo_disponible)
            VALUES (2, 1, 1, 'PERSONAL', 100000.00, 100000.00)
        """)

        # 5. Empleos Disponibles
        cursor.execute("""
            INSERT INTO empleos (id_empleo, id_servidor, nombre_empleo, tarifa_base)
            VALUES
            (1, 1, 'Mecánico de Los Santos Custom', 250.00),
            (2, 1, 'Transportista de Mercancías', 180.00),
            (3, 1, 'Minero de Cantera Davis Quartz', 220.00),
            (4, 1, 'Comerciante Concesionario', 300.00)
        """)

        # 6. Inventario Inicial de Cardona222
        cursor.execute("""
            INSERT INTO items (id_jugador, nombre, precio, tiene_deuda, antiguedad_dias, estado_custodia, tipo_propietario)
            VALUES
            (1, 'Coche Deportivo', 50000.00, FALSE, 0, 'PERSONAL', 'JUGADOR'),
            (1, 'Reloj de Lujo', 5000.00, FALSE, 0, 'PERSONAL', 'JUGADOR'),
            (1, 'Kit de Reparación', 150.00, FALSE, 0, 'PERSONAL', 'JUGADOR'),
            (1, 'Maletín Blindado', 8500.00, FALSE, 0, 'PERSONAL', 'JUGADOR')
        """)

    print("Base de datos configurada desde cero con éxito (Tablas en plural y Admin Cardona222 activo).")

if __name__ == "__main__":
    reseed()
