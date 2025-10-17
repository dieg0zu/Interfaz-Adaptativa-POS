import pandas as pd
from src.motor_difuso import crear_motor_difuso
from src.asignador_interfaz import asignar_interfaz

def evaluar_y_asignar():
    df = pd.read_csv("data/dataset_pos.csv")

    if df.empty:
        return "Intermedio → Interfaz equilibrada", 50.0

    tiempo_prom = df['duracion'].mean()
    errores = len(df[df['exito'] == 0])
    tareas = len(df[df['exito'] == 1])

    motor = crear_motor_difuso()
    motor.input['TiempoPromedioAccion'] = tiempo_prom
    motor.input['ErroresSesion'] = errores
    motor.input['TareasCompletadas'] = tareas
    motor.compute()

    nivel = motor.output['NivelUsuario']
    interfaz = asignar_interfaz(nivel)

    return interfaz, nivel
