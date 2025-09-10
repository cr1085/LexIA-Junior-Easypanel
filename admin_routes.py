from flask import Blueprint, render_template, abort, redirect, url_for
from flask_login import login_required, current_user
import sqlite3
from functools import wraps
from config import Config

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Decorador para asegurarse de que solo los administradores puedan acceder
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403) # Error de "Prohibido"
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Muestra el panel de administración principal."""
    conn = get_db_connection()
    
    # --- Obtener estadísticas ---
    total_users = conn.execute('SELECT COUNT(id) FROM users').fetchone()[0]
    # Asumimos que tienes una tabla para logs de preguntas
    try:
        total_queries = conn.execute('SELECT COUNT(id) FROM query_log').fetchone()[0]
        recent_queries = conn.execute('SELECT q.question, u.username, q.timestamp FROM query_log q JOIN users u ON q.user_id = u.id ORDER BY q.timestamp DESC LIMIT 10').fetchall()
    except sqlite3.OperationalError:
        # Si la tabla no existe, la creamos
        conn.execute('''
            CREATE TABLE query_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        conn.commit()
        total_queries = 0
        recent_queries = []

    conn.close()

    stats = {
        'total_users': total_users,
        'total_queries': total_queries
    }

    return render_template('admin_dashboard.html', stats=stats, recent_queries=recent_queries)
