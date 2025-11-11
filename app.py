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
    try:
        # Verificar si la primera fila tiene valores válidos
        primera_fila = df.iloc[0]
        
        # Verificar si SesionID está vacío o es NaN (indica fila vacía)
        sesion_id = str(primera_fila.get('SesionID', '')).strip()
        if not sesion_id or sesion_id == '' or sesion_id.lower() == 'nan':
            print(f"\n{'='*60}")
            print(f"🆕 CSV SOLO CON ENCABEZADO - Mostrando interfaz original")
            print(f"{'='*60}")
            return redirect(url_for("original"))
        
        errores = pd.to_numeric(primera_fila.get('ErroresSesion', 0), errors='coerce')
        tareas = pd.to_numeric(primera_fila.get('TareasCompletadas', 0), errors='coerce')
        
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
    """Registrar evento y re-evaluar interfaz"""
    global interfaz_actual
    
    tipo_evento = request.form.get("tipo_evento")
    duracion = float(request.form.get("duracion", 0))
    exito = request.form.get("exito", "true") == "true"

    registrar_evento(tipo_evento, duracion, exito)
    interfaz, nivel = evaluar_y_asignar()

    # Determinar nueva interfaz
    nueva_interfaz = ""
    if nivel < 40:
        nueva_interfaz = "novato"
    elif 40 <= nivel < 70:
        nueva_interfaz = "intermedio"
    else:
        nueva_interfaz = "experto"
    
    if nueva_interfaz != interfaz_actual:
        print(f"\n🔄 [CAMBIO DE INTERFAZ] {interfaz_actual.upper()} → {nueva_interfaz.upper()}\n")
        interfaz_actual = nueva_interfaz
    
    # Siempre redirigir a la nueva interfaz determinada
    return redirect(url_for(nueva_interfaz))

@app.route("/api/evento", methods=["POST"])
def evento_api():
    """Endpoint API para registrar eventos (AJAX)"""
    global interfaz_actual
    
    data = request.json
    tipo_evento = data.get("tipo_evento")
    duracion = float(data.get("duracion", 0))
    exito = data.get("exito", True)

    registrar_evento(tipo_evento, duracion, exito)
    interfaz, nivel = evaluar_y_asignar()
    
    nueva_interfaz = ""
    if nivel < 40:
        nueva_interfaz = "novato"
    elif 40 <= nivel < 70:
        nueva_interfaz = "intermedio"
    else:
        nueva_interfaz = "experto"
    
    cambio = nueva_interfaz != interfaz_actual
    if cambio:
        print(f"\n🔄 [CAMBIO DETECTADO VIA API] {interfaz_actual.upper()} → {nueva_interfaz.upper()}\n")
        interfaz_actual = nueva_interfaz
    
    return jsonify({
        "status": "ok",
        "nivel": nivel,
        "interfaz": nueva_interfaz,
        "cambio_interfaz": cambio
    })

@app.route("/api/estado", methods=["GET"])
def obtener_estado():
    """Obtiene el estado actual del sistema"""
    archivo = "data/dataset_pos.csv"
    
    if not os.path.exists(archivo):
        return jsonify({
            "eventos": 0,
            "tiempo_promedio": 0,
            "errores": 0,
            "tareas": 0,
            "nivel": "Novato"
        })
    
    df = pd.read_csv(archivo)
    if df.empty:
        return jsonify({
            "eventos": 0,
            "tiempo_promedio": 0,
            "errores": 0,
            "tareas": 0,
            "nivel": "Novato"
        })
    
    return jsonify({
        "eventos": int(df['ErroresSesion'].iloc[0] + df['TareasCompletadas'].iloc[0]),
        "tiempo_promedio": float(df['TiempoPromedioAccion(s)'].iloc[0]),
        "errores": int(df['ErroresSesion'].iloc[0]),
        "tareas": int(df['TareasCompletadas'].iloc[0]),
        "nivel": str(df['NivelClasificado'].iloc[0])
    })

# Rutas para cada interfaz principal
@app.route("/novato")
def novato():
    return render_template("interfaz_novato/interfaz_novato.html", nivel_actual="novato")

@app.route("/intermedio")
def intermedio():
    return render_template("interfaz_intermedio/interfaz_intermedio.html", nivel_actual="intermedio")

@app.route("/experto")
def experto():
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