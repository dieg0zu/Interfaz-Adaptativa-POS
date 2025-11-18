"""
Script de prueba para verificar la clasificación difusa del sistema
Verifica que el nivel clasificado sea el correcto para cada usuario
"""
import sys
import os
import json
from datetime import datetime

# Agregar el directorio raíz del proyecto al path
directorio_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, directorio_raiz)

from src.motor_difuso import crear_motor_difuso
from src.asignador_interfaz import asignar_interfaz

def obtener_nivel_esperado(interfaz_str):
    """Extrae el nivel esperado de la cadena de interfaz"""
    if "novato" in interfaz_str.lower():
        return "novato"
    elif "intermedio" in interfaz_str.lower():
        return "intermedio"
    elif "experto" in interfaz_str.lower():
        return "experto"
    return None

def test_clasificacion():
    """Prueba la clasificación con diferentes escenarios y verifica que sea correcta"""
    
    print("\n" + "="*70)
    print("🧪 PRUEBA DE CLASIFICACIÓN DIFUSA")
    print("="*70)
    
    # Casos de prueba: (tiempo, errores, tareas, nivel_esperado, descripcion)
    casos_prueba = [
        (8.0, 7, 5, "novato", "Usuario lento con muchos errores - NOVATO"),
        (5.0, 3, 10, "intermedio", "Usuario promedio - INTERMEDIO"),
        (2.0, 0, 25, "experto", "Usuario rápido, sin errores, muchas tareas - EXPERTO"),
        (1.5, 1, 20, "experto", "Usuario muy rápido, pocos errores - EXPERTO"),
        (6.0, 2, 15, "intermedio", "Usuario medio-lento, pocos errores - INTERMEDIO"),
        (9.0, 1, 8, "novato", "Usuario lento pero preciso - NOVATO"),
        (3.0, 4, 12, "intermedio", "Usuario rápido pero con errores - INTERMEDIO"),
        (4.0, 0, 18, "intermedio", "Usuario medio, sin errores - INTERMEDIO"),
        (7.0, 5, 6, "novato", "Usuario lento con errores - NOVATO"),
        (2.5, 2, 22, "experto", "Usuario rápido, pocos errores, muchas tareas - EXPERTO"),
    ]
    
    pruebas_exitosas = 0
    pruebas_fallidas = 0
    resultados_detallados = []
    
    for tiempo, errores, tareas, nivel_esperado, descripcion in casos_prueba:
        # Crear un nuevo motor para cada prueba (evita problemas de estado)
        motor = crear_motor_difuso()
        
        # Normalizar valores
        tiempo_norm = max(0, min(tiempo, 10.0))
        errores_norm = max(0, min(errores, 10))
        tareas_norm = max(0, min(tareas, 30))
        
        # Asignar al motor
        motor.input['TiempoPromedioAccion'] = tiempo_norm
        motor.input['ErroresSesion'] = errores_norm
        motor.input['TareasCompletadas'] = tareas_norm
        
        # Computar
        try:
            motor.compute()
            # Verificar que el output existe
            if 'NivelUsuario' not in motor.output:
                print(f"   ❌ ERROR: No se pudo calcular el nivel para este caso")
                print(f"   Output disponible: {list(motor.output.keys())}")
                pruebas_fallidas += 1
                continue
            
            nivel_calculado = float(motor.output['NivelUsuario'])
            interfaz_asignada = asignar_interfaz(nivel_calculado)
            nivel_obtenido = obtener_nivel_esperado(interfaz_asignada)
        except Exception as e:
            print(f"   ❌ ERROR al computar: {str(e)}")
            import traceback
            traceback.print_exc()
            pruebas_fallidas += 1
            continue
        
        # Verificar si la clasificación es correcta
        es_correcto = nivel_obtenido == nivel_esperado.lower()
        
        if es_correcto:
            pruebas_exitosas += 1
            estado = "✅ CORRECTO"
        else:
            pruebas_fallidas += 1
            estado = "❌ INCORRECTO"
        
        # Guardar resultado detallado
        resultado_detalle = {
            "descripcion": descripcion,
            "input": {
                "tiempo": tiempo_norm,
                "errores": errores_norm,
                "tareas": tareas_norm
            },
            "resultado": {
                "nivel_calculado": nivel_calculado,
                "interfaz_asignada": interfaz_asignada,
                "nivel_esperado": nivel_esperado,
                "nivel_obtenido": nivel_obtenido,
                "es_correcto": es_correcto
            },
            "timestamp": datetime.now().isoformat()
        }
        resultados_detallados.append(resultado_detalle)
        
        # Mostrar resultado
        print(f"\n📊 Caso: {descripcion}")
        print(f"   Input: Tiempo={tiempo_norm:.1f}s, Errores={errores_norm}, Tareas={tareas_norm}")
        print(f"   → Nivel calculado: {nivel_calculado:.2f} / 100")
        print(f"   → Interfaz asignada: {interfaz_asignada}")
        print(f"   → Nivel esperado: {nivel_esperado.upper()}")
        print(f"   → Nivel obtenido: {nivel_obtenido.upper() if nivel_obtenido else 'N/A'}")
        print(f"   {estado}")
        print("-" * 70)
    
    # Resumen final
    total_pruebas = pruebas_exitosas + pruebas_fallidas
    porcentaje_exito = (pruebas_exitosas / total_pruebas * 100) if total_pruebas > 0 else 0
    
    print(f"\n{'='*70}")
    print(f"📊 RESUMEN DE PRUEBAS")
    print(f"{'='*70}")
    print(f"   ✅ Pruebas exitosas: {pruebas_exitosas}/{total_pruebas}")
    print(f"   ❌ Pruebas fallidas: {pruebas_fallidas}/{total_pruebas}")
    print(f"   📈 Porcentaje de éxito: {porcentaje_exito:.1f}%")
    
    if pruebas_fallidas == 0:
        print(f"\n🎉 ¡TODAS LAS PRUEBAS PASARON CORRECTAMENTE!\n")
    else:
        print(f"\n⚠️  HAY {pruebas_fallidas} PRUEBA(S) FALLIDA(S)\n")
    
    # Guardar resultados en JSON
    guardar_resultados_json(pruebas_exitosas, pruebas_fallidas, total_pruebas, porcentaje_exito, resultados_detallados)

def guardar_resultados_json(pruebas_exitosas, pruebas_fallidas, total_pruebas, porcentaje_exito, resultados_detallados):
    """Guarda los resultados en un archivo JSON"""
    resultados = {
        "timestamp": datetime.now().isoformat(),
        "tipo_test": "clasificacion_difusa",
        "estadisticas": {
            "total_pruebas": total_pruebas,
            "pruebas_exitosas": pruebas_exitosas,
            "pruebas_fallidas": pruebas_fallidas,
            "porcentaje_exito": porcentaje_exito
        },
        "resultados_detallados": resultados_detallados
    }
    
    # Crear carpeta de resultados si no existe
    os.makedirs("pruebas/resultados", exist_ok=True)
    archivo_resultados = f"pruebas/resultados/clasificacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(archivo_resultados, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Resultados guardados en: {archivo_resultados}")

if __name__ == "__main__":
    test_clasificacion()












