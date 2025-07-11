# Дипломный проект по профессии «Fullstack-разработчик на Python»
Облачное хранилище My Cloud (сервер)

ip-адрес: 89.104.71.24

frontend: https://github.com/LagutaNV2/Diploma_MyCloud_frontend



Проект разворачивается на виртуальном сервере (Reg.ru) на основе:

- Ubuntu
- Nginx (как веб-сервер и обратный прокси)
- Gunicorn (для запуска Django-приложения)
- PostgreSQL (база данных)

# Схема проекта:
/var/www/my_cloud/
├── backend/

│   ├── venv/

│   ├── staticfiles/    # collectstatic

│   ├── storage_files/  # пользовательские файлы

│   ├── .env            # production settings

│   └── ...             # исходный код

|   └──  gunicorn.service

└── frontend/

    ├── dist/           # собранный фронтенд

    └── .env.production # production env vars


# План действий:

Подготовка сервера:
- Ключи и заказ сервера
- Обновление системы на сервере
- Установка необходимых пакетов (Python, pip, PostgreSQL, Nginx и т.д.)

Настройка базы данных PostgreSQL:
- Создание базы данных и пользователя для Django-проекта

Настройка бекенда (Django):
- Клонирование репозитория на сервер
- Создание виртуального окружения и установка зависимостей
- Настройка переменных окружения (файл .env) для production
- Применение миграций, сбор статики, создание суперпользователя

Настройка фронтенда:
- Сборка фронтенда в production-режиме
- Размещение собранных файлов фронтенда в директории, откуда backend будет раздавать статику

Настройка Gunicorn:
- Создание systemd-сервиса для запуска Gunicorn

Настройка Nginx:
- Конфигурация Nginx для обслуживания статических файлов и проксирования запросов к Gunicorn
- Настройка для работы с фронтендом (SPA) и API бекенда



# Пошаговая инструкция для деплоя на REG.RU
1.	Закажите на рег.ру VPS сервер [Рег.облако].

2. Подключитесь к серверу по SSH:

   2.1. создайте ssh-ключ и (если не было):

        ssh-keygen -t rsa

   2.2. скопируйте публичную часть ключа

        cat ~/.ssh/id_rsa.pub

   2.3. создайте ключ на рег.ру (дайте имя и вставьте скопированное)

   2.4. выполните подключение к серверу:

        ssh root@ip-adress

3. Обновление системы и установка базовых компонентов:

    sudo apt update && sudo apt upgrade -y

    sudo apt install -y git nginx libpq-dev python3-pip

    sudo apt install -y python3 python3-venv python3-dev

    sudo apt install -y postgresql postgresql-contrib


 Настройка firewall:

    sudo ufw allow 'Nginx Full'

    sudo ufw enable

4. Настройка базы данных PostgreSQL

    4.1. Создайте базу данных и пользователя для вашего проекта:

        sudo -u postgres psql

    4.2. выполните следующие команды (замените значения переменных на свои):

        CREATE DATABASE mycloud_db;

        CREATE USER mycloud_user WITH PASSWORD 'your_password';

        ALTER ROLE mycloud_user SET client_encoding TO 'utf8';

        ALTER ROLE mycloud_user SET default_transaction_isolation TO 'read committed';

        ALTER ROLE mycloud_user SET timezone TO 'Europe/Moscow';

        GRANT ALL PRIVILEGES ON DATABASE mycloud_db TO mycloud_user;


    4.3. Выйдите из `psql`:

        \q

5. Создание директории и системного пользователя для проекта:

    5.1. Создайте системного пользователя
       (например, для 'django'- adduser django):

        adduser www

    5.2. Добавьте пользователя www в группу sudo:

        usermod -aG sudo www

    5.3. Переключитесь на системного пользователя, под которым будет размещен проект:

        sudo su www

    5.4. Создайте директорию для проекта и перейдите в нее (например, mkdir /home/django/my_cloud/backend):

        Создаем корневую директорию проекта в домашней директории

            mkdir -p ~/my_cloud

        Создаем директорию для бекенда

            mkdir ~/my_cloud/backend

        Переходим в рабочую директорию

            cd ~/my_cloud/backend



6. Разворачиваем backend (Django)

    6.1. Клонирование проекта из репозитория Git https://github.com/LagutaNV2/Diploma_MyCloud_backend в папку /var/www/my_cloud/backend:

        git clone https://github.com/LagutaNV2/Diploma_MyCloud_backend.git .


    6.2. Создание виртуального окружения

          6.2.1. Создайте и активируйте виртуальное окружение для python3.10:

              python3 -m venv venv
              source venv/bin/activate

          6.2.2. Установите зависимости из файла `requirements.txt`:

              pip install -r requirements.txt


    6.3. Настройка конфигурации Django

      6.3.1. Для хранения переменных окружения используется '.env'. Создайте файл '.env' на сервере в /var/www/my_cloud/backend (образец: '.env.example'):

          nano .env

        Чтобы предотвратить несанкционированный доступ к .env, установите права доступа:

          sudo chown django:django /var/www/my_cloud/backend/.env
          sudo chmod 600 /var/www/my_cloud/backend/.env

      6.3.2. Файл `config/settings.py` настроен на универсальное использование, но если есть необходимость, отредактируйте:

          предоставление прав user django:

              sudo chown django:django config/settings.py

          открыть для редактирования:

              nano config/settings.py




      6.3.3. Выполните миграции для создания таблиц в базе данных:

          python manage.py makemigrations

          python manage.py migrate



      6.3.4. Соберите статические файлы сервера:

          python manage.py collectstatic


      6.3.5. Создайте суперпользователя для административной панели:

          python manage.py createsuperuser


7.  Настройка Gunicorn

    7.1. Установка Gunicorn

        pip install gunicorn

    7.2. В корне backend создаём файл сервиса для Gunicorn:

        sudo nano /etc/systemd/system/gunicorn.service

    7.3. Добавим содержимое, обращая внимание на пути, имя проекта и пользователя (здесь - для пути: "/home/django/my_cloud/backend"):

            [Unit]
            Description=Gunicorn for Cloud Storage Django "My cloud"
            After=network.target

            [Service]
            User=django

            Group=django

            WorkingDirectory=/var/www/my_cloud/backend
            (   например,  /home/django/my_cloud/backend )

            Environment="PATH=/var/www/my_cloud/backend/venv/bin"

            ExecStart=/var/www/my_cloud/backend/venv/bin/gunicorn \
                    --workers 3 \
                    --bind unix:/tmp/gunicorn.sock \
                    config.wsgi:application
            (или '--bind': 'unix:/home/django/my_cloud/backend/gunicorn.sock')

            [Install]
            WantedBy=multi-user.target

    7.4. Запустите и включите сервис:

            sudo systemctl daemon-reload
            sudo systemctl start gunicorn
            sudo systemctl enable gunicorn

8.  Разворачиваем frontend (React)

    8.1. Клонирование проекта из репозитория [Git https://github.com/LagutaNV2/Diploma_MyCloud_backend] на локальную машину.

    8.2. Установить зависимости и собрать проект:

            npm install
            npm run build


    8.3. Копируем статику из папки dist на сервер, после чего директория /var/www/frontend будет содержать статические HTML, JS и CSS файлы:

        scp -r dist/* root@ваш-ip:/var/www/my_cloud/frontend/dist


    8.4. Создание .env.production в папке /var/www/my_cloud/frontend:

          nano .env.production

        содержание:

            API_BASE_URL=/api
            DEBUG=false
            PUBLIC_PATH=/

9.    Настройка Nginx

    9.1. Создайте конфигурационный файл для Nginx:

        sudo nano /etc/nginx/sites-available/my_cloud


    9.2. Содержимое файла:

        server {
            listen 80;
            listen [::]:80;

            # Ваш IP-адрес сервера
            server_name ваш-ip-адрес ваш-домен;

            # Корень для фронтенда
            root /var/www/my_cloud/frontend/dist;

            # Статика фронтенда
            location / {
                try_files $uri $uri/ /index.html;
                add_header Cache-Control "no-cache, no-store, must-revalidate";
                add_header Pragma "no-cache";
                add_header Expires "0";
            }

            # Статика Django (admin, DRF)
            location /static/ {
                alias /var/www/my_cloud/backend/staticfiles/;
                expires 30d;
                access_log off;
            }

            # Медиафайлы (загруженные пользователями)
            location /storage/ {
                alias /var/www/my_cloud/backend/storage_files/;
                expires 30d;
                access_log off;
            }

            # API endpoints
            location /api/ {
                include proxy_params;
                proxy_pass http://unix:/home/django/my_cloud/backend/gunicorn.sock;
                (или proxy_pass http://unix:/tmp/gunicorn.sock;)
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header Host $http_host;
                proxy_redirect off;

                # Увеличение таймаутов для загрузки файлов
                proxy_connect_timeout 300s;
                proxy_send_timeout 300s;
                proxy_read_timeout 300s;
                send_timeout 300s;
            }

            # Django admin
            location /admin/ {
                proxy_pass http://unix:/var/www/my_cloud/backend/gunicorn.sock;
                (или proxy_pass http://unix:/tmp/gunicorn.sock;)
            }

            # Health check endpoint
            location /health/ {
                proxy_pass http://unix:/var/www/my_cloud/backend/gunicorn.sock;
                (или proxy_pass http://unix:/tmp/gunicorn.sock;)
            }

            if ($scheme = http) {
                return 301 https://$server_name$request_uri;
            }

            # Обработка ошибок
            error_page 500 502 503 504 /50x.html;
            location = /50x.html {
                root /usr/share/nginx/html;
            }
        }

    9.3. Активируйте конфигурацию:

        sudo ln -s /etc/nginx/sites-available/my_cloud /etc/nginx/sites-enabled/
        sudo nginx -t
        sudo systemctl restart nginx


10.  Проверка работоспособности

     Проверка Gunicorn:

        sudo systemctl status gunicorn
        journalctl -u gunicorn --since "5 minutes ago"


    Проверка Nginx:

        sudo nginx -t
        sudo systemctl status nginx
        tail -f /var/log/nginx/error.log

    Тестовые запросы:

        Проверка API

            curl http://194.67.74.177/api/health/

        Проверка статики Django

            curl -I http://194.67.74.177/static/admin/css/base.css

        Проверка фронтенда

            curl -I http://194.67.74.177

        Проверка работы приложения

          - Откройте браузер и перейдите по адресу `http://your-domain.com`.
          - Убедитесь, что проект загружается корректно.
          - Проверьте административную панель по адресу `http://your-domain.com/admin`.
