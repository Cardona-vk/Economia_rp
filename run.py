import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    print(f"[*] Iniciando Economy RP en http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
