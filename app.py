from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import jwt
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/mydatabase'
app.config['SECRET_KEY'] = 'my-secret-key'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

@app.route('/login')
def protected_route():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return jsonify({'error': 'Authentication required'}), 401

    user = User.query.filter_by(username=auth.username).first()

    if not user or not check_password_hash(user.password_hash, auth.password):
        return jsonify({'error': 'Invalid username or password'}), 401

    token = jwt.encode({'username': user.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

    return jsonify({'message': f'Hello, {user.username}!', 'token': token.decode('UTF-8')})

@app.route('/signup', methods=['POST'])
def create_user():
    data = request.get_json()

    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400

    password_hash = generate_password_hash(data['password'])
    user = User(username=data['username'], password_hash=password_hash, email=data['email'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': f'User {data["username"]} created successfully'}), 201
