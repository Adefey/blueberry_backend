from pydantic import BaseModel


class AuthRequestModel(BaseModel):
    login: str = ""
    password: str = ""


class AuthResponseModel(BaseModel):
    login: str = ""
