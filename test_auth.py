import unittest
from app import app, db
from models import Users

class AuthTestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_login(self):
        with app.test_client() as client:
            user = Users(name='test_user', password='password')
            app.app_context().push()
            db.session.add(user)
            db.session.commit()
            response = client.post('/login', data=dict(
                name='test_user',
                password='password'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Welcome, test_user!', response.data)

    def test_login_invalid_credentials(self):
        with app.test_client() as client:
            response = client.post('/login', data=dict(
                name='test_user',
                password='password'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Invalid username or password', response.data)

if __name__ == '__main__':
    unittest.main()
