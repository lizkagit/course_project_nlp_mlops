 
##   Docker запуск
### Быстрый запуск:
```bash
# 1. Соберите образ
docker build -t mlops-api -f service/Dockerfile .

# 2. Запустите контейнер
docker run -p 8000:8000 mlops-api

# 3. Проверьте
curl http://localhost:8000/health
 