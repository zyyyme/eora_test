from bot import start_bot
from database import get_bots_tokens

bots_tokens = get_bots_tokens()

for token in bots_tokens:
    start_bot(token)