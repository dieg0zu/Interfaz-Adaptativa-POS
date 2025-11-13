import csv
from datetime import datetime
import os
import pandas as pd

def generar_nueva_sesion_id():
    """Genera un nuevo ID de sesión basado en timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"S_{timestamp}"

def registrar_evento(tipo_evento, duracion, exito=True, tiempo_activo=None):
    """
    Registra un evento y actualiza las métricas de sesión acumuladas.
    Si el evento es 'compra_finalizada', finaliza la sesión actual y crea una nueva.
    Formato compatible con Dataset_POS.csv
    """
    os.makedirs("data", exist_ok=True)
    
    archivo_sesion = "data/dataset_pos.csv"
    es_compra_finalizada = (tipo_evento == "compra_finalizada")
    
    # Verificar si existe el archivo de sesión
    if not os.path.exists(archivo_sesion):
        # Crear archivo con formato del dataset
        nueva_sesion_id = generar_nueva_sesion_id()
        with open(archivo_sesion, "w", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["SesionID", "TiempoPromedioAccion(s)", "ErroresSesion", "TareasCompletadas", "NivelClasificado"])
            # Inicializar con valores por defecto (novato)
            writer.writerow([nueva_sesion_id, 0, 0, 0, "Novato"])
        print(f"[LOGGER] Archivo de sesión creado con nueva sesión: {nueva_sesion_id}")
    
    # Leer datos actuales
    df = pd.read_csv(archivo_sesion)
    
    # Obtener métricas actuales de la última sesión
    if len(df) > 0:
        # Obtener la última fila (sesión actual)
        ultima_fila = df.iloc[-1]
        sesion_actual = str(ultima_fila.get('SesionID', '')).strip()
        
        # Si la sesión actual es vacía o no existe, crear una nueva
        if not sesion_actual or sesion_actual == '' or sesion_actual.lower() == 'nan':
            sesion_actual = generar_nueva_sesion_id()
        
        tiempo_actual = pd.to_numeric(ultima_fila.get('TiempoPromedioAccion(s)', 0), errors='coerce') or 0
        errores_actual = pd.to_numeric(ultima_fila.get('ErroresSesion', 0), errors='coerce') or 0
        tareas_actual = pd.to_numeric(ultima_fila.get('TareasCompletadas', 0), errors='coerce') or 0
        
        # Convertir NaN a 0
        if pd.isna(tiempo_actual):
            tiempo_actual = 0
        if pd.isna(errores_actual):
            errores_actual = 0
        if pd.isna(tareas_actual):
            tareas_actual = 0
            
        eventos_totales = int(errores_actual) + int(tareas_actual)
    else:
        sesion_actual = generar_nueva_sesion_id()
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
    # PRIORIDAD: Si tenemos tiempo activo, usarlo para calcular mejor el tiempo promedio por acción
    if tiempo_activo is not None and tiempo_activo > 0 and eventos_totales > 0:
        # Calcular tiempo promedio basado en tiempo activo total dividido por número de acciones
        tiempo_promedio_activo = tiempo_activo / eventos_totales
        
        # Si el tiempo activo es significativo (usuario lento), usarlo como tiempo promedio
        # Esto refleja mejor si el usuario es lento en general
        if tiempo_promedio_activo > 2.0:  # Si el promedio activo es > 2s, el usuario es lento
            tiempo_nuevo = tiempo_promedio_activo
        else:
            # Si el tiempo activo es bajo, usar el máximo entre duración y tiempo activo
            tiempo_nuevo = max(duracion, tiempo_promedio_activo)
        
        # Limitar a máximo 10 segundos (rango del motor difuso)
        tiempo_nuevo = min(10.0, tiempo_nuevo)
        
        print(f"[LOGGER] Tiempo activo usado: {tiempo_activo:.2f}s / {eventos_totales} acciones = {tiempo_promedio_activo:.2f}s promedio")
    else:
        # Si no hay tiempo activo, usar el método tradicional
        if eventos_totales == 1:
            tiempo_nuevo = duracion
        else:
            tiempo_nuevo = ((tiempo_actual * (eventos_totales - 1)) + duracion) / eventos_totales
        # Limitar a máximo 10 segundos
        tiempo_nuevo = min(10.0, tiempo_nuevo)
    
    # Si es compra finalizada, guardar la sesión actual como NUEVA FILA (no sobrescribir)
    if es_compra_finalizada:
        # Guardar los datos de la sesión completada
        nivel_actual = str(ultima_fila.get('NivelClasificado', 'Novato')) if len(df) > 0 else 'Novato'
        datos_sesion_completada = {
            'SesionID': sesion_actual,
            'TiempoPromedioAccion(s)': round(tiempo_nuevo, 2),
            'ErroresSesion': errores_actual,
            'TareasCompletadas': tareas_actual,
            'NivelClasificado': nivel_actual
        }
        
        # Verificar si la última fila es la sesión actual (tiene eventos) o es una sesión vacía
        eventos_ultima = int(ultima_fila.get('ErroresSesion', 0) or 0) + int(ultima_fila.get('TareasCompletadas', 0) or 0)
        
        if eventos_ultima == 0:
            # La última fila es una sesión vacía, reemplazarla con la sesión completada
            df.loc[df.index[-1], 'SesionID'] = datos_sesion_completada['SesionID']
            df.loc[df.index[-1], 'TiempoPromedioAccion(s)'] = datos_sesion_completada['TiempoPromedioAccion(s)']
            df.loc[df.index[-1], 'ErroresSesion'] = datos_sesion_completada['ErroresSesion']
            df.loc[df.index[-1], 'TareasCompletadas'] = datos_sesion_completada['TareasCompletadas']
            df.loc[df.index[-1], 'NivelClasificado'] = datos_sesion_completada['NivelClasificado']
        else:
            # La última fila es la sesión actual con eventos
            # IMPORTANTE: Agregar como NUEVA FILA, no sobrescribir
            # Primero actualizar la última fila con los datos finales
            df.loc[df.index[-1], 'SesionID'] = datos_sesion_completada['SesionID']
            df.loc[df.index[-1], 'TiempoPromedioAccion(s)'] = datos_sesion_completada['TiempoPromedioAccion(s)']
            df.loc[df.index[-1], 'ErroresSesion'] = datos_sesion_completada['ErroresSesion']
            df.loc[df.index[-1], 'TareasCompletadas'] = datos_sesion_completada['TareasCompletadas']
            df.loc[df.index[-1], 'NivelClasificado'] = datos_sesion_completada['NivelClasificado']
        
        # Guardar temporalmente para que evaluar_y_asignar pueda leerla (sin la nueva sesión aún)
        df.to_csv(archivo_sesion, index=False)
        
        print(f"[LOGGER] ✅ Venta completada - Sesión {sesion_actual} finalizada")
        print(f"[LOGGER]   Datos guardados para evaluación")
        print(f"[LOGGER]   Total de sesiones en CSV: {len(df)}")
        
        # Retornar los datos de la sesión completada para evaluación
        # La nueva sesión se creará DESPUÉS de la evaluación en app.py
        return es_compra_finalizada, sesion_actual, datos_sesion_completada
    else:
        # Solo actualizar la última fila (sesión actual)
        if len(df) > 0:
            df.loc[df.index[-1], 'SesionID'] = sesion_actual
            df.loc[df.index[-1], 'TiempoPromedioAccion(s)'] = round(tiempo_nuevo, 2)
            df.loc[df.index[-1], 'ErroresSesion'] = errores_actual
            df.loc[df.index[-1], 'TareasCompletadas'] = tareas_actual
            # No actualizar NivelClasificado durante el proceso, solo al finalizar
        else:
            # Si no hay filas, crear una nueva
            nueva_fila = pd.DataFrame([{
                'SesionID': sesion_actual,
                'TiempoPromedioAccion(s)': round(tiempo_nuevo, 2),
                'ErroresSesion': errores_actual,
                'TareasCompletadas': tareas_actual,
                'NivelClasificado': ""
            }])
            df = pd.concat([df, nueva_fila], ignore_index=True)
    
    # Guardar el archivo
    df.to_csv(archivo_sesion, index=False)
    
    print(f"[LOG] {tipo_evento} | Sesión: {sesion_actual} | Tiempo: {tiempo_nuevo:.2f}s | Errores: {errores_actual} | Tareas: {tareas_actual} | {'✓' if exito else '✗'}")
    
    # Si no es compra finalizada, retornar sin datos de sesión completada
    if not es_compra_finalizada:
        return es_compra_finalizada, sesion_actual, None