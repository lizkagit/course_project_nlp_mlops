import requests
import time

# Простые тексты про метро
test_texts = [
    # Короткие
    "Метро работает отлично!",
    "Плохое расписание метро",
    "Станции чистые и удобные",
    "Очень тесно в час пик",
    
    # Средние  
    "Сегодня утром в метро было необычно пусто, возможно из-за праздника. Составы ходили по расписанию.",
    "Ремонт на кольцевой линии создает большие неудобства. Приходится делать пересадки.",
    
    # Длинные
    """Развитие метрополитена в нашем городе идет быстрыми темпами. 
    Строятся новые станции, обновляется подвижной состав, внедряются 
    современные системы оплаты проезда. Это делает поездки более 
    комфортными и безопасными для пассажиров.""",
    
    """К сожалению, в последнее время участились случаи задержек поездов 
    на красной линии. Это связано с техническими работами и обновлением 
    сигнального оборудования. Администрация метро обещает, что ситуация 
    нормализуется к концу месяца, и просит пассажиров учитывать это при 
    планировании поездок."""
]


print("\n" + "=" * 60)
print("НАЧИНАЕМ ТЕСТИРОВАНИЕ")
print("=" * 60)

# Просто тестируем первый текст
test_text = test_texts[7]

print(f"\nТестовый текст: '{test_text}'")
print("-" * 40)

# Тест FastAPI
print("\n1. Тестируем FastAPI (порт 8000):")
try:
    start = time.time()
    response = requests.post(
        "http://localhost:8000/predict",
        json={"text": test_text},
        timeout=5
    )
    fastapi_time = time.time() - start
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Успех!")
        print(f"   📊 Предсказание: {result.get('prediction', 'N/A')}")
        print(f"   ⏱️  Время: {fastapi_time:.3f} секунд")
    else:
        print(f"   ❌ Ошибка: {response.status_code}")
        print(f"   📄 Ответ: {response.text}")
except Exception as e:
    print(f"   ❌ Исключение: {e}")

# Тест BentoML  
print("\n2. Тестируем BentoML (порт 3000):")
try:
    start = time.time()
    
    # Пробуем JSON
    response = requests.post(
        "http://localhost:3000/predict",
        json={"text": test_text},
        timeout=5
    )
    
    # Если не сработало, пробуем text/plain
    if response.status_code != 200:
        response = requests.post(
            "http://localhost:3000/predict",
            data=test_text,
            headers={"Content-Type": "text/plain"},
            timeout=5
        )
    
    bentoml_time = time.time() - start
    
    if response.status_code == 200:
        result = response.json() if response.headers.get('content-type') == 'application/json' else response.text
        print(f"   ✅ Успех!")
        print(f"   📊 Результат: {result}")
        print(f"   ⏱️  Время: {bentoml_time:.3f} секунд")
    else:
        print(f"   ❌ Ошибка: {response.status_code}")
        print(f"   📄 Ответ: {response.text}")
except Exception as e:
    print(f"   ❌ Исключение: {e}")

print("\n" + "=" * 60)
print("ТЕСТИРУЕМ ЕЩЕ НЕСКОЛЬКО ТЕКСТОВ")
print("=" * 60)

# Тестируем еще несколько текстов
for i, text in enumerate(test_texts[1:4], 2):
    print(f"\n{i}. Текст: '{text[:50]}...'")
    
    # FastAPI
    try:
        response = requests.post(
            "http://localhost:8000/predict",
            json={"text": text},
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   FastAPI: {result.get('prediction', 'N/A')}")
        else:
            print(f"   FastAPI: ошибка")
    except:
        print(f"   FastAPI: не отвечает")
    
    # BentoML
    try:
        response = requests.post(
            "http://localhost:3000/predict",
            json={"text": text},
            timeout=5
        )
        if response.status_code != 200:
            response = requests.post(
                "http://localhost:3000/predict",
                data=text,
                headers={"Content-Type": "text/plain"},
                timeout=5
            )
        
        if response.status_code == 200:
            result = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"   BentoML: {result}")
        else:
            print(f"   BentoML: ошибка")
    except:
        print(f"   BentoML: не отвечает")

print("\n" + "=" * 60)
print("КАК ЭТО ЗАПУСТИТЬ:")
print("=" * 60)
print("""
1. Сохраните этот файл как test_metro_apis.py
2. Убедитесь, что сервисы запущены:
   - FastAPI: python api.py (порт 8000)
   - BentoML: bentoml serve ... (порт 3000)
3. Запустите: python test_metro_apis.py
""")

