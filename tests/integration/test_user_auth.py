import pytest

from datetime import timedelta
from fastapi import HTTPException

from app.models.user import User
from app.schemas.token import TokenType
from app.auth.jwt import create_token
from tests.conftest import create_fake_user


def test_hashed_password(db_session):

    # Test that user.hased_password returns the hashed password

    user_data = create_fake_user()
    User.register(db_session, user_data)
    user_row = db_session.query(User).filter_by(
        email=user_data['email'],
    ).first()
    assert user_row.hashed_password is not None
    assert user_row.hashed_password != user_data['password']

def test_verify_password(db_session):

    # Test that user.verify_password checks the password

    user_data = create_fake_user()
    User.register(db_session, user_data)
    user_row = db_session.query(User).filter_by(
        email=user_data['email'],
    ).first()
    assert user_row.verify_password(user_data['password'])

def test_register_with_short_password(db_session):

    # Test that user.register fails for a short password

    user_data = create_fake_user()
    user_data['password'] = 'pass1'
    with pytest.raises(ValueError, match='Password must be at least 6 characters long'):
        User.register(db_session, user_data)

def test_register_duplicate_user(db_session):

    # Test that user.register fails for a duplicate email or username

    user_data_1 = create_fake_user()
    User.register(db_session, user_data_1)

    user_data_2 = dict(user_data_1)
    user_data_2['email'] += 'abc'
    with pytest.raises(ValueError, match='Username or email already exists'):
        User.register(db_session, user_data_2)

    user_data_3 = dict(user_data_1)
    user_data_3['username'] += 'abc'
    with pytest.raises(ValueError, match='Username or email already exists'):
        User.register(db_session, user_data_3)

def test_authenticate(db_session):

    # Test successful authentication

    user_data = create_fake_user()
    User.register(db_session, user_data)
    result = User.authenticate(db_session, user_data['email'], user_data['password'])

    assert 'access_token' in result
    assert 'refresh_token' in result
    assert 'token_type' in result
    assert 'expires_at' in result
    assert 'user' in result

def test_authenticate_fail(db_session):

    # Test failed authentication

    user_data = create_fake_user()
    User.register(db_session, user_data)
    result = User.authenticate(db_session, user_data['email'], user_data['password'] + 'xxxx')

    assert result == None

def test_verify_token(db_session):

    # Test that token gets verified properly

    user_data = create_fake_user()
    User.register(db_session, user_data)
    auth_result = User.authenticate(db_session, user_data['email'], user_data['password'])
    assert auth_result is not None, 'Auth failed'
    access_token = auth_result['access_token']
    assert access_token is not None, 'access_token is None'
    assert User.verify_token(access_token) != None

def test_verify_token_fail_1(db_session):

    # Test that invalid token gets rejected

    user_data = create_fake_user()
    User.register(db_session, user_data)
    auth_result = User.authenticate(db_session, user_data['email'], user_data['password'])
    assert auth_result is not None, 'Auth failed'
    access_token = 'bad-access-token'
    assert User.verify_token(access_token) == None

def test_verify_token_fail_2(monkeypatch, db_session):

    # Test that invalid token gets rejected

    def fake_decode(*args, **kwargs):
        return {'no-sub': 'xyz'}

    monkeypatch.setattr('app.models.user.jwt.decode', fake_decode)

    user_data = create_fake_user()
    User.register(db_session, user_data)
    auth_result = User.authenticate(db_session, user_data['email'], user_data['password'])
    assert auth_result is not None, 'Auth failed'
    access_token = auth_result['access_token']
    assert access_token is not None, 'access_token is None'
    assert User.verify_token(access_token) == None

def test_verify_token_fail_3(monkeypatch, db_session):

    # Test that invalid token gets rejected

    def fake_decode(*args, **kwargs):
        return {'sub': 'not-a-uuid'}

    monkeypatch.setattr('app.models.user.jwt.decode', fake_decode)

    user_data = create_fake_user()
    User.register(db_session, user_data)
    auth_result = User.authenticate(db_session, user_data['email'], user_data['password'])
    assert auth_result is not None, 'Auth failed'
    access_token = auth_result['access_token']
    assert access_token is not None, 'access_token is None'
    assert User.verify_token(access_token) == None


def test_create_token_expires_delta(db_session):

    user_data = create_fake_user()
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    user_row = db_session.query(User).filter_by(
        email=user_data['email'],
    ).first()

    token = create_token(
        user_id=user_row.id,
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(seconds=1),
    )

    assert token is not None

def test_create_token_fail(monkeypatch, db_session):

    # Test that create_token raises HTTPException on failure

    def fake_encode(*args, **kwargs):
        raise ValueError('force_failure')

    monkeypatch.setattr('app.auth.jwt.jwt.encode', fake_encode)

    user_data = create_fake_user()
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    user_row = db_session.query(User).filter_by(
        email=user_data['email'],
    ).first()

    with pytest.raises(HTTPException, match='500: Could not create token: force_failure'):
        create_token(
            user_id=user_row.id,
            token_type=TokenType.ACCESS,
            expires_delta=timedelta(seconds=1),
        )
