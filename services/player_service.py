from mysql.connector import Error
from core.database import get_db_cursor, ensure_scalar

def consultar_saldo(id_jugador):
    """Obtiene el saldo disponible total de las cuentas (o cuenta principal PERSONAL) del jugador."""
    id_clean = ensure_scalar(id_jugador)
    if not id_clean:
        return None, "ID de jugador inválido"

    try:
        with get_db_cursor() as (cursor, _):
            query = "SELECT saldo_disponible FROM cuentas WHERE id_jugador = %s ORDER BY (tipo_cuenta = 'PERSONAL') DESC, id_cuenta ASC LIMIT 1"
            cursor.execute(query, (id_clean,))
            result = cursor.fetchone()
            if result is not None:
                return float(result[0]), "Saldo recuperado"
            return 0.0, "Cuenta no encontrada para este jugador"
    except Error as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)

def consultar_inventario(id_jugador):
    """Retorna la lista de ítems / bienes propiedad del jugador."""
    id_clean = ensure_scalar(id_jugador)
    if not id_clean:
        return None, "ID de jugador inválido"

    try:
        with get_db_cursor(dictionary=True) as (cursor, _):
            query = "SELECT * FROM items WHERE id_jugador = %s ORDER BY fecha DESC"
            cursor.execute(query, (id_clean,))
            items = cursor.fetchall()
            return items, "Inventario recuperado"
    except Error as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)

def consultar_metricas_dashboard(id_jugador):
    """
    Retorna métricas consolidadas para el Dashboard: saldo, inventario, valor bienes,
    patrimonio total, conteo de libres/deuda, total transacciones y límites del servidor.
    """
    id_clean = ensure_scalar(id_jugador)
    if not id_clean:
        return None, "ID de jugador inválido"

    try:
        with get_db_cursor(dictionary=True) as (cursor, _):
            # 1. Saldo disponible de cuenta PERSONAL / Principal
            cursor.execute("SELECT saldo_disponible FROM cuentas WHERE id_jugador = %s ORDER BY (tipo_cuenta = 'PERSONAL') DESC, id_cuenta ASC LIMIT 1", (id_clean,))
            row_saldo = cursor.fetchone()
            saldo = float(row_saldo['saldo_disponible']) if row_saldo else 0.0

            # 2. Inventario
            cursor.execute("SELECT id_item, nombre, precio, tiene_deuda, antiguedad_dias, fecha, estado_custodia, tipo_propietario FROM items WHERE id_jugador = %s ORDER BY fecha DESC", (id_clean,))
            inventario = cursor.fetchall() or []

            # 3. Cálculos de patrimonio e inventario
            total_items = len(inventario)
            valor_inventario = sum(float(item['precio'] or 0.0) for item in inventario)
            patrimonio_total = saldo + valor_inventario
            items_con_deuda = sum(1 for item in inventario if item.get('tiene_deuda'))
            items_libres = total_items - items_con_deuda

            # 4. Total trades / transacciones del jugador
            cursor.execute("""
                SELECT COUNT(DISTINCT t.id_transaccion) AS total_trades
                FROM transacciones t
                JOIN detalles_transacciones dt ON dt.id_transaccion = t.id_transaccion
                JOIN cuentas c ON (dt.cuenta_origen = c.id_cuenta OR dt.cuenta_destino = c.id_cuenta)
                WHERE c.id_jugador = %s AND t.estado_transaccion = 'COMPLETADA'
            """, (id_clean,))
            row_trades = cursor.fetchone()
            total_trades = row_trades['total_trades'] if row_trades else 0

            # 5. Parámetros del Servidor
            cursor.execute("SELECT porcentaje_comision, limite_bienes_por_jugador, tiempo_enfriamiento_min FROM servidores WHERE id_servidor = 1")
            row_srv = cursor.fetchone()
            limite_bienes = row_srv['limite_bienes_por_jugador'] if row_srv else 100
            comision = float(row_srv['porcentaje_comision']) if row_srv else 5.0

            return {
                "saldo": saldo,
                "inventario": inventario,
                "total_items": total_items,
                "valor_inventario": valor_inventario,
                "patrimonio_total": patrimonio_total,
                "items_con_deuda": items_con_deuda,
                "items_libres": items_libres,
                "total_trades": total_trades,
                "limite_bienes": limite_bienes,
                "porcentaje_comision": comision
            }, "OK"
    except Exception as e:
        return None, str(e)

def pagar_jornada(id_jugador, id_empleo, horas):
    """Procesa el pago de salario registrando jornada y partida doble inmutable (RN001, RN003, RN005, RN008)."""
    id_jugador_clean = ensure_scalar(id_jugador)
    id_empleo_clean = ensure_scalar(id_empleo)
    horas_val = float(horas)

    try:
        with get_db_cursor(commit=True) as (cursor, _):
            # 1. Verificar enfriamiento laboral (RN008)
            cursor.execute("""
                SELECT MAX(fecha_hora) AS ultima_fecha 
                FROM jornadas_laborales 
                WHERE id_jugador = %s AND id_empleo = %s
            """, (id_jugador_clean, id_empleo_clean))
            row_jornada = cursor.fetchone()
            
            cursor.execute("""
                SELECT s.tiempo_enfriamiento_min 
                FROM jugadores j JOIN servidores s ON j.id_servidor = s.id_servidor 
                WHERE j.id_jugador = %s
            """, (id_jugador_clean,))
            row_serv = cursor.fetchone()
            enfriamiento = row_serv[0] if row_serv else 15

            if row_jornada and row_jornada[0]:
                cursor.execute("SELECT TIMESTAMPDIFF(MINUTE, %s, NOW())", (row_jornada[0],))
                mins = cursor.fetchone()[0]
                if mins is not None and mins < enfriamiento:
                    return False, f"El operador aún se encuentra en periodo de enfriamiento ({enfriamiento - mins} min restantes) (RN008)."

            # 2. Obtener tarifa del empleo
            cursor.execute("SELECT tarifa_base FROM empleos WHERE id_empleo = %s", (id_empleo_clean,))
            row_emp = cursor.fetchone()
            if not row_emp:
                return False, "Empleo no encontrado."
            tarifa = float(row_emp[0])
            monto_total = round(tarifa * horas_val, 2)

            # 3. Registrar jornada laboral
            cursor.execute("""
                INSERT INTO jornadas_laborales (id_jugador, id_empleo, horas_trabajadas, monto_pagado)
                VALUES (%s, %s, %s, %s)
            """, (id_jugador_clean, id_empleo_clean, horas_val, monto_total))
            id_jornada = cursor.lastrowid

            # 4. Obtener cuentas
            cursor.execute("SELECT id_cuenta FROM cuentas WHERE id_jugador = %s ORDER BY (tipo_cuenta = 'PERSONAL') DESC, id_cuenta ASC LIMIT 1", (id_jugador_clean,))
            row_cj = cursor.fetchone()
            if not row_cj:
                return False, "El jugador no posee cuenta bancaria activa."
            id_cuenta_jugador = row_cj[0]

            cursor.execute("SELECT id_cuenta FROM cuentas WHERE tipo_cuenta = 'SISTEMA' LIMIT 1")
            row_cs = cursor.fetchone()
            id_cuenta_sistema = row_cs[0] if row_cs else 1

            # 5. Registrar Transacción Inmutable (RN003)
            cursor.execute("""
                INSERT INTO transacciones (id_jornada, tipo_transaccion, estado_transaccion, monto)
                VALUES (%s, 'PAGO_SALARIO', 'COMPLETADA', %s)
            """, (id_jornada, monto_total))
            id_trx = cursor.lastrowid

            # 6. Registrar Partida Doble simétrica (RN003, RN005)
            cursor.execute("""
                INSERT INTO detalles_transacciones (id_transaccion, cuenta_origen, cuenta_destino, tipo_movimiento, monto_detalle, concepto)
                VALUES 
                (%s, %s, %s, 'DEBITO', %s, 'PAGO_SALARIO'),
                (%s, %s, %s, 'CREDITO', %s, 'PAGO_SALARIO')
            """, (id_trx, id_cuenta_sistema, id_cuenta_jugador, monto_total,
                  id_trx, id_cuenta_sistema, id_cuenta_jugador, monto_total))

            # 7. Actualizar balances contables
            cursor.execute("UPDATE cuentas SET saldo_disponible = saldo_disponible - %s WHERE id_cuenta = %s", (monto_total, id_cuenta_sistema))
            cursor.execute("UPDATE cuentas SET saldo_disponible = saldo_disponible + %s WHERE id_cuenta = %s", (monto_total, id_cuenta_jugador))

            return True, f"Pago de jornada por ${monto_total:,.2f} procesado y acreditado exitosamente."
    except Error as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)
