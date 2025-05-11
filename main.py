from telethon import TelegramClient, events
import re
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
# ===== Configuración de Flask (para evitar que Render duerma el bot) =====
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot activo! Revisando mensajes en segundo plano."

def run_flask():
    app.run(host='0.0.0.0', port=8000)

# ===== Configuración del Bot =====
load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_NAME = os.getenv('STRING_SESSION')
GRUPO_A = int(os.getenv('SOURCE_CHAT_ID'))
GRUPO_B = int(os.getenv('TARGET_CHAT_ID'))


client = TelegramClient(StringSession(os.getenv('STRING_SESSION')), API_ID, API_HASH)
mensajes_reenviados = {}

def get_message_link(chat_id, msg_id):
    if chat_id < 0:
        chat_id = abs(chat_id) - 10**12
    return f"https://t.me/c/{chat_id}/{msg_id}"

@client.on(events.NewMessage(chats=GRUPO_A, from_users='fun_message_scoring_bot'))
async def handler(event):
    message = event.message
    text = message.text or message.caption or ""
    enlace = get_message_link(message.chat_id, message.id)

    if re.search(r'Choose the correct option below', text, re.DOTALL):
        mensaje_reenviado = await client.send_message(
            GRUPO_B,
            f"{text}\n\n🔗 {enlace}"
        )
        mensajes_reenviados[message.id] = mensaje_reenviado.id
        print(f"Pregunta reenviada: {message.id}")

    elif re.search(r'The correct answer was', text, re.DOTALL):
        if message.reply_to_msg_id and message.reply_to_msg_id in mensajes_reenviados:
            await client.send_message(
                GRUPO_B,
                f"{text}\n\n🔗 {enlace}",
                reply_to=mensajes_reenviados[message.reply_to_msg_id]
            )
            print(f"Respuesta reenviada en hilo: {message.reply_to_msg_id}")

async def run_telethon():
    await client.start()
    print("Bot de Telegram iniciado. Monitoreando mensajes...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    # Inicia Flask en un hilo separado
    Thread(target=run_flask).start()

    # Inicia el bot de Telegram
    import asyncio
    asyncio.run(run_telethon())
