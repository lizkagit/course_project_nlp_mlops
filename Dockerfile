# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY service/ ./service/
COPY configs/ ./configs/

# Открываем порты
EXPOSE 8000 7860

# Запускаем оба сервиса
CMD ["sh", "-c", "python -m uvicorn service.api:app --host 0.0.0.0 --port 8000 & sleep 3 && python service/gradio_ui.py"]