# School Diary API

API для системы школьного дневника

## Как запустить проект

### 1. Клонирование репозитория
```bash
git clone <репозиторий>
cd school-diary-backend
```

### 2. Настройка конфигурации
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

### 4. Доступ к API
- Разработка: https://localhost
- Продакшн: https://your-domain.com (укажите свой домен в Caddyfile.prod)

## Документация API
- Swagger UI: /docs
- Схема OpenAPI: /api/v1/openapi.json
