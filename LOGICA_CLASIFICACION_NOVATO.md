# 📋 Lógica de Clasificación: ¿Cuándo un usuario es NOVATO?

## 🎯 Condiciones para ser NOVATO (según las reglas difusas)

### Regla 1 (Principal): 
**Tiempo ALTO (≥6 segundos) O Errores ALTOS (≥4 errores)** → NOVATO
- Si el usuario tarda ≥6 segundos por acción promedio → NOVATO
- Si el usuario tiene ≥4 errores → NOVATO

### Regla 7:
**Tiempo ALTO (≥6s) Y Errores BAJOS (≤1)** → NOVATO
- Usuario lento pero preciso → Aún es NOVATO

### Regla 8:
**Tiempo MEDIO (2-8s) Y Errores ALTOS (≥4)** → NOVATO
- Usuario promedio pero con muchos errores → NOVATO

### Regla 12:
**Tiempo ALTO (≥6s) Y Errores MEDIOS (1-5)** → NOVATO
- Usuario lento y con algunos errores → NOVATO

## 📊 Rangos de las Variables

### Tiempo Promedio por Acción:
- **BAJO**: 0-3 segundos
- **MEDIO**: 2-8 segundos  
- **ALTO**: 6-10 segundos

### Errores de Sesión:
- **BAJO**: 0-1 errores
- **MEDIO**: 1-5 errores
- **ALTO**: 4-10 errores

### Tareas Completadas:
- **BAJO**: 0-10 tareas
- **MEDIO**: 8-20 tareas
- **ALTO**: 18-30 tareas

## ⚠️ PROBLEMA ACTUAL

Según tu CSV:
- **Tiempo**: 0.22s (BAJO - debería ser ALTO si eres lento)
- **Errores**: 0 (BAJO - debería ser ALTO si haces clicks incorrectos)
- **Tareas**: 54 (ALTO - muchas acciones)

**Resultado**: Se activa la Regla 3 → EXPERTO
- Regla 3: Tiempo BAJO + Errores BAJOS + Tareas ALTAS → EXPERTO

## 🔍 ¿Por qué pasa esto?

1. **Tiempo muy bajo (0.22s)**: El sistema no está detectando correctamente que eres lento
2. **0 errores**: Los clicks incorrectos no se están registrando como errores
3. **Muchas tareas (54)**: Cada acción exitosa cuenta como tarea, aunque sean lentas

## ✅ Para ser NOVATO necesitas:

**Opción 1**: Tiempo ≥6 segundos (lento)
**Opción 2**: Errores ≥4 (muchos clicks incorrectos)
**Opción 3**: Tiempo ≥6s Y Errores ≥1 (lento y con errores)

## 🛠️ Solución

El problema está en:
1. El tiempo no se está calculando correctamente (debería reflejar lentitud)
2. Los errores no se están detectando (clicks incorrectos no se registran)

