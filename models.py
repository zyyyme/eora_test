from pydantic import BaseModel

from typing import Optional, List


class User(BaseModel):
    username: str
    password: str


class UserInDB(User):
    username: str
    password: str
    bots: List[int]

    def bots_limit(self):
        return len(self.bots) >= 5

    def has_bot(self, bot_id):
        return bot_id in self.bots





class Bot(BaseModel):
    token: str
    name: str
    username: str
    bot_id: int