from flask import Flask, render_template, request, redirect, url_for
from src.adaptador import evaluar_y_asignar
from src.logger import registrar_evento
import os

app = Flask(__name__)

# Página inicial
@app.route("/")
def home():
    return render_template("interfaz_estática.html")

@app.route("/evento", methods=["POST"])
def evento():
    tipo_evento = request.form.get("tipo_evento")
    duracion = float(request.form.get("duracion"))
    exito = request.form.get("exito") == "true"

    registrar_evento(tipo_evento, duracion, exito)

    interfaz, nivel = evaluar_y_asignar()
    print(f"[INFO] Nivel detectado: {nivel:.2f} → {interfaz}")

    if "novato" in interfaz.lower():
        return redirect(url_for("novato"))
    elif "intermedio" in interfaz.lower():
        return redirect(url_for("intermedio"))
    else:
        return redirect(url_for("experto"))

# Interfaces por nivel
@app.route("/novato")
def novato():
    return render_template("interfaz_novato.html")

@app.route("/intermedio")
def intermedio():
    return render_template("interfaz_intermedio.html")

@app.route("/experto")
def experto():
    return render_template("interfaz_experto.html")

if __name__ == "__main__":
    if not os.path.exists("data/dataset_pos.csv"):
        with open("data/dataset_pos.csv", "w") as f:
            f.write("fecha,tipo_evento,duracion,exito\n")
    app.run(debug=True)
