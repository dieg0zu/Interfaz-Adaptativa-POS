from flask import Flask, render_template, request, redirect, url_for, jsonify
from src.adaptador import evaluar_y_asignar
from src.logger import registrar_evento
import os
import pandas as pd

app = Flask(__name__, template_folder='ui')

interfaz_actual = "novato"

@app.route("/")
def home():
    """Página inicial - detecta nivel y redirige"""
    global interfaz_actual
    
    archivo = "data/dataset_pos.csv"
    
    # Verificar si es la primera vez (sin datos)
    es_primera_vez = False
    if not os.path.exists(archivo):
        es_primera_vez = True
        print(f"\n{'='*60}")
        print(f"🆕 PRIMERA VEZ - Mostrando interfaz original")
        print(f"{'='*60}")
        return redirect(url_for("original"))
    
    df = pd.read_csv(archivo)
    
    # Verificar si hay datos reales (no solo encabezado)
    if df.empty or len(df) == 0:
        print(f"\n{'='*60}")
        print(f"🆕 SIN DATOS - Mostrando interfaz original")
        print(f"{'='*60}")
        return redirect(url_for("original"))
    
    # Verificar si hay una fila válida con datos
    # Leer la ÚLTIMA fila (sesión actual), no la primera
    try:
        # Verificar si la última fila tiene valores válidos (sesión actual)
        ultima_fila = df.iloc[-1]
        
        # Verificar si SesionID está vacío o es NaN (indica fila vacía)
        sesion_id = str(ultima_fila.get('SesionID', '')).strip()
        if not sesion_id or sesion_id == '' or sesion_id.lower() == 'nan':
            print(f"\n{'='*60}")
            print(f"🆕 CSV SOLO CON ENCABEZADO - Mostrando interfaz original")
            print(f"{'='*60}")
            return redirect(url_for("original"))
        
        errores = pd.to_numeric(ultima_fila.get('ErroresSesion', 0), errors='coerce')
        tareas = pd.to_numeric(ultima_fila.get('TareasCompletadas', 0), errors='coerce')
        
        # Si son NaN, convertirlos a 0
        if pd.isna(errores):
            errores = 0
        if pd.isna(tareas):
            tareas = 0
            
        eventos = int(errores) + int(tareas)
        
        # Si no hay eventos registrados, mostrar interfaz original
        if eventos == 0:
            print(f"\n{'='*60}")
            print(f"🆕 SIN EVENTOS - Mostrando interfaz original")
            print(f"   Errores: {errores}, Tareas: {tareas}")
            print(f"{'='*60}")
            return redirect(url_for("original"))
        
        print(f"\n{'='*60}")
        print(f"🚀 INICIO DE SESIÓN - {eventos} eventos acumulados")
        print(f"   Errores: {errores}, Tareas: {tareas}")
        print(f"{'='*60}")
    except (IndexError, KeyError, ValueError) as e:
        # Si hay algún error al leer los datos, mostrar interfaz original
        print(f"\n{'='*60}")
        print(f"🆕 ERROR AL LEER DATOS - Mostrando interfaz original")
        print(f"   Error: {str(e)}")
        print(f"{'='*60}")
        return redirect(url_for("original"))
    
    interfaz, nivel = evaluar_y_asignar()
    
    # Determinar ruta según nivel
    if nivel < 40:
        interfaz_actual = "novato"
        return redirect(url_for("novato"))
    elif 40 <= nivel < 70:
        interfaz_actual = "intermedio"
        return redirect(url_for("intermedio"))
    else:
        interfaz_actual = "experto"
        return redirect(url_for("experto"))

@app.route("/evento", methods=["POST"])
def evento():
    """Registrar evento (ruta antigua - redirige a /api/evento)
    Esta ruta ya no debería usarse, pero se mantiene por compatibilidad
    """
    # Redirigir a la API moderna
    return redirect(url_for("evento_api"))

@app.route("/api/evento", methods=["POST"])
def evento_api():
    """Endpoint API para registrar eventos (AJAX)
    Solo evalúa y cambia de interfaz cuando se completa una venta (compra_finalizada)
    """
    global interfaz_actual
    
    try:
        data = request.json
        tipo_evento = data.get("tipo_evento", "accion_generica")
        duracion = float(data.get("duracion", 0))
        exito = data.get("exito", True)
        tiempo_activo = data.get("tiempo_activo", None)  # Tiempo activo de la sesión

        # Registrar el evento
        resultado = registrar_evento(tipo_evento, duracion, exito, tiempo_activo)
        es_compra_finalizada = resultado[0]
        sesion_id = resultado[1]
        datos_sesion_completada = resultado[2] if len(resultado) > 2 else None
        
        # SOLO evaluar y clasificar si se completó una venta
        cambio = False
        nueva_interfaz = interfaz_actual
        nivel = 0
        
        if es_compra_finalizada:
            print(f"\n{'='*60}")
            print(f"💰 VENTA COMPLETADA - Evaluando clasificación...")
            print(f"   Sesión completada: {sesion_id}")
            print(f"{'='*60}")
            
            # Evaluar y clasificar usando lógica difusa
            # evaluar_y_asignar leerá la última fila que ahora es la sesión completada
            # (antes de que se agregue la nueva sesión vacía)
            interfaz, nivel = evaluar_y_asignar()
            
            # Determinar nueva interfaz basada en el nivel
            if nivel < 40:
                nueva_interfaz = "novato"
            elif 40 <= nivel < 70:
                nueva_interfaz = "intermedio"
            else:
                nueva_interfaz = "experto"
            
            # IMPORTANTE: Actualizar interfaz_actual ANTES de verificar el cambio
            # para que la comparación sea correcta
            interfaz_anterior = interfaz_actual
            
            # Verificar si hubo cambio de interfaz
            cambio = nueva_interfaz != interfaz_anterior
            if cambio:
                print(f"\n🔄 [CAMBIO DE INTERFAZ] {interfaz_anterior.upper()} → {nueva_interfaz.upper()}")
                print(f"   Nivel: {nivel:.2f}")
                print(f"   Sesión completada: {sesion_id}")
                print(f"{'='*60}\n")
                interfaz_actual = nueva_interfaz  # Actualizar la variable global
            else:
                print(f"   Nivel actual: {nivel:.2f} → Interfaz: {nueva_interfaz.upper()} (sin cambios)")
                print(f"   Sesión completada: {sesion_id}")
                print(f"{'='*60}\n")
                interfaz_actual = nueva_interfaz  # Actualizar aunque no haya cambio (para mantener consistencia)
            
            # AHORA crear la nueva sesión vacía para la próxima venta
            # IMPORTANTE: Agregar como NUEVA FILA, no sobrescribir
            from src.logger import generar_nueva_sesion_id
            import pandas as pd
            
            nueva_sesion_id = generar_nueva_sesion_id()
            df = pd.read_csv("data/dataset_pos.csv")
            
            # Agregar nueva fila al final (nueva sesión vacía)
            nueva_fila = pd.DataFrame([{
                'SesionID': nueva_sesion_id,
                'TiempoPromedioAccion(s)': 0,
                'ErroresSesion': 0,
                'TareasCompletadas': 0,
                'NivelClasificado': nueva_interfaz.capitalize()  # Usar el nivel recién calculado
            }])
            
            # Concatenar al final (agregar nueva fila)
            df = pd.concat([df, nueva_fila], ignore_index=True)
            df.to_csv("data/dataset_pos.csv", index=False)
            
            print(f"[LOGGER] 🆕 Nueva sesión iniciada: {nueva_sesion_id}")
            print(f"[LOGGER] 📊 Total de sesiones en CSV: {len(df)}")
        else:
            # Para eventos normales, solo registrar sin evaluar
            print(f"[EVENTO] {tipo_evento} registrado (sin evaluación - esperando finalizar venta)")
        
        respuesta = {
            "status": "ok",
            "nivel": round(nivel, 2) if es_compra_finalizada else None,
            "interfaz": nueva_interfaz,
            "cambio_interfaz": cambio,
            "sesion_id": sesion_id,
            "mensaje": f"Evento registrado. {'Evaluación completada.' if es_compra_finalizada else 'Esperando finalizar venta para evaluar.'}"
        }
        
        # Si hay cambio de interfaz, forzar redirección inmediata
        if cambio and es_compra_finalizada:
            respuesta["redirigir"] = True
            respuesta["url_redireccion"] = f"/{nueva_interfaz}"
        
        return jsonify(respuesta)
        
    except Exception as e:
        print(f"❌ Error en evento_api: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "mensaje": f"Error al procesar evento: {str(e)}"
        }), 500

@app.route("/api/estado", methods=["GET"])
def obtener_estado():
    """Obtiene el estado actual del sistema"""
    archivo = "data/dataset_pos.csv"
    
    try:
        if not os.path.exists(archivo):
            return jsonify({
                "eventos": 0,
                "tiempo_promedio": 0,
                "errores": 0,
                "tareas": 0,
                "nivel": "Novato",
                "interfaz": "original"
            })
        
        df = pd.read_csv(archivo)
        if df.empty or len(df) == 0:
            return jsonify({
                "eventos": 0,
                "tiempo_promedio": 0,
                "errores": 0,
                "tareas": 0,
                "nivel": "Novato",
                "interfaz": "original"
            })
        
        # Verificar si hay datos válidos - leer la ÚLTIMA fila (sesión actual)
        ultima_fila = df.iloc[-1]
        sesion_id = str(ultima_fila.get('SesionID', '')).strip()
        if not sesion_id or sesion_id == '' or sesion_id.lower() == 'nan':
            return jsonify({
                "eventos": 0,
                "tiempo_promedio": 0,
                "errores": 0,
                "tareas": 0,
                "nivel": "Novato",
                "interfaz": "original"
            })
        
        # Leer métricas de la última fila (sesión actual)
        tiempo_prom = pd.to_numeric(ultima_fila.get('TiempoPromedioAccion(s)', 0), errors='coerce') or 0
        errores = pd.to_numeric(ultima_fila.get('ErroresSesion', 0), errors='coerce') or 0
        tareas = pd.to_numeric(ultima_fila.get('TareasCompletadas', 0), errors='coerce') or 0
        nivel_texto = str(ultima_fila.get('NivelClasificado', 'Novato')) if 'NivelClasificado' in ultima_fila else "Novato"
        
        eventos_totales = int(errores) + int(tareas)
        
        # Determinar interfaz actual
        # NO evaluar aquí para evitar logs durante el proceso
        # Solo leer el nivel del CSV si está disponible
        if eventos_totales == 0:
            interfaz_actual = "original"
        else:
            # Leer el nivel del CSV sin evaluar (para no generar logs)
            try:
                nivel_texto_lower = nivel_texto.lower() if nivel_texto else "novato"
                if "novato" in nivel_texto_lower:
                    interfaz_actual = "novato"
                elif "intermedio" in nivel_texto_lower:
                    interfaz_actual = "intermedio"
                elif "experto" in nivel_texto_lower:
                    interfaz_actual = "experto"
                else:
                    # Si no está claro, usar el nivel numérico del CSV
                    # Pero sin evaluar (para evitar logs)
                    interfaz_actual = nivel_texto_lower
            except:
                interfaz_actual = nivel_texto.lower() if nivel_texto else "novato"
        
        return jsonify({
            "eventos": eventos_totales,
            "tiempo_promedio": float(tiempo_prom),
            "errores": int(errores),
            "tareas": int(tareas),
            "nivel": nivel_texto,
            "interfaz": interfaz_actual
        })
        
    except Exception as e:
        print(f"❌ Error en obtener_estado: {e}")
        return jsonify({
            "eventos": 0,
            "tiempo_promedio": 0,
            "errores": 0,
            "tareas": 0,
            "nivel": "Novato",
            "interfaz": "original",
            "error": str(e)
        }), 500

# Rutas para cada interfaz principal
@app.route("/novato")
def novato():
    global interfaz_actual
    interfaz_actual = "novato"  # Sincronizar con la ruta actual
    return render_template("interfaz_novato/interfaz_novato.html", nivel_actual="novato")

@app.route("/intermedio")
def intermedio():
    global interfaz_actual
    interfaz_actual = "intermedio"  # Sincronizar con la ruta actual
    return render_template("interfaz_intermedio/interfaz_intermedio.html", nivel_actual="intermedio")

@app.route("/experto")
def experto():
    global interfaz_actual
    interfaz_actual = "experto"  # Sincronizar con la ruta actual
    return render_template("interfaz_experto/interfaz_experto.html", nivel_actual="experto")

# Rutas para pantallas de pago
@app.route("/novato/pago")
def novato_pago():
    return render_template("interfaz_novato/interfaz_novato2.html", nivel_actual="novato")

@app.route("/intermedio/pago")
def intermedio_pago():
    return render_template("interfaz_intermedio/interfaz_intermedio2.html", nivel_actual="intermedio")

@app.route("/experto/pago")
def experto_pago():
    return render_template("interfaz_experto/interfaz_experto2.html", nivel_actual="experto")

@app.route("/original")
def original():
    """Interfaz original de Wally POS (pantalla inicial sin datos)"""
    return render_template("interfaz_original.html")

@app.route("/original/pago")
def original_pago():
    """Pantalla de pago para la interfaz original"""
    return render_template("interfaz_original_2.html")

@app.route("/reset", methods=["POST", "GET"])
def reset():
    """Reinicia el sistema (borra datos acumulados)"""
    global interfaz_actual
    archivo = "data/dataset_pos.csv"
    if os.path.exists(archivo):
        os.remove(archivo)
        print("\n" + "="*60)
        print("🔄 SISTEMA REINICIADO - Datos borrados")
        print("="*60 + "\n")
        interfaz_actual = "original"
    # Redirigir a la interfaz original
    return redirect(url_for("original"))

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    
    print("\n" + "="*60)
    print("🚀 SISTEMA POS ADAPTATIVO")
    print("="*60)
    print("📊 Formato de datos: Dataset_POS.csv compatible")
    print("🎯 Columnas: SesionID | TiempoPromedioAccion(s) | ErroresSesion | TareasCompletadas | NivelClasificado")
    print("📍 URL: http://localhost:5000")
    print("🔄 Reset: http://localhost:5000/reset")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)