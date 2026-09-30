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
            SELECT id_item, id_jugador, nombre, precio, fecha, tiene_deuda, antiguedad_dias
            FROM T_Item
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

    try:
        monto_j1_clean = float(monto_j1) if monto_j1 not in (None, '') else 0.0
        monto_j2_clean = float(monto_j2) if monto_j2 not in (None, '') else 0.0
    except (TypeError, ValueError):
        monto_j1_clean, monto_j2_clean = 0.0, 0.0

    items_j1_list = _parse_id_list(item_j1)
    items_j2_list = _parse_id_list(item_j2)

    primary_item_j1 = items_j1_list[0] if items_j1_list else None
    primary_item_j2 = items_j2_list[0] if items_j2_list else None

    items_j1_str = ','.join(map(str, items_j1_list)) if items_j1_list else None
    items_j2_str = ','.join(map(str, items_j2_list)) if items_j2_list else None
    exp_clean = ensure_scalar(exp) or 10

    try:
        with get_db_cursor(commit=True, dictionary=True) as (cursor, _):
            # 1. Validar estado de los jugadores (RN009: No Bancarrota / Suspendido)
            cursor.execute("SELECT id_jugador, nombre_usuario, estado FROM T_Jugador WHERE id_jugador IN (%s, %s)", (id_j1_clean, id_j2_clean))
            jugadores_db = {row['id_jugador']: row for row in cursor.fetchall()}
            
            j1_data = jugadores_db.get(id_j1_clean)
            j2_data = jugadores_db.get(id_j2_clean)
            if not j1_data or not j2_data:
                return False, "Uno de los operadores no existe en el sistema."
            if j1_data['estado'] in ('BANCARROTA', 'SUSPENDIDO'):
                return False, f"El operador {j1_data['nombre_usuario']} está en estado {j1_data['estado']} y tiene las operaciones bloqueadas (RN009)."
            if j2_data['estado'] in ('BANCARROTA', 'SUSPENDIDO'):
                return False, f"El operador receptor {j2_data['nombre_usuario']} está en estado {j2_data['estado']} (RN009)."

            # 2. Validar límite diario de tradeos (RN011: Máx 5 tradeos por día calendario)
            cursor.execute("""
                SELECT COUNT(*) AS total_hoy FROM T_Transaccion t
                JOIN T_Negociacion_Tradeo n ON t.id_negociacion = n.id_negociacion
                WHERE t.tipo_transaccion = 'TRADEO_P2P' AND t.estado_transaccion = 'COMPLETADA'
                  AND DATE(t.fecha_hora) = CURDATE()
                  AND (n.id_jugador_1 = %s OR n.id_jugador_2 = %s)
            """, (id_j1_clean, id_j1_clean))
            row_trades_j1 = cursor.fetchone()
            if row_trades_j1 and row_trades_j1['total_hoy'] >= 5:
                return False, "Has alcanzado el límite máximo de 5 tradeos diarios permitidos (RN011)."

            # 3. Validar negociaciones abiertas simultáneas (RN012: Solo 1 trade activo a la vez)
            cursor.execute("""
                SELECT COUNT(*) AS total_pend FROM T_Negociacion_Tradeo
                WHERE estado IN ('PENDIENTE', 'EN_PROCESO', 'ACEPTADO', 'ESPERANDO_CONFIRMACION_FINAL')
                  AND (id_jugador_1 IN (%s, %s) OR id_jugador_2 IN (%s, %s))
            """, (id_j1_clean, id_j2_clean, id_j1_clean, id_j2_clean))
            row_pend = cursor.fetchone()
            if row_pend and row_pend['total_pend'] > 0:
                return False, "Uno de los operadores ya tiene una negociación activa o pendiente en curso (RN012)."

            # 4. Validar saldo suficiente para el monto ofrecido (RN009)
            if monto_j1_clean > 0:
                cursor.execute("SELECT saldo_disponible FROM T_Cuenta WHERE id_jugador = %s AND tipo_cuenta = 'PERSONAL'", (id_j1_clean,))
                cuenta_j1 = cursor.fetchone()
                if not cuenta_j1 or float(cuenta_j1['saldo_disponible']) < monto_j1_clean:
                    return False, f"Saldo insuficiente para respaldar la oferta monetaria de $ {monto_j1_clean:,.2f}."

            # 5. Validar propiedad y gravámenes de los ítems ofrecidos (RN002, RN004)
            if items_j1_list:
                format_strings = ','.join(['%s'] * len(items_j1_list))
                cursor.execute(f"SELECT id_item, nombre, id_jugador, tiene_deuda FROM T_Item WHERE id_item IN ({format_strings})", tuple(items_j1_list))
                items_db = cursor.fetchall()
                if len(items_db) != len(items_j1_list):
                    return False, "Uno o más bienes seleccionados no existen en el registro oficial."
                for item in items_db:
                    if item['id_jugador'] != id_j1_clean:
                        return False, f"El bien '{item['nombre']}' no te pertenece legítimamente (RN002)."
                    if item['tiene_deuda']:
                        return False, f"El bien '{item['nombre']}' posee deuda pendiente o gravamen y no es transferible (RN004)."

            # 6. Validar límite máximo de bienes para el receptor (RN007)
            cursor.execute("""
                SELECT s.limite_bienes_por_jugador 
                FROM T_Jugador j JOIN T_Servidor s ON j.id_servidor = s.id_servidor 
                WHERE j.id_jugador = %s
            """, (id_j2_clean,))
            servidor_cfg = cursor.fetchone()
            limite_bienes = servidor_cfg['limite_bienes_por_jugador'] if servidor_cfg else 100

            cursor.execute("SELECT COUNT(*) AS total_items FROM T_Item WHERE id_jugador = %s", (id_j2_clean,))
            items_actuales_j2 = cursor.fetchone()['total_items']
            if items_actuales_j2 + len(items_j1_list) > limite_bienes:
                return False, f"El receptor superaría el límite máximo de {limite_bienes} bienes permitido por el servidor (RN007)."

            # 7. Registrar e iniciar la negociación
            cursor.execute("""
                INSERT INTO T_Negociacion_Tradeo
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
        with get_db_cursor(commit=True, dictionary=True) as (cursor, _):
            cursor.execute("""
                UPDATE T_Negociacion_Tradeo 
                SET estado = 'EXPIRADO' 
                WHERE estado = 'PENDIENTE' AND fecha_expiracion < NOW()
            """)

            query = """
            SELECT n.*, 
                   j1.nombre_usuario AS emisor, 
                   i1.nombre AS item_ofrecido,
                   TIMESTAMPDIFF(SECOND, NOW(), n.fecha_expiracion) AS segundos_restantes
            FROM T_Negociacion_Tradeo n
            JOIN T_Jugador j1 ON n.id_jugador_1 = j1.id_jugador
            LEFT JOIN T_Item i1 ON n.id_item_j1 = i1.id_item
            WHERE n.id_jugador_2 = %s AND n.estado = 'PENDIENTE'
            ORDER BY n.fecha_creacion DESC
            """
            cursor.execute(query, (id_clean,))
            ofertas = cursor.fetchall() or []

            for of in ofertas:
                raw_ids = of.get('items_j1_ids') or of.get('id_item_j1')
                of['items_list'] = _get_items_details(raw_ids)
                if of['items_list']:
                    of['item_ofrecido'] = ', '.join([item['nombre'] for item in of['items_list']])

            return ofertas, "Ofertas recuperadas"
    except Error as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)

def consultar_mesa_activa(id_jugador):
    """Retorna la negociación activa en curso del jugador con temporizador de sala en vivo."""
    id_clean = ensure_scalar(id_jugador)
    if not id_clean:
        return None, "ID de jugador inválido"

    try:
        with get_db_cursor(commit=True, dictionary=True) as (cursor, _):
            cursor.execute("""
                UPDATE T_Negociacion_Tradeo 
                SET estado = 'EXPIRADO' 
                WHERE estado IN ('ACEPTADO', 'EN_PROCESO', 'ESPERANDO_CONFIRMACION_FINAL') 
                  AND fecha_expiracion < NOW()
            """)

            query = """
            SELECT n.*,
                   i1.nombre AS nombre_item_j1,
                   i2.nombre AS nombre_item_j2,
                   j1.nombre_usuario AS username_j1,
                   j2.nombre_usuario AS username_j2,
                   (n.id_jugador_1 = %s) AS es_jugador_1,
                   TIMESTAMPDIFF(SECOND, NOW(), n.fecha_expiracion) AS segundos_restantes
            FROM T_Negociacion_Tradeo n
            JOIN T_Jugador j1 ON n.id_jugador_1 = j1.id_jugador
            JOIN T_Jugador j2 ON n.id_jugador_2 = j2.id_jugador
            LEFT JOIN T_Item i1 ON n.id_item_j1 = i1.id_item
            LEFT JOIN T_Item i2 ON n.id_item_j2 = i2.id_item
            WHERE (n.id_jugador_1 = %s OR n.id_jugador_2 = %s)
              AND n.estado IN ('ACEPTADO', 'EN_PROCESO', 'ESPERANDO_CONFIRMACION_FINAL')
            LIMIT 1
            """
            cursor.execute(query, (id_clean, id_clean, id_clean))
            trade = cursor.fetchone()
            if not trade:
                return None, "No hay mesa activa"

            ids_j1 = trade.get('items_j1_ids') or trade.get('id_item_j1')
            ids_j2 = trade.get('items_j2_ids') or trade.get('id_item_j2')
            trade['items_j1_list'] = _get_items_details(ids_j1)
            trade['items_j2_list'] = _get_items_details(ids_j2)

            return trade, "Mesa recuperada"
    except Error as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)

def obtener_detalle_trade(id_trade):
    """Obtiene los detalles completos de un comercio por su ID con temporizador."""
    id_clean = ensure_scalar(id_trade)
    if not id_clean:
        return None, "ID de trade inválido"

    try:
        with get_db_cursor(dictionary=True) as (cursor, _):
            query = """
            SELECT n.*,
                   i1.nombre AS nombre_item_j1,
                   i2.nombre AS nombre_item_j2,
                   j1.nombre_usuario AS username_j1,
                   j2.nombre_usuario AS username_j2,
                   TIMESTAMPDIFF(SECOND, NOW(), n.fecha_expiracion) AS segundos_restantes
            FROM T_Negociacion_Tradeo n
            JOIN T_Jugador j1 ON n.id_jugador_1 = j1.id_jugador
            JOIN T_Jugador j2 ON n.id_jugador_2 = j2.id_jugador
            LEFT JOIN T_Item i1 ON n.id_item_j1 = i1.id_item
            LEFT JOIN T_Item i2 ON n.id_item_j2 = i2.id_item
            WHERE n.id_negociacion = %s
            """
            cursor.execute(query, (id_clean,))
            trade = cursor.fetchone()
            if trade:
                ids_j1 = trade.get('items_j1_ids') or trade.get('id_item_j1')
                ids_j2 = trade.get('items_j2_ids') or trade.get('id_item_j2')
                trade['items_j1_list'] = _get_items_details(ids_j1)
                trade['items_j2_list'] = _get_items_details(ids_j2)
                return trade, "Detalle recuperado"
            return None, "Tradeo no encontrado"
    except Error as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)

def aceptar_invitacion_trade(id_trade, id_jugador):
    """El receptor acepta la invitación y la sala pasa al estado EN_PROCESO con 3 minutos para negociar."""
    id_trade_clean = ensure_scalar(id_trade)
    id_jugador_clean = ensure_scalar(id_jugador)

    if not id_trade_clean or not id_jugador_clean:
        return False, "Parámetros inválidos"

    try:
        with get_db_cursor(commit=True, dictionary=True) as (cursor, _):
            # Validar que el receptor no esté en bancarrota
            cursor.execute("SELECT estado FROM T_Jugador WHERE id_jugador = %s", (id_jugador_clean,))
            j = cursor.fetchone()
            if j and j['estado'] in ('BANCARROTA', 'SUSPENDIDO'):
                return False, f"Tu cuenta está en estado {j['estado']}, no puedes operar (RN009)."

            query = """
            UPDATE T_Negociacion_Tradeo 
            SET estado = 'EN_PROCESO', fecha_expiracion = DATE_ADD(NOW(), INTERVAL 3 MINUTE)
            WHERE id_negociacion = %s AND id_jugador_2 = %s AND estado = 'PENDIENTE'
            """
            cursor.execute(query, (id_trade_clean, id_jugador_clean))
            if cursor.rowcount > 0:
                return True, "Invitación aceptada"
            return False, "No se encontró la invitación pendiente para aceptar."
    except Error as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def actualizar_oferta_jugador(id_trade, id_jugador, monto, id_item):
    """
    Actualiza la oferta de un participante en la mesa activa con validación de fondos y deuda.
    Resetea automáticamente la confirmación de ambos (RN010).
    """
    id_trade_clean = ensure_scalar(id_trade)
    id_jugador_clean = ensure_scalar(id_jugador)
    
    item_ids_list = _parse_id_list(id_item)
    primary_item = item_ids_list[0] if item_ids_list else None
    items_str = ','.join(map(str, item_ids_list)) if item_ids_list else None

    try:
        monto_clean = float(monto) if monto not in (None, '') else 0.0
    except (TypeError, ValueError):
        monto_clean = 0.0

    try:
        with get_db_cursor(commit=True, dictionary=True) as (cursor, _):
            cursor.execute("SELECT id_jugador_1, id_jugador_2, estado FROM T_Negociacion_Tradeo WHERE id_negociacion = %s", (id_trade_clean,))
            trade = cursor.fetchone()
            if not trade:
                return False, "Tradeo no encontrado"
            
            is_j1 = (trade['id_jugador_1'] == id_jugador_clean)
            is_j2 = (trade['id_jugador_2'] == id_jugador_clean)

            if not is_j1 and not is_j2:
                return False, "No perteneces a esta negociación"

            # Validar saldo suficiente
            if monto_clean > 0:
                cursor.execute("SELECT saldo_disponible FROM T_Cuenta WHERE id_jugador = %s AND tipo_cuenta = 'PERSONAL'", (id_jugador_clean,))
                cuenta = cursor.fetchone()
                if not cuenta or float(cuenta['saldo_disponible']) < monto_clean:
                    return False, f"Saldo insuficiente ($ {monto_clean:,.2f} requeridos)."

            # Validar propiedad y gravamen de bienes ofrecidos (RN002, RN004)
            if item_ids_list:
                format_strings = ','.join(['%s'] * len(item_ids_list))
                cursor.execute(f"SELECT id_item, nombre, id_jugador, tiene_deuda FROM T_Item WHERE id_item IN ({format_strings})", tuple(item_ids_list))
                items_db = cursor.fetchall()
                if len(items_db) != len(item_ids_list):
                    return False, "Uno o más bienes seleccionados no existen."
                for item in items_db:
                    if item['id_jugador'] != id_jugador_clean:
                        return False, f"El bien '{item['nombre']}' no te pertenece (RN002)."
                    if item['tiene_deuda']:
                        return False, f"El bien '{item['nombre']}' tiene deuda o gravamen pendiente (RN004)."

            # Actualizar oferta y resetear confirmaciones (RN010)
            if is_j1:
                sql = """
                UPDATE T_Negociacion_Tradeo 
                SET monto_j1 = %s, id_item_j1 = %s, items_j1_ids = %s, confirmacion_j1 = 0, confirmacion_j2 = 0, estado = 'EN_PROCESO' 
                WHERE id_negociacion = %s
                """
            else:
                sql = """
                UPDATE T_Negociacion_Tradeo 
                SET monto_j2 = %s, id_item_j2 = %s, items_j2_ids = %s, confirmacion_j1 = 0, confirmacion_j2 = 0, estado = 'EN_PROCESO' 
                WHERE id_negociacion = %s
                """
            cursor.execute(sql, (monto_clean, primary_item, items_str, id_trade_clean))
            return True, "Oferta actualizada y confirmaciones reiniciadas (RN010)."
    except Error as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def lock_trade_player(id_negociacion, is_player_1):
    """
    Fija la confirmación individual de un jugador en la mesa (RN010).
    Si ambos confirman, eleva el estado a ESPERANDO_CONFIRMACION_FINAL.
    """
    id_clean = ensure_scalar(id_negociacion)
    try:
        with get_db_cursor(commit=True, dictionary=True) as (cursor, _):
            if is_player_1:
                cursor.execute("UPDATE T_Negociacion_Tradeo SET confirmacion_j1 = TRUE WHERE id_negociacion = %s", (id_clean,))
            else:
                cursor.execute("UPDATE T_Negociacion_Tradeo SET confirmacion_j2 = TRUE WHERE id_negociacion = %s", (id_clean,))
            
            cursor.execute("SELECT confirmacion_j1, confirmacion_j2 FROM T_Negociacion_Tradeo WHERE id_negociacion = %s", (id_clean,))
            res = cursor.fetchone()
            
            both_confirmed = False
            if res and res['confirmacion_j1'] and res['confirmacion_j2']:
                cursor.execute("UPDATE T_Negociacion_Tradeo SET estado = 'ESPERANDO_CONFIRMACION_FINAL' WHERE id_negociacion = %s", (id_clean,))
                both_confirmed = True
                
            return True, "Oferta bloqueada y confirmada", both_confirmed
    except Error as e:
        return False, str(e), False
    except Exception as e:
        return False, str(e), False

def finalizar_tradeo(id_negociacion):
    """
    Ejecuta el intercambio atómico de bienes y dinero bajo una transacción ACID completa:
    1. Traspaso de propiedad exclusiva de bienes (RN002).
    2. Retención y acreditación de comisión de drenaje al Sistema (RN006).
    3. Liquidación neta monetaria en cuentas de operadores (RN005).
    4. Registro inmutable en T_Transaccion y partida doble en T_Detalle_Transaccion (RN003).
    """
    id_clean = ensure_scalar(id_negociacion)
    try:
        with get_db_cursor(commit=True, dictionary=True) as (cursor, _):
            cursor.execute("SELECT * FROM T_Negociacion_Tradeo WHERE id_negociacion = %s", (id_clean,))
            n = cursor.fetchone()
            if not n:
                return False, "Negociación no encontrada"
            
            id_j1 = n['id_jugador_1']
            id_j2 = n['id_jugador_2']

            # 1. Recuperar cuentas bancarias
            cursor.execute("SELECT id_cuenta, saldo_disponible FROM T_Cuenta WHERE id_jugador = %s AND tipo_cuenta = 'PERSONAL'", (id_j1,))
            c_j1 = cursor.fetchone()
            cursor.execute("SELECT id_cuenta, saldo_disponible FROM T_Cuenta WHERE id_jugador = %s AND tipo_cuenta = 'PERSONAL'", (id_j2,))
            c_j2 = cursor.fetchone()
            cursor.execute("SELECT id_cuenta FROM T_Cuenta WHERE tipo_cuenta = 'SISTEMA' LIMIT 1")
            c_sistema = cursor.fetchone()

            if not c_j1 or not c_j2:
                return False, "No se encontraron las cuentas bancarias de los operadores."
            id_cuenta_j1 = c_j1['id_cuenta']
            id_cuenta_j2 = c_j2['id_cuenta']
            id_cuenta_sis = c_sistema['id_cuenta'] if c_sistema else None

            # 2. Obtener porcentaje de comisión configurado en el Servidor (RN006)
            cursor.execute("""
                SELECT s.porcentaje_comision 
                FROM T_Jugador j JOIN T_Servidor s ON j.id_servidor = s.id_servidor 
                WHERE j.id_jugador = %s
            """, (id_j1,))
            srv = cursor.fetchone()
            pct_comision = float(srv['porcentaje_comision']) if srv else 5.0

            monto_j1 = float(n.get('monto_j1') or 0)
            monto_j2 = float(n.get('monto_j2') or 0)

            # Validar fondos
            if monto_j1 > 0 and float(c_j1['saldo_disponible']) < monto_j1:
                return False, "El operador 1 no posee fondos suficientes para liquidar la operación."
            if monto_j2 > 0 and float(c_j2['saldo_disponible']) < monto_j2:
                return False, "El operador 2 no posee fondos suficientes para liquidar la operación."

            # 3. Traspaso atómico de ítems
            items_j1_all = _parse_id_list(n.get('items_j1_ids') or n.get('id_item_j1'))
            for item_id in items_j1_all:
                cursor.execute("UPDATE T_Item SET id_jugador = %s WHERE id_item = %s", (id_j2, item_id))

            items_j2_all = _parse_id_list(n.get('items_j2_ids') or n.get('id_item_j2'))
            for item_id in items_j2_all:
                cursor.execute("UPDATE T_Item SET id_jugador = %s WHERE id_item = %s", (id_j1, item_id))

            # 4. Insertar Transacción Principal
            monto_total = monto_j1 + monto_j2
            primary_item = items_j1_all[0] if items_j1_all else (items_j2_all[0] if items_j2_all else None)
            cursor.execute("""
                INSERT INTO T_Transaccion (id_item_afectado, id_negociacion, tipo_transaccion, estado_transaccion, monto) 
                VALUES (%s, %s, 'TRADEO_P2P', 'COMPLETADA', %s)
            """, (primary_item, id_clean, monto_total))
            id_transaccion = cursor.lastrowid

            # 5. Liquidación Monetaria y Doble Partida con Comisión (RN006)
            # Liquidación Jugador 1 -> Jugador 2
            if monto_j1 > 0:
                comision_j1 = round(monto_j1 * (pct_comision / 100.0), 2)
                neto_j1 = round(monto_j1 - comision_j1, 2)

                cursor.execute("UPDATE T_Cuenta SET saldo_disponible = saldo_disponible - %s WHERE id_cuenta = %s", (monto_j1, id_cuenta_j1))
                cursor.execute("UPDATE T_Cuenta SET saldo_disponible = saldo_disponible + %s WHERE id_cuenta = %s", (neto_j1, id_cuenta_j2))
                if id_cuenta_sis and comision_j1 > 0:
                    cursor.execute("UPDATE T_Cuenta SET saldo_disponible = saldo_disponible + %s WHERE id_cuenta = %s", (comision_j1, id_cuenta_sis))

                # Asientos contables inmutables (T_Detalle_Transaccion)
                cursor.execute("""
                    INSERT INTO T_Detalle_Transaccion (id_transaccion, cuenta_origen, cuenta_destino, tipo_movimiento, monto_detalle, concepto)
                    VALUES (%s, %s, %s, 'DEBITO', %s, 'PAGO_TRADEO_J1'),
                           (%s, %s, %s, 'CREDITO', %s, 'COBRO_TRADEO_J1')
                """, (id_transaccion, id_cuenta_j1, id_cuenta_j2, neto_j1,
                      id_transaccion, id_cuenta_j1, id_cuenta_j2, neto_j1))

                if id_cuenta_sis and comision_j1 > 0:
                    cursor.execute("""
                        INSERT INTO T_Detalle_Transaccion (id_transaccion, cuenta_origen, cuenta_destino, tipo_movimiento, monto_detalle, concepto)
                        VALUES (%s, %s, %s, 'DEBITO', %s, 'COMISION_DRENAJE_SISTEMA'),
                               (%s, %s, %s, 'CREDITO', %s, 'COMISION_DRENAJE_SISTEMA')
                    """, (id_transaccion, id_cuenta_j1, id_cuenta_sis, comision_j1,
                          id_transaccion, id_cuenta_j1, id_cuenta_sis, comision_j1))

            # Liquidación Jugador 2 -> Jugador 1
            if monto_j2 > 0:
                comision_j2 = round(monto_j2 * (pct_comision / 100.0), 2)
                neto_j2 = round(monto_j2 - comision_j2, 2)

                cursor.execute("UPDATE T_Cuenta SET saldo_disponible = saldo_disponible - %s WHERE id_cuenta = %s", (monto_j2, id_cuenta_j2))
                cursor.execute("UPDATE T_Cuenta SET saldo_disponible = saldo_disponible + %s WHERE id_cuenta = %s", (neto_j2, id_cuenta_j1))
                if id_cuenta_sis and comision_j2 > 0:
                    cursor.execute("UPDATE T_Cuenta SET saldo_disponible = saldo_disponible + %s WHERE id_cuenta = %s", (comision_j2, id_cuenta_sis))

                # Asientos contables inmutables (T_Detalle_Transaccion)
                cursor.execute("""
                    INSERT INTO T_Detalle_Transaccion (id_transaccion, cuenta_origen, cuenta_destino, tipo_movimiento, monto_detalle, concepto)
                    VALUES (%s, %s, %s, 'DEBITO', %s, 'PAGO_TRADEO_J2'),
                           (%s, %s, %s, 'CREDITO', %s, 'COBRO_TRADEO_J2')
                """, (id_transaccion, id_cuenta_j2, id_cuenta_j1, neto_j2,
                      id_transaccion, id_cuenta_j2, id_cuenta_j1, neto_j2))

                if id_cuenta_sis and comision_j2 > 0:
                    cursor.execute("""
                        INSERT INTO T_Detalle_Transaccion (id_transaccion, cuenta_origen, cuenta_destino, tipo_movimiento, monto_detalle, concepto)
                        VALUES (%s, %s, %s, 'DEBITO', %s, 'COMISION_DRENAJE_SISTEMA'),
                               (%s, %s, %s, 'CREDITO', %s, 'COMISION_DRENAJE_SISTEMA')
                    """, (id_transaccion, id_cuenta_j2, id_cuenta_sis, comision_j2,
                          id_transaccion, id_cuenta_j2, id_cuenta_sis, comision_j2))

            # 6. Marcar tradeo como COMPLETADO
            cursor.execute("UPDATE T_Negociacion_Tradeo SET estado = 'COMPLETADO' WHERE id_negociacion = %s", (id_clean,))
            return True, "Comercio completado con éxito"
    except Error as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def cancelar_tradeo(id_negociacion):
    """Cancela una negociación en curso y libera la sala."""
    id_clean = ensure_scalar(id_negociacion)
    try:
        with get_db_cursor(commit=True) as (cursor, _):
            cursor.execute("UPDATE T_Negociacion_Tradeo SET estado = 'CANCELADO' WHERE id_negociacion = %s", (id_clean,))
            return True, "Tradeo cancelado exitosamente"
    except Error as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def limpieza_forzada_trades():
    """Utilidad para resetear negociaciones colgadas (entorno de pruebas / admin)."""
    try:
        with get_db_cursor(commit=True) as (cursor, _):
            sql = "DELETE FROM T_Negociacion_Tradeo WHERE estado IN ('PENDIENTE', 'EN_PROCESO', 'ACEPTADO', 'ABIERTO', 'ESPERANDO_CONFIRMACION_FINAL')"
            cursor.execute(sql)
            return True, f"Se han eliminado {cursor.rowcount} registros bloqueantes."
    except Error as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)
