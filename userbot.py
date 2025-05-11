from telethon import TelegramClient, events
import re
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_NAME = 'userbot_espia'
GRUPO_A = int(os.getenv('SOURCE_CHAT_ID'))  # ID numérico del grupo origen
GRUPO_B = int(os.getenv('TARGET_CHAT_ID'))  # ID del grupo destino

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Diccionario para hilos (pregunta -> respuesta)
mensajes_reenviados = {}

# Función para generar el enlace
def get_message_link(chat_id, msg_id):
    if chat_id < 0:
        chat_id = abs(chat_id) - 10**12  # Remueve el "-100" inicial
    return f"https://t.me/c/{chat_id}/{msg_id}"

@client.on(events.NewMessage(chats=GRUPO_A, from_users='fun_message_scoring_bot'))
async def handler(event):
    message = event.message
    text = message.text or message.caption or ""
     # Genera el enlace
    enlace = get_message_link(message.chat_id, message.id)

    # Filtros con regex (más robusto que 'in')
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


async def main():
    await client.start()
    print("Monitoreando mensajes...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
