from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, check_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = User.get_by_username(username)
        
        if user_data and check_password(user_data['password_hash'], password):
            user_obj = User.get(user_data['id'])
            login_user(user_obj)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.get_by_username(username):
            flash('El nombre de usuario ya existe.', 'error')
        elif User.create(username, email, password):
            flash('¡Cuenta creada exitosamente! Por favor, inicia sesión.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Ocurrió un error al crear la cuenta.', 'error')

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))