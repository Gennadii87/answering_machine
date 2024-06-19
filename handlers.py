import datetime
import time
import asyncio
from configparser import ConfigParser

from pyrogram.errors import UserIsBlocked, UserDeactivated, UserDeactivatedBan, PeerIdInvalid
from dao.base import get_user, add_user, update_user_status, get_all_users


config = ConfigParser()

config.read('message_config.ini', encoding='utf-8')

msg_1 = config.get('pyrogram', 'msg_1')
msg_2 = config.get('pyrogram', 'msg_2')
msg_3 = config.get('pyrogram', 'msg_3')

# Хранение активных задач
active_tasks = {}


async def message_print(message, me):
    if not message.from_user.is_self:
        print(f"[Получено от {message.from_user.first_name} {message.from_user.last_name}]: {message.text}")
    else:
        print(f"[Вы - {me.username}]:  {message.text}")


async def handle_message(client, message, me):

    """Обработчик сообщений"""

    trigger_phrase = "Запустить для пользователя"
    user_id = message.from_user.id
    user = await get_user(user_id)

    if not user:
        await add_user(user_id, f"инициализация пользователя {user_id}")
        status = "alive"
    else:
        status = user.status

    if message.from_user.is_self and trigger_phrase in message.text:

        # Перезапуск воронки и очистка диалога
        try:
            target_user_id = int(message.text.split(trigger_phrase)[-1].strip())

            if not await get_user(target_user_id):
                await client.send_message(me.id, f"Пользователь {target_user_id} не найден.")

            await update_user_status(target_user_id, "alive",
                                     f"воронка для пользователя {target_user_id} обновлена")

            if target_user_id in active_tasks:
                active_tasks[target_user_id].cancel()
                del active_tasks[target_user_id]

            message_ids = []

            async for msg in client.get_chat_history(target_user_id):
                message_ids.append(msg.id)

            if message_ids:
                await client.delete_messages(target_user_id, message_ids)
                print(f"Диалог с пользователем {target_user_id} очищен.")

            print(f"Статус пользователя {target_user_id} обновлен на 'alive'")
        except ValueError:
            print("Неверный формат идентификатора пользователя")

    if user_id not in active_tasks and not message.from_user.is_self and status == 'alive':
        task = asyncio.create_task(auto_responder(client, user_id, status, me))
        active_tasks[user_id] = task
        print(f"Создана задача {active_tasks}")

    elif user_id in active_tasks:
        print(f"Воронка для {user_id} статус {status}")


async def auto_responder(client, user_id: int, status: str, me):

    """Функция автоответчика"""

    try:
        if status == "alive":
            while True:
                await asyncio.sleep(360)
                if not await monitor_triggers(client, me):

                    await client.send_message(user_id, msg_1)
                    msg_1_sent_time = time.time()
                    print(f"Дата {datetime.datetime.now()} - {msg_1}")

                else:
                    if user_id in active_tasks:
                        active_tasks[user_id].cancel()
                    break

                interval_since_msg_1 = time.time() - msg_1_sent_time
                time_slip_msg2 = interval_since_msg_1 + 2340
                await asyncio.sleep(time_slip_msg2)

                if not await monitor_triggers(client, me):
                    msg_2_sent_time = None
                    if msg_1_sent_time is not None:

                        await client.send_message(user_id, msg_2)
                        msg_2_sent_time = time.time()
                        print(f"Дата {datetime.datetime.now()} - {msg_2}")

                else:
                    if user_id in active_tasks:
                        del active_tasks[user_id]
                    break

                interval_since_msg_2 = time.time() - msg_2_sent_time
                time_slip_msg3 = interval_since_msg_2 + (1 * 24 * 3600 + 2 * 3600)
                await asyncio.sleep(time_slip_msg3)

                if not await monitor_triggers(client, me):

                    if msg_2_sent_time is not None:
                        await client.send_message(user_id, msg_3)
                        print(f"Дата {datetime.datetime.now()} - {msg_3}")

                else:
                    if user_id in active_tasks:
                        del active_tasks[user_id]
                    break

    except (UserIsBlocked, UserDeactivated, UserDeactivatedBan, PeerIdInvalid):
        await update_user_status(user_id, "dead", "заблокирован")


async def monitor_triggers(client, me):

    """Функция для мониторинга триггеров отмены"""

    users = await get_all_users()
    message_count = 0

    for user in users:
        user_id = user.id
        user_status = user.status

        if user_status == "alive":

            async for message in client.get_chat_history(user_id, limit=10, offset_id=-1):
                cancel_triggers = ["прекрасно", "ожидать", "стоп"]

                if message.text and message.outgoing and any(trigger in message.text for trigger in cancel_triggers):
                    print(f"Обнаружено слово-триггер в чате пользователя {user_id}")

                    await update_user_status(
                        user_id, "finished", f"воронка для пользователя {user_id} завершена")
                    await client.send_message(
                        me.id, f"Последовательность сообщений для пользователя {user_id} отменена.")

                    return True

        elif user_status != "alive":
            print(f"Воронка с клиентом {user_id} - не активна ⛔")

        message_count += 1
        if message_count >= 5:
            await asyncio.sleep(1)

    return False
