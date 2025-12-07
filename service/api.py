from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
from predictor import ModelPredictor
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# Импортируем конфигурацию
from config_loader import config
from predictor import ModelPredictor

# Получаем конфиг
inference_config = config.get_inference_config()

# Создаем FastAPI приложение
app = FastAPI(
    title=inference_config.api.title,
    description="API для предсказания количества комментариев по тексту поста",
    version=inference_config.api.version,
    docs_url=inference_config.api.docs_url,
    redoc_url=inference_config.api.redoc_url
)

# Инициализируем предиктор с конфигом
predictor = ModelPredictor(
    model_path=inference_config.model.model_path,
    vectorizer_path=inference_config.model.vectorizer_path
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

# Эндпоинты
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
        host=inference_config.server.host,
        port=inference_config.server.port,
        reload=inference_config.server.reload
    )