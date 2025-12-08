FROM python:3.11-slim

WORKDIR /app

# Сначала копируем только requirements.txt для кэширования
COPY service/requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY service/api.py .
COPY service/predictor.py .
COPY service/models ./models/
COPY config_loader.py .

# Копируем конфиги
COPY configs ./configs/

# Проверяем что скопировалось
RUN echo "📁 Структура проекта:" && \
    ls -la && \
    echo "📁 Содержимое configs:" && \
    ls -la configs/ && \
    echo "📁 Содержимое models:" && \
    ls -la models/

EXPOSE 8000

CMD ["python", "api.py"]