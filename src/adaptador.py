import pandas as pd
import os
from src.motor_difuso import crear_motor_difuso
from src.asignador_interfaz import asignar_interfaz

def evaluar_y_asignar():
    """
    Evalúa el nivel del usuario basado en métricas acumuladas.
    Lee directamente el formato Dataset_POS.csv
    """
    archivo = "data/dataset_pos.csv"
    
    # ========== SIN DATOS O ARCHIVO NO EXISTE ==========
    if not os.path.exists(archivo):
        print("[ADAPTADOR] Archivo no encontrado → NOVATO (default)")
        return "Novato → Interfaz simplificada", 30.0
    
    df = pd.read_csv(archivo)
    
    if df.empty or len(df) == 0:
        print("[ADAPTADOR] Sin datos → NOVATO (default)")
        return "Novato → Interfaz simplificada", 30.0
    
    # Verificar si la fila tiene datos válidos (no solo encabezado)
    try:
        primera_fila = df.iloc[0]
        sesion_id = str(primera_fila.get('SesionID', '')).strip()
        if not sesion_id or sesion_id == '' or sesion_id.lower() == 'nan':
            print("[ADAPTADOR] CSV solo con encabezado → NOVATO (default)")
            return "Novato → Interfaz simplificada", 30.0
    except (IndexError, KeyError):
        print("[ADAPTADOR] Error al leer fila → NOVATO (default)")
        return "Novato → Interfaz simplificada", 30.0
    
    # ========== LEER MÉTRICAS DIRECTAMENTE ==========
    tiempo_prom = pd.to_numeric(df['TiempoPromedioAccion(s)'].iloc[0], errors='coerce') or 0
    errores = pd.to_numeric(df['ErroresSesion'].iloc[0], errors='coerce') or 0
    tareas = pd.to_numeric(df['TareasCompletadas'].iloc[0], errors='coerce') or 0
    
    # Convertir NaN a 0
    if pd.isna(tiempo_prom):
        tiempo_prom = 0
    if pd.isna(errores):
        errores = 0
    if pd.isna(tareas):
        tareas = 0
    
    eventos_totales = int(errores) + int(tareas)
    
    print(f"\n{'='*60}")
    print(f"🧠 EVALUACIÓN DEL USUARIO")
    print(f"{'='*60}")
    print(f"📊 MÉTRICAS ACUMULADAS ({eventos_totales} eventos):")
    print(f"   • Tiempo Promedio: {tiempo_prom:.2f}s")
    print(f"   • Errores: {errores}")
    print(f"   • Tareas Completadas: {tareas}")
    print(f"{'-'*60}")
    
    # ========== CASOS ESPECIALES ==========
    
    # Usuario completamente nuevo (0 eventos)
    if eventos_totales == 0:
        print("🆕 Usuario nuevo → NOVATO (sin datos para evaluar)")
        print(f"{'='*60}\n")
        return "Novato → Interfaz simplificada", 30.0
    
    # ========== EVALUACIÓN CON LÓGICA DIFUSA ==========
    # Siempre usar lógica difusa cuando hay al menos 1 evento
    print(f"✅ Evaluación con lógica difusa ({eventos_totales} eventos)")
    
    motor = crear_motor_difuso()
    
    # Normalizar valores al rango esperado del motor difuso
    # Tiempo: 0-10 segundos
    tiempo_normalizado = max(0, min(float(tiempo_prom), 10.0))
    # Errores: 0-10
    errores_normalizados = max(0, min(int(errores), 10))
    # Tareas: 0-30
    tareas_normalizadas = max(0, min(int(tareas), 30))
    
    # Asignar valores al motor difuso
    motor.input['TiempoPromedioAccion'] = tiempo_normalizado
    motor.input['ErroresSesion'] = errores_normalizados
    motor.input['TareasCompletadas'] = tareas_normalizadas
    
    print(f"📥 INPUTS AL MOTOR DIFUSO:")
    print(f"   • Tiempo: {tiempo_normalizado:.2f}s (normalizado)")
    print(f"   • Errores: {errores_normalizados}")
    print(f"   • Tareas: {tareas_normalizadas}")
    
    try:
        # Ejecutar inferencia difusa
        motor.compute()
        nivel = float(motor.output['NivelUsuario'])
        
        # Asegurar que el nivel esté en el rango válido [0, 100]
        nivel = max(0, min(100, nivel))
        
        # Determinar interfaz basada en el nivel
        interfaz = asignar_interfaz(nivel)
        
        # Determinar nivel de confianza basado en número de eventos
        if eventos_totales < 5:
            confianza = "Baja (pocos datos)"
        elif eventos_totales < 10:
            confianza = "Media"
        else:
            confianza = "Alta"
        
        print(f"🎯 RESULTADO DE CLASIFICACIÓN:")
        print(f"   • Nivel Difuso: {nivel:.2f} / 100")
        print(f"   • Interfaz Asignada: {interfaz}")
        print(f"   • Confianza: {confianza} ({eventos_totales} eventos)")
        print(f"{'='*60}\n")
        
        # Actualizar el nivel clasificado en el CSV
        actualizar_nivel_clasificado(interfaz, archivo)
        
        return interfaz, nivel
        
    except Exception as e:
        print(f"❌ Error en motor difuso: {e}")
        import traceback
        traceback.print_exc()
        print(f"   → Fallback a evaluación simple")
        
        # Fallback: evaluación simple basada en reglas básicas
        if tiempo_prom > 7 or errores > 5:
            nivel_fallback = 25.0  # Novato
            interfaz_fallback = "Novato → Interfaz simplificada"
        elif tiempo_prom < 3 and errores < 2 and tareas > 15:
            nivel_fallback = 75.0  # Experto
            interfaz_fallback = "Experto → Interfaz avanzada"
        else:
            nivel_fallback = 50.0  # Intermedio
            interfaz_fallback = "Intermedio → Interfaz equilibrada"
        
        print(f"   → Nivel Fallback: {nivel_fallback:.2f} → {interfaz_fallback}")
        print(f"{'='*60}\n")
        
        actualizar_nivel_clasificado(interfaz_fallback, archivo)
        return interfaz_fallback, nivel_fallback

def actualizar_nivel_clasificado(interfaz, archivo):
    """Actualiza la columna NivelClasificado en el CSV"""
    try:
        df = pd.read_csv(archivo)
        
        # Determinar nivel basado en la interfaz asignada
        if "novato" in interfaz.lower():
            nivel_texto = "Novato"
        elif "intermedio" in interfaz.lower():
            nivel_texto = "Intermedio"
        elif "experto" in interfaz.lower():
            nivel_texto = "Experto"
        else:
            # Si no se puede determinar, usar el nivel por defecto
            nivel_texto = "Novato"
        
        # Asegurar que la columna existe
        if 'NivelClasificado' not in df.columns:
            df['NivelClasificado'] = nivel_texto
        else:
            df['NivelClasificado'] = nivel_texto
        
        # Guardar el CSV
        df.to_csv(archivo, index=False)
        print(f"📝 Nivel actualizado en CSV: {nivel_texto}")
        
    except Exception as e:
        print(f"⚠️  Error al actualizar nivel en CSV: {e}")
        # No lanzar excepción, solo registrar el error