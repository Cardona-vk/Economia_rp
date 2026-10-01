import mysql.connector
from mysql.connector import Error, pooling
from contextlib import contextmanager
from core.config import Config

_db_pool = None

def _get_pool():
    global _db_pool
    if _db_pool is None:
        try:
            _db_pool = pooling.MySQLConnectionPool(
                pool_name="economy_pool",
                pool_size=5,
                pool_reset_session=True,
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                port=Config.DB_PORT,
                connect_timeout=8
            )
        except Exception as e:
            print(f"[DB Pool Error] Fallo al crear pool: {e}")
            _db_pool = None
    return _db_pool

def get_db_connection():
    """Retorna una conexión activa desde el pool o una conexión directa de respaldo."""
    pool = _get_pool()
    if pool:
        try:
            return pool.get_connection()
        except Error as e:
            print(f"[DB Pool Warning] No se pudo obtener conexión del pool: {e}, intentando directa...")

    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )
        return connection
    except Error as e:
        print(f"[DB Error] Error conectando a MySQL: {e}")
        return None

@contextmanager
def get_db_cursor(dictionary=False, commit=False):
    """
    Context manager para manejo seguro de conexiones y cursores.
    Realiza commit automático si commit=True, y rollback si ocurre una excepción.
    Garantiza el cierre del cursor y la conexión.
    """
    conn = get_db_connection()
    if not conn:
        raise ConnectionError("No se pudo establecer conexión con la base de datos.")
    
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield cursor, conn
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def ensure_scalar(val):
    """Extrae un valor entero o escalar limpio a partir de primitivos o diccionarios."""
    if val is None:
        return None
    if isinstance(val, dict):
        return val.get('id_usuario') or val.get('id_jugador') or val.get('id_item')
    try:
        return int(val)
    except (TypeError, ValueError):
        return None
