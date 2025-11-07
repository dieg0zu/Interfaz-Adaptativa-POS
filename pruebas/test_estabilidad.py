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
import shutil
import json

class TestEstabilidad:
    def __init__(self, num_sesiones=30):
        self.num_sesiones = num_sesiones
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.carpeta_prueba = f"pruebas/datos_prueba/estabilidad_{self.timestamp}"
        self.archivo_log = f"pruebas/logs/estabilidad_{self.timestamp}.log"
        self.archivo_csv = None
        
        # Crear carpetas
        os.makedirs(self.carpeta_prueba, exist_ok=True)
        os.makedirs("pruebas/logs", exist_ok=True)
        os.makedirs("pruebas/resultados", exist_ok=True)
        
        # Configurar archivo CSV de prueba
        self.configurar_entorno()
        
        # Métricas de la prueba
        self.errores_criticos = []
        self.advertencias = []
        self.sesiones_exitosas = 0
        self.tiempo_inicio = None
        self.tiempo_fin = None
        
    def configurar_entorno(self):
        """Configura el entorno de prueba"""
        # Backup del CSV original si existe
        if os.path.exists("data/dataset_pos.csv"):
            shutil.copy("data/dataset_pos.csv", f"{self.carpeta_prueba}/backup_original.csv")
            self.log("✅ Backup del CSV original creado")
        
        # Usar un CSV temporal para las pruebas
        self.archivo_csv = f"{self.carpeta_prueba}/dataset_pos.csv"
        
        # Modificar temporalmente la ruta en logger
        import src.logger as logger_module
        self.ruta_original = "data/dataset_pos.csv"
        
        self.log("🔧 Entorno de prueba configurado")
        self.log(f"📁 Carpeta: {self.carpeta_prueba}")
    
    def log(self, mensaje, nivel="INFO"):
        """Registra mensaje en log y consola"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        linea = f"[{timestamp}] [{nivel}] {mensaje}"
        
        print(linea)
        
        with open(self.archivo_log, "a", encoding="utf-8") as f:
            f.write(linea + "\n")
    
    def simular_sesion(self, sesion_id, perfil="aleatorio"):
        """Simula una sesión completa de usuario"""
        self.log(f"\n{'='*70}")
        self.log(f"🎮 SESIÓN {sesion_id}/{self.num_sesiones} - Perfil: {perfil}")
        self.log(f"{'='*70}")
        
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
        
        self.log(f"👤 Perfil: {perfil.upper()}")
        self.log(f"📊 Acciones planificadas: {num_acciones}")
        
        # Resetear sesión (crear nuevo CSV)
        if os.path.exists(self.archivo_csv):
            os.remove(self.archivo_csv)
        
        # Cambiar temporalmente la ruta del logger
        import src.logger as logger_module
        ruta_backup = "data/dataset_pos.csv"
        
        # Simular acciones
        errores_sesion = 0
        exitos_sesion = 0
        
        for i in range(num_acciones):
            tipo_evento = random.choice([
                "agregar_producto", "eliminar_producto", "buscar_cliente",
                "aplicar_descuento", "procesar_venta", "generar_reporte",
                "consultar_inventario", "modificar_precio"
            ])
            
            duracion = random.uniform(*rango_tiempo)
            exito = random.random() > prob_error
            
            try:
                # Modificar temporalmente la ruta en logger
                original_file = logger_module.__file__
                
                # Registrar evento en la ruta de prueba
                with open(self.archivo_csv, "a", newline="", encoding="utf-8") as f:
                    import csv
                    writer = csv.writer(f)
                    
                    if i == 0:
                        writer.writerow(["SesionID", "TiempoPromedioAccion(s)", "ErroresSesion", "TareasCompletadas", "NivelClasificado"])
                        writer.writerow([f"S{sesion_id:03d}", 0, 0, 0, "Novato"])
                    
                    if not os.path.exists(self.archivo_csv) or os.path.getsize(self.archivo_csv) == 0:
    # Si el archivo no existe o está vacío, inicialízalo
                        df_nuevo = pd.DataFrame([{
                            'SesionID': f"S{sesion_id:03d}",
                            'TiempoPromedioAccion(s)': 0,
                            'ErroresSesion': 0,
                            'TareasCompletadas': 0,
                            'NivelClasificado': ''
                        }])
                        df_nuevo.to_csv(self.archivo_csv, index=False)
                    
                    # Leer y actualizar
                    df = pd.read_csv(self.archivo_csv)

                    # Convertir valores a tipo numérico
                    df['TiempoPromedioAccion(s)'] = pd.to_numeric(df['TiempoPromedioAccion(s)'], errors='coerce').fillna(0)
                    df['ErroresSesion'] = pd.to_numeric(df['ErroresSesion'], errors='coerce').fillna(0)
                    df['TareasCompletadas'] = pd.to_numeric(df['TareasCompletadas'], errors='coerce').fillna(0)

                    tiempo_actual = df['TiempoPromedioAccion(s)'].iloc[0]
                    errores_actual = df['ErroresSesion'].iloc[0]
                    tareas_actual = df['TareasCompletadas'].iloc[0]
                    eventos_totales = errores_actual + tareas_actual
                    
                    if exito:
                        tareas_actual += 1
                        exitos_sesion += 1
                    else:
                        errores_actual += 1
                        errores_sesion += 1
                    
                    eventos_totales += 1
                    
                    if eventos_totales == 1:
                        tiempo_nuevo = duracion
                    else:
                        tiempo_nuevo = ((tiempo_actual * (eventos_totales - 1)) + duracion) / eventos_totales
                    
                    # Reescribir archivo
                    df_nuevo = pd.DataFrame([{
                        'SesionID': f"S{sesion_id:03d}",
                        'TiempoPromedioAccion(s)': round(tiempo_nuevo, 2),
                        'ErroresSesion': errores_actual,
                        'TareasCompletadas': tareas_actual,
                        'NivelClasificado': ''
                    }])
                    
                    df_nuevo.to_csv(self.archivo_csv, index=False)
                
                if i % 5 == 0:
                    self.log(f"  📝 Acción {i+1}/{num_acciones}: {tipo_evento} ({duracion:.2f}s) {'✅' if exito else '❌'}")
                
                time.sleep(0.05)  # Pequeña pausa para simular realismo
                
            except Exception as e:
                self.log(f"❌ ERROR en acción {i+1}: {str(e)}", "ERROR")
                self.errores_criticos.append({
                    'sesion': sesion_id,
                    'accion': i+1,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                return False
        
        # Evaluar nivel final
        try:
            # Temporalmente copiar el CSV de prueba a data/
            shutil.copy(self.archivo_csv, "data/dataset_pos.csv")
            interfaz, nivel = evaluar_y_asignar()
            
            # Actualizar nivel clasificado
            df = pd.read_csv(self.archivo_csv)
            if "novato" in interfaz.lower():
                nivel_texto = "Novato"
            elif "intermedio" in interfaz.lower():
                nivel_texto = "Intermedio"
            else:
                nivel_texto = "Experto"
            
            df['NivelClasificado'] = nivel_texto
            df.to_csv(self.archivo_csv, index=False)
            
            self.log(f"🎯 Nivel final: {nivel:.2f} → {nivel_texto}")
            
        except Exception as e:
            self.log(f"⚠️  ADVERTENCIA: Error al evaluar nivel: {str(e)}", "WARNING")
            self.advertencias.append({
                'sesion': sesion_id,
                'tipo': 'evaluacion_nivel',
                'detalle': str(e)
            })
        
        # Copiar resultado a carpeta de resultados
        resultado_sesion = f"{self.carpeta_prueba}/sesion_{sesion_id:03d}.csv"
        shutil.copy(self.archivo_csv, resultado_sesion)
        
        self.log(f"✅ Sesión {sesion_id} completada: {exitos_sesion} éxitos, {errores_sesion} errores")
        self.sesiones_exitosas += 1
        
        return True
    
    def verificar_integridad(self):
        """Verifica la integridad de todos los CSVs generados"""
        self.log(f"\n{'='*70}")
        self.log("🔍 VERIFICACIÓN DE INTEGRIDAD")
        self.log(f"{'='*70}")
        
        archivos_csv = [f for f in os.listdir(self.carpeta_prueba) if f.startswith("sesion_") and f.endswith(".csv")]
        
        if len(archivos_csv) != self.num_sesiones:
            self.log(f"⚠️  Advertencia: Se esperaban {self.num_sesiones} archivos, se encontraron {len(archivos_csv)}", "WARNING")
        
        sesiones_validas = 0
        sesiones_invalidas = 0
        
        for archivo in sorted(archivos_csv):
            ruta = os.path.join(self.carpeta_prueba, archivo)
            
            try:
                df = pd.read_csv(ruta)
                
                # Verificar columnas
                columnas_esperadas = ['SesionID', 'TiempoPromedioAccion(s)', 'ErroresSesion', 'TareasCompletadas', 'NivelClasificado']
                if list(df.columns) != columnas_esperadas:
                    raise ValueError(f"Columnas incorrectas: {list(df.columns)}")
                
                # Verificar datos
                if df.empty:
                    raise ValueError("DataFrame vacío")
                
                if len(df) != 1:
                    raise ValueError(f"Se esperaba 1 fila, se encontraron {len(df)}")
                
                # Verificar tipos de datos
                tiempo = df['TiempoPromedioAccion(s)'].iloc[0]
                errores = df['ErroresSesion'].iloc[0]
                tareas = df['TareasCompletadas'].iloc[0]
                
                if not isinstance(tiempo, (int, float)) or tiempo < 0:
                    raise ValueError(f"Tiempo inválido: {tiempo}")
                
                if not isinstance(errores, (int, float)) or errores < 0:
                    raise ValueError(f"Errores inválidos: {errores}")
                
                if not isinstance(tareas, (int, float)) or tareas < 0:
                    raise ValueError(f"Tareas inválidas: {tareas}")
                
                sesiones_validas += 1
                
            except Exception as e:
                self.log(f"❌ {archivo}: INVÁLIDO - {str(e)}", "ERROR")
                sesiones_invalidas += 1
                self.errores_criticos.append({
                    'archivo': archivo,
                    'error': str(e),
                    'tipo': 'integridad'
                })
        
        self.log(f"\n📊 Resumen de Integridad:")
        self.log(f"   ✅ Sesiones válidas: {sesiones_validas}")
        self.log(f"   ❌ Sesiones inválidas: {sesiones_invalidas}")
        
        integridad_porcentaje = (sesiones_validas / len(archivos_csv) * 100) if archivos_csv else 0
        self.log(f"   📈 Integridad: {integridad_porcentaje:.2f}%")
        
        return integridad_porcentaje
    
    def verificar_duplicados(self):
        """Verifica que no haya sesiones duplicadas"""
        self.log(f"\n🔍 Verificando duplicados...")
        
        archivos_csv = [f for f in os.listdir(self.carpeta_prueba) if f.startswith("sesion_") and f.endswith(".csv")]
        
        sesiones_ids = []
        for archivo in archivos_csv:
            ruta = os.path.join(self.carpeta_prueba, archivo)
            try:
                df = pd.read_csv(ruta)
                sesion_id = df['SesionID'].iloc[0]
                sesiones_ids.append(sesion_id)
            except:
                pass
        
        duplicados = len(sesiones_ids) - len(set(sesiones_ids))
        
        if duplicados > 0:
            self.log(f"❌ Se encontraron {duplicados} IDs duplicados", "ERROR")
            return False
        else:
            self.log(f"✅ No se encontraron duplicados")
            return True
    
    def generar_reporte(self, integridad_porcentaje):
        """Genera reporte final de la prueba"""
        tiempo_total = self.tiempo_fin - self.tiempo_inicio
        
        reporte = {
            'fecha': datetime.now().isoformat(),
            'duracion_segundos': tiempo_total,
            'sesiones_planificadas': self.num_sesiones,
            'sesiones_exitosas': self.sesiones_exitosas,
            'sesiones_fallidas': self.num_sesiones - self.sesiones_exitosas,
            'errores_criticos': len(self.errores_criticos),
            'advertencias': len(self.advertencias),
            'integridad_porcentaje': integridad_porcentaje,
            'cumple_criterio': integridad_porcentaje == 100 and len(self.errores_criticos) == 0,
            'detalles_errores': self.errores_criticos,
            'detalles_advertencias': self.advertencias
        }
        
        # Guardar reporte JSON
        archivo_reporte_json = f"pruebas/resultados/estabilidad_{self.timestamp}.json"
        with open(archivo_reporte_json, "w", encoding="utf-8") as f:
            json.dump(reporte, f, indent=4, ensure_ascii=False)
        
        # Guardar reporte TXT legible
        archivo_reporte_txt = f"pruebas/resultados/estabilidad_{self.timestamp}.txt"
        with open(archivo_reporte_txt, "w", encoding="utf-8") as f:
            f.write("="*80 + "\n")
            f.write("REPORTE DE PRUEBA DE ESTABILIDAD\n")
            f.write("Sistema POS Adaptativo\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"⏱️  Duración: {tiempo_total:.2f} segundos ({tiempo_total/60:.2f} minutos)\n")
            f.write(f"📁 Carpeta de datos: {self.carpeta_prueba}\n")
            f.write(f"📄 Log detallado: {self.archivo_log}\n\n")
            
            f.write("-"*80 + "\n")
            f.write("RESULTADOS\n")
            f.write("-"*80 + "\n\n")
            
            f.write(f"🎯 Sesiones planificadas: {self.num_sesiones}\n")
            f.write(f"✅ Sesiones exitosas: {self.sesiones_exitosas}\n")
            f.write(f"❌ Sesiones fallidas: {self.num_sesiones - self.sesiones_exitosas}\n")
            f.write(f"📊 Integridad de datos: {integridad_porcentaje:.2f}%\n")
            f.write(f"🐛 Errores críticos: {len(self.errores_criticos)}\n")
            f.write(f"⚠️  Advertencias: {len(self.advertencias)}\n\n")
            
            f.write("-"*80 + "\n")
            f.write("CRITERIOS DE ACEPTACIÓN\n")
            f.write("-"*80 + "\n\n")
            
            f.write(f"• 0 errores críticos: {'✅ CUMPLE' if len(self.errores_criticos) == 0 else '❌ NO CUMPLE'}\n")
            f.write(f"• 100% de integridad: {'✅ CUMPLE' if integridad_porcentaje == 100 else '❌ NO CUMPLE'}\n")
            f.write(f"• 30+ sesiones: {'✅ CUMPLE' if self.num_sesiones >= 30 else '❌ NO CUMPLE'}\n\n")
            
            if reporte['cumple_criterio']:
                f.write("🎉 RESULTADO FINAL: ✅ PRUEBA SUPERADA\n\n")
            else:
                f.write("⚠️  RESULTADO FINAL: ❌ PRUEBA NO SUPERADA\n\n")
            
            if self.errores_criticos:
                f.write("-"*80 + "\n")
                f.write("ERRORES CRÍTICOS DETALLADOS\n")
                f.write("-"*80 + "\n\n")
                for i, error in enumerate(self.errores_criticos, 1):
                    f.write(f"{i}. {error}\n\n")
            
            if self.advertencias:
                f.write("-"*80 + "\n")
                f.write("ADVERTENCIAS\n")
                f.write("-"*80 + "\n\n")
                for i, adv in enumerate(self.advertencias, 1):
                    f.write(f"{i}. {adv}\n\n")
        
        self.log(f"\n📄 Reporte guardado:")
        self.log(f"   JSON: {archivo_reporte_json}")
        self.log(f"   TXT: {archivo_reporte_txt}")
        
        return reporte
    
    def ejecutar(self):
        """Ejecuta la prueba completa"""
        self.log("\n" + "="*70)
        self.log("🚀 INICIANDO PRUEBA DE ESTABILIDAD")
        self.log("="*70)
        self.log(f"📊 Sesiones a simular: {self.num_sesiones}")
        self.log(f"🕐 Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.tiempo_inicio = time.time()
        
        # Ejecutar sesiones
        for i in range(1, self.num_sesiones + 1):
            perfil = random.choice(["novato", "intermedio", "experto"])
            exito = self.simular_sesion(i, perfil)
            
            if not exito:
                self.log(f"❌ Sesión {i} falló", "ERROR")
            
            # Pequeña pausa entre sesiones
            time.sleep(0.1)
        
        self.tiempo_fin = time.time()
        
        # Verificaciones
        integridad = self.verificar_integridad()
        self.verificar_duplicados()
        
        # Generar reporte
        reporte = self.generar_reporte(integridad)
        
        # Resumen final
        self.log(f"\n{'='*70}")
        self.log("🏁 PRUEBA FINALIZADA")
        self.log(f"{'='*70}")
        self.log(f"⏱️  Tiempo total: {self.tiempo_fin - self.tiempo_inicio:.2f}s")
        self.log(f"✅ Sesiones exitosas: {self.sesiones_exitosas}/{self.num_sesiones}")
        self.log(f"📊 Integridad: {integridad:.2f}%")
        self.log(f"🐛 Errores críticos: {len(self.errores_criticos)}")
        
        if reporte['cumple_criterio']:
            self.log(f"\n🎉 {'='*68}")
            self.log(f"   ✅ PRUEBA SUPERADA - Todos los criterios cumplidos")
            self.log(f"   {'='*68}\n")
        else:
            self.log(f"\n⚠️  {'='*68}")
            self.log(f"   ❌ PRUEBA NO SUPERADA - Revisar errores")
            self.log(f"   {'='*68}\n")
        
        # Restaurar CSV original si existía
        if os.path.exists(f"{self.carpeta_prueba}/backup_original.csv"):
            shutil.copy(f"{self.carpeta_prueba}/backup_original.csv", "data/dataset_pos.csv")
            self.log("✅ CSV original restaurado")
        
        return reporte

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 PRUEBA DE ESTABILIDAD - Sistema POS Adaptativo")
    print("="*70)
    print("\nEsta prueba simulará 30 sesiones consecutivas de usuarios")
    print("y verificará la integridad de los datos registrados.\n")
    
    respuesta = input("¿Deseas continuar? (s/n): ")
    
    if respuesta.lower() == 's':
        num_sesiones = input("\n¿Cuántas sesiones deseas simular? (default: 30): ")
        num_sesiones = int(num_sesiones) if num_sesiones.strip() else 30
        
        test = TestEstabilidad(num_sesiones=num_sesiones)
        reporte = test.ejecutar()
        
        print(f"\n✅ Prueba completada. Revisa los resultados en:")
        print(f"   📁 {test.carpeta_prueba}")
        print(f"   📄 pruebas/resultados/estabilidad_{test.timestamp}.txt")
    else:
        print("\n❌ Prueba cancelada")