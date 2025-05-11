from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os

API_ID = 21355756
API_HASH = "91e2d7d11800a359759128e9f8994b0c"

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    print("STRING_SESSION:", client.session.save())
