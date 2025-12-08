import joblib
import numpy as np
from typing import Dict, Any
import time
import os

class ModelPredictor:
    def __init__(self, model_path: str, vectorizer_path: str):
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        self.model = None
        self.vectorizer = None
        self.is_loaded = False
        
        print(f"🔄 Инициализация предиктора:")
        print(f"   Путь к модели: {model_path}")
        print(f"   Путь к векторайзеру: {vectorizer_path}")
        
        self.load()
    
    def load(self) -> bool:
        """Загружает модель и векторайзер"""
        try:
            print(f"🔍 Загружаю модель...")
            self.model = joblib.load(self.model_path)
            print(f"✅ Модель загружена")
            
            print(f"🔍 Загружаю векторайзер...")
            self.vectorizer = joblib.load(self.vectorizer_path)
            print(f"✅ Векторайзер загружен")
            
            self.is_loaded = True
            print(f"🎯 Модель готова к работе!")
            print(f"   Тип модели: {type(self.model).__name__}")
            print(f"   Размер словаря: {len(self.vectorizer.vocabulary_) if hasattr(self.vectorizer, 'vocabulary_') else 'N/A'}")
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
        
        info = {
            "is_loaded": True,
            "model_type": type(self.model).__name__,
            "model_path": self.model_path,
            "vectorizer_path": self.vectorizer_path
        }
        
        if hasattr(self.vectorizer, 'vocabulary_'):
            info["vocabulary_size"] = len(self.vectorizer.vocabulary_)
        
        if hasattr(self.model, 'get_params'):
            info["model_params"] = str(self.model.get_params())
        
        return info