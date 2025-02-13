from pyrogram import Client, filters, idle
from pyrogram.errors import PeerIdInvalid, ChatAdminRequired, FloodWait
import asyncio

def get_peer_type_new(peer_id: int) -> str:
    peer_id_str = str(peer_id)
    if not peer_id_str.startswith('-'):
        return "user"
    elif peer_id_str.startswith("-100"):
        return "channel"
    else:
        return "чат"

# Переопределяем метод get_peer_type в модуле utils
from pyrogram import utils
utils.get_peer_type = get_peer_type_new

API_ID = 27796627
API_HASH = '6c1421d554df1927173c6f6871097beb'
SOURCE_CHANNEL_ID = -1002414449317
TARGET_CHANNEL_ID = -1002401059843

app = Client("my_account", api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.chat(SOURCE_CHANNEL_ID))
async def forward_messages(client, message):
    try:
        # Получаем информацию о исходном канале
        source_chat = await app.get_chat(SOURCE_CHANNEL_ID)
        
        # Создаем текст с ссылкой на источник
        if source_chat.username:
            # Публичный канал
            source_link = f"https://t.me/{source_chat.username}/{message.id}"
        else:
            # Приватный канал
            source_link = f"https://t.me/c/{str(source_chat.id)[4:]}/{message.id}"
        
        source_link_text = f"\n\nИсточник: [{source_chat.title}]({source_link})"
        
        # Проверяем тип сообщения и формируем текст
        if message.caption:
            new_caption = message.caption + source_link_text
            await message.copy(chat_id=TARGET_CHANNEL_ID, caption=new_caption)
        elif message.text:
            new_text = message.text + source_link_text
            await app.send_message(chat_id=TARGET_CHANNEL_ID, text=new_text)
        elif message.photo:
            await message.copy(chat_id=TARGET_CHANNEL_ID, caption=source_link_text)
        else:
            await message.copy(chat_id=TARGET_CHANNEL_ID)
        
        print(f"Сообщение {message.id} из канала {SOURCE_CHANNEL_ID} успешно скопировано в канал {TARGET_CHANNEL_ID}.")
    except PeerIdInvalid:
        print(f"Неверный Peer ID: {TARGET_CHANNEL_ID}. Проверьте правильность ID целевого канала.")
    except ChatAdminRequired:
        print(f"У вас нет прав администратора в целевом канале {TARGET_CHANNEL_ID}. Убедитесь, что у вас есть необходимые права.")
    except FloodWait as e:
        print(f"Необходимо ждать {e.x} секунд из-за ограничений на частоту запросов.")
        await asyncio.sleep(e.x)
    except Exception as e:
        print(f"Произошла ошибка: {e}")

async def main():
    await app.start()
    print("Бот запущен!")

    # Получение информации о целевом канале для инициализации хранилища
    try:
        target_chat = await app.get_chat(TARGET_CHANNEL_ID)
        print(f"Целевой канал '{target_chat.title}' успешно инициализирован.")
    except PeerIdInvalid:
        print(f"Неверный Peer ID: {TARGET_CHANNEL_ID}. Проверьте правильность ID целевого канала.")
        await app.stop()
        return
    except ChatAdminRequired:
        print(f"У вас нет доступа к целевому каналу {TARGET_CHANNEL_ID}. Убедитесь, что вы подписаны на канал и у вас есть необходимые права.")
        await app.stop()
        return
    except FloodWait as e:
        print(f"Необходимо ждать {e.x} секунд из-за ограничений на частоту запросов.")
        await asyncio.sleep(e.x)
    except Exception as e:
        print(f"Произошла ошибка при инициализации целевого канала: {e}")
        await app.stop()
        return

    await idle()

if __name__ == "__main__":
    app.run(main())
