import pandas as pd
from motor_difuso import crear_motor_difuso
from asignador_interfaz import asignar_interfaz

df = pd.read_csv("data/Dataset_POS.csv")

motor = crear_motor_difuso()

# Clasificar cada sesión
resultados = []
for i, row in df.iterrows():
    motor.input['TiempoPromedioAccion'] = row['TiempoPromedioAccion(s)']
    motor.input['ErroresSesion'] = row['ErroresSesion']
    motor.input['TareasCompletadas'] = row['TareasCompletadas']
    
    motor.compute()
    nivel = motor.output['NivelUsuario']
    interfaz = asignar_interfaz(nivel)
    
    resultados.append((row['SesionID'], nivel, interfaz))

# Mostrar resultados
for r in resultados[:10]:
    print(f"Sesion {r[0]} → Nivel: {r[1]:.2f} → {r[2]}")
