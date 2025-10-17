import csv
from datetime import datetime
import os

def registrar_evento(tipo_evento, duracion, exito=True):
    """Registra eventos del usuario (acciones, errores, etc.) en el dataset."""
    os.makedirs("data", exist_ok=True)

    archivo = "data/dataset_pos.csv"
    existe = os.path.exists(archivo)

    with open(archivo, "a", newline="") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["fecha", "tipo_evento", "duracion", "exito"])
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([fecha, tipo_evento, duracion, int(exito)])

    print(f"[LOG] Evento registrado: {tipo_evento} ({'Éxito' if exito else 'Error'}) - {duracion:.2f}s")
