#!/bin/bash

# Определяем текущую ветку Git
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "Detected Git branch: $CURRENT_BRANCH"

# Выбираем подходящую конфигурацию Caddy
if [ "$CURRENT_BRANCH" = "main" ]; then
    echo "Using production Caddy configuration..."
    cp Caddyfile.prod Caddyfile
    echo "Switched to production configuration."
else
    echo "Using development Caddy configuration..."
    cp Caddyfile.dev Caddyfile
    echo "Switched to development configuration."
fi

# Перезапускаем Caddy, если контейнер запущен
if sudo docker ps | grep -q caddy; then
    echo "Restarting Caddy container..."
    sudo docker-compose restart caddy
    echo "Caddy restarted."
else
    echo "Caddy container is not running. No restart needed."
fi

echo "Configuration update complete!" 