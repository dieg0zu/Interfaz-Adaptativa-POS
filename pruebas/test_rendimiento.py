"""
Test de Rendimiento - Sistema POS Adaptativo
Evalúa el tiempo de procesamiento y adaptación de la interfaz
"""

import time
import requests
import statistics
import json
from datetime import datetime
import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestRendimiento:
    def __init__(self, base_url="http://localhost:5000", num_pruebas=100):
        self.base_url = base_url
        self.num_pruebas = num_pruebas
        self.tiempos_adaptacion = []
        self.tiempos_procesamiento = []
        self.eventos_registrados = []
        self.resultados = []
        
    def simular_evento(self, tipo_evento, duracion=0.5, exito=True, tiempo_activo=None):
        """Simula un evento enviado al sistema"""
        inicio = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/api/evento",
                json={
                    "tipo_evento": tipo_evento,
                    "duracion": duracion,
                    "exito": exito,
                    "tiempo_activo": tiempo_activo
                },
                timeout=5
            )
            
            tiempo_procesamiento = (time.time() - inicio) * 1000  # Convertir a ms
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "exito": True,
                    "tiempo_procesamiento": tiempo_procesamiento,
                    "respuesta": data,
                    "tiempo_adaptacion": tiempo_procesamiento  # Para eventos normales
                }
            else:
                return {
                    "exito": False,
                    "tiempo_procesamiento": tiempo_procesamiento,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            tiempo_procesamiento = (time.time() - inicio) * 1000
            return {
                "exito": False,
                "tiempo_procesamiento": tiempo_procesamiento,
                "error": str(e)
            }
    
    def simular_compra_completa(self):
        """Simula una compra completa con múltiples eventos"""
        eventos_sesion = []
        tiempo_inicio_sesion = time.time()
        tiempo_activo_acumulado = 0
        tiempo_ultima_accion = tiempo_inicio_sesion
        
        # Simular secuencia de eventos típica
        secuencia_eventos = [
            ("agregar_producto_carrito", 0.3, True),
            ("agregar_producto_carrito", 0.4, True),
            ("aumentar_cantidad", 0.2, True),
            ("eliminar_producto_carrito", 0.3, True),
            ("agregar_producto_carrito", 0.5, True),
            ("ir_a_pago", 0.8, True),
            ("compra_finalizada", 0.2, True)  # Este es el que activa la evaluación
        ]
        
        for tipo_evento, duracion, exito in secuencia_eventos:
            # Calcular tiempo activo desde la última acción
            ahora = time.time()
            tiempo_desde_ultima = ahora - tiempo_ultima_accion
            
            # Si hay menos de 30 segundos entre acciones, contar como tiempo activo
            if tiempo_desde_ultima < 30:
                tiempo_activo_acumulado += tiempo_desde_ultima
            
            tiempo_activo = tiempo_activo_acumulado if tiempo_activo_acumulado > 0 else None
            
            # Simular el evento
            inicio_evento = time.time()
            resultado = self.simular_evento(tipo_evento, duracion, exito, tiempo_activo)
            tiempo_total = (time.time() - inicio_evento) * 1000  # ms
            
            resultado["tipo_evento"] = tipo_evento
            resultado["tiempo_total"] = tiempo_total
            resultado["timestamp"] = datetime.now().isoformat()
            
            eventos_sesion.append(resultado)
            tiempo_ultima_accion = ahora
            
            # Si es compra finalizada, medir tiempo de adaptación
            if tipo_evento == "compra_finalizada" and resultado["exito"]:
                if "respuesta" in resultado and resultado["respuesta"].get("nivel") is not None:
                    # Tiempo desde el evento hasta la respuesta completa
                    tiempo_adaptacion = resultado["tiempo_total"]
                    self.tiempos_adaptacion.append(tiempo_adaptacion)
                    resultado["tiempo_adaptacion"] = tiempo_adaptacion
            
            # Pequeña pausa entre eventos para simular comportamiento real
            time.sleep(0.1)
        
        return eventos_sesion
    
    def ejecutar_prueba(self):
        """Ejecuta la prueba de rendimiento completa"""
        print(f"\n{'='*70}")
        print(f"🚀 INICIANDO TEST DE RENDIMIENTO")
        print(f"{'='*70}")
        print(f"📊 Configuración:")
        print(f"   • URL Base: {self.base_url}")
        print(f"   • Número de pruebas: {self.num_pruebas}")
        print(f"   • Objetivo: < 1000ms en 95% de los casos")
        print(f"{'='*70}\n")
        
        # Verificar que el servidor esté corriendo
        try:
            response = requests.get(f"{self.base_url}/api/estado", timeout=2)
            if response.status_code != 200:
                print(f"❌ Error: El servidor no responde correctamente")
                return
        except Exception as e:
            print(f"❌ Error: No se puede conectar al servidor en {self.base_url}")
            print(f"   Asegúrate de que Flask esté corriendo: python app.py")
            return
        
        print("✅ Servidor conectado correctamente\n")
        
        # Ejecutar pruebas
        for i in range(self.num_pruebas):
            print(f"📝 Prueba {i+1}/{self.num_pruebas}...", end=" ", flush=True)
            
            inicio_prueba = time.time()
            eventos = self.simular_compra_completa()
            tiempo_total_prueba = (time.time() - inicio_prueba) * 1000
            
            # Guardar resultados
            self.resultados.append({
                "prueba": i + 1,
                "eventos": eventos,
                "tiempo_total": tiempo_total_prueba,
                "timestamp": datetime.now().isoformat()
            })
            
            # Extraer tiempos de procesamiento
            for evento in eventos:
                if evento.get("exito") and "tiempo_procesamiento" in evento:
                    self.tiempos_procesamiento.append(evento["tiempo_procesamiento"])
            
            # Mostrar resultado
            if eventos and eventos[-1].get("exito"):
                tiempo_adapt = eventos[-1].get("tiempo_adaptacion", 0)
                if tiempo_adapt > 0:
                    status = "✅" if tiempo_adapt < 2500 else "⚠️"
                    print(f"{status} {tiempo_adapt:.2f}ms")
                else:
                    print("✅ OK")
            else:
                print("❌ Error")
            
            # Pequeña pausa entre pruebas
            time.sleep(0.2)
        
        # Calcular estadísticas
        self.calcular_estadisticas()
    
    def calcular_estadisticas(self):
        """Calcula estadísticas de rendimiento"""
        print(f"\n{'='*70}")
        print(f"📊 RESULTADOS DEL TEST DE RENDIMIENTO")
        print(f"{'='*70}\n")
        
        if not self.tiempos_adaptacion:
            print("❌ No se registraron tiempos de adaptación")
            return
        
        # Estadísticas de tiempo de adaptación
        tiempos_ms = self.tiempos_adaptacion
        promedio = statistics.mean(tiempos_ms)
        mediana = statistics.median(tiempos_ms)
        desviacion = statistics.stdev(tiempos_ms) if len(tiempos_ms) > 1 else 0
        minimo = min(tiempos_ms)
        maximo = max(tiempos_ms)
        
        # Calcular percentiles
        tiempos_ordenados = sorted(tiempos_ms)
        p50 = tiempos_ordenados[int(len(tiempos_ordenados) * 0.50)]
        p95 = tiempos_ordenados[int(len(tiempos_ordenados) * 0.95)]
        p99 = tiempos_ordenados[int(len(tiempos_ordenados) * 0.99)]
        
        # Contar casos que superan 1000ms
        casos_sobre_1000ms = sum(1 for t in tiempos_ms if t > 1000)
        porcentaje_sobre_1000ms = (casos_sobre_1000ms / len(tiempos_ms)) * 100
        
        print(f"⏱️  TIEMPO DE ADAPTACIÓN (ms):")
        print(f"   • Promedio: {promedio:.2f}ms")
        print(f"   • Mediana: {mediana:.2f}ms")
        print(f"   • Desviación estándar: {desviacion:.2f}ms")
        print(f"   • Mínimo: {minimo:.2f}ms")
        print(f"   • Máximo: {maximo:.2f}ms")
        print(f"\n📈 PERCENTILES:")
        print(f"   • P50 (mediana): {p50:.2f}ms")
        print(f"   • P95: {p95:.2f}ms")
        print(f"   • P99: {p99:.2f}ms")
        print(f"\n🎯 CUMPLIMIENTO DE OBJETIVO:")
        print(f"   • Casos sobre 1000ms: {casos_sobre_1000ms}/{len(tiempos_ms)} ({porcentaje_sobre_1000ms:.2f}%)")
        
        if p95 < 1000:
            print(f"   ✅ CUMPLE: P95 ({p95:.2f}ms) < 1000ms")
        else:
            print(f"   ❌ NO CUMPLE: P95 ({p95:.2f}ms) >= 1000ms")
        
        # Estadísticas de tiempo de procesamiento general
        if self.tiempos_procesamiento:
            prom_proc = statistics.mean(self.tiempos_procesamiento)
            print(f"\n⚙️  TIEMPO DE PROCESAMIENTO GENERAL (ms):")
            print(f"   • Promedio: {prom_proc:.2f}ms")
            print(f"   • Total de eventos procesados: {len(self.tiempos_procesamiento)}")
        
        # Guardar resultados en archivo
        self.guardar_resultados(promedio, desviacion, p95, porcentaje_sobre_1000ms)
    
    def guardar_resultados(self, promedio, desviacion, p95, porcentaje_sobre_1000ms):
        """Guarda los resultados en un archivo JSON"""
        resultados = {
            "timestamp": datetime.now().isoformat(),
            "configuracion": {
                "base_url": self.base_url,
                "num_pruebas": self.num_pruebas
            },
            "estadisticas": {
                "tiempo_promedio_adaptacion_ms": promedio,
                "desviacion_estandar_ms": desviacion,
                "percentil_95_ms": p95,
                "porcentaje_sobre_1000ms": porcentaje_sobre_1000ms,
                "total_pruebas": len(self.tiempos_adaptacion)
            },
            "tiempos_adaptacion": self.tiempos_adaptacion,
            "resultados_detallados": self.resultados
        }
        
        os.makedirs("pruebas/resultados", exist_ok=True)
        archivo_resultados = f"pruebas/resultados/rendimiento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(archivo_resultados, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: {archivo_resultados}")
        print(f"{'='*70}\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test de Rendimiento - Sistema POS Adaptativo')
    parser.add_argument('--url', type=str, default='http://localhost:5000',
                       help='URL base del servidor Flask (default: http://localhost:5000)')
    parser.add_argument('--pruebas', type=int, default=100,
                       help='Número de pruebas a ejecutar (default: 100)')
    
    args = parser.parse_args()
    
    test = TestRendimiento(base_url=args.url, num_pruebas=args.pruebas)
    test.ejecutar_prueba()

