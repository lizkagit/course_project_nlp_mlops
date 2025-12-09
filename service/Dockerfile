FROM python:3.11-slim

WORKDIR /app

# Копируем requirements
COPY service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY service/api.py .
COPY service/predictor.py .
COPY service/models ./models/
COPY config_loader.py .
COPY configs ./configs/

# Копируем BentoML файл
COPY service/bentoml_service.py .

EXPOSE 8000 3000

# Запускаем оба сервиса (правильная команда для BentoML 1.4+)
CMD ["sh", "-c", "python api.py & bentoml serve bentoml_service.py:CommentPredictor --port 3000 --host 0.0.0.0"]