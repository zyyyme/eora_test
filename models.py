from pydantic import BaseModel

from typing import Optional, List


class User(BaseModel):
    username: str
    password: str
    bots: List[int]


class UserRegister(User):
    username: str
    password: str
    bots: List[int] = []


class Bot(BaseModel):
    token: str
    name: str
    username: str
    bot_id: int