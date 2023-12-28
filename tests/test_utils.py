from datetime import timedelta, datetime, timezone
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from env_setup import db_setup, db_session, anyio_backend
from utils.password_utils import verify_password, get_password_hash
from utils.jwt import create_access_token, create_refresh_token, decode_token, get_jwt_username
from utils.crud import UserCRUD, TokenCRUD
import utils.crud
from schemas.user_schemas import UserCreate, UserUpdate
from schemas.token_schemas import TokenCreate



class TestPasswordUtils:
    def test_password_hash(self):
        password = "test"
        password_hash = get_password_hash(password)
        assert password != password_hash
        
    def test_password_verification(self):
        password = "test"
        password_hash = get_password_hash(password)
        assert verify_password(password, password_hash) == True
        
    def test_password_verification_2(self):
        password = "test"
        password_hash = get_password_hash(password)
        invalid_password = "test_2"
        assert verify_password(invalid_password, password_hash) == False

class TestJWT:
    def test_create_access_token(self):
        access_token = create_access_token("test", timedelta(seconds=10))
        assert access_token != None
    
    def test_create_refresh_token(self):
        refresh_token = create_refresh_token()
        assert refresh_token != None
    
    def test_decode_access_token(self):
        with patch("utils.jwt.datetime") as mock_datetime:
            now = datetime.now(tz=timezone.utc)
            mock_datetime.now.return_value = now
            access_token = create_access_token("test", timedelta(seconds=10))
            payload = decode_token(access_token)
            expected_expire_timestamp = (now + timedelta(seconds=10)).timestamp()
            assert payload["sub"] == "test"
            assert abs(expected_expire_timestamp - payload["exp"]) < 1
    
    def test_get_jwt_username(self):
        access_token = create_access_token("test", timedelta(seconds=10))
        username = get_jwt_username(access_token)
        assert username == "test"
    
    def test_get_jwt_username_invalid_jwt(self):
        with pytest.raises(HTTPException) as http_401:
            get_jwt_username("invalid_token")
        assert http_401.value.status_code == 401

class TestCRUD:    
    @pytest.mark.anyio
    async def test_create_user(self, db_setup, db_session):
        user = UserCreate(username="test", password="password", email="email@gmail.com")
        user = await UserCRUD.create_user(db_session, user)
        assert user.username == "test"
        assert verify_password("password", user.password_hash) == True
        assert user.email == "email@gmail.com"
    
    @pytest.mark.anyio
    async def test_get_user_by_username(self, db_setup, db_session):
        user = UserCreate(username="test", password="password", email="email@gmail.com")
        await UserCRUD.create_user(db_session, user)
        user = await UserCRUD.get_user_by_username(db_session, "test")
        assert user.username == "test"
        assert verify_password("password", user.password_hash) == True
        assert user.email == "email@gmail.com"    
    
    @pytest.mark.anyio
    async def test_get_user_by_id(self, db_setup, db_session):
        user = UserCreate(username="test", password="password", email="email@gmail.com")
        user = await UserCRUD.create_user(db_session, user)
        user = await UserCRUD.get_user_by_id(db_session, user.id)
        assert user.username == "test"
        assert verify_password("password", user.password_hash) == True
        assert user.email == "email@gmail.com"
    
    @pytest.mark.anyio
    async def test_delete_user_by_username(self, db_setup, db_session):
        user = UserCreate(username="test", password="password", email="email@gmail.com")
        user = await UserCRUD.create_user(db_session, user)
        delete_count = await UserCRUD.delete_user_by_username(db_session, "test")
        assert delete_count == 1
    
    @pytest.mark.anyio
    async def test_update_user(self, db_setup, db_session):
        update_info = UserUpdate(username="test2", password="password2", email="email2@gmail.com")
        user = UserCreate(username="test", password="password", email="email@gmail.com")
        user = await UserCRUD.create_user(db_session, user)
        user = await UserCRUD.update_user(db_session, user.id, update_info)
        assert user.username == "test2"
        assert verify_password("password2", user.password_hash) == True
        assert user.email == "email2@gmail.com"

    @pytest.mark.anyio
    async def test_create_access_token(self, db_setup, db_session):
        user = UserCreate(username="test", password="password", email="email@gmail.com")
        user = await UserCRUD.create_user(db_session, user)
        user_id = user.id
        token = TokenCreate(token="access token", user_id=user_id)
        token = await TokenCRUD.create_access_token(db_session, token)
        assert token.access_token == "access token"
        assert token.user_id == user_id
    
    @pytest.mark.anyio
    async def test_create_refresh_token(self, db_setup, db_session):
        user = UserCreate(username="test", password="password", email="email@gmail.com")
        user = await UserCRUD.create_user(db_session, user)
        user_id = user.id
        token = TokenCreate(token="refresh token", user_id=user_id)
        token = await TokenCRUD.create_refresh_token(db_session, token)
        assert token.refresh_token == "refresh token"
        assert token.user_id == user_id
    
    @pytest.mark.anyio
    async def test_create_refresh_token_duplicate_userid(self, db_setup, db_session):
        user = UserCreate(username="test", password="password", email="email@gmail.com")
        user = await UserCRUD.create_user(db_session, user)
        user_id = user.id
        token = TokenCreate(token="refresh token", user_id=user_id)
        await TokenCRUD.create_refresh_token(db_session, token)
        with pytest.raises(IntegrityError) as duplicate_userid:
            await TokenCRUD.create_refresh_token(db_session, token)
        assert duplicate_userid.typename == "IntegrityError"
        
    @pytest.mark.anyio
    async def test_get_refresh_token_by_userid(self, db_setup, db_session):
        user = UserCreate(username="test", password="password", email="email@gmail.com")
        user = await UserCRUD.create_user(db_session, user)
        user_id = user.id
        token = TokenCreate(token="refresh token", user_id=user_id)
        await TokenCRUD.create_refresh_token(db_session, token)
        token = await TokenCRUD.get_refresh_token_by_userid(db_session, user_id)
        assert token.refresh_token == "refresh token"
        assert token.user_id == user_id
    
    @pytest.mark.anyio
    async def test_update_refresh_token(self, db_setup, db_session):
        user = UserCreate(username="test", password="password", email="email@gmail.com")
        user = await UserCRUD.create_user(db_session, user)
        user_id = user.id
        token = TokenCreate(token="refresh token", user_id=user_id)
        await TokenCRUD.create_refresh_token(db_session, token)
        token = TokenCreate(token="refresh token 2", user_id=user_id)
        token = await TokenCRUD.update_refresh_token(db_session, token)
        assert token.refresh_token == "refresh token 2"
        assert token.user_id == user_id
    
    @pytest.fixture
    def override_token_expiration(self):
        original_access_expire_value = utils.crud.ACCESS_TOKEN_EXPIRE_MINUTES
        original_refresh_expire_value = utils.crud.REFRESH_TOKEN_EXPIRE_DAYS
        utils.crud.ACCESS_TOKEN_EXPIRE_MINUTES = 0
        utils.crud.REFRESH_TOKEN_EXPIRE_DAYS = 0
        yield
        utils.crud.ACCESS_TOKEN_EXPIRE_MINUTES = original_access_expire_value
        utils.crud.REFRESH_TOKEN_EXPIRE_DAYS = original_refresh_expire_value

    @pytest.mark.anyio
    async def test_delete_expired_access_tokens(self, db_setup, db_session, override_token_expiration):
        user = UserCreate(username="test", password="password", email="email@gmail.com")
        user = await UserCRUD.create_user(db_session, user)
        token = TokenCreate(token="access token",user_id=user.id)
        token = await TokenCRUD.create_access_token(db_session, token)
        delete_count = await TokenCRUD.delete_expired_access_tokens(db_session)
        assert delete_count == 1
    
    @pytest.mark.anyio
    async def test_delete_expired_refresh_tokens(self, db_setup, db_session, override_token_expiration):
        user = UserCreate(username="test", password="password", email="email@gmail.com")
        user = await UserCRUD.create_user(db_session, user)
        token = TokenCreate(token="refresh token",user_id=user.id)
        token = await TokenCRUD.create_refresh_token(db_session, token)
        delete_count = await TokenCRUD.delete_expired_refresh_tokens(db_session)
        assert delete_count == 1