# 🎯 Cómo Funciona la Clasificación en Tiempo Real

## ✅ SÍ, el sistema te clasificará cuando simules ser un usuario

El sistema está configurado para **clasificarte automáticamente** mientras interactúas con la interfaz. Aquí te explico cómo funciona:

## 🔄 Flujo de Clasificación Automática

### 1. **Inicio del Sistema**
- Si no hay datos → Muestra **Interfaz Original**
- Si hay datos → Evalúa con lógica difusa y muestra la interfaz correspondiente

### 2. **Registro de Eventos en Tiempo Real**
Cada vez que realizas una acción, se registra automáticamente:

#### Acciones que se registran:
- ✅ **Agregar producto al carrito** → `agregar_producto_carrito`
- ✅ **Eliminar producto** → `eliminar_producto_carrito`
- ✅ **Aumentar cantidad** → `aumentar_cantidad`
- ✅ **Disminuir cantidad** → `disminuir_cantidad`
- ✅ **Ir a pago** → `ir_a_pago`
- ✅ **Finalizar compra** → `compra_finalizada`
- ✅ **Cualquier click en botones** → Se registra automáticamente
- ✅ **Carga de página** → `carga_pagina`

### 3. **Clasificación Automática**
Después de **cada evento registrado**:
1. Se actualizan las métricas (tiempo promedio, errores, tareas)
2. Se ejecuta la **lógica difusa** con las reglas originales
3. Se calcula el nivel (0-100)
4. Se determina la interfaz (Novato/Intermedio/Experto)
5. Si cambia el nivel → Se redirige automáticamente a la nueva interfaz

### 4. **Actualización del CSV**
- El nivel clasificado se guarda en `data/dataset_pos.csv`
- Las métricas se actualizan en tiempo real
- El sistema mantiene un historial de tus acciones

## 📊 Métricas que se Rastrean

### Tiempo Promedio por Acción
- Se mide el tiempo que tardas en realizar cada acción
- Se calcula un promedio ponderado
- Rango: 0-10 segundos

### Errores de Sesión
- Acciones fallidas (botones deshabilitados, intentos inválidos)
- Rango: 0-10

### Tareas Completadas
- Acciones exitosas (agregar producto, ir a pago, etc.)
- Rango: 0-30

## 🎯 Ejemplo de Clasificación en Tiempo Real

### Escenario 1: Usuario Novato
```
1. Agrega producto → Tiempo: 8s, Éxito: ✓
2. Sistema evalúa → Nivel: 25 → Interfaz: Novato
3. Agrega otro producto → Tiempo: 7s, Éxito: ✓
4. Sistema evalúa → Nivel: 28 → Interfaz: Novato (mantiene)
5. Intenta cobrar sin productos → Error: ✗
6. Sistema evalúa → Nivel: 22 → Interfaz: Novato (mantiene)
```

### Escenario 2: Usuario que Mejora
```
1. Agrega producto → Tiempo: 8s, Éxito: ✓ → Nivel: 25 (Novato)
2. Agrega producto → Tiempo: 5s, Éxito: ✓ → Nivel: 35 (Novato)
3. Agrega producto → Tiempo: 3s, Éxito: ✓ → Nivel: 42 (Intermedio) 🔄
4. Va a pago → Tiempo: 2s, Éxito: ✓ → Nivel: 48 (Intermedio)
5. Finaliza compra → Tiempo: 1s, Éxito: ✓ → Nivel: 55 (Intermedio)
```

### Escenario 3: Usuario Experto
```
1. Agrega producto → Tiempo: 2s, Éxito: ✓ → Nivel: 45 (Intermedio)
2. Agrega producto → Tiempo: 1.5s, Éxito: ✓ → Nivel: 52 (Intermedio)
3. Agrega producto → Tiempo: 1s, Éxito: ✓ → Nivel: 58 (Intermedio)
4. Va a pago → Tiempo: 0.8s, Éxito: ✓ → Nivel: 65 (Intermedio)
5. Finaliza compra → Tiempo: 0.5s, Éxito: ✓ → Nivel: 72 (Experto) 🔄
```

## 🔍 Cómo Verificar la Clasificación

### 1. **Consola del Navegador**
Abre la consola del navegador (F12) y verás:
```
[TRACKER] Sistema de tracking inicializado
[TRACKER] agregar_producto_carrito - 0.15s - OK
[TRACKER] Evento registrado. Nivel: 35.2, Interfaz: novato
```

### 2. **Consola del Servidor**
En la terminal donde corre Flask, verás:
```
[LOG] agregar_producto_carrito | Tiempo: 0.15s | Errores: 0 | Tareas: 1 | ✓
🧠 EVALUACIÓN DEL USUARIO
📊 MÉTRICAS ACUMULADAS (1 eventos):
   • Tiempo Promedio: 0.15s
   • Errores: 0
   • Tareas Completadas: 1
✅ Evaluación con lógica difusa (1 eventos)
🎯 RESULTADO DE CLASIFICACIÓN:
   • Nivel Difuso: 35.20 / 100
   • Interfaz Asignada: Novato → Interfaz simplificada
   • Confianza: Baja (pocos datos) (1 eventos)
```

### 3. **Archivo CSV**
Revisa `data/dataset_pos.csv`:
```csv
SesionID,TiempoPromedioAccion(s),ErroresSesion,TareasCompletadas,NivelClasificado
S_ACTUAL,2.5,1,5,Intermedio
```

## 🚀 Para Probar el Sistema

### Paso 1: Iniciar el Sistema
```bash
python app.py
```

### Paso 2: Acceder a la Interfaz
- Abre `http://localhost:5000`
- Si es la primera vez → Verás la **Interfaz Original**

### Paso 3: Simular Acciones de Usuario
1. **Agrega productos** al carrito (click en productos)
2. **Elimina productos** del carrito
3. **Aumenta/disminuye cantidades**
4. **Intenta ir a pago**
5. **Finaliza una compra**

### Paso 4: Observar la Clasificación
- **Abre la consola del navegador** (F12) para ver los eventos
- **Revisa la terminal** donde corre Flask para ver la evaluación
- **Verifica el CSV** para ver las métricas acumuladas

## 📈 Progresión Esperada

### Novato → Intermedio
- Necesitas: ~5-10 acciones exitosas
- Tiempo promedio: < 5 segundos
- Errores: < 3

### Intermedio → Experto
- Necesitas: ~15-20 acciones exitosas
- Tiempo promedio: < 3 segundos
- Errores: < 2
- Tareas completadas: > 15

## ⚠️ Notas Importantes

1. **Primera vez**: Si no hay datos, verás la interfaz original
2. **Eventos mínimos**: Necesitas al menos 1 evento para que se active la clasificación
3. **Confianza**: Con pocos eventos (< 5), la confianza es baja
4. **Cambios automáticos**: Si tu nivel cambia, verás una notificación y serás redirigido
5. **Persistencia**: Tus métricas se guardan en el CSV y persisten entre sesiones

## 🎮 Simulación Rápida

Para probar rápidamente, puedes:

1. **Resetear el sistema**: `http://localhost:5000/reset`
2. **Agregar productos rápidamente** (simula usuario experto)
3. **Agregar productos lentamente** (simula usuario novato)
4. **Hacer errores** (click en botones deshabilitados, etc.)

El sistema te clasificará automáticamente según tu comportamiento! 🎯












