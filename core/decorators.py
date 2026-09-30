from functools import wraps
from flask import session, redirect, url_for, jsonify, request
from core.database import get_db_cursor

def get_current_user_id():
    """Helper para obtener el ID escalar del usuario en la sesión actual."""
    user_id = session.get('user_id')
    if isinstance(user_id, dict):
        return user_id.get('id_usuario') or user_id.get('id_jugador')
    try:
        return int(user_id) if user_id is not None else None
    except (TypeError, ValueError):
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_current_user_id():
            if request.path.startswith('/api/'):
                return jsonify({"success": False, "message": "No autenticado"}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_current_user_id()
        if not user_id:
            if request.path.startswith('/api/'):
                return jsonify({"success": False, "message": "No autenticado"}), 401
            return redirect(url_for('auth.login'))
        
        try:
            with get_db_cursor() as (cursor, _):
                cursor.execute("SELECT es_admin FROM T_Jugador WHERE id_jugador = %s", (user_id,))
                res = cursor.fetchone()
                if not res or not res[0]:
                    if request.path.startswith('/api/'):
                        return jsonify({"success": False, "message": "Acceso denegado: solo administradores."}), 403
                    return "Acceso denegado, esta sección es solo para administradores.", 403
        except Exception as e:
            if request.path.startswith('/api/'):
                return jsonify({"success": False, "message": f"Error verificando permisos: {str(e)}"}), 500
            return "Error de permisos en base de datos", 500

        return f(*args, **kwargs)
    return decorated_function
