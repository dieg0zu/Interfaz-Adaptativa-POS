import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def crear_motor_difuso():
    # Variables de entrada
    tiempo = ctrl.Antecedent(np.arange(0, 11, 1), 'TiempoPromedioAccion')
    errores = ctrl.Antecedent(np.arange(0, 11, 1), 'ErroresSesion')
    tareas = ctrl.Antecedent(np.arange(0, 31, 1), 'TareasCompletadas')

    # Variable de salida
    nivel = ctrl.Consequent(np.arange(0, 101, 1), 'NivelUsuario')

    # Funciones de pertenencia
    tiempo['bajo'] = fuzz.trimf(tiempo.universe, [0, 0, 3])
    tiempo['medio'] = fuzz.trimf(tiempo.universe, [2, 5, 8])
    tiempo['alto'] = fuzz.trimf(tiempo.universe, [6, 10, 10])

    errores['bajo'] = fuzz.trimf(errores.universe, [0, 0, 1])
    errores['medio'] = fuzz.trimf(errores.universe, [1, 3, 5])
    errores['alto'] = fuzz.trimf(errores.universe, [4, 8, 10])

    tareas['bajo'] = fuzz.trimf(tareas.universe, [0, 0, 10])
    tareas['medio'] = fuzz.trimf(tareas.universe, [8, 15, 20])
    tareas['alto'] = fuzz.trimf(tareas.universe, [18, 25, 30])

    nivel['novato'] = fuzz.trimf(nivel.universe, [0, 0, 40])
    nivel['intermedio'] = fuzz.trimf(nivel.universe, [30, 50, 70])
    nivel['experto'] = fuzz.trimf(nivel.universe, [60, 100, 100])

    # Reglas difusas
    rule1 = ctrl.Rule(tiempo['alto'] | errores['alto'], nivel['novato'])
    rule2 = ctrl.Rule(tiempo['medio'] & errores['medio'], nivel['intermedio'])
    rule3 = ctrl.Rule(tiempo['bajo'] & errores['bajo'] & tareas['alto'], nivel['experto'])

    # Crear controlador
    nivel_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
    return ctrl.ControlSystemSimulation(nivel_ctrl)
