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
    
    if df.empty:
        print("[ADAPTADOR] Sin datos → NOVATO (default)")
        return "Novato → Interfaz simplificada", 30.0
    
    # ========== LEER MÉTRICAS DIRECTAMENTE ==========
    tiempo_prom = df['TiempoPromedioAccion(s)'].iloc[0]
    errores = df['ErroresSesion'].iloc[0]
    tareas = df['TareasCompletadas'].iloc[0]
    
    eventos_totales = errores + tareas
    
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
        print("🆕 Usuario nuevo → NOVATO")
        print(f"{'='*60}\n")
        return "Novato → Interfaz simplificada", 30.0
    
    # Evaluación preliminar (1-3 eventos)
    if eventos_totales <= 3:
        print(f"⚠️  Pocos eventos ({eventos_totales}) → Evaluación preliminar")
        
        # Si es rápido y sin errores desde el inicio = posible experto
        if tiempo_prom < 3.5 and errores == 0 and tareas >= 2:
            print("   → Usuario muestra experiencia → INTERMEDIO")
            print(f"{'='*60}\n")
            return "Intermedio → Interfaz equilibrada", 55.0
        else:
            print("   → Mantener NOVATO (seguro)")
            print(f"{'='*60}\n")
            return "Novato → Interfaz simplificada", 35.0
    
    # ========== EVALUACIÓN CON LÓGICA DIFUSA (4+ eventos) ==========
    print(f"✅ Evaluación completa con lógica difusa")
    
    motor = crear_motor_difuso()
    
    # Normalizar valores al rango esperado
    motor.input['TiempoPromedioAccion'] = min(tiempo_prom, 10)
    motor.input['ErroresSesion'] = min(errores, 10)
    motor.input['TareasCompletadas'] = min(tareas, 30)
    
    try:
        motor.compute()
        nivel = motor.output['NivelUsuario']
        
        interfaz = asignar_interfaz(nivel)
        
        print(f"🎯 RESULTADO:")
        print(f"   • Nivel Difuso: {nivel:.2f} / 100")
        print(f"   • Interfaz: {interfaz}")
        print(f"{'='*60}\n")
        
        # Actualizar el nivel clasificado en el CSV
        actualizar_nivel_clasificado(interfaz, archivo)
        
        return interfaz, nivel
        
    except Exception as e:
        print(f"❌ Error en motor difuso: {e}")
        print(f"   → Fallback a INTERMEDIO")
        print(f"{'='*60}\n")
        return "Intermedio → Interfaz equilibrada", 50.0

def actualizar_nivel_clasificado(interfaz, archivo):
    """Actualiza la columna NivelClasificado en el CSV"""
    df = pd.read_csv(archivo)
    
    if "novato" in interfaz.lower():
        nivel_texto = "Novato"
    elif "intermedio" in interfaz.lower():
        nivel_texto = "Intermedio"
    else:
        nivel_texto = "Experto"
    
    df['NivelClasificado'] = nivel_texto
    df.to_csv(archivo, index=False)