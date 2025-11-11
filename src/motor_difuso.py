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

    # ========== REGLAS DIFUSAS ORIGINALES (MANTENIDAS) ==========
    # Regla 1: Tiempo alto O errores altos → Novato
    rule1 = ctrl.Rule(tiempo['alto'] | errores['alto'], nivel['novato'])
    
    # Regla 2: Tiempo medio Y errores medios → Intermedio
    rule2 = ctrl.Rule(tiempo['medio'] & errores['medio'], nivel['intermedio'])
    
    # Regla 3: Tiempo bajo Y errores bajos Y tareas altas → Experto
    rule3 = ctrl.Rule(tiempo['bajo'] & errores['bajo'] & tareas['alto'], nivel['experto'])
    
    # ========== REGLAS ADICIONALES PARA MEJORAR CLASIFICACIÓN ==========
    # Estas reglas complementan las originales para casos más específicos
    
    # Regla 4: Tiempo bajo + pocos errores + muchas tareas medias = Experto
    rule4 = ctrl.Rule(tiempo['bajo'] & errores['bajo'] & tareas['medio'], nivel['experto'])
    
    # Regla 5: Tiempo medio + pocos errores + tareas medias = Intermedio
    rule5 = ctrl.Rule(tiempo['medio'] & errores['bajo'] & tareas['medio'], nivel['intermedio'])
    
    # Regla 6: Tiempo bajo + errores medios + tareas altas = Intermedio
    rule6 = ctrl.Rule(tiempo['bajo'] & errores['medio'] & tareas['alto'], nivel['intermedio'])
    
    # Regla 7: Tiempo alto + errores bajos = Novato (lento pero preciso, aún novato)
    rule7 = ctrl.Rule(tiempo['alto'] & errores['bajo'], nivel['novato'])
    
    # Regla 8: Tiempo medio + errores altos = Novato (promedio pero muchos errores)
    rule8 = ctrl.Rule(tiempo['medio'] & errores['alto'], nivel['novato'])
    
    # Regla 9: Tiempo bajo + errores bajos + pocas tareas = Intermedio (rápido pero poca experiencia)
    rule9 = ctrl.Rule(tiempo['bajo'] & errores['bajo'] & tareas['bajo'], nivel['intermedio'])
    
    # Regla 10: Tiempo medio + errores bajos + muchas tareas = Intermedio-Experto
    rule10 = ctrl.Rule(tiempo['medio'] & errores['bajo'] & tareas['alto'], nivel['intermedio'])
    
    # Regla 11: Tiempo bajo + errores medios + tareas medias = Intermedio
    rule11 = ctrl.Rule(tiempo['bajo'] & errores['medio'] & tareas['medio'], nivel['intermedio'])
    
    # Regla 12: Tiempo alto + errores medios = Novato (lento y con errores)
    rule12 = ctrl.Rule(tiempo['alto'] & errores['medio'], nivel['novato'])

    # Crear controlador con todas las reglas
    # Las 3 reglas originales son prioritarias, las adicionales refinan la clasificación
    nivel_ctrl = ctrl.ControlSystem([
        rule1, rule2, rule3,  # Reglas originales (mantenidas)
        rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12  # Reglas adicionales
    ])
    return ctrl.ControlSystemSimulation(nivel_ctrl)
