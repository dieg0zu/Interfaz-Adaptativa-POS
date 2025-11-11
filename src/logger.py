import csv
from datetime import datetime
import os
import pandas as pd

def registrar_evento(tipo_evento, duracion, exito=True):
    """
    Registra un evento y actualiza las métricas de sesión acumuladas.
    Formato compatible con Dataset_POS.csv
    """
    os.makedirs("data", exist_ok=True)
    
    archivo_sesion = "data/dataset_pos.csv"
    
    # Verificar si existe el archivo de sesión
    if not os.path.exists(archivo_sesion):
        # Crear archivo con formato del dataset
        with open(archivo_sesion, "w", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["SesionID", "TiempoPromedioAccion(s)", "ErroresSesion", "TareasCompletadas", "NivelClasificado"])
            # Inicializar con valores por defecto (novato)
            writer.writerow(["S_ACTUAL", 0, 0, 0, "Novato"])
        print("[LOGGER] Archivo de sesión creado con valores iniciales")
    
    # Leer datos actuales
    df = pd.read_csv(archivo_sesion)
    
    # Obtener métricas actuales
    if len(df) > 0:
        tiempo_actual = pd.to_numeric(df['TiempoPromedioAccion(s)'].iloc[0], errors='coerce') or 0
        errores_actual = pd.to_numeric(df['ErroresSesion'].iloc[0], errors='coerce') or 0
        tareas_actual = pd.to_numeric(df['TareasCompletadas'].iloc[0], errors='coerce') or 0
        
        # Convertir NaN a 0
        if pd.isna(tiempo_actual):
            tiempo_actual = 0
        if pd.isna(errores_actual):
            errores_actual = 0
        if pd.isna(tareas_actual):
            tareas_actual = 0
            
        eventos_totales = int(errores_actual) + int(tareas_actual)
    else:
        tiempo_actual = 0
        errores_actual = 0
        tareas_actual = 0
        eventos_totales = 0
    
    # Actualizar métricas
    if exito:
        tareas_actual += 1
    else:
        errores_actual += 1
    
    eventos_totales += 1
    
    # Calcular nuevo tiempo promedio (promedio ponderado)
    if eventos_totales == 1:
        tiempo_nuevo = duracion
    else:
        tiempo_nuevo = ((tiempo_actual * (eventos_totales - 1)) + duracion) / eventos_totales
    
    # Actualizar archivo (sobreescribir)
    with open(archivo_sesion, "w", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["SesionID", "TiempoPromedioAccion(s)", "ErroresSesion", "TareasCompletadas", "NivelClasificado"])
        writer.writerow(["S_ACTUAL", round(tiempo_nuevo, 2), errores_actual, tareas_actual, ""])
    
    print(f"[LOG] {tipo_evento} | Tiempo: {tiempo_nuevo:.2f}s | Errores: {errores_actual} | Tareas: {tareas_actual} | {'✓' if exito else '✗'}")