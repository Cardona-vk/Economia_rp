
USE economy_rp;

INSERT INTO T_Item (id_jugador, nombre, precio, fecha, tiene_deuda, antiguedad_dias)
VALUES
(1, 'Coche Deportivo', 50000.00, NOW(), FALSE, 0),
(1, 'Reloj de Lujo', 5000.00, NOW(), FALSE, 0),
(1, 'Casa de Campo', 150000.00, NOW(), FALSE, 0);
UPDATE T_Cuenta SET saldo_disponible = saldo_disponible + 50000.00 WHERE id_jugador = 1 AND tipo_cuenta = 'PERSONAL';

INSERT INTO T_Item (id_jugador, nombre, precio, fecha, tiene_deuda, antiguedad_dias)
VALUES
(2, 'Coche Deportivo', 50000.00, NOW(), FALSE, 0),
(2, 'Reloj de Lujo', 5000.00, NOW(), FALSE, 0),
(2, 'Casa de Campo', 150000.00, NOW(), FALSE, 0);
UPDATE T_Cuenta SET saldo_disponible = saldo_disponible + 50000.00 WHERE id_jugador = 2 AND tipo_cuenta = 'PERSONAL';