import sys
import os
import pytest
from App import app, get_seed_suffix, generate_password_logic, evaluate_password, is_in_leaked_database
from unittest.mock import patch
import json
import random
import hashlib

sys.path.append(r"C:\Users\user\Documents\PasswordPill\keynest\server")

MOCK_SYLLABLES_TWO = {
    "te": "тест",
    "pa": "пасс",
    "wo": "ворд"
}
MOCK_SYLLABLES_THREE = {
    "cod": "код",
    "saf": "сейф",
    "loc": "лок"
}
MOCK_YEARS_MEANING = {
    "23": "двадцать три",
    "24": "двадцать четыре",
    "25": "двадцать пять"
}

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def patch_app_globals():
    import App
    App.SYLLABLES_TWO = MOCK_SYLLABLES_TWO
    App.SYLLABLES_THREE = MOCK_SYLLABLES_THREE
    App.YEARS_MEANING = MOCK_YEARS_MEANING
    random.seed(42)

def test_home_endpoint(client):
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == "Welcome to Keynest API! Use /generate to create a password or /check to evaluate a password."

def test_generate_valid_request(client):
    response = client.post('/generate', json={
        'syllables': 2,
        'numbers': True,
        'symbols': True,
        'seed': 'привет'
    })
    data = response.get_json()
    assert 'password' in data
    assert 'associations' in data
    assert data['password'].startswith('pri-')
    assert len(data['associations']) == 5
    assert 'код: pri' in data['associations']

def test_generate_invalid_syllables(client):
    response = client.post('/generate', json={
        'syllables': "abc",
        'numbers': False,
        'symbols': False,
        'seed': ''
    })
    data = response.get_json()
    assert data['error'] == 'Invalid syllables value, must be an integer'

def test_generate_invalid_seed(client):
    response = client.post('/generate', json={
        'syllables': 2,
        'numbers': False,
        'symbols': False,
        'seed': '123'
    })
    data = response.get_json()
    assert data['password'].count('-') == 1 
    assert all('код:' not in assoc for assoc in data['associations'])

def test_check_valid_strong_password(client, requests_mock):
    sha1 = hashlib.sha1('TestPassword123!'.encode('utf-8')).hexdigest().upper()
    prefix = sha1[:5]  # 382CA
    requests_mock.get(f'https://api.pwnedpasswords.com/range/{prefix}', text='')
    
    response = client.post('/check', json={
        'password': 'TestPassword123!'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['strength'] == 'Надежный'
    assert 'лет' in data['time']
    assert data['suggestion'] is None

def test_check_compromised_password(client, requests_mock):
    sha1_prefix = '5BAA6'
    requests_mock.get(
        f'https://api.pwnedpasswords.com/range/{sha1_prefix}',
        text='1E4C9B93F3F0682250B6CF8331B7EE68FD8:5'
    )
    
    response = client.post('/check', json={'password': 'password'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['strength'] == 'Компрометирован'
    assert data['time'] == 'Мгновенно'
    assert 'утечек' in data['suggestion']


def test_check_empty_password(client):
    response = client.post('/check', json={
        'password': ''
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['strength'] == 'Компрометирован'
    assert data['time'] == 'Мгновенно'
    assert 'Этот пароль найден в базе утечек 7 раз(а).' in data['suggestion']

def test_get_seed_suffix():
    assert get_seed_suffix('Привет123!') == 'pri'
    assert get_seed_suffix('123') == ''
    assert get_seed_suffix('') == ''
    assert get_seed_suffix('ABC') == 'abc'

def test_generate_password_logic():
    password, associations = generate_password_logic(
        syllables=2,
        include_numbers=True,
        include_symbols=True,
        seed_suffix='abc'
    )
    assert password.startswith('abc-')
    assert len(associations) == 5
    assert 'код: abc' in associations

def test_evaluate_password_strong():
    result = evaluate_password('lol-ID-FRI-OWN-GO-UP1789%')
    assert result['strength'] == 'Надежный'
    assert result['time'] == '6751336164691997767508198162432 лет'
    assert result['suggestion'] is None

def test_evaluate_password_weak():
    result = evaluate_password('cuhsemphti')
    assert result['strength'] == 'Слабый'
    assert result['time'] == '23 минут'

def test_is_in_leaked_database(requests_mock):
    sha1_prefix = '5BAA6'
    requests_mock.get(
        'https://api.pwnedpasswords.com/range/5BAA6',
        text='1E4C9B93F3F0682250B6CF8331B7EE68FD8:5'
    )
    count = is_in_leaked_database('password')
    assert count == 5

    sha1 = hashlib.sha1('TestPassword123!'.encode('utf-8')).hexdigest().upper()
    prefix = sha1[:5]  # 382CA
    requests_mock.get(
        f'https://api.pwnedpasswords.com/range/{prefix}',
        text=''
    )
    count = is_in_leaked_database('TestPassword123!')
    assert count == 0