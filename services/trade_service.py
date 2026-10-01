from mysql.connector import Error
from core.database import get_db_cursor, ensure_scalar

def _parse_id_list(val):
    """Convierte una lista, entero o cadena separada por comas en una lista limpia de enteros únicos."""
    if val is None or val == '':
        return []
    if isinstance(val, (list, tuple, set)):
        result = []
        for x in val:
            clean = ensure_scalar(x)
            if clean:
                try:
                    result.append(int(clean))
                except (ValueError, TypeError):
                    pass
        return list(dict.fromkeys(result))
    if isinstance(val, int):
        return [val]
    if isinstance(val, str):
        parts = [p.strip() for p in val.split(',') if p.strip()]
        result = []
        for p in parts:
            try:
                result.append(int(p))
            except ValueError:
                pass
        return list(dict.fromkeys(result))
    return []

def _get_items_details(item_ids):
    """Recupera los detalles completos de una lista de IDs de ítems."""
    clean_ids = _parse_id_list(item_ids)
    if not clean_ids:
        return []
    try:
        with get_db_cursor(dictionary=True) as (cursor, _):
            format_strings = ','.join(['%s'] * len(clean_ids))
            query = f"""
            SELECT id_item, id_jugador, nombre, precio, fecha, tiene_deuda, antiguedad_dias, estado_custodia, tipo_propietario
            FROM items
            WHERE id_item IN ({format_strings})
            """
            cursor.execute(query, tuple(clean_ids))
            return cursor.fetchall() or []
    except Exception:
        return []

def abrir_negociacion(id_j1, id_j2, item_j1=None, item_j2=None, monto_j1=0.0, monto_j2=0.0, exp=10):
    """
    Inicia una negociación de comercio P2P con validación integral de Reglas de Negocio (RN001 - RN012).
    """
    id_j1_clean = ensure_scalar(id_j1)
    id_j2_clean = ensure_scalar(id_j2)
    
    if not id_j1_clean or not id_j2_clean:
        return False, "IDs de operadores inválidos."
    if id_j1_clean == id_j2_clean:
        return False, "No puedes iniciar una negociación contigo mismo (RN002)."

    items_j1_list = _parse_id_list(item_j1)
    items_j2_list = _parse_id_list(item_j2)
    
    primary_item_j1 = items_j1_list[0] if items_j1_list else None
    primary_item_j2 = items_j2_list[0] if items_j2_list else None
    items_j1_str = ','.join(map(str, items_j1_list)) if items_j1_list else None
    items_j2_str = ','.join(map(str, items_j2_list)) if items_j2_list else None

    try:
        monto_j1_clean = float(monto_j1 or 0.0)
        monto_j2_clean = float(monto_j2 or 0.0)
        exp_clean = int(exp if exp is not None else 10)
    except (ValueError, TypeError):
        return False, "Montos o tiempo de expiración inválidos."

    if monto_j1_clean < 0 or monto_j2_clean < 0:
        return False, "Los montos de oferta no pueden ser negativos."

    if not items_j1_list and not items_j2_list and monto_j1_clean == 0 and monto_j2_clean == 0:
        return False, "La propuesta comercial no puede estar completamente vacía."

    try:
        with get_db_cursor(commit=True, dictionary=True) as (cursor, _):
            # 1. Verificar estado de los jugadores (RN009)
            cursor.execute("SELECT id_jugador, nombre_usuario, estado FROM jugadores WHERE id_jugador IN (%s, %s)", (id_j1_clean, id_j2_clean))
            rows = cursor.fetchall()
            if len(rows) < 2:
                return False, "Uno de los operadores no existe en el sistema."
            
            for p in rows:
                if p['estado'] == 'BANCARROTA':
                    return False, f"El operador {p['nombre_usuario']} está en BANCARROTA y no puede realizar transacciones comerciales (RN009)."
                if p['estado'] == 'SUSPENDIDO':
                    return False, f"El operador {p['nombre_usuario']} se encuentra suspendido del servidor."

            # 2. Límite diario de tradeos (RN011: máx 5 tradeos/día)
            cursor.execute("""
                SELECT COUNT(*) AS total_hoy FROM transacciones t
                JOIN negociaciones_tradeos n ON t.id_negociacion = n.id_negociacion
                WHERE t.tipo_transaccion = 'TRADEO_P2P' 
                  AND DATE(t.fecha_hora) = CURDATE()
                  AND (n.id_jugador_1 = %s OR n.id_jugador_2 = %s)
            """, (id_j1_clean, id_j1_clean))
            tradeos_hoy = cursor.fetchone()['total_hoy']
            if tradeos_hoy >= 5:
                return False, "Has alcanzado el límite regulatorio de 5 tradeos por día (RN011)."

            # 3. Negociación activa simultánea (RN012)
            cursor.execute("""
                SELECT COUNT(*) AS total_pend FROM negociaciones_tradeos
                WHERE estado IN ('PENDIENTE', 'ACEPTADO', 'EN_PROCESO', 'ESPERANDO_CONFIRMACION_FINAL')
                  AND (id_jugador_1 IN (%s, %s) OR id_jugador_2 IN (%s, %s))
            """, (id_j1_clean, id_j2_clean, id_j1_clean, id_j2_clean))
            if cursor.fetchone()['total_pend'] > 0:
                return False, "Uno de los operadores ya tiene una mesa de negociación activa en curso (RN012)."

            # 4. Solvencia de saldo del proponente
            if monto_j1_clean > 0:
                cursor.execute("SELECT saldo_disponible FROM cuentas WHERE id_jugador = %s ORDER BY (tipo_cuenta = 'PERSONAL') DESC, id_cuenta ASC LIMIT 1", (id_j1_clean,))
                res_saldo = cursor.fetchone()
                saldo_actual = float(res_saldo['saldo_disponible']) if res_saldo else 0.0
                if saldo_actual < monto_j1_clean:
                    return False, f"Saldo insuficiente. Dispones de ${saldo_actual:,.2f} y ofertaste ${monto_j1_clean:,.2f}."

            # 5. Posesión y Deuda de los ítems ofrecidos (RN002, RN004)
            if items_j1_list:
                format_strings = ','.join(['%s'] * len(items_j1_list))
                cursor.execute(f"SELECT id_item, nombre, id_jugador, tiene_deuda, estado_custodia FROM items WHERE id_item IN ({format_strings})", tuple(items_j1_list))
                items_db = cursor.fetchall()
                if len(items_db) != len(items_j1_list):
                    return False, "Uno o más bienes seleccionados no existen en el registro central."
                
                for itm in items_db:
                    if itm['id_jugador'] != id_j1_clean:
                        return False, f"No eres el propietario legítimo del bien '{itm['nombre']}' (RN002)."
                    if itm['tiene_deuda']:
                        return False, f"El bien '{itm['nombre']}' posee gravamen o deuda pendiente (RN004)."
                    if itm.get('estado_custodia') == 'EMBARGADO':
                        return False, f"El bien '{itm['nombre']}' se encuentra embargado por el servidor."

            # 6. Límite máximo de bienes del receptor (RN007)
            cursor.execute("""
                SELECT s.limite_bienes_por_jugador 
                FROM jugadores j JOIN servidores s ON j.id_servidor = s.id_servidor 
                WHERE j.id_jugador = %s
            """, (id_j2_clean,))
            servidor_cfg = cursor.fetchone()
            limite_bienes = servidor_cfg['limite_bienes_por_jugador'] if servidor_cfg else 100

            cursor.execute("SELECT COUNT(*) AS total_items FROM items WHERE id_jugador = %s", (id_j2_clean,))
            items_actuales_j2 = cursor.fetchone()['total_items']
            if items_actuales_j2 + len(items_j1_list) > limite_bienes:
                return False, f"El receptor superaría el límite máximo de {limite_bienes} bienes permitido por el servidor (RN007)."

            # 7. Registrar e iniciar la negociación
            cursor.execute("""
                INSERT INTO negociaciones_tradeos
                (id_jugador_1, id_jugador_2, id_item_j1, id_item_j2, items_j1_ids, items_j2_ids, monto_j1, monto_j2, fecha_expiracion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, DATE_ADD(NOW(), INTERVAL %s MINUTE))
            """, (id_j1_clean, id_j2_clean, primary_item_j1, primary_item_j2, items_j1_str, items_j2_str, monto_j1_clean, monto_j2_clean, exp_clean))
            
            return True, "Propuesta de intercambio enviada y registrada exitosamente."
    except Error as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def consultar_ofertas_pendientes(id_jugador):
    """Retorna las invitaciones de comercio pendientes con temporizador de expiración en tiempo real."""
    id_clean = ensure_scalar(id_jugador)
    if not id_clean:
        return None, "ID de jugador inválido"

    try:
        with get_db_cursor(dictionary=True, commit=True) as (cursor, _):
            cursor.execute("""
                UPDATE negociaciones_tradeos 
                SET estado = 'EXPIRADO' 
                WHERE estado IN ('PENDIENTE', 'ACEPTADO', 'EN_PROCESO', 'ESPERANDO_CONFIRMACION_FINAL') 
                  AND fecha_expiracion < NOW()
            """)

            cursor.execute("""
                SELECT 
                    n.id_negociacion, n.id_jugador_1, n.id_jugador_2, n.estado,
                    n.monto_j1, n.monto_j2, n.id_item_j1, n.id_item_j2,
                    n.items_j1_ids, n.items_j2_ids,
                    n.fecha_creacion, n.fecha_expiracion,
                    TIMESTAMPDIFF(SECOND, NOW(), n.fecha_expiracion) AS segundos_restantes,
                    j1.nombre_usuario AS usuario_j1,
                    i1.nombre AS nombre_item_j1, i1.precio AS precio_item_j1
                FROM negociaciones_tradeos n
                JOIN jugadores j1 ON n.id_jugador_1 = j1.id_jugador
                LEFT JOIN items i1 ON n.id_item_j1 = i1.id_item
                WHERE n.id_jugador_2 = %s AND n.estado = 'PENDIENTE'
                ORDER BY n.fecha_creacion DESC
            """, (id_clean,))
            ofertas = cursor.fetchall()
            
            for of in ofertas:
                raw_ids = of.get('items_j1_ids') or of.get('id_item_j1')
                of['items_j1_details'] = _get_items_details(raw_ids)

            return ofertas, "Ofertas pendientes obtenidas"
    except Exception as e:
        return None, str(e)

def aceptar_invitacion_trade(id_trade, id_jugador):
    """El receptor acepta la invitación y la mesa pasa al estado EN_PROCESO para intercambio en vivo."""
    id_trade_clean = ensure_scalar(id_trade)
    id_jugador_clean = ensure_scalar(id_jugador)
    if not id_trade_clean or not id_jugador_clean:
        return False, "Parámetros inválidos"

    try:
        with get_db_cursor(commit=True, dictionary=True) as (cursor, _):
            cursor.execute("""
                UPDATE negociaciones_tradeos
                SET estado = 'EN_PROCESO'
                WHERE id_negociacion = %s AND id_jugador_2 = %s AND estado = 'PENDIENTE'
            """, (id_trade_clean, id_jugador_clean))
            if cursor.rowcount > 0:
                return True, "Negociación aceptada. Ingresando a la mesa de intercambio."
            return False, "La oferta ya no está disponible o ha expirado."
    except Exception as e:
        return False, str(e)

def consultar_mesa_activa(id_jugador):
    """Obtiene la sesión de negociación activa para renderizar la interfaz P2P reactiva."""
    id_clean = ensure_scalar(id_jugador)
    if not id_clean:
        return None, "ID de jugador inválido"

    try:
        with get_db_cursor(dictionary=True) as (cursor, _):
            cursor.execute("""
                SELECT 
                    n.*,
                    j1.nombre_usuario AS usuario_j1,
                    j2.nombre_usuario AS usuario_j2,
                    TIMESTAMPDIFF(SECOND, NOW(), n.fecha_expiracion) AS segundos_restantes
                FROM negociaciones_tradeos n
                JOIN jugadores j1 ON n.id_jugador_1 = j1.id_jugador
                JOIN jugadores j2 ON n.id_jugador_2 = j2.id_jugador
                WHERE (n.id_jugador_1 = %s OR n.id_jugador_2 = %s)
                  AND n.estado IN ('PENDIENTE', 'ACEPTADO', 'EN_PROCESO', 'ESPERANDO_CONFIRMACION_FINAL')
                LIMIT 1
            """, (id_clean, id_clean))
            trade = cursor.fetchone()
            if not trade:
                return None, "No hay mesa de negociación activa"

            ids_j1 = trade.get('items_j1_ids') or trade.get('id_item_j1')
            ids_j2 = trade.get('items_j2_ids') or trade.get('id_item_j2')
            details_j1 = _get_items_details(ids_j1)
            details_j2 = _get_items_details(ids_j2)
            trade['items_j1_details'] = details_j1
            trade['items_j2_details'] = details_j2
            trade['items_j1_list'] = details_j1
            trade['items_j2_list'] = details_j2

            if trade['id_jugador_1'] == id_clean:
                trade['es_j1'] = True
                trade['mi_confirmacion'] = bool(trade['confirmacion_j1'])
                trade['otro_confirmacion'] = bool(trade['confirmacion_j2'])
            else:
                trade['es_j1'] = False
                trade['mi_confirmacion'] = bool(trade['confirmacion_j2'])
                trade['otro_confirmacion'] = bool(trade['confirmacion_j1'])

            return trade, "Mesa activa encontrada"
    except Exception as e:
        return None, str(e)

def obtener_detalle_trade(id_trade):
    """Consulta los datos enriquecidos de una negociación específica por su ID."""
    id_clean = ensure_scalar(id_trade)
    if not id_clean:
        return None, "ID inválido"

    try:
        with get_db_cursor(dictionary=True) as (cursor, _):
            cursor.execute("""
                SELECT 
                    n.*,
                    j1.nombre_usuario AS usuario_j1,
                    j2.nombre_usuario AS usuario_j2,
                    i1.nombre AS nombre_item_j1,
                    i2.nombre AS nombre_item_j2,
                    TIMESTAMPDIFF(SECOND, NOW(), n.fecha_expiracion) AS segundos_restantes
                FROM negociaciones_tradeos n
                JOIN jugadores j1 ON n.id_jugador_1 = j1.id_jugador
                JOIN jugadores j2 ON n.id_jugador_2 = j2.id_jugador
                LEFT JOIN items i1 ON n.id_item_j1 = i1.id_item
                LEFT JOIN items i2 ON n.id_item_j2 = i2.id_item
                WHERE n.id_negociacion = %s
            """, (id_clean,))
            trade = cursor.fetchone()
            if not trade:
                return None, "Negociación no encontrada"

            ids_j1 = trade.get('items_j1_ids') or trade.get('id_item_j1')
            ids_j2 = trade.get('items_j2_ids') or trade.get('id_item_j2')
            details_j1 = _get_items_details(ids_j1)
            details_j2 = _get_items_details(ids_j2)
            trade['items_j1_details'] = details_j1
            trade['items_j2_details'] = details_j2
            trade['items_j1_list'] = details_j1
            trade['items_j2_list'] = details_j2

            return trade, "Detalle obtenido"
    except Exception as e:
        return None, str(e)

def cancelar_tradeo(id_trade, id_jugador):
    """Cancela voluntariamente la sesión de tradeo."""
    id_trade_clean = ensure_scalar(id_trade)
    id_jugador_clean = ensure_scalar(id_jugador)
    if not id_trade_clean or not id_jugador_clean:
        return False, "Parámetros inválidos"

    try:
        with get_db_cursor(commit=True, dictionary=True) as (cursor, _):
            cursor.execute("""
                UPDATE negociaciones_tradeos
                SET estado = 'CANCELADO'
                WHERE id_negociacion = %s 
                  AND (id_jugador_1 = %s OR id_jugador_2 = %s)
                  AND estado IN ('PENDIENTE', 'ACEPTADO', 'EN_PROCESO', 'ESPERANDO_CONFIRMACION_FINAL')
            """, (id_trade_clean, id_jugador_clean, id_jugador_clean))
            
            if cursor.rowcount > 0:
                return True, "Negociación cancelada exitosamente."
            return False, "No se pudo cancelar: la negociación ya no está activa."
    except Exception as e:
        return False, str(e)

def actualizar_oferta_jugador(id_trade, id_jugador, monto=0.0, item_ids=None):
    """
    Actualiza la oferta de un operador y resetea las confirmaciones mutuas (RN010).
    """
    id_trade_clean = ensure_scalar(id_trade)
    id_jugador_clean = ensure_scalar(id_jugador)
    if not id_trade_clean or not id_jugador_clean:
        return False, "Parámetros inválidos"

    item_ids_list = _parse_id_list(item_ids)
    primary_item = item_ids_list[0] if item_ids_list else None
    items_str = ','.join(map(str, item_ids_list)) if item_ids_list else None

    try:
        monto_float = max(0.0, float(monto or 0.0))
    except (ValueError, TypeError):
        monto_float = 0.0

    try:
        with get_db_cursor(commit=True, dictionary=True) as (cursor, _):
            cursor.execute("SELECT id_jugador_1, id_jugador_2, estado FROM negociaciones_tradeos WHERE id_negociacion = %s", (id_trade_clean,))
            trade = cursor.fetchone()
            if not trade or trade['estado'] not in ('PENDIENTE', 'ACEPTADO', 'EN_PROCESO', 'ESPERANDO_CONFIRMACION_FINAL'):
                return False, "La mesa de negociación ya no está abierta a modificaciones."

            if id_jugador_clean not in (trade['id_jugador_1'], trade['id_jugador_2']):
                return False, "No tienes autorización sobre esta mesa."

            if monto_float > 0:
                cursor.execute("SELECT saldo_disponible FROM cuentas WHERE id_jugador = %s ORDER BY (tipo_cuenta = 'PERSONAL') DESC, id_cuenta ASC LIMIT 1", (id_jugador_clean,))
                res_saldo = cursor.fetchone()
                saldo_actual = float(res_saldo['saldo_disponible']) if res_saldo else 0.0
                if saldo_actual < monto_float:
                    return False, f"Saldo insuficiente. Dispones de ${saldo_actual:,.2f}."

            if item_ids_list:
                format_strings = ','.join(['%s'] * len(item_ids_list))
                cursor.execute(f"SELECT id_item, nombre, id_jugador, tiene_deuda FROM items WHERE id_item IN ({format_strings})", tuple(item_ids_list))
                items_db = cursor.fetchall()
                for itm in items_db:
                    if itm['id_jugador'] != id_jugador_clean:
                        return False, f"El bien '{itm['nombre']}' no te pertenece (RN002)."
                    if itm['tiene_deuda']:
                        return False, f"El bien '{itm['nombre']}' tiene deuda pendiente (RN004)."

            if trade['id_jugador_1'] == id_jugador_clean:
                cursor.execute("""
                    UPDATE negociaciones_tradeos
                    SET monto_j1 = %s, id_item_j1 = %s, items_j1_ids = %s, confirmacion_j1 = 0, confirmacion_j2 = 0, estado = 'EN_PROCESO'
                    WHERE id_negociacion = %s
                """, (monto_float, primary_item, items_str, id_trade_clean))
            else:
                cursor.execute("""
                    UPDATE negociaciones_tradeos
                    SET monto_j2 = %s, id_item_j2 = %s, items_j2_ids = %s, confirmacion_j1 = 0, confirmacion_j2 = 0, estado = 'EN_PROCESO'
                    WHERE id_negociacion = %s
                """, (monto_float, primary_item, items_str, id_trade_clean))

            return True, "Oferta actualizada. Las confirmaciones se han reiniciado (RN010)."
    except Exception as e:
        return False, str(e)

def lock_trade_player(id_trade, id_jugador):
    """Registra el bloqueo/confirmación individual de un operador en la mesa."""
    id_trade_clean = ensure_scalar(id_trade)
    id_jugador_clean = ensure_scalar(id_jugador)
    if not id_trade_clean or not id_jugador_clean:
        return False, "Parámetros inválidos"

    try:
        with get_db_cursor(commit=True, dictionary=True) as (cursor, _):
            cursor.execute("SELECT id_jugador_1, id_jugador_2, estado FROM negociaciones_tradeos WHERE id_negociacion = %s", (id_trade_clean,))
            trade = cursor.fetchone()
            if not trade or trade['estado'] not in ('PENDIENTE', 'ACEPTADO', 'EN_PROCESO', 'ESPERANDO_CONFIRMACION_FINAL'):
                return False, "Negociación no disponible."

            if trade['id_jugador_1'] == id_jugador_clean:
                cursor.execute("UPDATE negociaciones_tradeos SET confirmacion_j1 = TRUE WHERE id_negociacion = %s", (id_trade_clean,))
            elif trade['id_jugador_2'] == id_jugador_clean:
                cursor.execute("UPDATE negociaciones_tradeos SET confirmacion_j2 = TRUE WHERE id_negociacion = %s", (id_trade_clean,))
            else:
                return False, "Operador no participante."

            cursor.execute("SELECT confirmacion_j1, confirmacion_j2 FROM negociaciones_tradeos WHERE id_negociacion = %s", (id_trade_clean,))
            check = cursor.fetchone()
            
            if check and check['confirmacion_j1'] and check['confirmacion_j2']:
                cursor.execute("UPDATE negociaciones_tradeos SET estado = 'ESPERANDO_CONFIRMACION_FINAL' WHERE id_negociacion = %s", (id_trade_clean,))
                return True, "Ambos operadores han confirmado los términos (RN010). Listos para liquidar."

            return True, "Oferta confirmada. Esperando al otro operador."
    except Exception as e:
        return False, str(e)

def finalizar_tradeo(id_trade):
    """
    Ejecuta atómicamente la liquidación final del tradeo:
    1. Transferencia simétrica de bienes (RN002).
    2. Drenaje de comisión del sistema (RN006).
    3. Validación de solvencia (RN009).
    4. Registro inmutable en transacciones y partida doble en detalles_transacciones (RN003).
    """
    id_clean = ensure_scalar(id_trade)
    if not id_clean:
        return False, "ID inválido"

    try:
        with get_db_cursor(commit=True, dictionary=True) as (cursor, _):
            cursor.execute("SELECT * FROM negociaciones_tradeos WHERE id_negociacion = %s FOR UPDATE", (id_clean,))
            n = cursor.fetchone()
            if not n or n['estado'] not in ('EN_PROCESO', 'ESPERANDO_CONFIRMACION_FINAL', 'PENDIENTE', 'ACEPTADO'):
                return False, "La negociación ya fue procesada o cancelada."

            id_j1 = n['id_jugador_1']
            id_j2 = n['id_jugador_2']
            monto_j1 = float(n['monto_j1'] or 0.0)
            monto_j2 = float(n['monto_j2'] or 0.0)

            cursor.execute("SELECT id_cuenta, saldo_disponible FROM cuentas WHERE id_jugador = %s ORDER BY (tipo_cuenta = 'PERSONAL') DESC, id_cuenta ASC LIMIT 1 FOR UPDATE", (id_j1,))
            c_j1 = cursor.fetchone()
            cursor.execute("SELECT id_cuenta, saldo_disponible FROM cuentas WHERE id_jugador = %s ORDER BY (tipo_cuenta = 'PERSONAL') DESC, id_cuenta ASC LIMIT 1 FOR UPDATE", (id_j2,))
            c_j2 = cursor.fetchone()
            cursor.execute("SELECT id_cuenta FROM cuentas WHERE tipo_cuenta = 'SISTEMA' LIMIT 1 FOR UPDATE")
            c_sis = cursor.fetchone()

            if not c_j1 or not c_j2 or not c_sis:
                return False, "Error al acceder a las cuentas bancarias de los operadores o del sistema."

            id_cuenta_j1, saldo_j1 = c_j1['id_cuenta'], float(c_j1['saldo_disponible'])
            id_cuenta_j2, saldo_j2 = c_j2['id_cuenta'], float(c_j2['saldo_disponible'])
            id_cuenta_sis = c_sis['id_cuenta']

            if monto_j1 > 0 and saldo_j1 < monto_j1:
                cursor.execute("UPDATE negociaciones_tradeos SET estado = 'CANCELADO' WHERE id_negociacion = %s", (id_clean,))
                return False, "Fondos insuficientes en el Operador 1. Negociación cancelada."

            if monto_j2 > 0 and saldo_j2 < monto_j2:
                cursor.execute("UPDATE negociaciones_tradeos SET estado = 'CANCELADO' WHERE id_negociacion = %s", (id_clean,))
                return False, "Fondos insuficientes en el Operador 2. Negociación cancelada."

            cursor.execute("SELECT s.porcentaje_comision FROM jugadores j JOIN servidores s ON j.id_servidor = s.id_servidor WHERE j.id_jugador = %s", (id_j1,))
            row_srv = cursor.fetchone()
            porcentaje = float(row_srv['porcentaje_comision']) if row_srv else 5.0

            comision_j1 = round(monto_j1 * (porcentaje / 100.0), 2)
            neto_j1 = monto_j1 - comision_j1
            comision_j2 = round(monto_j2 * (porcentaje / 100.0), 2)
            neto_j2 = monto_j2 - comision_j2

            items_j1_all = _parse_id_list(n.get('items_j1_ids') or n.get('id_item_j1'))
            for item_id in items_j1_all:
                cursor.execute("UPDATE items SET id_jugador = %s, estado_custodia = 'PERSONAL' WHERE id_item = %s", (id_j2, item_id))

            items_j2_all = _parse_id_list(n.get('items_j2_ids') or n.get('id_item_j2'))
            for item_id in items_j2_all:
                cursor.execute("UPDATE items SET id_jugador = %s, estado_custodia = 'PERSONAL' WHERE id_item = %s", (id_j1, item_id))

            item_afectado_principal = items_j1_all[0] if items_j1_all else (items_j2_all[0] if items_j2_all else None)
            total_monto_trx = monto_j1 + monto_j2

            cursor.execute("""
                INSERT INTO transacciones (id_item_afectado, id_negociacion, tipo_transaccion, estado_transaccion, monto)
                VALUES (%s, %s, 'TRADEO_P2P', 'COMPLETADA', %s)
            """, (item_afectado_principal, id_clean, total_monto_trx))
            id_transaccion = cursor.lastrowid

            if monto_j1 > 0:
                cursor.execute("UPDATE cuentas SET saldo_disponible = saldo_disponible - %s WHERE id_cuenta = %s", (monto_j1, id_cuenta_j1))
                cursor.execute("UPDATE cuentas SET saldo_disponible = saldo_disponible + %s WHERE id_cuenta = %s", (neto_j1, id_cuenta_j2))
                if comision_j1 > 0:
                    cursor.execute("UPDATE cuentas SET saldo_disponible = saldo_disponible + %s WHERE id_cuenta = %s", (comision_j1, id_cuenta_sis))

                cursor.execute("""
                    INSERT INTO detalles_transacciones (id_transaccion, cuenta_origen, cuenta_destino, tipo_movimiento, monto_detalle, concepto)
                    VALUES 
                    (%s, %s, %s, 'DEBITO', %s, 'PAGO_TRADEO_J1'),
                    (%s, %s, %s, 'CREDITO', %s, 'COBRO_TRADEO_J1')
                """, (id_transaccion, id_cuenta_j1, id_cuenta_j2, neto_j1,
                      id_transaccion, id_cuenta_j1, id_cuenta_j2, neto_j1))

                if comision_j1 > 0:
                    cursor.execute("""
                        INSERT INTO detalles_transacciones (id_transaccion, cuenta_origen, cuenta_destino, tipo_movimiento, monto_detalle, concepto)
                        VALUES 
                        (%s, %s, %s, 'DEBITO', %s, 'COMISION_DRENAJE_SISTEMA'),
                        (%s, %s, %s, 'CREDITO', %s, 'COMISION_DRENAJE_SISTEMA')
                    """, (id_transaccion, id_cuenta_j1, id_cuenta_sis, comision_j1,
                          id_transaccion, id_cuenta_j1, id_cuenta_sis, comision_j1))

            if monto_j2 > 0:
                cursor.execute("UPDATE cuentas SET saldo_disponible = saldo_disponible - %s WHERE id_cuenta = %s", (monto_j2, id_cuenta_j2))
                cursor.execute("UPDATE cuentas SET saldo_disponible = saldo_disponible + %s WHERE id_cuenta = %s", (neto_j2, id_cuenta_j1))
                if comision_j2 > 0:
                    cursor.execute("UPDATE cuentas SET saldo_disponible = saldo_disponible + %s WHERE id_cuenta = %s", (comision_j2, id_cuenta_sis))

                cursor.execute("""
                    INSERT INTO detalles_transacciones (id_transaccion, cuenta_origen, cuenta_destino, tipo_movimiento, monto_detalle, concepto)
                    VALUES 
                    (%s, %s, %s, 'DEBITO', %s, 'PAGO_TRADEO_J2'),
                    (%s, %s, %s, 'CREDITO', %s, 'COBRO_TRADEO_J2')
                """, (id_transaccion, id_cuenta_j2, id_cuenta_j1, neto_j2,
                      id_transaccion, id_cuenta_j2, id_cuenta_j1, neto_j2))

                if comision_j2 > 0:
                    cursor.execute("""
                        INSERT INTO detalles_transacciones (id_transaccion, cuenta_origen, cuenta_destino, tipo_movimiento, monto_detalle, concepto)
                        VALUES 
                        (%s, %s, %s, 'DEBITO', %s, 'COMISION_DRENAJE_SISTEMA'),
                        (%s, %s, %s, 'CREDITO', %s, 'COMISION_DRENAJE_SISTEMA')
                    """, (id_transaccion, id_cuenta_j2, id_cuenta_sis, comision_j2,
                          id_transaccion, id_cuenta_j2, id_cuenta_sis, comision_j2))

            cursor.execute("UPDATE negociaciones_tradeos SET estado = 'COMPLETADO' WHERE id_negociacion = %s", (id_clean,))
            return True, "Intercambio completado y liquidado con éxito contable inmutable."
    except Exception as e:
        return False, str(e)

def limpieza_forzada_trades():
    """Cancela o purga todas las negociaciones activas en caso de reinicio o mantenimiento."""
    try:
        with get_db_cursor(commit=True) as (cursor, _):
            cursor.execute("DELETE FROM negociaciones_tradeos WHERE estado IN ('PENDIENTE', 'EN_PROCESO', 'ACEPTADO', 'ABIERTO', 'ESPERANDO_CONFIRMACION_FINAL')")
            return True, "Mesa de negociaciones reseteada."
    except Exception as e:
        return False, str(e)
