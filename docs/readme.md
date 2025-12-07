 
##   Docker запуск
### Быстрый запуск:
```bash
# 1. Соберите образ
cd service
docker build -t mlops-api .

# 2. Запустите контейнер
docker run -p 8000:8000 mlops-api

# 3. Проверьте
curl http://localhost:8000/health
 # Способ 2: Через docker-compose из корня
docker-compose up --build