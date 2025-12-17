# service/gradio_ui.py - КОМПАКТНАЯ ВЕРСИЯ
import gradio as gr
import requests
import time
from typing import Dict, List
import plotly.graph_objects as go
import pandas as pd
import os

class MetroPredictor:
    def __init__(self):
        self.api_url = os.getenv("API_URL", "http://localhost:8000")
        self.history = []
        print(f"🌐 API: {self.api_url}")
    
    def predict_single(self, text: str) -> Dict:
        """Предсказание для одного текста"""
        if not text.strip():
            return {"error": "Введите текст"}
        
        start_time = time.perf_counter()
        
        try:
            response = requests.post(
                f"{self.api_url}/predict",
                json={"text": text},
                timeout=5
            )
            
            latency = (time.perf_counter() - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                
                # Добавляем в историю
                self.history.append({
                    "type": "single",
                    "text": text[:50],
                    "latency_ms": round(latency, 2),
                    "prediction": result.get("prediction", 0)
                })
                
                return {
                    "status": "success",
                    "prediction": round(float(result.get("prediction", 0)), 1),
                    "latency_ms": round(latency, 2)
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def predict_batch(self, texts: List[str]) -> Dict:
        """Batch предсказание"""
        if not texts:
            return {"error": "Введите тексты"}
        
        start_time = time.perf_counter()
        
        try:
            response = requests.post(
                f"{self.api_url}/predict/batch",
                json={"texts": texts},
                timeout=10
            )
            
            total_latency = (time.perf_counter() - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                
                # Добавляем КАЖДЫЙ текст из батча в историю
                predictions = result.get("predictions", [])
                for i, pred in enumerate(predictions):
                    if i < len(texts):
                        self.history.append({
                            "type": "batch",
                            "text": texts[i][:50],
                            "latency_ms": round(total_latency / len(texts), 2),  # Среднее время на текст
                            "prediction": pred.get("prediction", 0)
                        })
                
                return {
                    "status": "success",
                    "total_texts": len(texts),
                    "total_latency_ms": round(total_latency, 2),
                    "avg_latency_per_text": round(total_latency / len(texts), 2)
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def create_latency_chart(self):
        """Создает график latency (и single и batch)"""
        if not self.history:
            fig = go.Figure()
            fig.update_layout(
                title="Запустите предсказания",
                xaxis_title="Номер запроса",
                yaxis_title="Latency (мс)",
                template="plotly_white"
            )
            return fig
        
        indices = list(range(len(self.history)))
        latencies = [h["latency_ms"] for h in self.history]
        types = [h["type"] for h in self.history]
        
        fig = go.Figure()
        
        # Добавляем точки разных цветов для single и batch
        single_indices = [i for i, t in enumerate(types) if t == "single"]
        batch_indices = [i for i, t in enumerate(types) if t == "batch"]
        
        if single_indices:
            fig.add_trace(go.Scatter(
                x=[i for i in single_indices],
                y=[latencies[i] for i in single_indices],
                mode='markers',
                name='Single',
                marker=dict(color='blue', size=10)
            ))
        
        if batch_indices:
            fig.add_trace(go.Scatter(
                x=[i for i in batch_indices],
                y=[latencies[i] for i in batch_indices],
                mode='markers',
                name='Batch',
                marker=dict(color='red', size=10)
            ))
        
        # Линия тренда
        if len(latencies) > 1:
            fig.add_trace(go.Scatter(
                x=indices,
                y=pd.Series(latencies).rolling(window=3, min_periods=1).mean(),
                mode='lines',
                name='Тренд',
                line=dict(color='green', width=2, dash='dash')
            ))
        
        fig.update_layout(
            title=f"Latency запросов (всего: {len(self.history)})",
            xaxis_title="Номер запроса",
            yaxis_title="Latency (мс)",
            showlegend=True,
            template="plotly_white",
            height=400
        )
        
        return fig
    
    def get_stats(self) -> Dict:
        """Статистика"""
        if not self.history:
            return {"total": 0}
        
        latencies = [h["latency_ms"] for h in self.history]
        single_count = len([h for h in self.history if h["type"] == "single"])
        batch_count = len([h for h in self.history if h["type"] == "batch"])
        
        return {
            "total_requests": len(self.history),
            "single_requests": single_count,
            "batch_requests": batch_count,
            "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
            "max_latency_ms": round(max(latencies), 2),
            "min_latency_ms": round(min(latencies), 2)
        }

# Инициализация
predictor = MetroPredictor()

# Создаем интерфейс
with gr.Blocks(title="Метро Москвы: Предсказание комментариев") as demo:
    
    gr.Markdown("# 🚇 Метро Москвы: Предсказание комментариев")
    
    with gr.Row():
        with gr.Column():
            # Single prediction
            gr.Markdown("## 📝 Одиночное предсказание")
            single_text = gr.Textbox(
                label="Текст поста",
                placeholder="Введите текст про метро...",
                lines=3
            )
            single_btn = gr.Button("🔮 Предсказать", variant="primary")
            single_result = gr.JSON(label="Результат")
            
            # Batch prediction
            gr.Markdown("## 📚 Batch предсказание")
            batch_texts = gr.Textbox(
                label="Тексты (каждый с новой строки)",
                placeholder="Текст 1\nТекст 2\nТекст 3",
                lines=4
            )
            batch_btn = gr.Button("📊 Batch анализ", variant="secondary")
            batch_result = gr.JSON(label="Batch результат")
        
        with gr.Column():
            # Статистика
            gr.Markdown("## 📊 Статистика")
            stats_display = gr.JSON(
                label="Статистика запросов",
                value=predictor.get_stats()
            )
            
            # График
            gr.Markdown("## 📈 График latency")
            latency_chart = gr.Plot(label="Время ответа")
    
    # Примеры
    gr.Markdown("## 🎯 Примеры")
    examples = gr.Examples(
        examples=[
            ["Новая станция метро открылась сегодня!"],
            ["Ужасные пробки на кольцевой линии"],
            ["Бесплатный Wi-Fi в метро работает отлично"]
        ],
        inputs=single_text
    )
    
    # Обработчики
    def handle_single(text):
        result = predictor.predict_single(text)
        return result, predictor.create_latency_chart(), predictor.get_stats()
    
    def handle_batch(texts):
        text_list = [t.strip() for t in texts.split('\n') if t.strip()]
        result = predictor.predict_batch(text_list)
        return result, predictor.create_latency_chart(), predictor.get_stats()
    
    single_btn.click(
        fn=handle_single,
        inputs=[single_text],
        outputs=[single_result, latency_chart, stats_display]
    )
    
    batch_btn.click(
        fn=handle_batch,
        inputs=[batch_texts],
        outputs=[batch_result, latency_chart, stats_display]
    )
    
    # Автозагрузка графика
    demo.load(
        fn=lambda: predictor.create_latency_chart(),
        inputs=[],
        outputs=[latency_chart]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)