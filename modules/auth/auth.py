import sqlite3
import os
from hashlib import sha256
import secrets

def init_db():
    """Inicializa la base de datos"""
    conn = sqlite3.connect('instance/legal_db.db')
    c = conn.cursor()
    
    # Tabla de usuarios
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de casos
    c.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client TEXT NOT NULL,
            type TEXT NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            due_date DATE,
            status TEXT DEFAULT 'Abierto',
            user_id INTEGER,
            priority TEXT DEFAULT 'media',
            estimated_value REAL,
            hours_invested REAL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash de contraseña con salt"""
    salt = secrets.token_hex(16)
    return sha256((password + salt).encode()).hexdigest() + ':' + salt

def check_password(hashed_password, user_password):
    """Verifica la contraseña"""
    if ':' not in hashed_password:
        return False
    stored_hash, salt = hashed_password.split(':')
    return stored_hash == sha256((user_password + salt).encode()).hexdigest()

class User:
    def __init__(self, id, username, email, role='user'):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return str(self.id)

    @staticmethod
    def get(user_id):
        conn = sqlite3.connect('instance/legal_db.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        conn.close()
        if user:
            return {'id': user[0], 'username': user[1], 'email': user[2], 
                   'password_hash': user[3], 'role': user[4]}
        return None

    @staticmethod
    def get_by_username(username):
        conn = sqlite3.connect('instance/legal_db.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        if user:
            return {'id': user[0], 'username': user[1], 'email': user[2], 
                   'password_hash': user[3], 'role': user[4]}
        return None

    @staticmethod
    def create(username, email, password):
        try:
            conn = sqlite3.connect('instance/legal_db.db')
            c = conn.cursor()
            password_hash = hash_password(password)
            c.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                     (username, email, password_hash))
            conn.commit()
            conn.close()
            return True
        except:
            return False