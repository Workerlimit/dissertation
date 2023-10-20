from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)

AUTH_SERVICE_URL = "http://localhost:5000"

SECRET_KEY = '32f7d11a6d4ab32c2ad57029f1c42b13e02e2707b4e3f30a4f1e3f4853a731e3'

products = []

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

    data = request.get_json()
    product = {
        'id': len(products) + 1,
        'name': data.get('name'),
        'description': data.get('description'),
        'price': data.get('price')
    }
    products.append(product)
    return jsonify({'message': 'Product created successfully', 'product': product}), 201

@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(products)

@app.route('/products/<int:product_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_product(product_id):
    if request.method == 'GET':
        product = next((p for p in products if p['id'] == product_id), None)
        if product:
            return jsonify(product)
        else:
            return jsonify({'message': 'Product not found'}), 404

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
        product = next((p for p in products if p['id'] == product_id), None)
        if product:
            product['name'] = data.get('name', product['name'])
            product['description'] = data.get('description', product['description'])
            product['price'] = data.get('price', product['price'])
            return jsonify({'message': 'Product updated successfully', 'product': product})

        return jsonify({'message': 'Product not found'}), 404

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

        product = next((p for p in products if p['id'] == product_id), None)
        if product:
            products.remove(product)
            return jsonify({'message': 'Product deleted successfully'})

        return jsonify({'message': 'Product not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, port=5001)
