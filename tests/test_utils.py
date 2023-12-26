from datetime import timedelta, datetime, timezone
from unittest.mock import patch

import pytest

from env_setup import db_setup, db_session, anyio_backend
from utils.password_utils import verify_password, get_password_hash
from utils.jwt import create_access_token, create_refresh_token, decode_token
from utils.crud import UserCRUD, TokenCRUD
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

class TestCRUD:    
    @pytest.mark.anyio
    async def test_create_user(self, db_setup, db_session):
        user = UserCreate(username="test", password="password", email="email")
        user = await UserCRUD.create_user(db_session, user)
        assert user.username == "test"
        assert verify_password("password", user.password_hash) == True
        assert user.email == "email"
    
    @pytest.mark.anyio
    async def test_get_user_by_username(self, db_setup, db_session):
        user = UserCreate(username="test", password="password", email="email")
        await UserCRUD.create_user(db_session, user)
        user = await UserCRUD.get_user_by_username(db_session, "test")
        assert user.username == "test"
        assert verify_password("password", user.password_hash) == True
        assert user.email == "email"    
    
    @pytest.mark.anyio
    async def test_get_user_by_id(self, db_setup, db_session):
        user = UserCreate(username="test", password="password", email="email")
        user = await UserCRUD.create_user(db_session, user)
        user = await UserCRUD.get_user_by_id(db_session, user.id)
        assert user.username == "test"
        assert verify_password("password", user.password_hash) == True
        assert user.email == "email"
    
    @pytest.mark.anyio
    async def test_delete_user_by_username(self, db_setup, db_session):
        user = UserCreate(username="test", password="password", email="email")
        user = await UserCRUD.create_user(db_session, user)
        delete_count = await UserCRUD.delete_user_by_username(db_session, "test")
        assert delete_count == 1
    
    @pytest.mark.anyio
    async def test_update_user(self, db_setup, db_session):
        update_info = UserUpdate(username="test2", password="password2", email="email2")
        user = UserCreate(username="test", password="password", email="email")
        user = await UserCRUD.create_user(db_session, user)
        user = await UserCRUD.update_user(db_session, user.id, update_info)
        assert user.username == "test2"
        assert verify_password("password2", user.password_hash) == True
        assert user.email == "email2"

    @pytest.mark.anyio
    async def test_create_token(self, db_setup, db_session):
        user = UserCreate(username="test", password="password", email="email")
        user = await UserCRUD.create_user(db_session, user)
        user_id = user.id
        token = TokenCreate(access_token="access token", refresh_token="refresh token", user_id=user_id)
        token = await TokenCRUD.create_token(db_session, token)
        assert token.access_token == "access token"
        assert token.refresh_token == "refresh token"
        assert token.status == True
        assert token.user_id == user_id
    
    @pytest.mark.anyio
    async def test_delete_expired_tokens(self, db_setup, db_session):
        user = UserCreate(username="test", password="password", email="email")
        user = await UserCRUD.create_user(db_session, user)
        token = TokenCreate(access_token="access token", refresh_token="refresh token", user_id=user.id)
        token = await TokenCRUD.create_token(db_session, token)
        delete_count = await TokenCRUD.delete_expired_tokens(db_session, timedelta(seconds=0))
        assert delete_count == 1