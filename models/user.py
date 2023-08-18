from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    id: Optional[int]
    email: str
    password: str
    name: str
    diet_type: str
    daily_budget: float


class UserEmailLogin(BaseModel):
    id: Optional[int]
    username: str
    password: str


class UserEmailSignUp(BaseModel):
    id: Optional[int]
    username: str
    email: str
    password: str
