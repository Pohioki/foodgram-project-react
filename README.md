# praktikum_new_diplom
IP серевера: http://84.201.164.48/
[![Foodgramm workflow](https://github.com/Pohioki/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/Pohioki/foodgram-project-react/actions/workflows/main.yml)

# **Foodgram project**

### _Продуктовый помощник_

# Описание

На сервисе **Продуктовый помощник** пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список **«Избранное»**, а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

# Шаблон заполнения .env файла

```python
DB_ENGINE='django.db.backends.postgresql'
POSTGRES_DB='foodgram' # Задаем имя для БД.
POSTGRES_USER='foodgram_u' # Задаем пользователя для БД.
POSTGRES_PASSWORD='foodgram_u_pass' # Задаем пароль для БД.
DB_HOST='db'
DB_PORT='5432'
SECRET_KEY='secret'  # Задаем секрет.
ALLOWED_HOSTS='127.0.0.1, backend' # Вставляем свой IP сервера.
```


# Подготовка сервера к деплою

```bash
# username - ваш логин, ip - ip ВМ под управлением Linux Дистрибутива с пакетной базой deb.
ssh username@ip
```

```bash
sudo apt update && sudo apt upgrade -y && sudo apt install curl -y
```

```bash
sudo curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && sudo rm get-docker.sh
```

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

```bash
sudo chmod +x /usr/local/bin/docker-compose
```

```bash
sudo systemctl start docker.service && sudo systemctl enable docker.service
```

Клонируем репозиторий с гита

git@github.com:Pohioki/foodgram-project-react.git

Копируем файлы из папки /infra на сервер

```bash
scp -r infra/* <server user>@<server IP>:/home/<server user>/foodgram/
```

Качаем образы на серевер

```bash
sudo docker pull pohioki/foodgram_backend:latest
sudo docker pull pohioki/foodgram_front:latest
```

Запускаем сайт

```bash
sudo docker-compose up -d
```

Загружаем базу данных

```bash
sudo docker-compose exec web python manage.py loaddata dump.json
```


# Примеры работы с API для пользователей

Для неавторизованных пользователей работа с API доступна в режиме чтения, что-либо изменить или создать не получится.

```bash
Права доступа: Доступно без токена.
GET /api/recipes/ - Получение списка всех рецептов
GET api/ingredients - Получение списка всех ингредиентов
GET /api/tags/ - Получение списка тэгов
POST /api/users/ - Регистрация пользователя
```

# Технологии

- [Python 3.8.8](https://www.python.org/downloads/release/python-388/)
- [Django 2.2.16](https://www.djangoproject.com/download/)
- [Django Rest Framework 3.13.1](https://www.django-rest-framework.org/)
- [PostgreSQL 13.0](https://www.postgresql.org/download/)
- [gunicorn 20.0.4](https://pypi.org/project/gunicorn/)
- [nginx 1.21.3](https://nginx.org/ru/download.html)
- [Docker 20.10.14](https://www.docker.com/)
- [Docker Compose 2.4.1](https://docs.docker.com/compose/)

## Об авторе
Юля & Яндекс.Практикум

Copyright (c) 2023, Julia Volskaya

All rights reserved.

