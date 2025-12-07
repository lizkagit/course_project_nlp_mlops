# service/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Устанавливаем системные зависимости (опционально - можно убрать если не нужны)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости ИЗ ТЕКУЩЕЙ ПАПКИ service
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код сервиса
COPY . .

# Копируем config_loader.py из родительской директории (если нужно)
# Вам нужно убедиться что он есть в service/ или скопировать

# Проверяем структуру
RUN echo "✅ Содержимое проекта:" && ls -la

# Открываем порт
EXPOSE 8000

# Запускаем API
CMD ["python", "api.py"]