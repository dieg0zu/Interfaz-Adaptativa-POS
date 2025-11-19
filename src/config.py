import os
import json

CONFIG_FILE = "data/config.json"

def cargar_config():
    """Carga la configuración del sistema"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # Configuración por defecto
    config = {
        "adaptacion_activa": True
    }
    guardar_config(config)
    return config

def guardar_config(config):
    """Guarda la configuración del sistema"""
    os.makedirs("data", exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def obtener_estado_adaptacion():
    """Obtiene el estado actual de la adaptación"""
    config = cargar_config()
    return config.get("adaptacion_activa", True)

def establecer_estado_adaptacion(activa):
    """Establece el estado de la adaptación"""
    config = cargar_config()
    config["adaptacion_activa"] = activa
    guardar_config(config)
    return activa

