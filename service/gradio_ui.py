import gradio as gr
import requests
import time
import json

class MLServiceClient:
    def __init__(self):
        self.fastapi_url = "http://localhost:8000"
        self.bentoml_url = "http://localhost:3000"

    def predict_fastapi_single(self, text):
        try:
            start = time.time()
            response = requests.post(f"{self.fastapi_url}/predict", json={"text": text}, timeout=5)
            latency = round((time.time() - start) * 1000, 1)
            return {**response.json(), "service": "FastAPI", "type": "single", "latency_ms": latency} if response.status_code == 200 else {"error": f"HTTP {response.status_code}", "service": "FastAPI"}
        except Exception as e:
            return {"error": str(e), "service": "FastAPI"}

    def predict_bentoml_single(self, text):
        try:
            start = time.time()
            response = requests.post(f"{self.bentoml_url}/predict", data=text, headers={"Content-Type": "text/plain"}, timeout=5)
            if response.status_code != 200:
                response = requests.post(f"{self.bentoml_url}/predict", json={"text": text}, timeout=5)
            latency = round((time.time() - start) * 1000, 1)
            return {**response.json(), "latency_ms": latency, "service": "BentoML"} if response.status_code == 200 else {"error": f"HTTP {response.status_code}: {response.text[:100]}", "service": "BentoML"}
        except Exception as e:
            return {"error": str(e), "service": "BentoML"}

    def predict_fastapi_batch(self, texts):
        try:
            start = time.time()
            response = requests.post(f"{self.fastapi_url}/predict/batch", json={"texts": texts}, timeout=10)
            latency = round((time.time() - start) * 1000, 1)
            return {**response.json(), "service": "FastAPI", "type": "batch", "latency_ms": latency, "texts_count": len(texts)} if response.status_code == 200 else {"error": f"HTTP {response.status_code}", "service": "FastAPI"}
        except Exception as e:
            return {"error": str(e), "service": "FastAPI"}

    def predict_bentoml_batch(self, texts):
        try:
            start = time.time()
            response = requests.post(f"{self.bentoml_url}/predict_batch", json={"texts": texts}, timeout=10)
            latency = round((time.time() - start) * 1000, 1)
            return {**response.json(), "service": "BentoML", "type": "batch", "latency_ms": latency, "texts_count": len(texts)} if response.status_code == 200 else {"error": f"HTTP {response.status_code}", "service": "BentoML"}
        except Exception as e:
            return {"error": str(e), "service": "BentoML"}

client = MLServiceClient()

def test_single_prediction(text):
    if not text.strip():
        return {}, {}, {}

    fastapi_result = client.predict_fastapi_single(text)
    bentoml_result = client.predict_bentoml_single(text)

    fast_lat = fastapi_result.get("latency_ms", float('inf'))
    bento_lat = bentoml_result.get("latency_ms", float('inf'))

    comparison = {
        "test_type": "single",
        "fastapi_latency": fast_lat,
        "bentoml_latency": bento_lat,
        "faster_service": "FastAPI" if fast_lat < bento_lat else "BentoML",
        "difference_ms": round(abs(fast_lat - bento_lat), 1)
    }

    return fastapi_result, bentoml_result, comparison

def test_batch_prediction(texts_input):
    if not texts_input.strip():
        return {}, {}, {}

    texts = [t.strip() for t in texts_input.split('\n') if t.strip()]
    if len(texts) < 2:
        return {"error": "Нужно минимум 2 текста"}, {"error": "Нужно минимум 2 текста"}, {}

    fastapi_result = client.predict_fastapi_batch(texts)
    bentoml_result = client.predict_bentoml_batch(texts)

    fast_lat = fastapi_result.get("latency_ms", 0)
    bento_lat = bentoml_result.get("latency_ms", 0)

    comparison = {
        "test_type": "batch",
        "texts_count": len(texts),
        "fastapi_latency": fast_lat,
        "bentoml_latency": bento_lat,
        "avg_time_per_text": {
            "FastAPI": round(fast_lat / len(texts), 2) if fast_lat > 0 else 0,
            "BentoML": round(bento_lat / len(texts), 2) if bento_lat > 0 else 0
        }
    }

    if fast_lat > 0 and bento_lat > 0:
        if fast_lat < bento_lat:
            comparison.update({
                "faster_service": "FastAPI",
                "difference_ms": round(bento_lat - fast_lat, 1),
                "difference_percent": round((bento_lat - fast_lat) / bento_lat * 100, 1)
            })
        else:
            comparison.update({
                "faster_service": "BentoML",
                "difference_ms": round(fast_lat - bento_lat, 1),
                "difference_percent": round((fast_lat - bento_lat) / fast_lat * 100, 1)
            })

    return fastapi_result, bentoml_result, comparison

batch_examples = """Метро работает отлично!
Пробки сегодня невыносимые
Новые станции очень красивые
В час пик не протолкнуться
Электрички ходят по расписанию
Парковка в центре - катастрофа
Общественный транспорт становится лучше
Цены на проезд слишком высокие"""

with gr.Blocks(title="ML Services Comparison") as demo:
    gr.Markdown("# Сравнение FastAPI и BentoML")
    gr.Markdown("Тестирование single и batch предсказаний")

    with gr.Tabs():
        with gr.TabItem("Single Prediction"):
            gr.Markdown("## 📝 Single Prediction (один текст)")
            single_text = gr.Textbox(label="Введите текст", placeholder="Пример: Метро сегодня работает отлично!", lines=3)
            single_btn = gr.Button("🚀 Тестировать Single", variant="primary")

            with gr.Row():
                single_fastapi = gr.JSON(label="FastAPI результат")
                single_bentoml = gr.JSON(label="BentoML результат")

            single_comparison = gr.JSON(label="⚖️ Сравнение")

            single_btn.click(test_single_prediction, inputs=single_text, outputs=[single_fastapi, single_bentoml, single_comparison])

            gr.Examples(
                examples=[
                    ["Метро работает отлично, поезда ходят по расписанию!"],
                    ["Ужасные пробки на кольцевой линии"],
                    ["Новые поезда очень комфортные и современные"],
                    ["В час пик в метро настоящий ад"]
                ],
                inputs=single_text
            )

        with gr.TabItem("Batch Prediction"):
            gr.Markdown("## 📚 Batch Prediction (несколько текстов)")
            gr.Markdown("Введите тексты, каждый с новой строки")
            batch_texts = gr.Textbox(label="Тексты (по одному на строку)", placeholder="Введите несколько текстов...", lines=8, value=batch_examples)
            batch_btn = gr.Button("🚀 Тестировать Batch", variant="primary")

            with gr.Row():
                batch_fastapi = gr.JSON(label="FastAPI batch результат")
                batch_bentoml = gr.JSON(label="BentoML batch результат")

            batch_comparison = gr.JSON(label="⚖️ Сравнение batch")

            batch_btn.click(test_batch_prediction, inputs=batch_texts, outputs=[batch_fastapi, batch_bentoml, batch_comparison])

            gr.Markdown("### 📊 Batch метрики:")
            gr.Markdown("""
            - **Total texts**: общее количество текстов
            - **Latency**: общее время обработки (мс)
            - **Avg time per text**: среднее время на один текст
            - **Throughput**: текстов в секунду
            - **Predictions summary**: статистика предсказаний (min, max, mean, std)
            """)

        with gr.TabItem("Диагностика"):
            gr.Markdown("## 🩺 Проверка сервисов")

            def check_services():
                results = {"FastAPI": {"status": "❌ Недоступен"}, "BentoML": {"status": "🔧 Проверяется при запросах", "urls": {"single_predict": "POST http://localhost:3000/predict", "batch_predict": "POST http://localhost:3000/predict_batch"}}}

                try:
                    resp = requests.get("http://localhost:8000/health", timeout=3)
                    results["FastAPI"] = {"status": "✅ Доступен" if resp.status_code == 200 else "❌ Ошибка", "code": resp.status_code, "docs": "http://localhost:8000/docs"}
                except:
                    pass

                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex(('localhost', 3000))
                    sock.close()
                    results["BentoML"]["port_check"] = "✅ Порт 3000 открыт" if result == 0 else "❌ Порт 3000 закрыт"
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
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
