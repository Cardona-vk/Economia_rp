from flask import Blueprint, render_template, request, redirect, url_for, session
from services import auth_service
from core.decorators import get_current_user_id

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    if get_current_user_id():
        return redirect(url_for('dashboard'))

    message = None
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        password = request.form.get('password', '')

        success, result = auth_service.iniciar_sesion(usuario, password)
        if success:
            session['user_id'] = result['id_usuario'] if isinstance(result, dict) else result
            session['username'] = usuario
            session['es_admin'] = bool(result.get('es_admin')) if isinstance(result, dict) else False
            return redirect(url_for('views.dashboard'))
        else:
            message = result

    return render_template('login.html', message=message)

@auth_bp.route('/register', methods=['GET', 'POST'], endpoint='register')
def register():
    if get_current_user_id():
        return redirect(url_for('dashboard'))

    message = None
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        correo = request.form.get('correo', '').strip()
        password = request.form.get('password', '')

        success, msg = auth_service.registrar_jugador(usuario, correo, password)
        if success:
            return redirect(url_for('login'))
        else:
            message = msg

    return render_template('register.html', message=message)

@auth_bp.route('/logout', endpoint='logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
