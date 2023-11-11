from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from models import db, Product
import jwt
import os
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
CORS(app)

base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, '../data/products.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///' + db_path)

db.init_app(app)

AUTH_SERVICE_URL = "http://localhost:5000"

SECRET_KEY = '32f7d11a6d4ab32c2ad57029f1c42b13e02e2707b4e3f30a4f1e3f4853a731e3'

@app.route('/')
def home():
    return 'Products Microservice is up and running!'

@app.route('/create_product', methods=['POST'])
def create_product():
    token = request.headers.get('Authorization')
    if token and token.startswith('Bearer '):
        token = token[7:] 
    if not token:
        return jsonify({"message": "Token is missing"}), 401

    try:
        jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

    data = data = request.get_json()
    new_product = Product(name=data.get('name'), description=data.get('description'), price=data.get('price'))
    db.session.add(new_product)

    try:
        db.session.commit()
        return jsonify({'message': 'Product created successfully', 'product': new_product.serialize()}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Product creation failed. Duplicate product name.'}), 400

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    products_data = [product.serialize() for product in products]
    return jsonify(products_data)

@app.route('/products/<int:product_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_product(product_id):
    product = Product.query.get(product_id)

    if not product:
        return jsonify({'message': 'Product not found'}), 404

    if request.method == 'GET':
        return jsonify(product.serialize())

    if request.method == 'PUT':
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:] 
        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        data = request.get_json()
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = data.get('price', product.price)

        db.session.commit()

        return jsonify({'message': 'Product updated successfully', 'product': product.serialize()})

    if request.method == 'DELETE':
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:] 
        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        db.session.delete(product)
        db.session.commit()

        return jsonify({'message': 'Product deleted successfully'})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
