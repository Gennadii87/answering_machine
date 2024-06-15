# MY_CLIENT
<h2>Автоответчик на pyrogram</h2>

Установка пакетов <code>`pip install -r .\requirement.txt`</code> <br/>

создайте файл `.env` и укажите там переменные, разместите в корне проекта <br/>

создайте в postgresQL базу данных с названием `my_client` <br/>

<code>

    POSTGRES_USER=<`полльзователь для базы данных`>
    POSTGRES_PASSWORD=<`пароль к базе данных`>
    POSTGRES_DB=my_client
    POSTGRES_HOST=localhost:5432
    
    API_ID=1234567 <укажите ваш id>
    API_HASH="1234567890" <укажите ваш hash>

</code>

Запуск клиента <code>`python main.py`</code> <br/>
