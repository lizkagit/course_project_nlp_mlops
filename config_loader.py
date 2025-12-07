# config_loader.py

import os
import yaml
from omegaconf import OmegaConf
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class ConfigLoader:
    """Загрузчик конфигураций"""
    
    def __init__(self):
        # Определяем путь к папке configs относительно этого файла
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.configs_dir = os.path.join(current_dir, "configs")
        
        print(f"Ищу конфиги в: {self.configs_dir}")
        
        # Проверяем существование папки
        if not os.path.exists(self.configs_dir):
            print(f"Папка не найдена. Существующие файлы в {current_dir}:")
            for item in os.listdir(current_dir):
                print(f"  - {item}")
        
        # Загружаем конфигурации
        self.train_config = self._load_config("train_config.yaml")
        self.inference_config = self._load_config("inference_config.yaml")
    
    def _load_config(self, filename):
        """Загружает YAML конфигурацию"""
        filepath = os.path.join(self.configs_dir, filename)
        
        if os.path.exists(filepath):
            print(f"✅ Найден файл: {filepath}")
            with open(filepath, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)
            return OmegaConf.create(config_dict)
        else:
            raise FileNotFoundError(f"Конфигурационный файл не найден: {filepath}")
    
    def get_experiment_config(self, exp_num):
        """Получает конфиг эксперимента"""
        key = f"experiment{exp_num}"
        return self.train_config.experiments[key]
    
    def get_inference_config(self):
        """Получает настройки для инференса"""
        return self.inference_config

# Создаем глобальный объект
config = ConfigLoader()