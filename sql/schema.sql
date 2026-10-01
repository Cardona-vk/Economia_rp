-- ====================================================================
-- SCHEMA DE BASE DE DATOS: ECONOMY RP (PRODUCCIÓN NUBE / AIVEN)
-- Tablas en PLURAL y sin prefijo T_
-- Compatible con MySQL 8.0+ / Aiven Cloud MySQL
-- ====================================================================

USE defaultdb;

-- 1. TABLA: servidores
CREATE TABLE IF NOT EXISTS servidores (
  id_servidor INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  porcentaje_comision DECIMAL(5,2) NOT NULL DEFAULT 5.00,
  limite_bienes_por_jugador INT NOT NULL DEFAULT 100,
  tiempo_enfriamiento_min INT NOT NULL DEFAULT 15
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. TABLA: jugadores
CREATE TABLE IF NOT EXISTS jugadores (
  id_jugador INT AUTO_INCREMENT PRIMARY KEY,
  id_servidor INT NOT NULL DEFAULT 1,
  nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
  correo VARCHAR(150) NOT NULL UNIQUE,
  contrasena_hash VARCHAR(255) NOT NULL,
  fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  estado VARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
  es_admin BOOLEAN NOT NULL DEFAULT FALSE,
  CONSTRAINT fk_jugador_servidor FOREIGN KEY (id_servidor) REFERENCES servidores(id_servidor) ON DELETE CASCADE,
  CONSTRAINT chk_jugador_estado CHECK (estado IN ('ACTIVO','BANCARROTA','SUSPENDIDO'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. TABLA: empleos
CREATE TABLE IF NOT EXISTS empleos (
  id_empleo INT AUTO_INCREMENT PRIMARY KEY,
  id_servidor INT NOT NULL DEFAULT 1,
  nombre_empleo VARCHAR(100) NOT NULL,
  tarifa_base DECIMAL(10,2) NOT NULL,
  CONSTRAINT fk_empleo_servidor FOREIGN KEY (id_servidor) REFERENCES servidores(id_servidor) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. TABLA: jornadas_laborales
CREATE TABLE IF NOT EXISTS jornadas_laborales (
  id_jornada INT AUTO_INCREMENT PRIMARY KEY,
  id_jugador INT NOT NULL,
  id_empleo INT NOT NULL,
  horas_trabajadas DECIMAL(6,2) NOT NULL,
  fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  monto_pagado DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  CONSTRAINT fk_jornada_jugador FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador) ON DELETE CASCADE,
  CONSTRAINT fk_jornada_empleo FOREIGN KEY (id_empleo) REFERENCES empleos(id_empleo) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. TABLA: cuentas
CREATE TABLE IF NOT EXISTS cuentas (
  id_cuenta INT AUTO_INCREMENT PRIMARY KEY,
  id_jugador INT NULL,
  id_servidor INT NULL,
  tipo_cuenta VARCHAR(20) NOT NULL,
  saldo_inicial DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  saldo_disponible DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  CONSTRAINT fk_cuenta_jugador FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador) ON DELETE CASCADE,
  CONSTRAINT fk_cuenta_servidor FOREIGN KEY (id_servidor) REFERENCES servidores(id_servidor) ON DELETE CASCADE,
  CONSTRAINT chk_cuenta_tipo CHECK (tipo_cuenta IN ('PERSONAL','SISTEMA'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. TABLA: items
CREATE TABLE IF NOT EXISTS items (
  id_item INT AUTO_INCREMENT PRIMARY KEY,
  id_jugador INT NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  precio DECIMAL(12,2) NOT NULL,
  fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  tiene_deuda BOOLEAN NOT NULL DEFAULT FALSE,
  antiguedad_dias INT NOT NULL DEFAULT 0,
  estado_custodia VARCHAR(20) NOT NULL DEFAULT 'PERSONAL',
  tipo_propietario VARCHAR(20) NOT NULL DEFAULT 'JUGADOR',
  CONSTRAINT fk_item_jugador FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador) ON DELETE CASCADE,
  CONSTRAINT chk_item_custodia CHECK (estado_custodia IN ('PERSONAL','EMBARGADO','EN_SUBASTA','EN_TRADE'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. TABLA: negociaciones_tradeos
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
  CONSTRAINT chk_negociacion_estado CHECK (estado IN ('PENDIENTE','ACEPTADO','EN_PROCESO','ESPERANDO_CONFIRMACION_FINAL','CONFIRMADO','COMPLETADO','CANCELADO','EXPIRADO'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. TABLA: transacciones
CREATE TABLE IF NOT EXISTS transacciones (
  id_transaccion INT AUTO_INCREMENT PRIMARY KEY,
  id_item_afectado INT NULL,
  id_negociacion INT NULL,
  id_jornada INT NULL,
  tipo_transaccion VARCHAR(30) NOT NULL,
  estado_transaccion VARCHAR(20) NOT NULL DEFAULT 'COMPLETADA',
  monto DECIMAL(12,2) NOT NULL,
  fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_transaccion_item FOREIGN KEY (id_item_afectado) REFERENCES items(id_item) ON DELETE SET NULL,
  CONSTRAINT fk_transaccion_negociacion FOREIGN KEY (id_negociacion) REFERENCES negociaciones_tradeos(id_negociacion) ON DELETE SET NULL,
  CONSTRAINT fk_transaccion_jornada FOREIGN KEY (id_jornada) REFERENCES jornadas_laborales(id_jornada) ON DELETE SET NULL,
  CONSTRAINT chk_transaccion_tipo CHECK (tipo_transaccion IN ('PAGO_SALARIO','TRADEO_P2P','COMPRA_COMERCIANTE','AJUSTE_ADMIN')),
  CONSTRAINT chk_transaccion_estado CHECK (estado_transaccion IN ('COMPLETADA','CANCELADA','REVERTIDA'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. TABLA: detalles_transacciones
CREATE TABLE IF NOT EXISTS detalles_transacciones (
  id_detalle INT AUTO_INCREMENT PRIMARY KEY,
  id_transaccion INT NOT NULL,
  cuenta_origen INT NOT NULL,
  cuenta_destino INT NOT NULL,
  tipo_movimiento VARCHAR(10) NOT NULL,
  monto_detalle DECIMAL(12,2) NOT NULL,
  concepto VARCHAR(80),
  CONSTRAINT fk_detalle_transaccion FOREIGN KEY (id_transaccion) REFERENCES transacciones(id_transaccion) ON DELETE CASCADE,
  CONSTRAINT fk_detalle_origen FOREIGN KEY (cuenta_origen) REFERENCES cuentas(id_cuenta),
  CONSTRAINT fk_detalle_destino FOREIGN KEY (cuenta_destino) REFERENCES cuentas(id_cuenta),
  CONSTRAINT chk_detalle_tipo CHECK (tipo_movimiento IN ('DEBITO','CREDITO'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. TABLA: notificaciones
CREATE TABLE IF NOT EXISTS notificaciones (
  id_notificacion INT AUTO_INCREMENT PRIMARY KEY,
  id_jugador INT NOT NULL,
  titulo VARCHAR(100) NOT NULL,
  mensaje TEXT NOT NULL,
  tipo VARCHAR(20) NOT NULL DEFAULT 'ADMIN',
  leido BOOLEAN NOT NULL DEFAULT FALSE,
  fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_notificacion_jugador FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ====================================================================
-- ÍNDICES DE RENDIMIENTO
-- ====================================================================
CREATE INDEX idx_jugador_servidor ON jugadores(id_servidor);
CREATE INDEX idx_item_jugador ON items(id_jugador);
CREATE INDEX idx_cuenta_jugador_tipo ON cuentas(id_jugador, tipo_cuenta);
CREATE INDEX idx_notif_jugador_leido ON notificaciones(id_jugador, leido);
CREATE INDEX idx_trade_j1_j2_estado ON negociaciones_tradeos(id_jugador_1, id_jugador_2, estado);
CREATE INDEX idx_transacciones_fecha ON transacciones(fecha_hora DESC);