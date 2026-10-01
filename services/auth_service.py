import bcrypt
from mysql.connector import Error
from core.database import get_db_cursor

def registrar_jugador(usuario, correo, password):
    """
    Registra un nuevo jugador y crea su cuenta bancaria PERSONAL inicial asociada al servidor por defecto.
    """
    if not usuario or not correo or not password:
        return False, "Todos los campos son obligatorios"

    try:
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        with get_db_cursor(commit=True) as (cursor, _):
            cursor.execute("SELECT id_servidor FROM servidores LIMIT 1")
            servidor = cursor.fetchone()
            if not servidor:
                return False, "No hay servidores configurados en servidores"
            
            id_servidor = servidor[0]
            
            # 1. Crear jugador
            query_jugador = """
                INSERT INTO jugadores (id_servidor, nombre_usuario, correo, contrasena_hash) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query_jugador, (id_servidor, usuario, correo, hashed_pw))
            id_jugador = cursor.lastrowid
            
            # 2. Crear cuenta bancaria inicial (PERSONAL)
            query_cuenta = """
                INSERT INTO cuentas (id_jugador, id_servidor, tipo_cuenta, saldo_inicial, saldo_disponible) 
                VALUES (%s, %s, 'PERSONAL', 0.00, 0.00)
            """
            cursor.execute(query_cuenta, (id_jugador, id_servidor))
            
            return True, "Jugador registrado y cuenta creada exitosamente"
    except Error as e:
        return False, f"Error al registrar jugador: {e}"
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"

def iniciar_sesion(usuario, password):
    """
    Autentica las credenciales del jugador y retorna sus datos básicos de sesión.
    """
    if not usuario or not password:
        return False, "Por favor ingrese usuario y contraseña"

    try:
        with get_db_cursor(dictionary=True) as (cursor, _):
            query = "SELECT id_jugador, contrasena_hash, es_admin, estado FROM jugadores WHERE nombre_usuario = %s"
            cursor.execute(query, (usuario,))
            result = cursor.fetchone()
            
            if result:
                db_pw = result['contrasena_hash']
                if isinstance(db_pw, str):
                    db_pw = db_pw.encode('utf-8')
                
                if bcrypt.checkpw(password.encode('utf-8'), db_pw):
                    if result.get('estado') == 'SUSPENDIDO':
                        return False, "Tu cuenta ha sido SUSPENDIDA / BANEADA por un Administrador."
                    return True, {
                        'id_usuario': result['id_jugador'], 
                        'usuario': usuario,
                        'es_admin': bool(result.get('es_admin')),
                        'estado': result.get('estado')
                    }
            return False, "Usuario o contraseña incorrectos"
    except Error as e:
        return False, f"Error durante el login: {e}"
    except Exception as e:
        return False, f"Error inesperado durante el login: {str(e)}"
