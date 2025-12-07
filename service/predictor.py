import joblib
import numpy as np
from typing import Dict, Any
import time
import os
import sys

# Добавляем корень проекта в путь
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

try:
    from config_loader import config
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False
    print("⚠️ Не удалось загрузить конфигурацию")

class ModelPredictor:
    def __init__(self, model_path: str = None, vectorizer_path: str = None):
        self.model = None
        self.vectorizer = None
        self.is_loaded = False
        
        # Используем пути из конфига если не указаны
        if model_path is None and HAS_CONFIG:
            model_path = config.get_inference_config().model.model_path
        elif model_path is None:
            model_path = "service_models/best_model.pkl"
            
        if vectorizer_path is None and HAS_CONFIG:
            vectorizer_path = config.get_inference_config().model.vectorizer_path
        elif vectorizer_path is None:
            vectorizer_path = "service_models/tfidf_vectorizer.pkl"
        
        # Проверяем абсолютные пути
        if not os.path.isabs(model_path):
            model_path = os.path.join(current_dir, model_path)
        if not os.path.isabs(vectorizer_path):
            vectorizer_path = os.path.join(current_dir, vectorizer_path)
        
        print(f"🔄 Загружаю модель из: {model_path}")
        print(f"🔄 Загружаю векторайзер из: {vectorizer_path}")
        
        self.load(model_path, vectorizer_path)
    
    
    def load(self, model_path: str, vectorizer_path: str) -> bool:
        """Загружает модель и векторайзер"""
        try:
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vectorizer_path)
            self.is_loaded = True
            print(f"✅ Модель загружена успешно")
            print(f"   Тип модели: {type(self.model).__name__}")
            print(f"   Размер словаря: {len(self.vectorizer.vocabulary_)} слов")
            return True
        except Exception as e:
            print(f"❌ Ошибка загрузки модели: {e}")
            self.is_loaded = False
            return False
    
    def predict(self, text: str) -> Dict[str, Any]:
        """Делает предсказание для одного текста"""
        start_time = time.time()
        
        if not self.is_loaded:
            return {
                "prediction": 0.0,
                "error": "Model not loaded",
                "processing_time_ms": 0
            }
        
        try:
            # Преобразуем текст в фичи
            features = self.vectorizer.transform([text])
            
            # Делаем предсказание
            prediction = float(self.model.predict(features)[0])
            
            # Время обработки
            processing_time = (time.time() - start_time) * 1000
            
            return {
                "prediction": prediction,
                "processing_time_ms": round(processing_time, 2),
                "features_count": features.shape[1],
                "error": None
            }
            
        except Exception as e:
            return {
                "prediction": 0.0,
                "processing_time_ms": 0,
                "error": str(e)
            }
    
    def batch_predict(self, texts: list) -> list:
        """Предсказание для нескольких текстов"""
        return [self.predict(text) for text in texts]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Возвращает информацию о модели"""
        if not self.is_loaded:
            return {"is_loaded": False}
        
        return {
            "is_loaded": True,
            "model_type": type(self.model).__name__,
            "vocabulary_size": len(self.vectorizer.vocabulary_),
            "model_params": str(self.model.get_params()) if hasattr(self.model, 'get_params') else "Unknown"
        }