from pydantic import BaseModel

from typing import Optional, List


class User(BaseModel):
    username: str
    password: str


class Bot(BaseModel):
    token: str
    name: str
    username: str
    bot_id: int