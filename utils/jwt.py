import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

from jose import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer


SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = os.environ.get("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRE_MINUTES", 10800)) #7 days


def create_access_token(username:str, expires_delta: timedelta = None):
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(tz=timezone.utc) + expires_delta
    payload = {
        "sub": username,
        "exp": expire
    }
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token() -> str:
    return str(uuid.uuid4())

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
TokenDependency = Annotated[str, Depends(oauth2_scheme)]