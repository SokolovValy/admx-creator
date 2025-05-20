import yaml
from pathlib import Path

def load_policies(config_path: str) -> dict:
    """Загружает и валидирует конфигурацию"""
    default_config = {
        "namespace": {
            "prefix": "alt",
            "uri": "ALT.Policies.1.0"
        },
        "policies": []
    }
    
    if not Path(config_path).exists():
        return default_config
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or default_config
        
        # Базовая валидация структуры
        if not isinstance(config.get("policies", []), list):
            config["policies"] = []
            
        # Добавляем тип по умолчанию для существующих политик
        for policy in config["policies"]:
            if "type" not in policy:
                policy["type"] = "boolean"
                
        return config
        
    except Exception as e:
        print(f"Ошибка загрузки конфига: {e}. Используется конфиг по умолчанию.")
        return default_config

def save_policies(config_path: str, data: dict):
    """Сохраняет конфиг в YAML"""
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)