import bcrypt
from core.database import get_db_cursor
from services import notification_service

def obtener_telemetria_global():
    """
    Retorna métricas agregadas globales del servidor para el Command Center.
    """
    try:
        with get_db_cursor(dictionary=True, commit=False) as (cursor, _):
            # 1. Fondos Tesorería Sistema (Cuenta ID 1)
            cursor.execute("SELECT saldo_disponible FROM T_Cuenta WHERE id_cuenta = 1")
            row_sis = cursor.fetchone()
            saldo_sistema = float(row_sis['saldo_disponible']) if row_sis else 0.0

            # 2. Total dinero de jugadores
            cursor.execute("SELECT COALESCE(SUM(saldo_disponible), 0) AS total_jugadores FROM T_Cuenta WHERE tipo_cuenta = 'PERSONAL'")
            row_jug = cursor.fetchone()
            saldo_jugadores = float(row_jug['total_jugadores']) if row_jug else 0.0

            # 3. Total ítems en circulación
            cursor.execute("SELECT COUNT(*) AS total_items FROM T_Item")
            total_items = cursor.fetchone()['total_items']

            # 4. Total jugadores registrados
            cursor.execute("SELECT COUNT(*) AS total_jugadores FROM T_Jugador")
            total_jugadores = cursor.fetchone()['total_jugadores']

            # 5. Total volumen transaccionado
            cursor.execute("SELECT COALESCE(SUM(monto), 0) AS volumen, COUNT(*) AS total_trx FROM T_Transaccion WHERE estado_transaccion = 'COMPLETADA'")
            row_trx = cursor.fetchone()
            volumen = float(row_trx['volumen']) if row_trx else 0.0
            total_trx = row_trx['total_trx'] if row_trx else 0

            # 6. Trades activos o pendientes
            cursor.execute("SELECT COUNT(*) AS trades_activos FROM T_Negociacion_Tradeo WHERE estado IN ('PENDIENTE', 'ACEPTADO', 'EN_PROCESO', 'ESPERANDO_CONFIRMACION_FINAL')")
            trades_activos = cursor.fetchone()['trades_activos']

            # 7. Parámetros del Servidor
            cursor.execute("SELECT id_servidor, nombre, porcentaje_comision, limite_bienes_por_jugador, tiempo_enfriamiento_min FROM T_Servidor WHERE id_servidor = 1")
            servidor = cursor.fetchone()

            return {
                "saldo_sistema": saldo_sistema,
                "saldo_jugadores": saldo_jugadores,
                "total_items": total_items,
                "total_jugadores": total_jugadores,
                "volumen_transaccionado": volumen,
                "total_transacciones": total_trx,
                "trades_activos": trades_activos,
                "servidor": servidor
            }, "OK"
    except Exception as e:
        return None, f"Error al obtener telemetría: {str(e)}"

def listar_todos_jugadores():
    """
    Retorna la lista completa de jugadores con su saldo, rol, estado y cantidad de ítems.
    """
    try:
        with get_db_cursor(dictionary=True, commit=False) as (cursor, _):
            cursor.execute("""
                SELECT 
                    j.id_jugador,
                    j.nombre_usuario,
                    j.correo,
                    j.estado,
                    j.es_admin,
                    j.fecha_registro,
                    COALESCE(c.saldo_disponible, 0.00) AS saldo,
                    (SELECT COUNT(*) FROM T_Item i WHERE i.id_jugador = j.id_jugador) AS total_items
                FROM T_Jugador j
                LEFT JOIN T_Cuenta c ON c.id_jugador = j.id_jugador
                ORDER BY j.id_jugador ASC
            """)
            players = cursor.fetchall()
            return players, "OK"
    except Exception as e:
        return None, f"Error al listar jugadores: {str(e)}"

def cambiar_estado_jugador(id_jugador: int, nuevo_estado: str):
    """
    Modera el estado de un jugador (ACTIVO, SUSPENDIDO, BANCARROTA) y le notifica en tiempo real.
    """
    if nuevo_estado not in ('ACTIVO', 'SUSPENDIDO', 'BANCARROTA'):
        return False, "Estado no válido."

    try:
        with get_db_cursor(commit=True) as (cursor, _):
            cursor.execute("UPDATE T_Jugador SET estado = %s WHERE id_jugador = %s", (nuevo_estado, id_jugador))
            
            tipo_alerta = 'WARNING' if nuevo_estado != 'ACTIVO' else 'SUCCESS'
            titulo = f"🛡 ESTADO DE CUENTA: {nuevo_estado}"
            mensaje = f"La Administración del Servidor ha actualizado el estado de tu cuenta a '{nuevo_estado}'."
            notification_service.crear_notificacion(id_jugador, titulo, mensaje, tipo_alerta)
            
            return True, f"Estado del jugador #{id_jugador} cambiado a {nuevo_estado} exitosamente."
    except Exception as e:
        return False, f"Error al cambiar estado: {str(e)}"

def cambiar_rol_admin(id_jugador: int, es_admin: bool):
    """
    Otorga o revoca permisos de administrador a un jugador.
    """
    try:
        with get_db_cursor(commit=True) as (cursor, _):
            cursor.execute("UPDATE T_Jugador SET es_admin = %s WHERE id_jugador = %s", (es_admin, id_jugador))
            
            titulo = "★ PRIVILEGIOS DE ADMINISTRADOR"
            mensaje = f"Has sido nombrado {'ADMINISTRADOR' if es_admin else 'JUGADOR ESTÁNDAR'} por la administración central."
            notification_service.crear_notificacion(id_jugador, titulo, mensaje, 'ADMIN')

            return True, f"Rol de administrador para jugador #{id_jugador} actualizado a {es_admin}."
    except Exception as e:
        return False, f"Error al cambiar rol: {str(e)}"

def ajustar_saldo_jugador(id_jugador: int, monto: float, operacion: str = 'SET'):
    """
    Ajusta el saldo de la cuenta personal de un jugador (ADD, SUBTRACT, SET) y emite notificación.
    """
    try:
        monto_float = float(monto)
        with get_db_cursor(dictionary=True, commit=True) as (cursor, _):
            cursor.execute("SELECT id_cuenta, saldo_disponible FROM T_Cuenta WHERE id_jugador = %s FOR UPDATE", (id_jugador,))
            cuenta = cursor.fetchone()
            if not cuenta:
                return False, f"No existe cuenta asociada al jugador #{id_jugador}."

            saldo_actual = float(cuenta['saldo_disponible'])
            op_upper = operacion.upper().strip()
            if op_upper in ('ADD', 'SUM'):
                nuevo_saldo = saldo_actual + monto_float
                desc = f"Abono de +${monto_float:,.2f}"
                tipo_notif = 'SUCCESS'
            elif op_upper in ('SUBTRACT', 'SUB'):
                if saldo_actual < monto_float:
                    return False, f"Fondos insuficientes para deducir ${monto_float:,.2f}. Saldo actual: ${saldo_actual:,.2f}"
                nuevo_saldo = saldo_actual - monto_float
                desc = f"Deducción de -${monto_float:,.2f}"
                tipo_notif = 'WARNING'
            elif op_upper == 'SET':
                nuevo_saldo = monto_float
                desc = f"Fijación de saldo en ${monto_float:,.2f}"
                tipo_notif = 'INFO'
            else:
                return False, f"Operación financiera '{operacion}' no reconocida."

            if nuevo_saldo < 0:
                return False, "El saldo no puede ser negativo."

            cursor.execute("UPDATE T_Cuenta SET saldo_disponible = %s WHERE id_cuenta = %s", (nuevo_saldo, cuenta['id_cuenta']))
            
            titulo = "💳 ACTUALIZACIÓN BANCARIA (ADMIN)"
            mensaje = f"El Administrador ha realizado una modificación en tu cuenta: {desc}. Tu nuevo saldo disponible es: ${nuevo_saldo:,.2f}."
            notification_service.crear_notificacion(id_jugador, titulo, mensaje, tipo_notif)

            return True, f"Saldo actualizado exitosamente. Nuevo saldo: ${nuevo_saldo:,.2f}"
    except Exception as e:
        return False, f"Error al ajustar saldo: {str(e)}"

def crear_jugador_admin(usuario: str, correo: str, password: str, saldo_inicial: float = 0.0, es_admin: bool = False):
    """
    Crea un nuevo jugador directamente desde la consola administrativa.
    """
    try:
        salt = bcrypt.gensalt()
        pw_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        with get_db_cursor(commit=True) as (cursor, _):
            cursor.execute("""
                INSERT INTO T_Jugador (id_servidor, nombre_usuario, correo, contrasena_hash, estado, es_admin)
                VALUES (1, %s, %s, %s, 'ACTIVO', %s)
            """, (usuario, correo, pw_hash, es_admin))
            nuevo_id = cursor.lastrowid

            # Crear cuenta bancaria
            cursor.execute("""
                INSERT INTO T_Cuenta (id_jugador, id_servidor, tipo_cuenta, saldo_inicial, saldo_disponible)
                VALUES (%s, 1, 'PERSONAL', %s, %s)
            """, (nuevo_id, float(saldo_inicial), float(saldo_inicial)))

            titulo = "🚀 BIENVENIDO A TRADE OS"
            mensaje = f"Tu cuenta ha sido dada de alta por la Administración con un saldo inicial de ${float(saldo_inicial):,.2f}."
            notification_service.crear_notificacion(nuevo_id, titulo, mensaje, 'SUCCESS')

            return True, f"Operador '{usuario}' creado exitosamente con ID #{nuevo_id}."
    except Exception as e:
        return False, f"Error al crear jugador: {str(e)}"

def obtener_inventario_jugador_admin(id_jugador: int):
    """
    Obtiene todos los bienes de un jugador específico para auditoría administrativa.
    """
    try:
        with get_db_cursor(dictionary=True, commit=False) as (cursor, _):
            cursor.execute("""
                SELECT id_item, nombre, precio, tiene_deuda, antiguedad_dias, fecha
                FROM T_Item
                WHERE id_jugador = %s
                ORDER BY id_item DESC
            """, (id_jugador,))
            items = cursor.fetchall()
            return items, "OK"
    except Exception as e:
        return None, f"Error al obtener inventario: {str(e)}"

def eliminar_item_admin(id_item: int):
    """
    Elimina/confisca forzosamente un ítem del inventario y le notifica al dueño en tiempo real.
    """
    try:
        with get_db_cursor(dictionary=True, commit=True) as (cursor, _):
            cursor.execute("SELECT id_jugador, nombre, precio FROM T_Item WHERE id_item = %s", (id_item,))
            item = cursor.fetchone()
            if not item:
                return False, f"El ítem #{id_item} no existe."

            id_jugador = item['id_jugador']
            nombre = item['nombre']

            cursor.execute("DELETE FROM T_Item WHERE id_item = %s", (id_item,))

            titulo = "⚠ INCAUTACIÓN DE BIEN (ADMIN)"
            mensaje = f"El Administrador ha decomisado o retirado el bien '{nombre}' (ID #{id_item}) de tu inventario."
            notification_service.crear_notificacion(id_jugador, titulo, mensaje, 'WARNING')

            return True, f"Ítem '{nombre}' (#{id_item}) eliminado e incautado exitosamente."
    except Exception as e:
        return False, f"Error al eliminar ítem: {str(e)}"

def inyectar_item_admin(id_jugador: int, nombre: str, precio: float, tiene_deuda: bool = False):
    """
    Inyecta un nuevo bien personalizado directamente al inventario de un operador y emite notificación.
    """
    try:
        with get_db_cursor(commit=True) as (cursor, _):
            cursor.execute("""
                INSERT INTO T_Item (id_jugador, nombre, precio, tiene_deuda, antiguedad_dias)
                VALUES (%s, %s, %s, %s, 0)
            """, (id_jugador, nombre, float(precio), tiene_deuda))
            nuevo_id_item = cursor.lastrowid

            titulo = "🎁 ¡NUEVO BIEN OTORGADO POR ADMINISTRACIÓN!"
            mensaje = f"El Administrador te ha otorgado el bien '{nombre}' valorado en ${float(precio):,.2f}{' (Con Gravamen/Deuda)' if tiene_deuda else ' (Libre)'}."
            notification_service.crear_notificacion(id_jugador, titulo, mensaje, 'SUCCESS')

            return True, f"Bien '{nombre}' (ID #{nuevo_id_item}) inyectado al jugador #{id_jugador} exitosamente."
    except Exception as e:
        return False, f"Error al inyectar ítem: {str(e)}"

def actualizar_parametros_servidor(porcentaje_comision: float, limite_bienes: int, tiempo_enfriamiento: int):
    """
    Actualiza la configuración central del servidor en T_Servidor.
    """
    try:
        with get_db_cursor(commit=True) as (cursor, _):
            cursor.execute("""
                UPDATE T_Servidor
                SET porcentaje_comision = %s,
                    limite_bienes_por_jugador = %s,
                    tiempo_enfriamiento_min = %s
                WHERE id_servidor = 1
            """, (float(porcentaje_comision), int(limite_bienes), int(tiempo_enfriamiento)))
            return True, "Parámetros globales del servidor actualizados en el Kernel."
    except Exception as e:
        return False, f"Error al actualizar servidor: {str(e)}"

def inyectar_fondos_tesoreria(monto: float):
    """
    Inyecta fondos de respaldo a la cuenta central de tesorería del sistema (ID: 1).
    """
    try:
        with get_db_cursor(commit=True) as (cursor, _):
            cursor.execute("""
                UPDATE T_Cuenta
                SET saldo_disponible = saldo_disponible + %s
                WHERE id_cuenta = 1
            """, (float(monto),))
            return True, f"Inyección de ${float(monto):,.2f} a la Tesorería Central completada."
    except Exception as e:
        return False, f"Error al inyectar a tesorería: {str(e)}"
