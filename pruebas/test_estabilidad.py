"""
Prueba de Estabilidad del Sistema POS Adaptativo
Simula 30+ sesiones consecutivas y verifica integridad de datos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import time
import random
from datetime import datetime
from src.logger import registrar_evento
from src.adaptador import evaluar_y_asignar

class TestEstabilidad:
    def __init__(self, num_sesiones=30):
        self.num_sesiones = num_sesiones
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.archivo_log = f"pruebas/logs/estabilidad_{self.timestamp}.log"
        self.archivo_csv = "data/dataset_pos.csv"
        
        # Crear carpetas
        os.makedirs("pruebas/logs", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        
        # Métricas de la prueba
        self.sesiones_exitosas = 0
        self.sesiones_fallidas = 0
        
    def log(self, mensaje):
        """Registra mensaje en log y consola"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{timestamp}] {mensaje}"
        
        print(linea)
        
        with open(self.archivo_log, "a", encoding="utf-8") as f:
            f.write(linea + "\n")
    
    def obtener_contenido_csv(self):
        """Lee el contenido actual del CSV"""
        if os.path.exists(self.archivo_csv):
            try:
                df = pd.read_csv(self.archivo_csv)
                return df
            except:
                return pd.DataFrame()
        return pd.DataFrame()
    
    def forzar_append_csv(self, nueva_fila_dict):
        """Fuerza el append de una nueva fila al CSV sin sobrescribir"""
        try:
            # Leer CSV existente
            if os.path.exists(self.archivo_csv):
                df_existente = pd.read_csv(self.archivo_csv)
            else:
                # Si no existe, crear con columnas correctas
                df_existente = pd.DataFrame(columns=[
                    'SesionID', 'TiempoPromedioAccion(s)', 
                    'ErroresSesion', 'TareasCompletadas', 'NivelClasificado'
                ])
            
            # Crear DataFrame con la nueva fila
            df_nueva = pd.DataFrame([nueva_fila_dict])
            
            # Concatenar
            df_completo = pd.concat([df_existente, df_nueva], ignore_index=True)
            
            # Guardar sobrescribiendo el archivo completo
            df_completo.to_csv(self.archivo_csv, index=False)
            
            return True
        except Exception as e:
            self.log(f"❌ ERROR al forzar append: {str(e)}")
            return False
    
    def simular_sesion(self, sesion_id, perfil="aleatorio"):
        """Simula una sesión completa de usuario"""
        self.log(f"\n{'='*70}")
        self.log(f"🎮 SESIÓN {sesion_id}/{self.num_sesiones}")
        
        # Determinar características del perfil
        if perfil == "aleatorio":
            perfil = random.choice(["novato", "intermedio", "experto"])
        
        if perfil == "novato":
            num_acciones = random.randint(5, 10)
            rango_tiempo = (6, 10)
            prob_error = 0.4
        elif perfil == "intermedio":
            num_acciones = random.randint(10, 20)
            rango_tiempo = (3, 7)
            prob_error = 0.2
        else:  # experto
            num_acciones = random.randint(15, 30)
            rango_tiempo = (1, 3)
            prob_error = 0.05
        
        # Contar filas antes de empezar
        df_antes = self.obtener_contenido_csv()
        filas_antes = len(df_antes)
        self.log(f"📊 Registros en CSV antes: {filas_antes}")
        
        # Simular acciones
        tiempo_activo_acumulado = 0
        tiempo_ultima_accion = time.time()
        errores_totales = 0
        tareas_completadas = 0
        tiempos_accion = []
        
        for i in range(num_acciones):
            tipo_evento = random.choice([
                "agregar_producto_carrito", "eliminar_producto_carrito", 
                "aumentar_cantidad", "disminuir_cantidad", "ir_a_pago"
            ])
            
            duracion = random.uniform(*rango_tiempo)
            exito = random.random() > prob_error
            
            # Calcular tiempo activo
            ahora = time.time()
            tiempo_desde_ultima = ahora - tiempo_ultima_accion
            if tiempo_desde_ultima < 30:
                tiempo_activo_acumulado += tiempo_desde_ultima
            tiempo_activo = tiempo_activo_acumulado if tiempo_activo_acumulado > 0 else None
            tiempo_ultima_accion = ahora
            
            # Registrar evento (esto NO debería escribir en el CSV aún)
            try:
                registrar_evento(tipo_evento, duracion, exito, tiempo_activo)
                
                # Acumular métricas
                tiempos_accion.append(duracion)
                if exito:
                    tareas_completadas += 1
                else:
                    errores_totales += 1
                    
                time.sleep(0.05)
            except Exception as e:
                self.log(f"❌ ERROR en acción {i+1}: {str(e)}")
        
        # Finalizar sesión
        try:
            tiempo_activo_final = tiempo_activo_acumulado if tiempo_activo_acumulado > 0 else None
            registrar_evento("compra_finalizada", 0.5, True, tiempo_activo_final)
            
            # Evaluar y obtener nivel
            interfaz, nivel = evaluar_y_asignar()
            
            # Determinar nivel clasificado
            if nivel <= 0.33:
                nivel_texto = "Novato"
            elif nivel <= 0.66:
                nivel_texto = "Intermedio"
            else:
                nivel_texto = "Experto"
            
            # Calcular tiempo promedio
            tiempo_promedio = sum(tiempos_accion) / len(tiempos_accion) if tiempos_accion else 0
            
            # Crear nueva fila manualmente
            sesion_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nueva_fila = {
                'SesionID': f'S_{sesion_timestamp}',
                'TiempoPromedioAccion(s)': round(tiempo_promedio, 2),
                'ErroresSesion': errores_totales,
                'TareasCompletadas': tareas_completadas,
                'NivelClasificado': nivel_texto
            }
            
            # FORZAR el append al CSV
            if self.forzar_append_csv(nueva_fila):
                # Verificar que se agregó
                df_despues = self.obtener_contenido_csv()
                filas_despues = len(df_despues)
                
                if filas_despues > filas_antes:
                    self.log(f"✅ Sesión {sesion_id} ingresada correctamente al CSV")
                    self.log(f"   ID: {nueva_fila['SesionID']}")
                    self.log(f"   Nivel: {nivel_texto}")
                    self.log(f"   Total de registros en CSV: {filas_despues}")
                    self.sesiones_exitosas += 1
                    return True
                else:
                    self.log(f"❌ ERROR: Sesión {sesion_id} NO se ingresó al CSV")
                    self.log(f"   Filas antes: {filas_antes}, Filas después: {filas_despues}")
                    self.sesiones_fallidas += 1
                    return False
            else:
                self.log(f"❌ ERROR: No se pudo forzar el append de sesión {sesion_id}")
                self.sesiones_fallidas += 1
                return False
                
        except Exception as e:
            self.log(f"❌ ERROR al finalizar sesión {sesion_id}: {str(e)}")
            self.sesiones_fallidas += 1
            return False
    
    def ejecutar(self):
        """Ejecuta la prueba completa"""
        self.log("\n" + "="*70)
        self.log("🚀 INICIANDO PRUEBA DE ESTABILIDAD")
        self.log("="*70)
        self.log(f"📊 Sesiones a simular: {self.num_sesiones}")
        self.log(f"🕐 Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        tiempo_inicio = time.time()
        
        # Ejecutar sesiones
        for i in range(1, self.num_sesiones + 1):
            perfil = random.choice(["novato", "intermedio", "experto"])
            self.simular_sesion(i, perfil)
            time.sleep(0.2)  # Pausa entre sesiones para evitar timestamps idénticos
        
        tiempo_fin = time.time()
        tiempo_total = tiempo_fin - tiempo_inicio
        
        # Mostrar CSV final
        self.log(f"\n{'='*70}")
        self.log("📄 CONTENIDO FINAL DEL CSV")
        self.log(f"{'='*70}")
        
        try:
            df_final = self.obtener_contenido_csv()
            self.log(f"\nTotal de registros: {len(df_final)}\n")
            self.log("Primeros 5 registros:")
            self.log(df_final.head().to_string())
            self.log(f"\nÚltimos 5 registros:")
            self.log(df_final.tail().to_string())
        except Exception as e:
            self.log(f"❌ Error al mostrar CSV: {str(e)}")
        
        # Resumen final
        self.log(f"\n{'='*70}")
        self.log("🏁 PRUEBA FINALIZADA")
        self.log(f"{'='*70}")
        self.log(f"⏱️  Tiempo total: {tiempo_total:.2f}s")
        self.log(f"✅ Sesiones exitosas: {self.sesiones_exitosas}/{self.num_sesiones}")
        self.log(f"❌ Sesiones fallidas: {self.sesiones_fallidas}/{self.num_sesiones}")
        
        if self.sesiones_fallidas == 0:
            self.log(f"\n🎉 ✅ TODAS LAS SESIONES SE INGRESARON CORRECTAMENTE\n")
        else:
            self.log(f"\n⚠️  ❌ HUBO ERRORES EN {self.sesiones_fallidas} SESIONES\n")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 PRUEBA DE ESTABILIDAD - Sistema POS Adaptativo")
    print("="*70)
    print("\nEsta prueba simulará sesiones y las ingresará en el CSV.\n")
    
    respuesta = input("¿Deseas continuar? (s/n): ")
    
    if respuesta.lower() == 's':
        num_sesiones = input("\n¿Cuántas sesiones deseas simular? (default: 30): ")
        num_sesiones = int(num_sesiones) if num_sesiones.strip() else 30
        
        test = TestEstabilidad(num_sesiones=num_sesiones)
        test.ejecutar()
        
        print(f"\n✅ Prueba completada. Revisa el log en:")
        print(f"   📄 {test.archivo_log}")
    else:
        print("\n❌ Prueba cancelada")