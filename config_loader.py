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
            
            # Сначала загружаем через yaml
            with open(filepath, 'r', encoding='utf-8') as f:
                yaml_content = yaml.safe_load(f)
            
            # Затем преобразуем в OmegaConf
            return OmegaConf.create(yaml_content)
        else:
            raise FileNotFoundError(f"Конфигурационный файл не найден: {filepath}")
    
    def get_experiment_config(self, exp_num):
        """Получает конфиг эксперимента как словарь Python"""
        key = f"experiment{exp_num}"
        
        # Проверяем существование эксперимента
        if key not in self.train_config.experiments:
            raise KeyError(f"Эксперимент {exp_num} не найден в конфиге")
        
        # Преобразуем в словарь
        exp_config = OmegaConf.to_container(self.train_config.experiments[key], resolve=True)
        
        # Дополнительная проверка на обязательные поля
        required_fields = ['name', 'type', 'dataset']
        for field in required_fields:
            if field not in exp_config:
                raise KeyError(f"Отсутствует обязательное поле '{field}' в эксперименте {exp_num}")
        
        return exp_config
    
    def get_experiment_config_omegaconf(self, exp_num):
        """Получает конфиг эксперимента как OmegaConf объект"""
        key = f"experiment{exp_num}"
        
        if key not in self.train_config.experiments:
            raise KeyError(f"Эксперимент {exp_num} не найден в конфиге")
        
        return self.train_config.experiments[key]
    
    def get_dataset_info(self, dataset_name):
        """Получает информацию о датасете"""
        if dataset_name not in self.train_config.datasets:
            raise KeyError(f"Датасет {dataset_name} не найден в конфиге")
        
        return OmegaConf.to_container(self.train_config.datasets[dataset_name], resolve=True)
    
    def get_inference_config(self):
        """Получает настройки для инференса"""
        return self.inference_config
    
    def get_training_params(self):
        """Получает общие параметры обучения"""
        return OmegaConf.to_container(self.train_config.training, resolve=True)

# Создаем глобальный объект
config = ConfigLoader()