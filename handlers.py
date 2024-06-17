import datetime
import time
import asyncio
from configparser import ConfigParser
from pyrogram.errors import UserIsBlocked, UserDeactivated, UserDeactivatedBan, PeerIdInvalid
from dao.base import get_user, add_user, update_user_status

config = ConfigParser()

config.read('message_config.ini', encoding='utf-8')

msg_1 = config.get('pyrogram', 'msg_1')
msg_2 = config.get('pyrogram', 'msg_2')
msg_3 = config.get('pyrogram', 'msg_3')

# Хранение активных задач
active_tasks = {}


async def handle_message(client, message):
    """Обработчик сообщений"""
    trigger_phrase = "запустить для пользователя"
    user_id = message.from_user.id
    if not await get_user(user_id):
        await add_user(user_id, f"инициализация пользователя {user_id}")

    if not message.from_user.is_self:
        print(f"[Получено от {message.from_user.first_name} {message.from_user.last_name}]: {message.text}")
    else:
        print(f"[Вы]: {message.text}")

    if message.from_user.is_self and trigger_phrase in message.text:

        # Перезапуск воронки
        try:
            target_user_id = int(message.text.split(trigger_phrase)[-1].strip())

            if not await get_user(target_user_id):
                me = await client.get_me()
                await client.send_message(me.id, f"пользователь {target_user_id} не найден.")

            await update_user_status(target_user_id, "alive",
                                     f"воронка для пользователя {target_user_id} обновлена")

            print(f"Статус пользователя {target_user_id} обновлен на 'alive'")
        except ValueError:
            print("Неверный формат идентификатора пользователя")

    if user_id not in active_tasks:
        task = asyncio.create_task(auto_responder(client, user_id))
        active_tasks[user_id] = task
        print(f"задача {active_tasks}")


async def auto_responder(client, user_id: int):
    """Функция автоответчика"""
    try:
        user = await get_user(user_id)
        user_status = user.status
        if user_status == "alive":
            msg_1_sent_time = None
            msg_2_sent_time = None
            while True:

                if not await monitor_triggers(client, user_id):

                    user = await get_user(user_id)
                    user_status = user.status

                    if user_status == "alive":
                        await asyncio.sleep(360)
                        await client.send_message(user_id, msg_1)
                        msg_1_sent_time = time.time()

                        print(f"время {datetime.datetime.now()} - {msg_1}")

                if not await monitor_triggers(client, user_id):

                    user = await get_user(user_id)
                    user_status = user.status

                    if user_status == "alive":
                        if msg_1_sent_time is not None:
                            current_time = time.time()
                            interval_since_msg_1 = current_time - msg_1_sent_time
                            time_slip_msg2 = interval_since_msg_1 + 2340

                            await asyncio.sleep(time_slip_msg2)
                            await client.send_message(user_id, msg_2)
                            msg_2_sent_time = time.time()

                            print(f"время {datetime.datetime.now()} - {msg_2}")

                if not await monitor_triggers(client, user_id):

                    user = await get_user(user_id)
                    user_status = user.status

                    if user_status == "alive":
                        if msg_2_sent_time is not None:
                            current_time = time.time()
                            interval_since_msg_2 = current_time - msg_2_sent_time
                            time_slip_msg3 = interval_since_msg_2 + (1 * 24 * 3600 + 2 * 3600)

                            await asyncio.sleep(time_slip_msg3)
                            await client.send_message(user_id, msg_3)

                            print(f"время {datetime.datetime.now()} - {msg_3}")

                del active_tasks[user_id]
                if not active_tasks:
                    break

                await asyncio.sleep(1)
                if user_status == "finished":
                    break

    except (UserIsBlocked, UserDeactivated, UserDeactivatedBan, PeerIdInvalid):
        await update_user_status(user_id, "dead", "заблокирован")


async def monitor_triggers(client, user_id: int):
    """Функция для мониторинга триггеров отмены"""
    cancel_triggers = ["прекрасно", "ожидать", "стоп"]
    message_count = 0
    async for message in client.get_chat_history(user_id, limit=3, offset_id=-1):
        await asyncio.sleep(2)
        me = await client.get_me()

        # if message.text and message.outgoing:
        if message.text:
            get_status = message.text.lower() in cancel_triggers
            if get_status:
                print(f"Обнаружено слово-триггер в чате пользователя {user_id}")
                await update_user_status(user_id, "finished", f"воронка для пользователя {user_id} завершена")
                await client.send_message(me.id, f"последовательность сообщений для пользователя {user_id} отменена.")
                return True

            message_count += 1
            if message_count >= 1:
                await asyncio.sleep(1)

        return False
