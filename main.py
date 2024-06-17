import os
import asyncio
from dotenv import load_dotenv

from pyrogram import Client, filters, idle

from database.database import init_db
from database.service import check_user_exists
from handlers import handle_message

# инициализируем таблицы
check_user = check_user_exists


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
    await handle_message(client, message)


async def main():

    print("Инициализация базы данных...")
    await init_db()

    print("Запуск клиента...")
    async with app:
        print("Клиент запущен!")

        await idle()

        print("Остановка клиента...")
        await asyncio.sleep(1)
        print("Клиент остановлен!")

if __name__ == "__main__":
    app.run(main())
