from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
import sys

# Добавляем путь к конфигам
current_dir = os.path.dirname(os.path.abspath(__file__))
configs_dir = os.path.join(current_dir, "..", "configs")
sys.path.insert(0, configs_dir)

# Пытаемся загрузить конфигурацию
try:
    from config_loader import config
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False
    print("⚠️ config_loader не найден, используем значения по умолчанию")

# Инициализируем предиктор
from predictor import ModelPredictor

# Создаем FastAPI приложение
app = FastAPI(
    title="NLP MLOps API",
    description="API для предсказания количества комментариев по тексту поста",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Пути к моделям по умолчанию
DEFAULT_MODEL_PATH = os.path.join(current_dir, "models", "best_model.pkl")
DEFAULT_VECTORIZER_PATH = os.path.join(current_dir, "models", "tfidf_vectorizer.pkl")

# Получаем пути из конфига или используем значения по умолчанию
if HAS_CONFIG:
    try:
        inference_config = config.get_inference_config()
        model_path = inference_config.model.model_path
        vectorizer_path = inference_config.model.vectorizer_path
        print(f"📁 Используем пути из конфига:")
        print(f"   Модель: {model_path}")
        print(f"   Векторайзер: {vectorizer_path}")
    except Exception as e:
        print(f"⚠️ Ошибка загрузки конфига: {e}")
        model_path = DEFAULT_MODEL_PATH
        vectorizer_path = DEFAULT_VECTORIZER_PATH
else:
    model_path = DEFAULT_MODEL_PATH
    vectorizer_path = DEFAULT_VECTORIZER_PATH
    print(f"📁 Используем пути по умолчанию:")
    print(f"   Модель: {model_path}")
    print(f"   Векторайзер: {vectorizer_path}")

# Проверяем существование файлов
print(f"🔍 Проверяем наличие файлов моделей:")
print(f"   Модель существует: {os.path.exists(model_path)}")
print(f"   Векторайзер существует: {os.path.exists(vectorizer_path)}")

# Инициализируем предиктор
predictor = ModelPredictor(
    model_path=model_path,
    vectorizer_path=vectorizer_path
)

# Модели данных (Pydantic схемы)
class PredictRequest(BaseModel):
    """Запрос для предсказания"""
    text: str
    model_type: Optional[str] = "ridge"

class PredictResponse(BaseModel):
    """Ответ с предсказанием"""
    prediction: float
    processing_time_ms: float
    features_count: Optional[int] = None
    error: Optional[str] = None

class BatchPredictRequest(BaseModel):
    """Запрос для batch предсказаний"""
    texts: List[str]

class HealthResponse(BaseModel):
    """Ответ для health check"""
    status: str
    model_loaded: bool
    model_type: Optional[str] = None

# Эндпоинты (оставляем без изменений)
@app.get("/", tags=["Root"])
async def root():
    """Корневой эндпоинт"""
    return {
        "service": "Comment Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "documentation": "/docs",
            "health_check": "/health",
            "single_prediction": "/predict",
            "batch_prediction": "/predict/batch"
        }
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Проверка здоровья сервиса"""
    info = predictor.get_model_info()
    return HealthResponse(
        status="healthy" if info["is_loaded"] else "degraded",
        model_loaded=info["is_loaded"],
        model_type=info.get("model_type")
    )

@app.post("/predict", response_model=PredictResponse, tags=["Prediction"])
async def predict_single(request: PredictRequest):
    """Предсказание для одного текста"""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    result = predictor.predict(request.text)
    
    if result["error"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return PredictResponse(**result)

@app.post("/predict/batch", tags=["Prediction"])
async def predict_batch(request: BatchPredictRequest):
    """Предсказание для нескольких текстов"""
    if not request.texts:
        raise HTTPException(status_code=400, detail="Texts list cannot be empty")
    
    results = predictor.batch_predict(request.texts)
    return {"predictions": results}

@app.get("/model/info", tags=["Model"])
async def model_info():
    """Информация о загруженной модели"""
    return predictor.get_model_info()

# Запуск сервера
if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )