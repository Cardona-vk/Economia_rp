from flask import Blueprint, request, jsonify
from core.decorators import login_required, admin_required, get_current_user_id
from services import (
    player_service,
    trade_service,
    history_service,
    admin_service,
    notification_service
)

api_bp = Blueprint('api', __name__, url_prefix='/api')

# --- NOTIFICACIONES EN TIEMPO REAL ---

@api_bp.route('/notifications/unread', methods=['GET'])
@login_required
def api_unread_notifications():
    user_id = get_current_user_id()
    notifs, msg = notification_service.obtener_notificaciones_no_leidas(user_id)
    return jsonify({
        "success": True,
        "notifications": notifs or []
    })

@api_bp.route('/notifications/mark-read', methods=['POST'])
@login_required
def api_mark_notifications_read():
    user_id = get_current_user_id()
    data = request.get_json(silent=True) or {}
    ids = data.get('ids')
    success, msg = notification_service.marcar_como_leidas(user_id, ids)
    return jsonify({"success": success, "message": msg})


# --- DASHBOARD & HISTORIAL ---

@api_bp.route('/dashboard', methods=['GET'])
@login_required
def api_dashboard():
    user_id = get_current_user_id()
    data, msg = player_service.consultar_metricas_dashboard(user_id)
    if not data:
        return jsonify({
            "success": False,
            "saldo": 0.0,
            "inventario": [],
            "error": msg
        }), 500

    return jsonify({
        "success": True,
        **data,
        "error": None
    })


@api_bp.route('/history', methods=['GET'])
@login_required
def api_history():
    user_id = get_current_user_id()
    historial, msg = history_service.obtener_historial_jugador(user_id)
    if historial is None:
        return jsonify({"success": False, "message": msg}), 500

    return jsonify({"success": True, "historial": historial})

# --- SISTEMA DE TRADEO EN TIEMPO REAL ---

@api_bp.route('/trades/open', methods=['POST'])
@login_required
def api_open_trade():
    try:
        user_id = get_current_user_id()
        data = request.get_json(silent=True) or {}

        try:
            destinatario = int(data.get('destinatario'))
        except (TypeError, ValueError):
            return jsonify({"success": False, "message": "ID de destinatario inválido"}), 400

        if user_id == destinatario:
            return jsonify({"success": False, "message": "No puedes iniciar una negociación contigo mismo."}), 400

        item_j1 = data.get('item_ids') or data.get('item_j1')
        monto_j1 = data.get('monto_j1', 0)
        expiracion = data.get('expiracion', 10)

        success, msg = trade_service.abrir_negociacion(
            id_j1=user_id,
            id_j2=destinatario,
            item_j1=item_j1,
            item_j2=None,
            monto_j1=monto_j1,
            monto_j2=0,
            exp=expiracion
        )

        return jsonify({"success": success, "message": msg}), (200 if success else 400)
    except Exception as e:
        return jsonify({"success": False, "message": f"Error interno: {str(e)}"}), 500

@api_bp.route('/trades/active', methods=['GET'])
@login_required
def api_trade_active():
    user_id = get_current_user_id()
    trade, msg = trade_service.consultar_mesa_activa(user_id)
    if not trade:
        return jsonify({"success": False, "message": msg})

    return jsonify({"success": True, "data": trade})

@api_bp.route('/trades/pending', methods=['GET'])
@login_required
def api_trades_pending():
    user_id = get_current_user_id()
    invitaciones, msg = trade_service.consultar_ofertas_pendientes(user_id)
    if invitaciones is None:
        return jsonify({"success": False, "message": msg}), 500

    return jsonify({"success": True, "invitaciones": invitaciones})

@api_bp.route('/trades/<int:id_trade>/status', methods=['GET'])
@login_required
def api_trade_status(id_trade):
    trade, msg = trade_service.obtener_detalle_trade(id_trade)
    if not trade:
        return jsonify({"success": False, "message": msg}), 404

    return jsonify({
        "success": True,
        "data": trade
    })

@api_bp.route('/trades/accept', methods=['POST'])
@login_required
def api_trades_accept():
    data = request.get_json(silent=True) or {}
    id_trade = data.get('id_trade')
    user_id = get_current_user_id()

    if not id_trade:
        return jsonify({"success": False, "message": "ID de tradeo faltante"}), 400

    success, msg = trade_service.aceptar_invitacion_trade(id_trade, user_id)
    return jsonify({"success": success, "message": msg}), (200 if success else 400)

@api_bp.route('/trades/update_offer', methods=['POST'])
@login_required
def api_update_offer():
    data = request.get_json(silent=True) or {}
    user_id = get_current_user_id()
    id_trade = data.get('id_trade')
    monto = data.get('monto', 0)
    id_item = data.get('item_ids') or data.get('id_items') or data.get('id_item')

    if not id_trade:
        return jsonify({"success": False, "message": "ID de tradeo faltante"}), 400

    success, msg = trade_service.actualizar_oferta_jugador(id_trade, user_id, monto, id_item)
    return jsonify({"success": success, "message": msg}), (200 if success else 400)

@api_bp.route('/trades/confirm', methods=['POST'])
@login_required
def api_trade_confirm():
    data = request.get_json(silent=True) or {}
    user_id = get_current_user_id()
    id_trade = data.get('id_trade')

    if not id_trade:
        return jsonify({"success": False, "message": "ID de tradeo faltante"}), 400

    trade_data, _ = trade_service.obtener_detalle_trade(id_trade)
    if not trade_data:
        return jsonify({"success": False, "message": "Tradeo no encontrado"}), 404

    success, msg, both_confirmed = trade_service.lock_trade_player(id_trade, user_id)

    if success and both_confirmed:
        final_success, final_msg = trade_service.finalizar_tradeo(id_trade)
        if final_success:
            return jsonify({"success": True, "message": "Tradeo completado exitosamente", "completed": True})
        else:
            return jsonify({"success": False, "message": f"Error al finalizar: {final_msg}"}), 500

    return jsonify({"success": success, "message": msg, "completed": False})

@api_bp.route('/trades/cancel', methods=['POST'])
@login_required
def api_trade_cancel():
    data = request.get_json(silent=True) or {}
    id_trade = data.get('id_trade')
    if not id_trade:
        return jsonify({"success": False, "message": "ID de tradeo faltante"}), 400

    success, msg = trade_service.cancelar_tradeo(id_trade)
    return jsonify({"success": success, "message": msg})

# ==============================================================================
# --- MÓDULO DE ADMINISTRACIÓN TOTAL (SYS_ADMIN_DECK_V2.4) ---
# ==============================================================================

@api_bp.route('/admin/telemetry', methods=['GET'])
@admin_required
def api_admin_telemetry():
    data, msg = admin_service.obtener_telemetria_global()
    if data is None:
        return jsonify({"success": False, "message": msg}), 500
    return jsonify({"success": True, "telemetry": data})

@api_bp.route('/admin/players', methods=['GET'])
@admin_required
def api_admin_players():
    jugadores, msg = admin_service.listar_todos_jugadores()
    if jugadores is None:
        return jsonify({"success": False, "message": msg}), 500
    return jsonify({"success": True, "players": jugadores})

@api_bp.route('/admin/players/<int:id_player>/status', methods=['POST'])
@admin_required
def api_admin_player_status(id_player):
    data = request.get_json(silent=True) or {}
    nuevo_estado = data.get('estado')
    if not nuevo_estado:
        return jsonify({"success": False, "message": "Estado faltante"}), 400

    success, msg = admin_service.cambiar_estado_jugador(id_player, nuevo_estado)
    return jsonify({"success": success, "message": msg}), (200 if success else 400)

@api_bp.route('/admin/players/<int:id_player>/role', methods=['POST'])
@admin_required
def api_admin_player_role(id_player):
    data = request.get_json(silent=True) or {}
    es_admin = data.get('es_admin', False)
    success, msg = admin_service.cambiar_rol_admin(id_player, es_admin)
    return jsonify({"success": success, "message": msg}), (200 if success else 400)

@api_bp.route('/admin/players/<int:id_player>/money', methods=['POST'])
@admin_required
def api_admin_player_money(id_player):
    data = request.get_json(silent=True) or {}
    monto = data.get('monto')
    operacion = data.get('operacion', 'SET')
    if monto is None:
        return jsonify({"success": False, "message": "Monto requerido"}), 400

    success, msg = admin_service.ajustar_saldo_jugador(id_player, monto, operacion)
    return jsonify({"success": success, "message": msg}), (200 if success else 400)

@api_bp.route('/admin/players/create', methods=['POST'])
@admin_required
def api_admin_player_create():
    data = request.get_json(silent=True) or {}
    usuario = data.get('usuario')
    correo = data.get('correo')
    password = data.get('password')
    saldo = data.get('saldo_inicial', 0.0)
    es_admin = data.get('es_admin', False)

    success, msg = admin_service.crear_jugador_admin(usuario, correo, password, saldo, es_admin)
    return jsonify({"success": success, "message": msg}), (200 if success else 400)

@api_bp.route('/admin/players/<int:id_player>/inventory', methods=['GET'])
@admin_required
def api_admin_player_inventory(id_player):
    items, msg = admin_service.obtener_inventario_jugador_admin(id_player)
    if items is None:
        return jsonify({"success": False, "message": msg}), 500
    return jsonify({"success": True, "inventory": items})

@api_bp.route('/admin/items/delete', methods=['POST'])
@admin_required
def api_admin_item_delete():
    data = request.get_json(silent=True) or {}
    id_item = data.get('id_item')
    if not id_item:
        return jsonify({"success": False, "message": "ID de ítem requerido"}), 400

    success, msg = admin_service.eliminar_item_admin(id_item)
    return jsonify({"success": success, "message": msg}), (200 if success else 400)

@api_bp.route('/admin/items/inject', methods=['POST'])
@admin_required
def api_admin_item_inject():
    data = request.get_json(silent=True) or {}
    id_jugador = data.get('id_jugador')
    nombre = data.get('nombre')
    precio = data.get('precio', 1000.0)
    tiene_deuda = data.get('tiene_deuda', False)

    if not id_jugador or not nombre:
        return jsonify({"success": False, "message": "ID de jugador y nombre de ítem requeridos"}), 400

    success, msg = admin_service.inyectar_item_admin(id_jugador, nombre, precio, tiene_deuda)
    return jsonify({"success": success, "message": msg}), (200 if success else 400)

@api_bp.route('/admin/server/config', methods=['POST'])
@admin_required
def api_admin_server_config():
    data = request.get_json(silent=True) or {}
    pct = data.get('porcentaje_comision', 5.0)
    limite = data.get('limite_bienes', 100)
    cooldown = data.get('tiempo_enfriamiento', 15)

    success, msg = admin_service.actualizar_parametros_servidor(pct, limite, cooldown)
    return jsonify({"success": success, "message": msg}), (200 if success else 400)

@api_bp.route('/admin/treasury/inject', methods=['POST'])
@admin_required
def api_admin_treasury_inject():
    data = request.get_json(silent=True) or {}
    monto = data.get('monto', 0.0)
    success, msg = admin_service.inyectar_fondos_tesoreria(monto)
    return jsonify({"success": success, "message": msg}), (200 if success else 400)

@api_bp.route('/admin/trades/force_clean', methods=['POST'])
@admin_required
def api_admin_trades_force_clean():
    success, msg = trade_service.limpieza_forzada_trades()
    return jsonify({"success": success, "message": msg}), (200 if success else 400)

