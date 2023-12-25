from datetime import timedelta, datetime, timezone
from unittest.mock import patch

from utils.password_utils import verify_password, get_password_hash
from utils.jwt import create_access_token, create_refresh_token, decode_token

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

class TestJWTUtils:
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
            
    
        