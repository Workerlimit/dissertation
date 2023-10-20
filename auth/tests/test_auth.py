import concurrent.futures
import pytest
import requests
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    yield client

def create_user(username, password, client):
    response = client.post('/signup', json={"username": username, "password": password})
    return response

def login_user(username, password, client):
    response = client.post('/signin', json={"username": username, "password": password})
    return response

def test_user_registration_and_login(client):
    user_credentials = [
        ("user16", "password16"),
        ("user20", "password20"),
        ("user12", "password12"),
        ("user23", "password23"),
        ("user15", "password15"),
        ("user21", "password21"),
        ("user10", "password10"),
        ("user29", "password29"),
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        registration_responses = list(executor.map(create_user, *zip(*user_credentials), [client] * len(user_credentials)))

        login_responses = list(executor.map(login_user, *zip(*user_credentials), [client] * len(user_credentials)))

    for response in registration_responses:
        assert response.status_code == 201

    for response in login_responses:
        assert response.status_code == 200