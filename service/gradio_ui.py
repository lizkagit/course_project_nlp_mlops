import gradio as gr
import requests
import time
import json

class MLServiceClient:
    """Клиент для работы с ML сервисами"""
    
    def __init__(self):
        self.fastapi_url = "http://localhost:8000"
        self.bentoml_url = "http://localhost:3000"
    
    def predict_fastapi_single(self, text):
        """Single prediction через FastAPI"""
        try:
            start = time.time()
            response = requests.post(
                f"{self.fastapi_url}/predict",
                json={"text": text},
                timeout=5
            )
            latency = time.time() - start
            
            if response.status_code == 200:
                result = response.json()
                result["service"] = "FastAPI"
                result["type"] = "single"
                result["latency_ms"] = round(latency * 1000, 1)
                return result
            return {"error": f"HTTP {response.status_code}", "service": "FastAPI"}
        except Exception as e:
            return {"error": str(e), "service": "FastAPI"}
    
    def predict_bentoml_single(self, text):
        
        try:
            start = time.time()
            
            # СНАЧАЛА пробуем text/plain (основной вариант)
            response = requests.post(
                "http://localhost:3000/predict",
                data=text,  # data=, не json=
                headers={"Content-Type": "text/plain"},
                timeout=5
            )
            
            # Если не сработало, пробуем JSON
            if response.status_code != 200:
                response = requests.post(
                    "http://localhost:3000/predict",
                    json={"text": text},  # json=
                    timeout=5
                )
            
            latency = time.time() - start
            
            if response.status_code == 200:
                result = response.json()
                result["latency_ms"] = round(latency * 1000, 1)
                result["service"] = "BentoML"
                return result
            else:
                return {
                    "error": f"HTTP {response.status_code}: {response.text[:100]}",
                    "service": "BentoML"
                }
                
        except Exception as e:
            return {"error": str(e), "service": "BentoML"}
        
    def predict_fastapi_batch(self, texts):
        """Batch prediction через FastAPI"""
        try:
            start = time.time()
            response = requests.post(
                f"{self.fastapi_url}/predict/batch",
                json={"texts": texts},
                timeout=10
            )
            latency = time.time() - start
            
            if response.status_code == 200:
                result = response.json()
                result["service"] = "FastAPI"
                result["type"] = "batch"
                result["latency_ms"] = round(latency * 1000, 1)
                result["texts_count"] = len(texts)
                return result
            return {"error": f"HTTP {response.status_code}", "service": "FastAPI"}
        except Exception as e:
            return {"error": str(e), "service": "FastAPI"}
    
    def predict_bentoml_batch(self, texts):
        """Batch prediction через BentoML"""
        try:
            start = time.time()
            response = requests.post(
                f"{self.bentoml_url}/predict_batch",
                json={"texts": texts},
                timeout=10
            )
            latency = time.time() - start
            
            if response.status_code == 200:
                result = response.json()
                result["service"] = "BentoML"
                result["type"] = "batch"
                result["latency_ms"] = round(latency * 1000, 1)
                result["texts_count"] = len(texts)
                return result
            return {"error": f"HTTP {response.status_code}", "service": "BentoML"}
        except Exception as e:
            return {"error": str(e), "service": "BentoML"}

# Создаем клиент
client = MLServiceClient()

def test_single_prediction(text):
    """Тест single prediction"""
    if not text.strip():
        return {}, {}, {}
    
    fastapi_result = client.predict_fastapi_single(text)
    bentoml_result = client.predict_bentoml_single(text)
    
    # Сравнение
    comparison = {
        "test_type": "single",
        "fastapi_latency": fastapi_result.get("latency_ms", 0),
        "bentoml_latency": bentoml_result.get("latency_ms", 0),
        "faster_service": ""
    }
    
    fast_lat = fastapi_result.get("latency_ms", float('inf'))
    bento_lat = bentoml_result.get("latency_ms", float('inf'))
    
    if fast_lat < bento_lat:
        comparison["faster_service"] = "FastAPI"
        comparison["difference_ms"] = round(bento_lat - fast_lat, 1)
    else:
        comparison["faster_service"] = "BentoML"
        comparison["difference_ms"] = round(fast_lat - bento_lat, 1)
    
    return fastapi_result, bentoml_result, comparison

def test_batch_prediction(texts_input):
    """Тест batch prediction"""
    if not texts_input.strip():
        return {}, {}, {}
    
    # Разбиваем текст на строки
    texts = [t.strip() for t in texts_input.split('\n') if t.strip()]
    
    if len(texts) < 2:
        return {"error": "Нужно минимум 2 текста"}, {"error": "Нужно минимум 2 текста"}, {}
    
    fastapi_result = client.predict_fastapi_batch(texts)
    bentoml_result = client.predict_bentoml_batch(texts)
    
    # Сравнение
    comparison = {
        "test_type": "batch",
        "texts_count": len(texts),
        "fastapi_latency": fastapi_result.get("latency_ms", 0),
        "bentoml_latency": bentoml_result.get("latency_ms", 0),
        "avg_time_per_text": {}
    }
    
    fast_lat = fastapi_result.get("latency_ms", 0)
    bento_lat = bentoml_result.get("latency_ms", 0)
    
    if fast_lat > 0 and bento_lat > 0:
        comparison["avg_time_per_text"] = {
            "FastAPI": round(fast_lat / len(texts), 2),
            "BentoML": round(bento_lat / len(texts), 2)
        }
        
        if fast_lat < bento_lat:
            comparison["faster_service"] = "FastAPI"
            comparison["difference_ms"] = round(bento_lat - fast_lat, 1)
            comparison["difference_percent"] = round((bento_lat - fast_lat) / bento_lat * 100, 1)
        else:
            comparison["faster_service"] = "BentoML"
            comparison["difference_ms"] = round(fast_lat - bento_lat, 1)
            comparison["difference_percent"] = round((fast_lat - bento_lat) / fast_lat * 100, 1)
    
    return fastapi_result, bentoml_result, comparison

# Примеры текстов для batch теста
batch_examples = """Метро работает отлично!
Пробки сегодня невыносимые
Новые станции очень красивые
В час пик не протолкнуться
Электрички ходят по расписанию
Парковка в центре - катастрофа
Общественный транспорт становится лучше
Цены на проезд слишком высокие"""

# Создаем интерфейс с вкладками
with gr.Blocks(title="ML Services Comparison") as demo:
    
    gr.Markdown("#Сравнение FastAPI и BentoML")
    gr.Markdown("Тестирование single и batch предсказаний")
    
    with gr.Tabs():
        # Вкладка 1: Single prediction
        with gr.TabItem("Single Prediction"):
            gr.Markdown("## 📝 Single Prediction (один текст)")
            
            single_text = gr.Textbox(
                label="Введите текст",
                placeholder="Пример: Метро сегодня работает отлично!",
                lines=3
            )
            
            single_btn = gr.Button("🚀 Тестировать Single", variant="primary")
            
            with gr.Row():
                single_fastapi = gr.JSON(label="FastAPI результат")
                single_bentoml = gr.JSON(label="BentoML результат")
            
            single_comparison = gr.JSON(label="⚖️ Сравнение")
            
            single_btn.click(
                fn=test_single_prediction,
                inputs=single_text,
                outputs=[single_fastapi, single_bentoml, single_comparison]
            )
            
            gr.Examples(
                examples=[
                    ["Метро работает отлично, поезда ходят по расписанию!"],
                    ["Ужасные пробки на кольцевой линии"],
                    ["Новые поезда очень комфортные и современные"],
                    ["В час пик в метро настоящий ад"]
                ],
                inputs=single_text
            )
        
        # Вкладка 2: Batch prediction
        with gr.TabItem("Batch Prediction"):
            gr.Markdown("## 📚 Batch Prediction (несколько текстов)")
            gr.Markdown("Введите тексты, каждый с новой строки")
            
            batch_texts = gr.Textbox(
                label="Тексты (по одному на строку)",
                placeholder="Введите несколько текстов...",
                lines=8,
                value=batch_examples
            )
            
            batch_btn = gr.Button("🚀 Тестировать Batch", variant="primary")
            
            with gr.Row():
                batch_fastapi = gr.JSON(label="FastAPI batch результат")
                batch_bentoml = gr.JSON(label="BentoML batch результат")
            
            batch_comparison = gr.JSON(label="⚖️ Сравнение batch")
            
            batch_btn.click(
                fn=test_batch_prediction,
                inputs=batch_texts,
                outputs=[batch_fastapi, batch_bentoml, batch_comparison]
            )
            
            gr.Markdown("### 📊 Batch метрики:")
            gr.Markdown("""
            - **Total texts**: общее количество текстов
            - **Latency**: общее время обработки (мс)
            - **Avg time per text**: среднее время на один текст
            - **Throughput**: текстов в секунду
            - **Predictions summary**: статистика предсказаний (min, max, mean, std)
            """)
        
        # Вкладка 3: Диагностика
        with gr.TabItem("Диагностика"):
            gr.Markdown("## 🩺 Проверка сервисов")
            
            def check_services():
                          
                results = {}
                
                # FastAPI - проверяем нормально
                try:
                    resp = requests.get("http://localhost:8000/health", timeout=3)
                    results["FastAPI"] = {
                        "status": "✅ Доступен" if resp.status_code == 200 else "❌ Ошибка",
                        "code": resp.status_code,
                        "has_health": True,
                        "docs": "http://localhost:8000/docs"
                    }
                except:
                    results["FastAPI"] = {
                        "status": "❌ Недоступен",
                        "has_health": True
                    }
                
                # BentoML - не проверяем health, проверяем работоспособность через тестовый запрос
                results["BentoML"] = {
                    "status": "🔧 Проверяется при запросах",
                    "note": "BentoML не имеет стандартного /health endpoint",
                    "check_method": "Тестовый POST запрос на /predict",
                    "urls": {
                        "single_predict": "POST http://localhost:3000/predict",
                        "batch_predict": "POST http://localhost:3000/predict_batch"
                    }
                }
                
                # Дополнительно: проверяем доступность порта
                try:
                    # Просто проверяем что порт открыт
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex(('localhost', 3000))
                    sock.close()
                    
                    if result == 0:
                        results["BentoML"]["port_check"] = "✅ Порт 3000 открыт"
                    else:
                        results["BentoML"]["port_check"] = "❌ Порт 3000 закрыт"
                except:
                    results["BentoML"]["port_check"] = "⚠️ Не удалось проверить порт"
                
                return results
            gr.Markdown("### 📋 Примеры batch запросов:")
            gr.Markdown("""
            ```bash
            # FastAPI batch
            curl -X POST http://localhost:8000/predict/batch \\
              -H "Content-Type: application/json" \\
              -d '{"texts": ["Текст 1", "Текст 2", "Текст 3"]}'
            
            # BentoML batch  
            curl -X POST http://localhost:3000/predict_batch \\
              -H "Content-Type: application/json" \\
              -d '{"texts": ["Текст 1", "Текст 2", "Текст 3"]}'
            
            # BentoML single (text/plain)
            curl -X POST http://localhost:3000/predict \\
              -H "Content-Type: text/plain" \\
              -d "Текст для предсказания"
            ```
            """)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )