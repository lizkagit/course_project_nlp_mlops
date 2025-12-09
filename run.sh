#!/bin/bash

# Останавливаем и удаляем старый контейнер, если он существует
echo "Stopping and removing old container if it exists..."
docker stop mlops-full 2>/dev/null || true
docker rm mlops-full 2>/dev/null || true

# Удаляем старый образ, если он существует
echo "Removing old image if it exists..."
docker rmi mlops-api 2>/dev/null || true

# Собираем новый образ
echo "Building Docker image..."
docker build --no-cache -t mlops-api -f service/Dockerfile .

# Запускаем контейнер
echo "Starting container..."
docker run -d -p 8000:8000 -p 3000:3000 --name mlops-full mlops-api

# Ждем, пока сервисы запустятся
echo "Waiting for services to start..."
sleep 10

# Проверяем статус контейнера
echo "Container status:"
docker ps | grep mlops-full

# Показываем логи
echo "Container logs:"
docker logs mlops-full
