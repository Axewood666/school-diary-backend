# School Diary API

API для системы школьного дневника

## Как запустить проект

## 1. Docker

### 1. Настройка окружения

Перед запуском необходимо настроить файл `.env`. В репозитории уже есть готовый файл с настройками по умолчанию.

Основные параметры в файле `.env`:

```
# Основные настройки приложения
PROJECT_NAME=School Diary API          # Название приложения
API_V1_STR=/api/v1                     # Префикс API
PORT=80                                # Порт внутри контейнера

# База данных
POSTGRES_USER=postgres                 # Пользователь PostgreSQL
POSTGRES_PASSWORD=postgres             # Пароль PostgreSQL
POSTGRES_DB=diary_db                   # Имя базы данных
POSTGRES_INITDB_ARGS=--locale=ru_RU.utf8  # Аргументы инициализации БД

# Настройки JWT
SECRET_KEY=nuts_key                    # Секретный ключ для JWT
ALGORITHM=HS256                        # Алгоритм шифрования
ACCESS_TOKEN_EXPIRE_MINUTES=600        # Время жизни токена в минутах

# MinIO настройки
MINIO_ACCESS_KEY=MY_ACCESS_MINIO       # Ключ доступа MinIO
MINIO_SECRET_KEY=MY_SECRET_MINIO       # Секретный ключ MinIO
MINIO_PUBLIC_BUCKET=public             # Имя публичного бакета
MINIO_REDIRECT_USE_HTTPS=false/true        # Использовать HTTPS для перенаправления на MinIO
MINIO_EXTERNAL_ENDPOINT=files.yourdomain.ru # Внешний адрес MinIO
MINIO_USE_HTTPS=false/true                     # Использовать HTTPS для MinIO
```

### 2. Настройка конфигурации Caddy

Перед запуском проекта, запустите скрипт для настройки Caddy в зависимости от текущей ветки:
```bash
./update-caddy-config.sh
```

Этот скрипт автоматически выберет конфигурацию:
- Для ветки `main` - продакшн конфигурация (Caddyfile.prod)
- Для ветки `development` и других - конфигурация для разработки (Caddyfile.dev)

### 3. Запуск проекта через Docker
```bash
docker-compose up -d
```

### 4. Миграции и начальные данные

Миграции запускаются автоматически при старте контейнера. При первом запуске будет создан пользователь с правами администратора:

- Логин: admin
- Пароль: admin
- Email: admin@example.com

**Важно**: Для продакшн окружения рекомендуется сразу сменить пароль администратора после первого входа!

### 5. Доступ к API
- Разработка: https://localhost
- Продакшн: https://your-domain.com (укажите свой домен в Caddyfile.prod)

## 2. Локальный запуск

### 1. Настройка окружения для локальной разработки

Создайте файл `.env.local` на основе `.env` и измените следующие параметры:

```
# Подключение к локальной базе данных
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/diary_db
DATABASE_URL_MIGRATE=postgresql+psycopg2://postgres:your_password@localhost:5432/diary_db

# Локальный MinIO
MINIO_ENDPOINT=localhost:9000
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Запуск миграций
```bash
alembic upgrade head
```

### 4. Запуск проекта
```bash
uvicorn app.main:app --reload --env-file .env.local
```

### 5. Доступ к API
http://localhost:8000/docs


## Документация API
- Swagger UI: /docs
- Схема OpenAPI: /api/v1/openapi.json

## Структура проекта
- `app/` - основной код приложения
  - `api/` - эндпоинты API
  - `core/` - основные настройки и компоненты
  - `db/` - модели и репозитории базы данных
  - `schemas/` - Pydantic модели
  - `services/` - бизнес-логика
- `alembic/` - миграции базы данных
