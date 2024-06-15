import datetime
import os
from dotenv import load_dotenv
from pyrogram import Client, filters, idle
from pyrogram.errors import UserIsBlocked, UserDeactivated, UserDeactivatedBan, PeerIdInvalid
from dao.base import get_user, add_user, update_user_status
from database.database import init_db
from database.service import check_user_exists
import time
import asyncio

# инициализируем проверку таблицы, если нет, создаем
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
async def handle_message(client, message):
    trigger_phrase = "запустить для пользователя"
    user_id = message.from_user.id
    if not await get_user(user_id):
        await add_user(user_id, f"инициализация пользователя {user_id}")

    if not message.from_user.is_self:
        print(f"[Получено от {message.from_user.first_name} {message.from_user.last_name}]: {message.text}")
    else:
        print(f"[Вы]: {message.text}")

    if message.from_user.is_self and trigger_phrase:

        # Перезапуск воронки
        if trigger_phrase in message.text:
            try:
                target_user_id = int(message.text.split(trigger_phrase)[-1].strip())

                if not await get_user(target_user_id):
                    me = await app.get_me()
                    await app.send_message(me.id, f"пользователь {target_user_id} не найден.")

                await update_user_status(target_user_id, "alive",
                                         f"воронка для пользователя {target_user_id} обновлена")

                print(f"Статус пользователя {target_user_id} обновлен на 'alive'")
            except ValueError:
                print("Неверный формат идентификатора пользователя")

    await auto_responder(user_id)


async def auto_responder(user_id):
    """Функция автоответчика"""
    try:
        user = await get_user(user_id)
        user_status = user.status
        if str(user_status) == "alive":
            msg_1_sent_time = None
            msg_2_sent_time = None
            while True:

                if not await monitor_triggers(user_id):

                    user = await get_user(user_id)
                    user_status = user.status
                    if str(user_status) == "alive":
                        await asyncio.sleep(360)
                        print(datetime.datetime.now())
                        await app.send_message(user_id, "msg_1")
                        msg_1_sent_time = time.time()

                if not await monitor_triggers(user_id):

                    user = await get_user(user_id)
                    user_status = user.status

                if str(user_status) == "alive":
                    if msg_1_sent_time is not None:
                        current_time = time.time()
                        interval_since_msg_1 = current_time - msg_1_sent_time
                        if interval_since_msg_1 >= 2340:
                            print(datetime.datetime.now())
                            await app.send_message(user_id, "msg_2")
                            msg_2_sent_time = time.time()

                if not await monitor_triggers(user_id):

                    user = await get_user(user_id)
                    user_status = user.status
                    if str(user_status) == "alive":
                        if msg_2_sent_time is not None:
                            current_time = time.time()
                            interval_since_msg_2 = current_time - msg_2_sent_time
                            if interval_since_msg_2 >= (1 * 24 * 3600 + 2 * 3600):
                                print(datetime.datetime.now())
                                await app.send_message(user_id, "msg_3")

                if str(user_status) == "finished":
                    break

    except (UserIsBlocked, UserDeactivated, UserDeactivatedBan, PeerIdInvalid):
        await update_user_status(user_id, "dead", "заблокирован")


async def monitor_triggers(user_id: int):
    """Функция для мониторинга триггеров отмены"""
    cancel_triggers = ["прекрасно", "ожидать", "стоп"]
    message_count = 0
    async for message in app.get_chat_history(user_id, limit=3, offset_id=-1):
        await asyncio.sleep(2)
        me = await app.get_me()
        if message.text and message.outgoing:
            get_status = message.text.lower() in cancel_triggers
            if get_status:
                print(f"Обнаружено слово-триггер в чате пользователя {user_id}")
                await update_user_status(user_id, "finished", f"воронка для пользователя {user_id} завершена")
                await app.send_message(me.id, f"последовательность сообщений для пользователя {user_id} отменена.")
                return True

            message_count += 1
            if message_count >= 1:
                await asyncio.sleep(1)

        return False


async def main():
    print("Инициализация базы данных...")
    await init_db()
    print("Запуск клиента...")
    await app.start()
    print("Клиент запущен!")

    await idle()

    print("Остановка клиента...")
    await asyncio.sleep(1)
    print("Клиент остановлен!")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
