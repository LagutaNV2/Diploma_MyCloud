# Дипломный проект по профессии «Fullstack-разработчик на Python»
Облачное хранилище My Cloud (сервер)

backend: «Brown Nihonium» с Django, IP-адрес 194.67.74.177

frontend: https://lagutanv2.github.io/Diploma_MyCloud_frontend/

# Инструкция для деплоя на REG.RU
1.	закажите облачный сервер на рег.ру, например, закажите новый VPS сервер [Рег.облако].

2. Подключитесь к серверу по SSH:

   2.1. создайте ssh-ключ и (если не было):

        ssh-keygen -t rsa

   2.2. скопируйте публичную часть ключа

        cat ~/.ssh/id_rsa.pub

   2.3. и создайте ключ на рег.ру (дайте имя и вставьте скопированное)

   2.4. выполните подключение к серверу:

        ssh root@ip-adress


3. Настройка базы данных PostgreSQL

3.1. Создайте базу данных и пользователя для вашего проекта:

    sudo -u postgres psql

3.2. выполните следующие команды (замените значения переменных на свои):

    CREATE DATABASE mycloud_db;
    CREATE USER mycloud_user WITH PASSWORD 'your_password';
    ALTER ROLE mycloud_user SET client_encoding TO 'utf8';
    ALTER ROLE mycloud_user SET default_transaction_isolation TO 'read committed';
    ALTER ROLE mycloud_user SET timezone TO 'Europe/Moscow';
    GRANT ALL PRIVILEGES ON DATABASE mycloud_db TO mycloud_user;

3.3. Выйдите из `psql`:

    \q

4. Создание директории и системного пользователя для проекта

4.1. Создайте системного пользователя, например, как используется здесь, 'django':

    adduser django

4.2. Добавьте пользователя django в группу sudo:

    usermod -aG sudo django

4.3. Переключитесь на системного пользователя, под которым будет размещен проект. Например, если пользователь называется 'django':

    sudo su django

4.4. Создайте директорию для проекта и перейдите в нее (здесь название проекта 'my_cloud'):

    mkdir /home/django/my_cloud
    cd /home/django/my_cloud


5. Клонирование проекта.

Клонируйте проект из репозитория Git https://github.com/LagutaNV2/Diploma_MyCloud_backend :

    git clone https://github.com/LagutaNV2/Diploma_MyCloud_backend.git .


6. Создание виртуального окружения

6.1. Создайте и активируйте виртуальное окружение для python3.10:

    sudo apt install python3.10 python3.10-venv python3.10-dev
    python3.10 -m venv env
    source venv/bin/activate

6.2. Установите зависимости из файла `requirements.txt`:

    pip install -r requirements.txt


7. Настройка конфигурации Django

7.1. Для хранения переменных окружения используется '.env'. Создайте файл '.env' на сервере в корне проекта (образец: '.env.example'):

    nano .env

7.2. Чтобы предотвратить несанкционированный доступ к .env, установите права доступа:

    chmod 600 /home/django/my_cloud/backend/.env
    chown django:django /home/django/my_cloud/backend/.env

7.3. Отредактируйте файл `config/settings.py`, чтобы настроить подключение к базе данных и домен (???????):

    предоставление прав user django:

        sudo chown django:django config/settings.py

    открыть для редактирования:

        nano config/settings.py


    содержание файла (проверить настройки):
<!-- ??????? оставить так , как  в файле: os.path.join(BASE_DIR, 'staticfiles') -->
        STATIC_ROOT = os.path.join(BASE_DIR, 'static/')


8. Выполните миграции для создания таблиц в базе данных:

    python manage.py makemigrations

    python manage.py migrate


9. Соберите статические файлы:

   python manage.py collectstatic

10. Создайте суперпользователя для административной панели:

    python manage.py createsuperuser


11.  Настройка Gunicorn

11.1. Создайте файл сервиса для Gunicorn (откройте, если сервер создан на шаблоне Django):

    sudo nano /etc/systemd/system/mycloud_gunicorn.service

11.2. Добавьте или отредактируйте следующее содержимое (здесь- для пути: "/home/django/my_cloud"):

        [Unit]
        Description=gunicorn daemon for My Cloud project
        After=network.target

        [Service]
        User=django
        Group=django
        WorkingDirectory=/home/django/my_cloud
        ExecStart=/home/django/my_cloud/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/django/my_cloud/mycloud.sock config.wsgi:application

        [Install]
        WantedBy=multi-user.target


11.3. Запустите и включите сервис:

    sudo systemctl daemon-reload
    sudo systemctl start mycloud_gunicorn
    sudo systemctl enable mycloud_gunicorn

12.   Настройка Nginx

12.1. Создайте конфигурационный файл для Nginx (откройте, если сервер использует шаблон Django):

    sudo nano /etc/nginx/sites-available/mycloud


12.2. Добавьте (отредактируйте) следующее содержимое
(здесь для пути: 'home/django/my_cloud/'):

        server {
            listen 80;
            listen [::]:80;

            server_name your-domain.com;
            <!-- здесь: server_name 194.67.74.177 -->

            location / {
                include proxy_params;
                proxy_pass http://unix:/home/django/my_cloud/mycloud.sock;
            }
<!-- for in the settings.py STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') -->
            location /static/ {
                root /home/django/my_cloud/staticfiles/;
            }
<!-- ??????? -->
            location = /favicon.ico {
                access_log off;
                log_not_found off;
            }

            location /storage/ {
                root /home/django/my_cloud/storage_files/;
            }

        }


12.3. Активируйте конфигурацию:

    sudo ln -s /etc/nginx/sites-available/mycloud /etc/nginx/sites-enabled/
    sudo systemctl restart nginx


12.4 Проверка работоспособности

- Откройте браузер и перейдите по адресу `http://your-domain.com`.
- Убедитесь, что проект загружается корректно.
- Проверьте административную панель по адресу `http://your-domain.com/admin`.
