## Проект: Анализ тональности текстов о метро (MLOps Pipeline)

Проект представляет собой MLOps-решение для анализа тональности текстовых отзывов о метрополитене. Включает модель машинного обучения, сервис для инференса и UI-интерфейс.

##  Структура проекта

```
.
├── .env                         # Переменные окружения
├── configs/                     # Конфигурационные файлы
│   ├── inference_config.yaml    # Конфиг для инференса
│   └── train_config.yaml       # Конфиг для обучения
├── data/                        # Данные
│   ├── processed/              # Обработанные данные
│   ├── experiments/            # Эксперименты
│   │   └── exp1_regress.csv   # Датасет для экпериментов предобработанный
│   ├── df_capped_csv          # Урезанный датасет (95 перцентиль)
│   └── raw/                    # Исходные данные
│       ├── all_posts_v1.csv   # Все посты
│       └── df_mosmetro_sample.csv  # Выборка по целевой группе
├── docs/                        # Документация
│   ├── DATASET_CARD.md         # Карточка датасета
│   ├── MODEL_CARD.md           # Карточка модели
│   └── readme.md              # Основная документация                  
├── notebooks/               
│   ├── models/                 # Сохраненные модели с экперементов
│   ├── service_models/         # Модели для сервисов(лучшие)
│   ├── course_mlops.ipynb     # Основной ноутбук
│   └── experiment_results_comparison.csv  # Сравнение экспериментов
├── service/                     # Сервисы  
│   ├── models/                 # Модели для сервисов
│   ├── api.py                  # FastAPI сервис
│   ├── gradio_ui.py                # Веб-интерфейс на Gradio
│   ├── Dockerfile                   # Docker-образ
│   ├── requirements.txt            # Основные зависимости
│   ├── predictor.py                # Модуль для предсказаний
│   └── bentoml_service.py     # BentoML сервис(не используется сейчас)
├── dockerignore                # Исключения для Docker
├── .gitignore                  # Исключения для Git
├── config_loader.py            # Загрузчик конфигов
├── docker-compose.yml          # Docker Compose конфигурация
├── requirements-dev.txt        # Зависимости для разработки
└── run.sh                      # Скрипт запуска (основной)
```


### Ручной запуск
```bash
# 1. Удалите старый контейнер если есть
docker rm -f metro-container 2>/dev/null || true

# 2. Пересоберите образ
docker build --no-cache -t metro-ml .

# 3. Запустите
docker run -d \
  --name metro-ml-app \
  -p 8000:8000 \
  -p 7860:7860 \
  metro-ml
```

После успешного запуска будут доступны:

| Сервис | URL | Порт | Описание |
|--------|-----|------|----------|
| **FastAPI** | http://localhost:8000 | 8000 | Основной API сервис |
| **FastAPI Docs** | http://localhost:8000/docs | 8000 | Интерактивная документация Swagger |
| **Gradio UI** | http://localhost:7860 | 7860 | Веб-интерфейс для тестирования |



### Структура конфигурации

- `configs/train_config.yaml` — параметры обучения модели
- `configs/inference_config.yaml` — параметры инференса


### Модели

- Лучшая модель: находится в `service/models/`
- Обучение: см. `notebooks/course_mlops.ipynb`
- Эксперименты: результаты в `service/models/models_summary.csv`


Проект разработан в учебных целях в рамках курса MLOps.
