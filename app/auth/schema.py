from pydantic import BaseModel


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str ="Bearer"

class LoginSchema(BaseModel):
    login: str
    password: str
