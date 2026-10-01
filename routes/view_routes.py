from flask import Blueprint, render_template, redirect, url_for, session
from core.decorators import login_required, admin_required, get_current_user_id
from services import player_service

views_bp = Blueprint('views', __name__)

@views_bp.route('/health', endpoint='health')
@views_bp.route('/healthz', endpoint='healthz')
def health():
    return {"status": "ok", "service": "Economy RP"}, 200

@views_bp.route('/', endpoint='index')
def index():
    if get_current_user_id():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@views_bp.route('/dashboard', endpoint='dashboard')
@login_required
def dashboard():
    user_id = get_current_user_id()
    metrics, _ = player_service.consultar_metricas_dashboard(user_id)
    return render_template(
        'dashboard.html',
        username=session.get('username'),
        player_id=user_id,
        metrics=metrics or {}
    )


@views_bp.route('/trade', endpoint='trade')
@login_required
def trade():
    user_id = get_current_user_id()
    inventario, _ = player_service.consultar_inventario(user_id)
    return render_template(
        'trade.html',
        username=session.get('username'),
        player_id=user_id,
        inventario=inventario or []
    )

@views_bp.route('/history', endpoint='history')
@login_required
def history():
    return render_template(
        'history.html',
        username=session.get('username')
    )

@views_bp.route('/admin', endpoint='admin')
@admin_required
def admin():
    return render_template(
        'admin.html',
        username=session.get('username')
    )
