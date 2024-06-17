# MY_CLIENT
<h2>Автоответчик на pyrogram</h2>

Установка пакетов <pre>`pip install -r .\requirement.txt`</pre> <br/>

Создайте файл `.env` и укажите там переменные, разместите в корне проекта <br/>

создайте в postgresQL базу данных с названием `my_client` <br/>

    POSTGRES_USER=<пользователь для базы данных>
    POSTGRES_PASSWORD=<пароль к базе данных>
    POSTGRES_DB=my_client
    POSTGRES_HOST=localhost:5432
    API_ID=1234567 <укажите ваш id>
    API_HASH="1234567890" <укажите ваш hash> 

Запуск клиента <pre>`python main.py`</pre> <br/>

Текст сообщений можно редактировать в файле `message_config.ini`

    [pyrogram]
    msg_1=<i>первое сообщение автоответчика 🖖</i>
    msg_2=<i>второе сообщение автоответчика 💤</i>
    msg_3=<i>третье сообщение автоответчика 👀</i>
