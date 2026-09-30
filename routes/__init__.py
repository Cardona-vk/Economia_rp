from .auth_routes import auth_bp
from .view_routes import views_bp
from .api_routes import api_bp

def register_routes(app):
    """Registra todos los Blueprints y aliases de endpoints en la aplicación Flask."""
    app.register_blueprint(auth_bp)
    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp)

    # Aliases de endpoints directos para máxima compatibilidad con templates
    app.add_url_rule('/login', endpoint='login', view_func=app.view_functions['auth.login'], methods=['GET', 'POST'])
    app.add_url_rule('/register', endpoint='register', view_func=app.view_functions['auth.register'], methods=['GET', 'POST'])
    app.add_url_rule('/logout', endpoint='logout', view_func=app.view_functions['auth.logout'])
    app.add_url_rule('/dashboard', endpoint='dashboard', view_func=app.view_functions['views.dashboard'])
    app.add_url_rule('/trade', endpoint='trade', view_func=app.view_functions['views.trade'])
    app.add_url_rule('/history', endpoint='history', view_func=app.view_functions['views.history'])
    app.add_url_rule('/admin', endpoint='admin', view_func=app.view_functions['views.admin'])
