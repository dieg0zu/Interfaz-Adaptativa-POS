"""
Test de Tiempo de Cambio de Interfaz - Sistema POS Adaptativo
Mide el tiempo que tarda el sistema en cambiar de una interfaz a otra
cuando se completa una venta y se detecta un cambio de nivel.
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

class TestTiempoCambioInterfaz:
    def __init__(self, base_url="http://localhost:5000", num_sesiones=5):
        self.base_url = base_url
        self.num_sesiones = num_sesiones
        self.tiempos_cambio = []  # Tiempos de cambio de interfaz
        self.cambios_detectados = []  # Información de cada cambio
        self.resultados_detallados = []
        
    def verificar_servidor(self):
        """Verifica que el servidor esté corriendo"""
        try:
            response = requests.get(f"{self.base_url}/api/estado", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def resetear_sistema(self):
        """Resetea el sistema para empezar desde cero"""
        try:
            response = requests.post(f"{self.base_url}/reset", timeout=5)
            print("   🔄 Sistema reseteado")
            time.sleep(0.5)  # Dar tiempo para que se procese el reset
            return True
        except Exception as e:
            print(f"   ⚠️  No se pudo resetear (continuando): {e}")
            return False
    
    def obtener_interfaz_actual(self):
        """Obtiene la interfaz actual del sistema"""
        try:
            response = requests.get(f"{self.base_url}/api/estado", timeout=2)
            if response.status_code == 200:
                data = response.json()
                return data.get("interfaz", "original")
            return "original"
        except:
            return "original"
    
    def simular_evento(self, tipo_evento, duracion=0.5, exito=True, tiempo_activo=None):
        """Simula un evento enviado al sistema"""
        try:
            response = requests.post(
                f"{self.base_url}/api/evento",
                json={
                    "tipo_evento": tipo_evento,
                    "duracion": duracion,
                    "exito": exito,
                    "tiempo_activo": tiempo_activo
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "exito": True,
                    "respuesta": response.json()
                }
            else:
                return {
                    "exito": False,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "exito": False,
                "error": str(e)
            }
    
    def medir_tiempo_carga_interfaz(self, interfaz):
        """
        Mide el tiempo que tarda en cargar/mostrar una interfaz HTML.
        Solo mide el tiempo de respuesta HTTP de la página, no APIs.
        """
        url_interfaz = f"{self.base_url}/{interfaz}"
        
        # ⏱️ INICIAR MEDICIÓN DE TIEMPO
        inicio = time.time()
        
        try:
            # Hacer GET request a la interfaz y esperar respuesta completa
            response = requests.get(url_interfaz, timeout=10)
            
            # ⏱️ FINALIZAR MEDICIÓN DE TIEMPO
            fin = time.time()
            tiempo_carga_ms = (fin - inicio) * 1000
            
            if response.status_code == 200:
                return {
                    "exito": True,
                    "tiempo_carga_ms": tiempo_carga_ms,
                    "status_code": response.status_code,
                    "tamaño_respuesta": len(response.content)
                }
            else:
                return {
                    "exito": False,
                    "tiempo_carga_ms": tiempo_carga_ms,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            fin = time.time()
            tiempo_carga_ms = (fin - inicio) * 1000
            return {
                "exito": False,
                "tiempo_carga_ms": tiempo_carga_ms,
                "error": str(e)
            }
    
    def simular_compra_completa(self, perfil="novato"):
        """
        Simula una compra completa con eventos típicos.
        Retorna el tiempo de carga de la interfaz HTML (no APIs).
        """
        # Obtener interfaz inicial
        interfaz_inicial = self.obtener_interfaz_actual()
        
        # Simular secuencia de eventos según perfil
        if perfil == "novato":
            # Usuario novato: más lento, más errores
            secuencia_eventos = [
                ("agregar_producto_carrito", 7.0, True),
                ("agregar_producto_carrito", 8.0, False),  # Error
                ("agregar_producto_carrito", 6.5, True),
                ("aumentar_cantidad", 5.0, True),
                ("ir_a_pago", 9.0, True),
            ]
        elif perfil == "intermedio":
            # Usuario intermedio: velocidad media, pocos errores
            secuencia_eventos = [
                ("agregar_producto_carrito", 4.0, True),
                ("agregar_producto_carrito", 5.0, True),
                ("aumentar_cantidad", 3.5, True),
                ("eliminar_producto_carrito", 4.5, True),
                ("agregar_producto_carrito", 3.0, True),
                ("ir_a_pago", 5.0, True),
            ]
        else:  # experto
            # Usuario experto: rápido, sin errores, muchas tareas
            secuencia_eventos = [
                ("agregar_producto_carrito", 1.5, True),
                ("agregar_producto_carrito", 2.0, True),
                ("agregar_producto_carrito", 1.8, True),
                ("aumentar_cantidad", 1.2, True),
                ("agregar_producto_carrito", 2.2, True),
                ("eliminar_producto_carrito", 1.5, True),
                ("agregar_producto_carrito", 1.8, True),
                ("ir_a_pago", 2.0, True),
            ]
        
        # Simular eventos previos a la compra finalizada
        tiempo_activo_acumulado = 0
        tiempo_ultima_accion = time.time()
        
        for tipo_evento, duracion, exito in secuencia_eventos:
            ahora = time.time()
            tiempo_desde_ultima = ahora - tiempo_ultima_accion
            if tiempo_desde_ultima < 30:
                tiempo_activo_acumulado += tiempo_desde_ultima
            tiempo_activo = tiempo_activo_acumulado if tiempo_activo_acumulado > 0 else None
            tiempo_ultima_accion = ahora
            
            self.simular_evento(tipo_evento, duracion, exito, tiempo_activo)
            time.sleep(0.1)  # Pequeña pausa entre eventos
        
        # ⏱️ (1) INICIAR CRONÓMETRO: Momento en que el backend recibe "compra_finalizada"
        tiempo_activo_final = tiempo_activo_acumulado if tiempo_activo_acumulado > 0 else None
        inicio_medicion = time.time()
        
        # Enviar evento "compra_finalizada" al backend
        resultado_compra = self.simular_evento("compra_finalizada", 0.5, True, tiempo_activo_final)
        
        # Determinar qué interfaz debería mostrarse (de la respuesta del backend)
        if resultado_compra.get("exito"):
            respuesta = resultado_compra.get("respuesta", {})
            interfaz_asignada = respuesta.get("interfaz", "original")
            nivel = respuesta.get("nivel")
            cambio_interfaz = respuesta.get("cambio_interfaz", False)
        else:
            # Si falla, obtener la interfaz actual
            interfaz_asignada = self.obtener_interfaz_actual()
            nivel = None
            cambio_interfaz = False
        
        # ⏱️ (2) OBTENER LA NUEVA INTERFAZ HTML (el cronómetro sigue corriendo)
        # Hacer GET a la interfaz asignada y esperar respuesta HTML completa
        url_interfaz = f"{self.base_url}/{interfaz_asignada}"
        try:
            response = requests.get(url_interfaz, timeout=10)
            # ⏱️ FINALIZAR CRONÓMETRO: Momento exacto en que se sirve la nueva interfaz HTML
            fin_medicion = time.time()
            tiempo_total_ms = (fin_medicion - inicio_medicion) * 1000
            
            if response.status_code == 200:
                resultado_carga = {
                    "exito": True,
                    "tiempo_carga_ms": tiempo_total_ms,
                    "status_code": response.status_code,
                    "tamaño_respuesta": len(response.content)
                }
            else:
                resultado_carga = {
                    "exito": False,
                    "tiempo_carga_ms": tiempo_total_ms,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            fin_medicion = time.time()
            tiempo_total_ms = (fin_medicion - inicio_medicion) * 1000
            resultado_carga = {
                "exito": False,
                "tiempo_carga_ms": tiempo_total_ms,
                "error": str(e)
            }
        
        # Obtener interfaz final después de la carga
        interfaz_final = self.obtener_interfaz_actual()
        hubo_cambio = interfaz_inicial != interfaz_final or cambio_interfaz
        
        if resultado_carga.get("exito"):
            return {
                "exito": True,
                "tiempo_cambio_ms": resultado_carga.get("tiempo_carga_ms", 0),
                "interfaz_inicial": interfaz_inicial,
                "interfaz_final": interfaz_final,
                "interfaz_asignada": interfaz_asignada,
                "hubo_cambio": hubo_cambio,
                "nivel": nivel,
                "cambio_detectado": cambio_interfaz,
                "tamaño_respuesta": resultado_carga.get("tamaño_respuesta", 0),
                "tiempo_desde_evento_hasta_html": resultado_carga.get("tiempo_carga_ms", 0)
            }
        else:
            return {
                "exito": False,
                "error": resultado_carga.get("error", "Error desconocido"),
                "tiempo_cambio_ms": resultado_carga.get("tiempo_carga_ms", 0),
                "interfaz_inicial": interfaz_inicial,
                "interfaz_final": interfaz_final,
                "tiempo_desde_evento_hasta_html": resultado_carga.get("tiempo_carga_ms", 0)
            }
    
    def ejecutar_test(self):
        """Ejecuta el test completo"""
        print(f"\n{'='*70}")
        print(f"⏱️  TEST DE TIEMPO DE CAMBIO DE INTERFAZ")
        print(f"{'='*70}")
        print(f"📊 Configuración:")
        print(f"   • URL Base: {self.base_url}")
        print(f"   • Número de sesiones: {self.num_sesiones}")
        print(f"   • Objetivo: Medir tiempo desde que el backend recibe 'compra_finalizada'")
        print(f"              hasta que se sirve la nueva interfaz HTML")
        print(f"   • Mide: (1) Recepción del evento → (2) Servicio de HTML completo")
        print(f"{'='*70}\n")
        
        # Verificar servidor
        if not self.verificar_servidor():
            print(f"❌ Error: No se puede conectar al servidor en {self.base_url}")
            print(f"   Asegúrate de que Flask esté corriendo: python app.py")
            return
        
        print("✅ Servidor conectado correctamente\n")
        
        # Resetear sistema para empezar desde cero
        print("🔄 Reseteando sistema para empezar desde cero...")
        self.resetear_sistema()
        time.sleep(1)
        
        # Ejecutar sesiones
        perfiles = ["novato", "intermedio", "experto"]
        
        for i in range(self.num_sesiones):
            perfil = perfiles[i % len(perfiles)]  # Rotar entre perfiles
            print(f"\n{'─'*70}")
            print(f"📝 Sesión {i+1}/{self.num_sesiones} - Perfil: {perfil.upper()}")
            print(f"{'─'*70}")
            
            # Obtener interfaz antes de la sesión
            interfaz_antes = self.obtener_interfaz_actual()
            print(f"   Interfaz inicial: {interfaz_antes}")
            
            # Simular compra completa
            print(f"   Simulando compra completa...")
            resultado = self.simular_compra_completa(perfil)
            
            if resultado.get("exito"):
                tiempo_cambio = resultado.get("tiempo_cambio_ms", 0)
                interfaz_inicial = resultado.get("interfaz_inicial", "desconocida")
                interfaz_final = resultado.get("interfaz_final", "desconocida")
                hubo_cambio = resultado.get("hubo_cambio", False)
                nivel = resultado.get("nivel")
                
                print(f"   ✅ Compra completada")
                print(f"   ⏱️  Tiempo total (evento → HTML): {tiempo_cambio:.2f}ms")
                print(f"   📊 Nivel detectado: {nivel:.2f}" if nivel else "   📊 Nivel: N/A")
                print(f"   🔄 Cambio: {interfaz_inicial} → {interfaz_final}")
                
                if hubo_cambio:
                    print(f"   ✨ ¡CAMBIO DE INTERFAZ DETECTADO!")
                    self.tiempos_cambio.append(tiempo_cambio)
                    self.cambios_detectados.append({
                        "sesion": i + 1,
                        "perfil": perfil,
                        "tiempo_cambio_ms": tiempo_cambio,
                        "interfaz_inicial": interfaz_inicial,
                        "interfaz_final": interfaz_final,
                        "nivel": nivel
                    })
                else:
                    print(f"   ℹ️  Sin cambio de interfaz (mismo nivel)")
                
                # Guardar resultado detallado
                self.resultados_detallados.append({
                    "sesion": i + 1,
                    "perfil": perfil,
                    "timestamp": datetime.now().isoformat(),
                    "resultado": resultado
                })
            else:
                print(f"   ❌ Error: {resultado.get('error', 'Error desconocido')}")
            
            # Pausa entre sesiones
            time.sleep(0.5)
        
        # Calcular y mostrar estadísticas
        self.mostrar_estadisticas()
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas de los tiempos de cambio"""
        print(f"\n{'='*70}")
        print(f"📊 ESTADÍSTICAS DE TIEMPO DE CAMBIO DE INTERFAZ")
        print(f"{'='*70}")
        print(f"   Mide: Desde recepción de 'compra_finalizada' hasta servicio de HTML")
        print(f"{'='*70}\n")
        
        if not self.tiempos_cambio:
            print("⚠️  No se detectaron cambios de interfaz durante las sesiones")
            print("   Esto puede deberse a que:")
            print("   • El usuario mantuvo el mismo nivel en todas las sesiones")
            print("   • El sistema ya estaba en el nivel correcto")
            print("\n💡 Sugerencia: Intenta con más sesiones o diferentes perfiles")
        else:
            # Estadísticas básicas
            tiempos_ms = self.tiempos_cambio
            promedio = statistics.mean(tiempos_ms)
            mediana = statistics.median(tiempos_ms)
            desviacion = statistics.stdev(tiempos_ms) if len(tiempos_ms) > 1 else 0
            minimo = min(tiempos_ms)
            maximo = max(tiempos_ms)
            
            # Percentiles
            tiempos_ordenados = sorted(tiempos_ms)
            p50 = tiempos_ordenados[int(len(tiempos_ordenados) * 0.50)]
            p75 = tiempos_ordenados[int(len(tiempos_ordenados) * 0.75)]
            p95 = tiempos_ordenados[int(len(tiempos_ordenados) * 0.95)] if len(tiempos_ordenados) > 1 else tiempos_ordenados[0]
            
            print(f"📈 RESUMEN:")
            print(f"   • Total de cambios detectados: {len(self.tiempos_cambio)}/{self.num_sesiones}")
            print(f"   • Porcentaje de cambios: {(len(self.tiempos_cambio)/self.num_sesiones)*100:.1f}%")
            
            print(f"\n⏱️  TIEMPO TOTAL (evento → HTML servido) (ms):")
            print(f"   • Promedio: {promedio:.2f}ms")
            print(f"   • Mediana: {mediana:.2f}ms")
            print(f"   • Desviación estándar: {desviacion:.2f}ms")
            print(f"   • Mínimo: {minimo:.2f}ms")
            print(f"   • Máximo: {maximo:.2f}ms")
            
            print(f"\n📊 PERCENTILES:")
            print(f"   • P50 (mediana): {p50:.2f}ms")
            print(f"   • P75: {p75:.2f}ms")
            print(f"   • P95: {p95:.2f}ms")
            
            # Detalles de cada cambio
            print(f"\n🔍 DETALLES DE CAMBIOS:")
            for cambio in self.cambios_detectados:
                print(f"   Sesión {cambio['sesion']} ({cambio['perfil']}):")
                print(f"      {cambio['interfaz_inicial']} → {cambio['interfaz_final']}")
                print(f"      Tiempo: {cambio['tiempo_cambio_ms']:.2f}ms")
                if cambio.get('nivel'):
                    print(f"      Nivel: {cambio['nivel']:.2f}")
            
            # Evaluación de rendimiento
            print(f"\n🎯 EVALUACIÓN:")
            if promedio < 500:
                print(f"   ✅ EXCELENTE: Tiempo promedio ({promedio:.2f}ms) < 500ms")
            elif promedio < 1000:
                print(f"   ✅ BUENO: Tiempo promedio ({promedio:.2f}ms) < 1000ms")
            elif promedio < 2000:
                print(f"   ⚠️  ACEPTABLE: Tiempo promedio ({promedio:.2f}ms) < 2000ms")
            else:
                print(f"   ❌ LENTO: Tiempo promedio ({promedio:.2f}ms) >= 2000ms")
        
        # Guardar resultados
        self.guardar_resultados()
    
    def guardar_resultados(self):
        """Guarda los resultados en un archivo JSON"""
        resultados = {
            "timestamp": datetime.now().isoformat(),
            "configuracion": {
                "base_url": self.base_url,
                "num_sesiones": self.num_sesiones
            },
            "estadisticas": {
                "total_cambios": len(self.tiempos_cambio),
                "total_sesiones": self.num_sesiones,
                "porcentaje_cambios": (len(self.tiempos_cambio)/self.num_sesiones)*100 if self.num_sesiones > 0 else 0,
                "tiempo_promedio_ms": statistics.mean(self.tiempos_cambio) if self.tiempos_cambio else 0,
                "tiempo_mediana_ms": statistics.median(self.tiempos_cambio) if self.tiempos_cambio else 0,
                "tiempo_minimo_ms": min(self.tiempos_cambio) if self.tiempos_cambio else 0,
                "tiempo_maximo_ms": max(self.tiempos_cambio) if self.tiempos_cambio else 0,
                "desviacion_estandar_ms": statistics.stdev(self.tiempos_cambio) if len(self.tiempos_cambio) > 1 else 0
            },
            "tiempos_cambio": self.tiempos_cambio,
            "cambios_detectados": self.cambios_detectados,
            "resultados_detallados": self.resultados_detallados
        }
        
        os.makedirs("pruebas/resultados", exist_ok=True)
        archivo_resultados = f"pruebas/resultados/tiempo_cambio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(archivo_resultados, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: {archivo_resultados}")
        print(f"{'='*70}\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test de Tiempo de Cambio de Interfaz - Sistema POS Adaptativo')
    parser.add_argument('--url', type=str, default='http://localhost:5000',
                       help='URL base del servidor Flask (default: http://localhost:5000)')
    parser.add_argument('--sesiones', type=int, default=5,
                       help='Número de sesiones a simular (default: 5)')
    
    args = parser.parse_args()
    
    test = TestTiempoCambioInterfaz(base_url=args.url, num_sesiones=args.sesiones)
    test.ejecutar_test()

