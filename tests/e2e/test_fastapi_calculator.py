import logging

from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import patch
from uuid import uuid4

from app.main import app
from app.main import lifespan

client = TestClient(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

def _parse_datetime(d: str) -> datetime:

    # Helper function to parse datetime strings from API responses

    if d.endswith('Z'):
        d = d.replace('Z', '+00:00')
    return datetime.fromisoformat(d)

def register_and_login(user_data: dict) -> dict:

    # Registers a new user and logs in

    reg_response = client.post('/auth/register', json=user_data)
    assert reg_response.status_code == 201, f'User registration failed: {reg_response.text}'

    login_payload = {
        'username': user_data['username'],
        'password': user_data['password'],
    }
    login_response = client.post('/auth/login', json=login_payload)
    assert login_response.status_code == 200, f'Login failed: {login_response.txt}'
    return login_response.json()

def test_health_endpoint():

    # Test endpoint health

    response = client.get('/health')
    assert response.status_code == 200, f'Expected status code 200, got {response.status_code}'
    assert response.json() == {'status': 'ok'}

def test_user_registration():

    # Test User registration

    payload = {
        'first_name': 'Alice',
        'last_name': 'Smith',
        'email': 'alice.smith@example.com',
        'username': 'alicesmith',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!',
    }
    response = client.post('/auth/register', json=payload)
    logger.info(response.text)
    assert response.status_code == 201
    data = response.json()
    for key in ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_verified']:
        assert key in data, f"Field '{key}' missing in registration response."

    assert data['username'] == payload['username']
    assert data['email'] == payload['email']
    assert data['first_name'] == payload['first_name']
    assert data['last_name'] == payload['last_name']
    assert data['is_active'] is True
    assert data['is_verified'] is False

def test_user_login():

    # Test login

    test_user = {
        'first_name': 'Bob',
        'last_name': 'Jones',
        'email': 'bob.jones@example.com',
        'username': 'bobjones',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!'
    }

    reg_response = client.post('/auth/register', json=test_user)
    assert reg_response.status_code == 201

    login_payload = {
        'username': test_user['username'],
        'password': test_user['password'],
    }
    login_response = client.post('/auth/login', json=login_payload)
    assert login_response.status_code == 200

    login_data = login_response.json()
    required_fields = {
        'access_token': str,
        'refresh_token': str,
        'token_type': str,
        'expires_at': str,  # ISO datetime string
        'user_id': str,     # UUID string
        'username': str,
        'email': str,
        'first_name': str,
        'last_name': str,
        'is_active': bool,
        'is_verified': bool,
    }

    for field, expected_type in required_fields.items():
        assert field in login_data, f'Missing field: {field}'
        assert isinstance(login_data[field], expected_type)

    assert login_data['token_type'].lower() == 'bearer'
    assert len(login_data['access_token']) > 0
    assert len(login_data['refresh_token']) > 0
    assert login_data['username'] == test_user['username']
    assert login_data['email'] == test_user['email']
    assert login_data['first_name'] == test_user['first_name']
    assert login_data['last_name'] == test_user['last_name']
    assert login_data['is_active'] is True

    expires_at = _parse_datetime(login_data['expires_at'])
    current_time = datetime.now(timezone.utc)
    assert expires_at.tzinfo is not None
    assert current_time.tzinfo is not None
    assert expires_at > current_time

##########################################
# Calculations
##########################################

def test_create_calculation_addition():

    # Test addition calculation

     user_data = {
        'first_name': 'Calc',
        'last_name': 'Adder',
        'email': f'calc.adder{uuid4()}@example.com',
        'username': f'calc_adder_{uuid4()}',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!'
    }
     token_data = register_and_login(user_data)
     access_token = token_data['access_token']
     headers = {'Authorization': f'Bearer {access_token}'}
     payload = {
         'type': 'addition',
         'inputs': [9, 3, -1.5],
         'user_id': str(uuid4()),
     }
     response = client.post('/calculations', json=payload, headers=headers)
     assert response.status_code == 201
     assert 'result' in response.json()
     actual = response.json()['result']
     expected = 10.5
     assert actual == expected

def test_create_calculation_subtraction():

    # Test subtraction calculation

     user_data = {
        'first_name': 'Calc',
        'last_name': 'Adder',
        'email': f'calc.adder{uuid4()}@example.com',
        'username': f'calc_adder_{uuid4()}',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!'
    }
     token_data = register_and_login(user_data)
     access_token = token_data['access_token']
     headers = {'Authorization': f'Bearer {access_token}'}
     payload = {
         'type': 'subtraction',
         'inputs': [9, 3, -1.5],
         'user_id': str(uuid4()),
     }
     response = client.post('/calculations', json=payload, headers=headers)
     assert response.status_code == 201
     assert 'result' in response.json()
     actual = response.json()['result']
     expected = 7.5
     assert actual == expected

def test_create_calculation_multiplication():

    # Test multiplication calculation

     user_data = {
        'first_name': 'Calc',
        'last_name': 'Adder',
        'email': f'calc.adder{uuid4()}@example.com',
        'username': f'calc_adder_{uuid4()}',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!'
    }
     token_data = register_and_login(user_data)
     access_token = token_data['access_token']
     headers = {'Authorization': f'Bearer {access_token}'}
     payload = {
         'type': 'multiplication',
         'inputs': [9, 3, -1.5],
         'user_id': str(uuid4()),
     }
     response = client.post('/calculations', json=payload, headers=headers)
     assert response.status_code == 201
     assert 'result' in response.json()
     actual = response.json()['result']
     expected = -40.5
     assert actual == expected

def test_create_calculation_division():

    # Test division calculation

     user_data = {
        'first_name': 'Calc',
        'last_name': 'Adder',
        'email': f'calc.adder{uuid4()}@example.com',
        'username': f'calc_adder_{uuid4()}',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!'
    }
     token_data = register_and_login(user_data)
     access_token = token_data['access_token']
     headers = {'Authorization': f'Bearer {access_token}'}
     payload = {
         'type': 'division',
         'inputs': [9, 3, -1.5],
         'user_id': str(uuid4()),
     }
     response = client.post('/calculations', json=payload, headers=headers)
     assert response.status_code == 201
     assert 'result' in response.json()
     actual = response.json()['result']
     expected = -2
     assert actual == expected

def test_create_calculation_value_error():

    # Test for unexpected error in calculation


    user_data = {
        'first_name': 'Calc',
        'last_name': 'Adder',
        'email': f'calc.adder{uuid4()}@example.com',
        'username': f'calc_adder_{uuid4()}',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!'
    }
    token_data = register_and_login(user_data)
    access_token = token_data['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    payload = {
        'type': 'addition',
        'inputs': [9, 3, -1.5],
        'user_id': str(uuid4()),
    }

    with patch('app.main.Calculation.create', side_effect=ValueError('fake_error')):

        response = client.post('/calculations', json=payload, headers=headers)
        assert response.status_code == 400
        result = response.json()
        assert 'detail' in result
        assert result['detail'] == 'fake_error'

def test_list_get_update_delete_calculation():

    # Test calculation delete

    user_data = {
        'first_name': 'Calc',
        'last_name': 'CRUD',
        'email': f'calc.crud{uuid4()}@example.com',
        'username': f'calc_crud_{uuid4()}',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!',
    }
    token_data = register_and_login(user_data)
    access_token = token_data['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    payload = {
        'type': 'multiplication',
        'inputs': [4, 5],
        'user_id': 'ignored',
    }
    create_response = client.post('/calculations', json=payload, headers=headers)
    assert create_response.status_code == 201
    calc = create_response.json()
    calc_id = calc['id']

    # List calculations
    list_response = client.get('/calculations', headers=headers)
    assert list_response.status_code == 200
    calc_list = list_response.json()
    assert any(c['id'] == calc_id for c in calc_list), 'Created calculation not found'

    # Get calculation by ID
    get_response = client.get(f'/calculations/{calc_id}', headers=headers)
    assert get_response.status_code == 200
    get_calc = get_response.json()
    assert get_calc['id'] == calc_id, 'Mismatch in calculation id'

    # Update calculation: change inputs
    update_payload = {'inputs': [2, 8]}
    update_response = client.put(f'/calculations/{calc_id}', json=update_payload, headers=headers)
    assert update_response.status_code == 200
    update_calc = update_response.json()
    expected = 16
    assert update_calc['result'] == expected

    # Delete calculation
    delete_response = client.delete(f'/calculations/{calc_id}', headers=headers)
    assert delete_response.status_code == 204

    # Verify delete
    get_response_after_delete = client.get(f'/calculations/{calc_id}', headers=headers)
    assert get_response_after_delete.status_code == 404

def test_lifespan():

    # Test lifespan function

    with patch('app.main.init_db') as mock_init:
        with TestClient(app) as client:
            # Trigger lifespan by making any request
            client.get("/health")

        mock_init.assert_called_once()

def test_fastapi_register_short_password():

    # Test short password is rejected

    payload = {
        'first_name': 'Alice',
        'last_name': 'Smith',
        'email': 'alice.smith@example.com',
        'username': 'alicesmith',
        'password': 'a1A!',
        'confirm_password': 'a1A!',
    }
    with patch('app.main.User.register', side_effect=ValueError('fake_error')):
        response = client.post('/auth/register', json=payload)
        assert response.status_code == 422

def test_fastapi_login_wrong_password():

    # Test wrong password causes failed login

    user_data = {
        'first_name': 'Calc',
        'last_name': 'Adder',
        'email': f'calc.adder{uuid4()}@example.com',
        'username': f'calc_adder_{uuid4()}',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!'
    }
    reg_response = client.post('/auth/register', json=user_data)
    assert reg_response.status_code == 201, f'User registration failed: {reg_response.text}'

    login_payload = {
        'username': user_data['username'],
        'password': user_data['password'] + 'xxx',
    }
    login_response = client.post('/auth/login', json=login_payload)
    assert login_response.status_code == 401

def test_login_form():

    # Test correct password with login_form

    user_data = {
        'first_name': 'Calc',
        'last_name': 'Adder',
        'email': f'calc.adder{uuid4()}@example.com',
        'username': f'calc_adder_{uuid4()}',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!'
    }
    reg_response = client.post('/auth/register', json=user_data)
    assert reg_response.status_code == 201, f'User registration failed: {reg_response.text}'

    response = client.post('/auth/token', data={
        'username': user_data['username'],
        'password': user_data['password'],
    })
    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert 'token_type' in response.json() and response.json()['token_type'] == 'bearer'

def test_login_form_no_match():

    # Test login_form for failure

    with patch('app.main.User.authenticate', return_value=None):
        response = client.post('/auth/token', data={'username': 'abcdefg', 'password': 'securePass123!'})
        assert response.status_code == 401

def test_get_calculation_value_error():

    # Test get_calculation with ValueError

    user_data = {
        'first_name': 'Calc',
        'last_name': 'CRUD',
        'email': f'calc.crud{uuid4()}@example.com',
        'username': f'calc_crud_{uuid4()}',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!',
    }
    token_data = register_and_login(user_data)
    access_token = token_data['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    create_response = client.get('/calculations/not-a-uid', headers=headers)
    assert create_response.status_code == 400
    calc = create_response.json()['detail'] == 'Invalid calculation id format.'

def test_update_calculation_value_error():

    # Test update_calculation with ValueError

    user_data = {
        'first_name': 'Calc',
        'last_name': 'CRUD',
        'email': f'calc.crud{uuid4()}@example.com',
        'username': f'calc_crud_{uuid4()}',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!',
    }
    token_data = register_and_login(user_data)
    access_token = token_data['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    # Update calculation: change inputs
    update_payload = {'inputs': [2, 8]}
    update_response = client.put(f'/calculations/not-a-uuid', json=update_payload, headers=headers)
    assert update_response.status_code == 400
    assert update_response.json()['detail'] == 'Invalid calculation id format.'

def test_update_calculation_not_found():

    # Test update_calculation where calc id is not found

    user_data = {
        'first_name': 'Calc',
        'last_name': 'CRUD',
        'email': f'calc.crud{uuid4()}@example.com',
        'username': f'calc_crud_{uuid4()}',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!',
    }
    token_data = register_and_login(user_data)
    access_token = token_data['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    # Update calculation: change inputs
    update_payload = {'inputs': [2, 8]}
    update_response = client.put(f'/calculations/{uuid4()}', json=update_payload, headers=headers)
    assert update_response.status_code == 404
    assert update_response.json()['detail'] == 'Calculation not found.'

def test_delete_calculation_value_error():

    # Test delete_calculation with ValueError

    user_data = {
        'first_name': 'Calc',
        'last_name': 'CRUD',
        'email': f'calc.crud{uuid4()}@example.com',
        'username': f'calc_crud_{uuid4()}',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!',
    }
    token_data = register_and_login(user_data)
    access_token = token_data['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    # Delete calculation
    update_response = client.delete(f'/calculations/not-a-uuid', headers=headers)
    assert update_response.status_code == 400
    assert update_response.json()['detail'] == 'Invalid calculation id format.'

def test_delete_calculation_not_found():

    # Test delete_calculation where calc id is not found

    user_data = {
        'first_name': 'Calc',
        'last_name': 'CRUD',
        'email': f'calc.crud{uuid4()}@example.com',
        'username': f'calc_crud_{uuid4()}',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!',
    }
    token_data = register_and_login(user_data)
    access_token = token_data['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    # Delete calculation
    delete_response = client.delete(f'/calculations/{uuid4()}', headers=headers)
    assert delete_response.status_code == 404
    assert delete_response.json()['detail'] == 'Calculation not found.'
