import os
from flask import Flask
from core.config import Config
from routes import register_routes

def create_app(config_class=Config):
    """
    Fábrica de aplicaciones (Application Factory Pattern).
    Inicializa la configuración, extensiones y registra los blueprints.
    """
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_class)
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 43200
    app.secret_key = config_class.SECRET_KEY

    # Registrar Blueprints de Rutas
    register_routes(app)

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    print(f"[*] Servidor Economy RP iniciado en http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)