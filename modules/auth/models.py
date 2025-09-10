# import sqlite3
# import hashlib
# import os
# from flask_login import UserMixin
# from config import Config

# def get_db_connection():
#     # Asegurarse de que el directorio 'instance' exista
#     instance_path = os.path.dirname(Config.DATABASE_PATH)
#     if not os.path.exists(instance_path):
#         os.makedirs(instance_path)
#     conn = sqlite3.connect(Config.DATABASE_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn

# def init_db():
#     conn = get_db_connection()
#     c = conn.cursor()
#     # Tabla de Usuarios
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT UNIQUE NOT NULL,
#             email TEXT UNIQUE NOT NULL,
#             password_hash TEXT NOT NULL,
#             role TEXT DEFAULT 'user'
#         )
#     ''')
#     conn.commit()
#     conn.close()

# def hash_password(password):
#     return hashlib.sha256(password.encode('utf-8')).hexdigest()

# def check_password(hashed_password, password):
#     return hashed_password == hashlib.sha256(password.encode('utf-8')).hexdigest()

# class User(UserMixin):
#     def __init__(self, id, username, email, role):
#         self.id = id
#         self.username = username
#         self.email = email
#         self.role = role

#     @staticmethod
#     def get(user_id):
#         conn = get_db_connection()
#         user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
#         conn.close()
#         if user:
#             return User(user['id'], user['username'], user['email'], user['role'])
#         return None

#     @staticmethod
#     def get_by_username(username):
#         conn = get_db_connection()
#         user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
#         conn.close()
#         return user

#     @staticmethod
#     def create(username, email, password):
#         conn = get_db_connection()
#         try:
#             conn.execute(
#                 'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
#                 (username, email, hash_password(password))
#             )
#             conn.commit()
#             return True
#         except sqlite3.IntegrityError:
#             return False
#         finally:
#             conn.close()


import sqlite3
import hashlib
import os
from flask_login import UserMixin
from config import Config

def get_db_connection():
    """Establece conexión con la base de datos y se asegura que la carpeta exista."""
    instance_path = os.path.dirname(Config.DATABASE_PATH)
    os.makedirs(instance_path, exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Crea la tabla de usuarios y la tabla de logs si no existen."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Tabla de Usuarios con el campo 'role'
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user' NOT NULL
        )
    ''')
    
    # Nueva tabla para registrar las consultas (logs)
    c.execute('''
        CREATE TABLE IF NOT EXISTS query_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    # Mensaje de confirmación que ahora verás
    print("Base de datos de usuarios y logs verificada/creada con éxito.")

# --- Funciones de Hash ---
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def check_password(hashed_password, password):
    return hashed_password == hashlib.sha256(password.encode('utf-8')).hexdigest()

# --- Clase User ---
class User(UserMixin):
    def __init__(self, id, username, email, role):
        self.id = id
        self.username = username
        self.email = email
        self.role = role

    @staticmethod
    def get(user_id):
        conn = get_db_connection()
        user_data = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if user_data:
            return User(user_data['id'], user_data['username'], user_data['email'], user_data['role'])
        return None

    @staticmethod
    def get_by_username(username):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        return user

    @staticmethod
    def create(username, email, password):
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, hash_password(password))
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError: # Evita duplicados de username o email
            return False
        finally:
            conn.close()

