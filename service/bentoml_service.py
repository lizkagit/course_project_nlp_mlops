import bentoml
import joblib
import os
import numpy as np
from typing import List

# Пути к моделям
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "models", "best_model.pkl")
vectorizer_path = os.path.join(current_dir, "models", "tfidf_vectorizer.pkl")

# Загружаем модель и векторайзер
model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

@bentoml.service(
    name="comment_predictor_batch",
    version="1.0.0"
)
class CommentPredictor:
    
    @bentoml.api
    def predict(self, text: str) -> dict:
        """Предсказание для одного текста"""
        try:
            features = vectorizer.transform([text])
            prediction = model.predict(features)
            return {
                "prediction": float(prediction[0]), 
                "status": "success",
                "type": "single"
            }
        except Exception as e:
            return {
                "prediction": 0.0, 
                "error": str(e), 
                "status": "error",
                "type": "single"
            }
    
    @bentoml.api
    def predict_batch(self, texts: List[str]) -> dict:
        """Batch предсказание для списка текстов"""
        try:
            # Преобразуем все тексты
            features = vectorizer.transform(texts)
            
            # Получаем предсказания для всего батча
            predictions = model.predict(features)
            
            return {
                "status": "success",
                "type": "batch",
                "total_texts": len(texts),
                "predictions": predictions.tolist(),
                "predictions_summary": {
                    "min": float(np.min(predictions)),
                    "max": float(np.max(predictions)),
                    "mean": float(np.mean(predictions)),
                    "std": float(np.std(predictions))
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "type": "batch",
                "error": str(e),
                "predictions": []
            }

    @bentoml.api
    def health(self) -> dict:
        return {
            "status": "healthy", 
            "model_loaded": True,
            "supports_batch": True
        }