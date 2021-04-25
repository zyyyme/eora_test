from bot import start_bot
from database import get_bots

bots = get_bots()

for bot in bots:
    start_bot(bot['token'])