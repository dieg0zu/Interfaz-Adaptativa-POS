def asignar_interfaz(nivel_predicho):
    if nivel_predicho < 40:
        return "Novato → Interfaz simplificada"
    elif 40 <= nivel_predicho < 70:
        return "Intermedio → Interfaz equilibrada"
    else:
        return "Experto → Interfaz avanzada"
