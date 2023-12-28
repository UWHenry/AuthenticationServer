from pydantic import BaseModel
from utils.jwt import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

    
class JWTToken(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    model_config = {"from_attributes": True}
    
class RefreshToken(BaseModel):
    refresh_token: str
    expires_in: int = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    model_config = {"from_attributes": True}

class TokenCreate(BaseModel):
    token: str
    user_id: int

class RefreshEndpointInput(BaseModel):
    refresh_token: str