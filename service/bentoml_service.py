import bentoml
import joblib
import os

# Пути к моделям
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "models", "best_model.pkl")
vectorizer_path = os.path.join(current_dir, "models", "tfidf_vectorizer.pkl")

# Загружаем модель и векторайзер
model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

@bentoml.service(
    name="comment_predictor",
    version="1.0.0"
)
class CommentPredictor:
    
    @bentoml.api
    def predict(self, text: str) -> dict:
        """Делает предсказание для текста."""
        try:
            features = vectorizer.transform([text])
            prediction = model.predict(features)
            return {"prediction": float(prediction[0]), "status": "success"}
        except Exception as e:
            return {"prediction": 0.0, "error": str(e), "status": "error"}

    @bentoml.api
    def health(self) -> dict:
        return {"status": "healthy", "model_loaded": True}