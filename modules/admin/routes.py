from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
import sqlite3
from functools import wraps
from config import Config

# --- AQUÍ ESTÁ LA PIEZA QUE FALTA ---
# Definimos el blueprint que la aplicación está buscando.
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
# ------------------------------------

# Decorador para proteger las rutas de admin y asegurarse de que solo los administradores puedan entrar
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica si el usuario ha iniciado sesión Y si su rol es 'admin'
        if not current_user.is_authenticated or not hasattr(current_user, 'role') or current_user.role != 'admin':
            abort(403) # Error de "Acceso Prohibido"
        return f(*args, **kwargs)
    return decorated_function

# Función para conectar a la base de datos
def get_db_connection():
    db_path = Config.DATABASE_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Ruta principal del panel de administración
@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    conn = get_db_connection()
    try:
        # Hacemos las consultas a la base de datos para obtener las estadísticas
        total_users = conn.execute('SELECT COUNT(id) FROM users').fetchone()[0]
        total_queries = conn.execute('SELECT COUNT(id) FROM query_log').fetchone()[0]
        recent_queries = conn.execute(
            'SELECT q.question, u.username, q.timestamp FROM query_log q JOIN users u ON q.user_id = u.id ORDER BY q.timestamp DESC LIMIT 10'
        ).fetchall()
    except sqlite3.OperationalError as e:
        print(f"ADVERTENCIA: La tabla 'query_log' aún no existe. Se mostrarán datos en cero. Error: {e}")
        # Si la tabla de logs no existe, no fallamos, mostramos datos en cero.
        total_users = conn.execute('SELECT COUNT(id) FROM users').fetchone()[0]
        total_queries = 0
        recent_queries = []
    finally:
        conn.close()

    # Preparamos los datos para enviarlos a la plantilla HTML
    stats = { 'total_users': total_users, 'total_queries': total_queries }
    return render_template('admin_dashboard.html', stats=stats, recent_queries=recent_queries)

