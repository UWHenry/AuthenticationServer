from pydantic import BaseModel

    
class JWTToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    model_config = {"from_attributes": True}

class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []

class TokenCreate(BaseModel):
    access_token: str
    refresh_token: str
    user_id: int