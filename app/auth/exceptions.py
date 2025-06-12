from fastapi import HTTPException

class WrongCredentials(HTTPException):
    def __init__(self, detail: str = "Login or Password is incorrect") -> None:
        super().__init__(401, detail=detail)

class UserIsNotActive(HTTPException):
    def __init__(self, detail: str = "User is not active") -> None:
        super().__init__(status_code=403, detail=detail)

class TokenInvalid(HTTPException):
    def __init__(self, detail: str = "Token is invalid") -> None:
        super().__init__(status_code=401, detail=detail)
