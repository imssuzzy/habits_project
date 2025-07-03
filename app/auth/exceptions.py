from fastapi import HTTPException


class WrongCredentials(HTTPException):
    def __init__(self, detail: str = "Login or Password is incorrect"):
        super().__init__(status_code=401, detail=detail)


class ProfileIsNotActive(HTTPException):
    def __init__(self, detail: str = "Profile is not active"):
        super().__init__(status_code=403, detail=detail)


class TokenInvalid(HTTPException):
    def __init__(self, detail: str = "Token is invalid"):
        super().__init__(status_code=401, detail=detail)
