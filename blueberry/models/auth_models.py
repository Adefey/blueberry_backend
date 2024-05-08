from pydantic import BaseModel


class AuthRequestModel(BaseModel):
    login: str = ""
    password: str = ""
