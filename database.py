"""
database.py - Capa de compatibilidad hacia atrás (Facade / Re-export).
Delega todas las operaciones a los módulos correspondientes en core/ y services/.
"""

from core.database import get_db_connection, get_db_cursor, ensure_scalar as _ensure_scalar
from services.auth_service import registrar_jugador, iniciar_sesion
from services.player_service import consultar_saldo, consultar_inventario, pagar_jornada
from services.trade_service import (
    abrir_negociacion,
    consultar_ofertas_pendientes,
    consultar_mesa_activa,
    obtener_detalle_trade,
    aceptar_invitacion_trade,
    actualizar_oferta_jugador,
    lock_trade_player,
    finalizar_tradeo,
    cancelar_tradeo,
    limpieza_forzada_trades
)
from services.history_service import obtener_historial_jugador

def confirmar_tradeo(id_negociacion, id_jugador):
    """Ejecuta el procedimiento almacenado sp_confirmar_tradeo (modo legado)."""
    conn = get_db_connection()
    if not conn:
        return False, "Error de conexión"
    try:
        cursor = conn.cursor()
        cursor.callproc('sp_confirmar_tradeo', (_ensure_scalar(id_negociacion), _ensure_scalar(id_jugador)))
        conn.commit()
        return True, "Confirmación de tradeo procesada"
    except Exception as e:
        return False, str(e)
    finally:
        if conn:
            conn.close()

__all__ = [
    'get_db_connection',
    'get_db_cursor',
    '_ensure_scalar',
    'registrar_jugador',
    'iniciar_sesion',
    'pagar_jornada',
    'abrir_negociacion',
    'confirmar_tradeo',
    'consultar_saldo',
    'consultar_inventario',
    'obtener_detalle_trade',
    'actualizar_oferta_jugador',
    'lock_trade_player',
    'consultar_mesa_activa',
    'limpieza_forzada_trades',
    'consultar_ofertas_pendientes',
    'aceptar_invitacion_trade',
    'finalizar_tradeo',
    'obtener_historial_jugador'
]

