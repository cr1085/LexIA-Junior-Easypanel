
from modules.db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	# username = db.Column(db.String(80), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password_hash = db.Column(db.Text, nullable=False)
	role = db.Column(db.String(20), default='user', nullable=False)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	@staticmethod
	def get_by_id(user_id):
		return User.query.get(user_id)

	# @staticmethod
	# def get_by_username(username):
	# 	return User.query.filter_by(username=username).first()
	
	@staticmethod
	def get_by_email(email):
		return User.query.filter_by(email=email).first()

	# @staticmethod
	# def create(username, email, password):
	# 	if User.query.filter((User.username == username) | (User.email == email)).first():
	# 		return False
	# 	user = User(username=username, email=email)
	# 	user.set_password(password)
	# 	db.session.add(user)
	# 	db.session.commit()
	# 	return True

	@staticmethod
	def create(email, password):
		if User.query.filter((User.email == email)).first():
			return False
		user = User(email=email)
		user.set_password(password)
		db.session.add(user)
		db.session.commit()
		return True

class QueryLog(db.Model):
	__tablename__ = 'query_log'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	question = db.Column(db.Text, nullable=False)
	timestamp = db.Column(db.DateTime, server_default=db.func.now())
	user = db.relationship('User', backref=db.backref('logs', lazy=True))

