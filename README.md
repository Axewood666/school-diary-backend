# School Diary API

API для системы школьного дневника

## Как запустить проект
## 1. Docker
### 1. Настройка конфигурации
Перед запуском проекта, запустите скрипт для настройки Caddy в зависимости от текущей ветки:
```bash
./update-caddy-config.sh
```

Этот скрипт автоматически выберет конфигурацию:
- Для ветки `main` - продакшн конфигурация (Caddyfile.prod)
- Для ветки `development` и других - конфигурация для разработки (Caddyfile.dev)

### 2. Запуск проекта через Docker
```bash
docker-compose up -d
```

### 3. Доступ к API
- Разработка: https://localhost
- Продакшн: https://your-domain.com (укажите свой домен в Caddyfile.prod)

## 2. Локальный запуск

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Запуск проекта
```bash
uvicorn app.main:app --reload
```

### 3. Миграции
```bash
alembic upgrade head
```

### 4. Доступ к API
http://localhost:8000/docs


## Документация API
- Swagger UI: /docs
- Схема OpenAPI: /api/v1/openapi.json