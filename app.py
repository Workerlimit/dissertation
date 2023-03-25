from flask import Flask, jsonify
from models import db, Users
from auth import auth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my-secret-key'
db.init_app(app)

app.register_blueprint(auth)

@app.route('/')
def home():
    users = Users.query.all()
    return jsonify([{'name': user.name, 'email': user.email} for user in users])

if __name__ == '__main__':
    app.run()
