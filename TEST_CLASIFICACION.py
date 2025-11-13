"""
Script de prueba para verificar la clasificación difusa del sistema
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.motor_difuso import crear_motor_difuso
from src.asignador_interfaz import asignar_interfaz

def test_clasificacion():
    """Prueba la clasificación con diferentes escenarios"""
    
    print("\n" + "="*70)
    print("🧪 PRUEBA DE CLASIFICACIÓN DIFUSA")
    print("="*70)
    
    # Casos de prueba
    casos_prueba = [
        # (tiempo, errores, tareas, descripcion)
        (8.0, 7, 5, "Usuario lento con muchos errores - NOVATO"),
        (5.0, 3, 10, "Usuario promedio - INTERMEDIO"),
        (2.0, 0, 25, "Usuario rápido, sin errores, muchas tareas - EXPERTO"),
        (1.5, 1, 20, "Usuario muy rápido, pocos errores - EXPERTO"),
        (6.0, 2, 15, "Usuario medio-lento, pocos errores - INTERMEDIO"),
        (9.0, 1, 8, "Usuario lento pero preciso - NOVATO"),
        (3.0, 4, 12, "Usuario rápido pero con errores - INTERMEDIO"),
        (4.0, 0, 18, "Usuario medio, sin errores - INTERMEDIO-EXPERTO"),
        (7.0, 5, 6, "Usuario lento con errores - NOVATO"),
        (2.5, 2, 22, "Usuario rápido, pocos errores, muchas tareas - EXPERTO"),
    ]
    
    motor = crear_motor_difuso()
    
    for tiempo, errores, tareas, descripcion in casos_prueba:
        # Normalizar valores
        tiempo_norm = max(0, min(tiempo, 10.0))
        errores_norm = max(0, min(errores, 10))
        tareas_norm = max(0, min(tareas, 30))
        
        # Asignar al motor
        motor.input['TiempoPromedioAccion'] = tiempo_norm
        motor.input['ErroresSesion'] = errores_norm
        motor.input['TareasCompletadas'] = tareas_norm
        
        # Computar
        motor.compute()
        nivel = motor.output['NivelUsuario']
        interfaz = asignar_interfaz(nivel)
        
        # Mostrar resultado
        print(f"\n📊 Caso: {descripcion}")
        print(f"   Input: Tiempo={tiempo_norm:.1f}s, Errores={errores_norm}, Tareas={tareas_norm}")
        print(f"   → Nivel: {nivel:.2f} / 100")
        print(f"   → Interfaz: {interfaz}")
        print("-" * 70)
    
    print("\n✅ Pruebas completadas\n")

if __name__ == "__main__":
    test_clasificacion()












