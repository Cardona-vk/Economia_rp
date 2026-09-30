from mysql.connector import Error
from core.database import get_db_cursor, ensure_scalar

def consultar_saldo(id_jugador):
    """Obtiene el saldo disponible de la cuenta PERSONAL del jugador."""
    id_clean = ensure_scalar(id_jugador)
    if not id_clean:
        return None, "ID de jugador inválido"

    try:
        with get_db_cursor() as (cursor, _):
            query = "SELECT saldo_disponible FROM T_Cuenta WHERE id_jugador = %s AND tipo_cuenta = 'PERSONAL'"
            cursor.execute(query, (id_clean,))
            result = cursor.fetchone()
            if result is not None:
                return float(result[0]), "Saldo recuperado"
            return None, "Cuenta no encontrada para este jugador"
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
            query = "SELECT * FROM T_Item WHERE id_jugador = %s ORDER BY fecha DESC"
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
            # 1. Saldo disponible
            cursor.execute("SELECT saldo_disponible FROM T_Cuenta WHERE id_jugador = %s AND tipo_cuenta = 'PERSONAL'", (id_clean,))
            row_saldo = cursor.fetchone()
            saldo = float(row_saldo['saldo_disponible']) if row_saldo else 0.0

            # 2. Inventario
            cursor.execute("SELECT id_item, nombre, precio, tiene_deuda, antiguedad_dias, fecha FROM T_Item WHERE id_jugador = %s ORDER BY fecha DESC", (id_clean,))
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
                FROM T_Transaccion t
                JOIN T_Detalle_Transaccion dt ON dt.id_transaccion = t.id_transaccion
                JOIN T_Cuenta c ON (dt.cuenta_origen = c.id_cuenta OR dt.cuenta_destino = c.id_cuenta)
                WHERE c.id_jugador = %s AND t.estado_transaccion = 'COMPLETADA'
            """, (id_clean,))
            row_trades = cursor.fetchone()
            total_trades = row_trades['total_trades'] if row_trades else 0


            # 5. Parámetros del Servidor
            cursor.execute("SELECT porcentaje_comision, limite_bienes_por_jugador, tiempo_enfriamiento_min FROM T_Servidor WHERE id_servidor = 1")
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
    """Ejecuta el procedimiento almacenado para procesar el pago de salario."""
    id_jugador_clean = ensure_scalar(id_jugador)
    id_empleo_clean = ensure_scalar(id_empleo)
    
    try:
        with get_db_cursor(commit=True) as (cursor, _):
            cursor.callproc('sp_pagar_jornada', (id_jugador_clean, id_empleo_clean, float(horas)))
            return True, "Pago de jornada procesado exitosamente"
    except Error as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)
