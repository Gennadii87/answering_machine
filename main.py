import os
import asyncio
from dotenv import load_dotenv

from pyrogram import Client, filters, idle

from database.database import init_db
from database.service import check_user_exists
from handlers import handle_message, monitor_triggers, message_print

# инициализируем таблицы
check_user = check_user_exists

me: object = None

load_dotenv()
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

# Параметры идентификации клиента
app = Client(
    "my_account",
    api_id=api_id,
    api_hash=api_hash,
    device_model="Asus X415",
    system_version="4.16.30-vxCUSTOM",
    app_version="1.0",
    lang_code="en",
)


@app.on_message(filters.private & filters.incoming)
async def on_message(client, message):
    await handle_message(client, message, me)
    await message_print(message, me)


async def get_me_id(client):
    """Получение объекта User(me)"""
    object_user = await client.get_me()
    return object_user


async def main():
    global me
    print("Инициализация базы данных... \nЗапуск клиента...")

    await asyncio.gather(init_db(), app.start())
    me = await get_me_id(app)
    asyncio.create_task(monitor_triggers(app, me))

    print(f"Клиент {app.device_model} запущен")

    await idle()

    print("Остановка клиента...")
    await asyncio.sleep(1)
    print("Клиент остановлен!")

if __name__ == "__main__":
    app.run(main())
