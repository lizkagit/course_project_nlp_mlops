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

# 3. Запуск
echo "▶️  Запуск контейнера с тремя сервисами..."
docker run -d \
  -p 8000:8000 \
  -p 3000:3000 \
  -p 7860:7860 \
  --name mlops-full \
  mlops-api:latest

echo ""
echo "✅ Контейнер запущен!"
echo ""

# 4. Ожидание запуска
echo "⏳ Ожидание запуска сервисов (15 секунд)..."
sleep 15

# 5. Проверка статуса
echo "📊 Статус контейнера:"
docker ps --filter "name=mlops-full" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🌐 Доступные сервисы:"
echo "   • FastAPI:      http://localhost:8000"
echo "   • FastAPI Docs: http://localhost:8000/docs"
echo "   • BentoML:      http://localhost:3000"
echo "   • Gradio UI:    http://localhost:7860"
echo ""