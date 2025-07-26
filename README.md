### Дипломный проект по профессии «Fullstack-разработчик на Python»
## Облачное хранилище My Cloud (сервер)

ip-адрес: [http://89.104.71.24]

frontend: [https://github.com/LagutaNV2/Diploma_MyCloud_frontend]



## **Проект разворачивается на виртуальном сервере (Reg.ru) на основе:**

- Ubuntu
- Nginx (как веб-сервер и обратный прокси)
- Gunicorn (для запуска Django-приложения)
- PostgreSQL (база данных)

## Системные требования (System Requirements)
Минимальные требования для сервера:

ОС: Ubuntu 22.04 LTS

Процессор: 1 ядро (x86_64)

Память: 1 ГБ RAM

Дисковое пространство: 10 ГБ (зависит от диска сервера)

Дополнительно:

PostgreSQL 14+
Python 3.10+
Nginx 1.18+
Node.js 18+ (для сборки фронтенда)

Рекомендуемые требования:

1vCPU, 1 ГБ RAM, 10ГБ SSD-диск

## Ограничения системы (System Limits)
По умолчанию:

Максимальный размер файла: 1 МБ

(ограничение Django,
можно изменить в File: storage/serializers.py и в конфигурационном файле Nginx )

Общий объем хранилища: 10 ГБ (зависит от диска сервера)

## Документация доступна по адресу (после деплоя):

http://ваш-ip/api/docs/


## Схема проекта:
/var/www/my_cloud/

├── backend/

│   ├── venv/

│   ├── staticfiles/    # collectstatic

│   ├── storage_files/  # пользовательские файлы

│   ├── .env            # production settings

│   └── ...             # исходный код


└── frontend/

    ├── dist/           # собранный фронтенд

    └── .env.production # production env vars


## План действий:

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



## Пошаговая инструкция для деплоя на REG.RU
1.	Закажите на рег.ру VPS сервер.

2. Подключитесь к серверу по SSH:

   2.1. на локальной машине:
   ```
    ssh-keygen -t rsa
    cat ~/.ssh/id_rsa.pub
   ```
   2.2. создайте ключ на рег.ру *(дайте имя и вставьте скопированное)*

   2.3. подключитесь к серверу *(терминал на локальной машине)*:
  ```
    ssh root@ip-adress
  ```
3. Обновление системы и установка базовых компонентов:
   ```
    sudo apt update && sudo apt upgrade -y

    sudo apt install -y git nginx libpq-dev python3-pip

    sudo apt install -y python3 python3-venv python3-dev

    sudo apt install -y postgresql postgresql-contrib


4. Настройка базы данных PostgreSQL
   ```
    sudo -u postgres psql
    CREATE DATABASE mycloud_db;
    CREATE USER mycloud_user WITH PASSWORD 'your_password';
    ALTER ROLE mycloud_user SET client_encoding TO 'utf8';
    ALTER ROLE mycloud_user SET default_transaction_isolation TO 'read committed';
    ALTER ROLE mycloud_user SET timezone TO 'Europe/Moscow';
    GRANT CREATE ON SCHEMA public TO mycloud_user;
    GRANT ALL PRIVILEGES ON DATABASE mycloud_db TO mycloud_user;
    GRANT ALL PRIVILEGES ON SCHEMA public TO mycloud_user;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mycloud_user;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mycloud_user;
    \q

5. Создание директории и системного пользователя для проекта:
    *(здесь www=django->adduser django)*

    adduser www

    usermod -aG sudo www *(usermod -aG sudo django)*

    sudo su www *(sudo su django)*

   Создайте директорию для проекта и перейдите в нее *(например, mkdir /home/django/my_cloud/backend)*:
   ```
    mkdir -p ~/my_cloud
    mkdir ~/my_cloud/backend
    cd ~/my_cloud/backend


6. Разворачиваем backend (Django)

    6.1. Клонирование проекта из репозитория Git  в папку my_cloud/backend:

        git clone https://github.com/LagutaNV2/Diploma_MyCloud_backend.git .


    6.2. Создание виртуального окружения и установка зависимостей:

        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt


    6.3. Настройка конфигурации Django

      6.3.1. Создайте файл '.env' на сервере в my_cloud/backend:

        nano .env

        содержание:

            ENVIRONMENT=production
            DEBUG=False
            SECRET_KEY=your_production_secret_key_here
            ALLOWED_HOSTS=your_server_ip
            DB_NAME=your_production_db_name
            DB_USER=your_production_db_user
            DB_PASSWORD=your_production_password
            DB_HOST=localhost
            DB_PORT=5432
            STORAGE_PATH=/var/www/my_cloud/storage_files
                # /home/django/my_cloud/storage_files
            CORS_ALLOWED_ORIGINS=http://ваш-ip,http://localhost:3000

      6.3.2. Файл `config/settings.py` настроен на универсальное использование, но если есть необходимость, отредактируйте:

            sudo chown django:django config/settings.py
            nano config/settings.py


      6.3.3. Выполните миграции и соберите статические файлы сервера:

            python manage.py makemigrations
            python manage.py migrate
            python manage.py collectstatic


      6.3.4. Создайте суперпользователя для административной панели:

            python manage.py createsuperuser


7.  Настройка Gunicorn (здесь - для пути: "/home/django/my_cloud/backend")

    7.1. Установка Gunicorn

        pip install gunicorn

    7.2. В корне backend создаём файл сервиса для Gunicorn:

        sudo nano /etc/systemd/system/gunicorn.service

    7.3. Добавим содержимое, обращая внимание на пути, имя проекта и пользователя:

            [Unit]
            Description=Gunicorn for Cloud Storage Django "My cloud"
            After=network.target

            [Service]
            User=django

            Group=django

            WorkingDirectory=/home/django/my_cloud/backend

            Environment="PATH=/home/django/my_cloud/backend/venv/bin"

            ExecStart=/home/django/my_cloud/backend/venv/bin/gunicorn \
                    --workers 3 \
                    --bind': 'unix:/home/django/my_cloud/backend/gunicorn.sock'
                    --forwarded-allow-ips="*"\                      --access-logfile - \
                    config.wsgi:application

            Restart=always
            UMask=0007

            [Install]
            WantedBy=multi-user.target

    7.4. обновите права:

        sudo chown django:django /home/django/my_cloud/backend
        sudo chmod 755 /home/django/my_cloud/backend

    7.5. Запустите и включите сервис:

        sudo systemctl daemon-reload
        sudo systemctl start gunicorn
        sudo systemctl enable gunicorn

8.  Разворачиваем frontend (React) *(здесь - для пути: "/home/django/my_cloud/frontend")*

    8.1. Клонирование проекта из репозитория [Git https://github.com/LagutaNV2/Diploma_MyCloud_backend] на локальную машину.

    8.2. Установить зависимости и собрать проект:

            npm install
            npm run build

    8.3. Создаем папку /home/django/frontend на сервере и копируем статику из папки dist на сервер, после чего она будет содержать статические HTML, JS и CSS файлы:

      на сервере:

        mkdir ~/my_cloud/frontend

      В терминале (на локальной машине):

        scp -r dist/* root@ваш-ip:/home/django/my_cloud/frontend/dist


    8.4. Создание .env.production в папке /home/django/my_cloud/frontend:

        nano .env.production

        содержание:

            API_BASE_URL=http://ваш-ip/api
            DEBUG=false
            PUBLIC_PATH=/
            NODE_ENV=production
            GENERATE_SOURCEMAP=false

    8.5. пдоставьте подльзователю права для работы с dist:

            sudo chmod -R 755 /home/django/my_cloud/frontend/dist
            sudo chown -R django:www-data /home/django/my_cloud/frontend/dist


9.    Настройка Nginx

    9.1. Создайте конфигурационный файл для Nginx:

        sudo nano /etc/nginx/sites-available/my_cloud


    9.2. Содержимое файла:

        ```
        server {
            listen 80;
            listen [::]:80;

            # Ваш IP-адрес сервера
            server_name ваш-ip-адрес ваш-домен;

            # Ограничение размера загружаемых файлов (увеличьте, если необходимо)
            client_max_body_size 1M;

            error_page 413 @413_json;
            location @413_json {
                add_header Content-Type application/json;
                return 413 '{"file": ["Файл слишком большой (превышает 1 MB). Максимальный размер: 1 MB"]}';
            }

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
                add_header X-Debug-Host $host;
                proxy_pass http://unix:/home/django/my_cloud/backend/gunicorn.sock;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;

                # Дополнительная защита - очистка дублированных заголовков
                proxy_set_header X-Forwarded-Host $server_name;proxy_set_header X-Original-Host "";

                proxy_redirect off;
                proxy_buffering off;

                # Увеличение таймаутов для загрузки файлов
                proxy_connect_timeout 300s;
                proxy_send_timeout 300s;
                proxy_read_timeout 300s;
                send_timeout 300s;

                #  добавьте поддержку CORS
                add_header 'Access-Control-Allow-Origin' 'http://89.104.71.24' always;
                add_header 'Access-Control-Allow-Credentials' 'true' always;
            }

            # Django admin
            location /admin/ {
                include proxy_params;
                proxy_pass http://unix:/var/www/my_cloud/backend/gunicorn.sock;
                (или proxy_pass http://unix:/tmp/gunicorn.sock;)
            }

            # Health check endpoint
            location /health/ {
                include proxy_params;
                proxy_pass http://unix:/var/www/my_cloud/backend/gunicorn.sock;
                (или proxy_pass http://unix:/tmp/gunicorn.sock;)
            }

            # Обработка ошибок
            error_page 500 502 503 504 /50x.html;
            location = /50x.html {
                root /usr/share/nginx/html;
            }
        }
        ```


    9.3. Активируйте конфигурацию:

        sudo ln -s /etc/nginx/sites-available/my_cloud /etc/nginx/sites-enabled/
        sudo nginx -t
        sudo systemctl restart nginx


10.  Проверка работоспособности

    Проверка Gunicorn:

        sudo systemctl status gunicorn
        journalctl -u gunicorn --since "5 minutes ago"

    Проверка Nginx:

        sudo systemctl status nginx
        tail -f /var/log/nginx/error.log

    Тестовые запросы:

        Проверка API

            curl http://ваш Ip/health/

        Проверка фронтенда

            curl -I http://ваш Ip

        Проверка работы приложения в браузере

          - Откройте браузер и перейдите по адресу `http://ваш Ip`.
          - Убедитесь, что проект загружается корректно.
          - Проверьте административную панель по адресу `http://ваш Ip/admin`.

11. Команды запуска приложения на VSR ip 89.104.71.24:
    win + R
    wsl

   ```
    ssh django@89.104.71.24
    source ~/my_cloud/backend/venv/bin/activate

    sudo systemctl daemon-reload

    sudo systemctl start gunicorn
    sudo systemctl enable gunicorn
    sudo systemctl status gunicorn

    sudo nginx -t
    sudo systemctl start nginx
    sudo systemctl enable nginx
    sudo systemctl restart nginx
    sudo systemctl status nginx

    Перезапуск служб:
    sudo systemctl daemon-reload
    sudo systemctl restart gunicorn
    sudo systemctl restart nginx

    проверка:
    sudo systemctl status gunicorn
    sudo systemctl status nginx
    journalctl -u gunicorn
    sudo tail -f /var/log/nginx/error.log
    tail -f /home/django/my_cloud/backend/logs/django_debug.log

    curl http://89.104.71.24/health/
    http://89.104.71.24
```


# Резервное копирование базы данных

## Создание дампа БД
### 1. Чтобы создать резервную копию базы данных, выполните следующую команду:

```
   sudo -u postgres pg_dump -U mycloud_user -h localhost -d mycloud_db > backup_$(date +%Y-%m-%d).sql
```

, где
  mycloud_user -  имя пользователя базы данных;
  mycloud_db - имя базы данных;
  $(date +%Y-%m-%d) - динамически подставляет текущую дату в имя файла (например, `backup_2023-10-05.sql`) для перенаправления вывода в файл с соответствующим именем.


### 2. Восстановление из резервной копии:

```
   sudo -u postgres psql -U mycloud_user -h localhost -d mycloud_db < backup_2025-07-25.sql
```
, где < backup_2025-07-25.sql -  перенаправление содержимого файла в базу данных.

### 3. **Важные замечания**
Выполняйте дамп по мере необходимости (например, перед крупными изменениями в базе данных).

Убедитесь, что пользователь, выполняющий команды, имеет доступ к базе данных и директории для хранения файлов.

Рекомендуется хранить резервные копии на отдельном сервере или облачном хранилище для защиты от физических сбоев.

Регулярно проверяйте, что резервные копии создаются корректно и могут быть восстановлены.




## 🛠 Troubleshooting

### 1. Ошибка 502 Bad Gateway
**Симптомы:**
- Nginx возвращает ошибку 502
- Gunicorn не отвечает

**Решение:**
```
# Проверьте статус Gunicorn
sudo systemctl status gunicorn

# Просмотрите логи Gunicorn
journalctl -u gunicorn --since "5 minutes ago"

# Перезапустите службу
sudo systemctl restart gunicorn
```

### 2. Ошибки подключения к базе данных

Симптомы:

Django выдает ошибки вида "could not connect to server"

Миграции не применяются.


**Решение:**
```
# Проверьте доступность PostgreSQL

sudo systemctl status postgresql

# Проверьте права пользователя

sudo -u postgres psql -c "\l"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mycloud_db TO mycloud_user;"
```

### 3. Проблемы с загрузкой файлов
Симптомы:

Ошибка 413 Request Entity Too Large

Файлы не сохраняются

**Решение:**
```
Увеличьте лимит в Nginx:

nginx
# В /etc/nginx/sites-available/my_cloud
client_max_body_size 500M;

Перезапустите Nginx:

sudo systemctl restart nginx
```

### 4. Проблемы с CORS
Симптомы:

Браузер блокирует запросы к API

Ошибки "Blocked by CORS policy"

**Решение:**
```
Проверьте настройки в .env:

CORS_ALLOWED_ORIGINS=http://ваш-ip,http://localhost:3000

Перезапустите Gunicorn:

sudo systemctl restart gunicorn

```

### 5. Документация API не отображается

**Решение:**
```
Проверьте установку drf-spectacular

source venv/bin/activate
pip list | grep drf-spectacular

Проверьте доступность схемы

curl http://localhost/api/schema/



### 6. Недостаток дискового пространства

**Решение:**

```
# Проверьте свободное место
df -h


# Очистка старых резервных копий

```
find /backups -name "*.sql" -mtime +30 -delete
```
