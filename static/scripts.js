class POSTracker {
    constructor() {
        this.inicioAccion = null;
        this.contadorErrores = 0;
        this.ultimaEvaluacion = Date.now();
        this.intervaloEvaluacion = 30000; // Evaluar cada 30 segundos
        
        // Tracking de tiempo activo
        this.primerClickTiempo = null; // Timestamp del primer click de la sesión
        this.ultimoClickTiempo = null; // Timestamp del último click
        this.tiempoInactividadMax = 30000; // 30 segundos de inactividad = pausa
        this.tiempoActivoTotal = 0; // Tiempo total activo acumulado
        this.tiempoUltimaAccion = null; // Timestamp de la última acción
        this.tiempoDemoraInicial = 0; // Tiempo de demora desde el primer click hasta la primera acción real
        this.primeraAccionReal = false; // Si ya se registró la primera acción real
        
        this.inicializar();
    }

    inicializar() {
        console.log('[TRACKER] Sistema de tracking inicializado');
        
        // Rastrear TODOS los clicks (no solo elementos específicos)
        // Esto permite detectar clicks incorrectos en áreas vacías
        document.addEventListener('click', (e) => {
            const elemento = e.target;
            
            // Verificar si es un elemento interactivo válido
            const esInteractivoValido = elemento.closest('button') || 
                                       elemento.closest('.btn') || 
                                       elemento.closest('[data-accion]') || 
                                       elemento.closest('a[href]') || 
                                       elemento.closest('.product-card') || 
                                       elemento.closest('.category-card') ||
                                       elemento.closest('[onclick]') ||
                                       elemento.onclick ||
                                       elemento.dataset.accion;
            
            // Si NO es interactivo válido, es un error (click incorrecto)
            if (!esInteractivoValido) {
                // Click en área vacía o elemento no interactivo = ERROR
                this.registrarAccion(elemento, true); // true = es error
            } else {
                // Es un elemento válido, registrar normalmente
                if (!elemento.hasAttribute('data-tracked')) {
                    this.registrarAccion(elemento, false); // false = no es error
                }
            }
        });

        // Rastrear formularios
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                this.registrarSubmit(form);
            });
        });

        // Evaluar periódicamente si necesita cambiar interfaz
        setInterval(() => this.verificarCambioInterfaz(), this.intervaloEvaluacion);

        // Registrar evento de carga de página (solo si hay datos, no en interfaz original)
        const ruta = window.location.pathname;
        if (ruta !== '/original' && ruta !== '/' && !ruta.includes('pago')) {
            this.enviarEvento('carga_pagina', 0.1, true);
        }
    }

    registrarAccion(elemento, esErrorForzado = null) {
        const ahora = Date.now();
        const inicio = performance.now();
        
        // Determinar tipo de acción
        let accion = elemento.dataset.accion;
        
        if (!accion) {
            // Intentar determinar la acción por el contexto
            if (elemento.classList.contains('product-card') || elemento.closest('.product-card')) {
                accion = 'agregar_producto';
            } else if (elemento.classList.contains('category-card') || elemento.closest('.category-card')) {
                accion = 'seleccionar_categoria';
            } else if (elemento.textContent) {
                accion = elemento.textContent.trim().toLowerCase().substring(0, 30);
            } else {
                accion = 'click_generico';
            }
        }
        
        // Detectar si fue un error (mejorado)
        // Si esErrorForzado es null, usar detección automática
        const esError = esErrorForzado !== null ? esErrorForzado : this.detectarError(elemento, accion);
        
        // Gestionar tiempo activo
        if (this.primerClickTiempo === null) {
            // Primer click de la sesión - iniciar tracking
            this.primerClickTiempo = ahora;
            this.ultimoClickTiempo = ahora;
            this.tiempoUltimaAccion = ahora;
            this.tiempoActivoTotal = 0; // Resetear tiempo activo
            this.tiempoDemoraInicial = 0; // Resetear demora inicial
            this.primeraAccionReal = false; // Resetear flag
            console.log(`[TRACKER] 🆕 Sesión iniciada - Primer click registrado`);
        } else {
            // Calcular tiempo desde la última acción
            const tiempoDesdeUltimaAccion = ahora - this.tiempoUltimaAccion;
            
            // Si es la primera acción real después del primer click, capturar el tiempo de demora inicial
            if (!this.primeraAccionReal && tiempoDesdeUltimaAccion > 0) {
                // El tiempo desde el primer click hasta ahora es el tiempo de demora inicial
                this.tiempoDemoraInicial = tiempoDesdeUltimaAccion;
                this.primeraAccionReal = true;
                console.log(`[TRACKER] ⏱️ Tiempo de demora inicial capturado: ${(this.tiempoDemoraInicial / 1000).toFixed(1)}s`);
            }
            
            if (tiempoDesdeUltimaAccion > this.tiempoInactividadMax) {
                // Hubo inactividad (más de 30 segundos), pero SIEMPRE contar el tiempo de demora inicial
                // Solo no contar inactividad entre acciones si ya pasó la primera acción
                if (this.primeraAccionReal) {
                    console.log(`[TRACKER] ⏸️ Inactividad detectada: ${(tiempoDesdeUltimaAccion / 1000).toFixed(1)}s - No contado`);
                }
            } else {
                // Tiempo activo: agregar al total
                this.tiempoActivoTotal += tiempoDesdeUltimaAccion;
            }
            
            this.ultimoClickTiempo = ahora;
            this.tiempoUltimaAccion = ahora;
        }
        
        // Calcular duración de la acción (tiempo real de procesamiento, no tiempo de espera)
        setTimeout(() => {
            const duracionProcesamiento = (performance.now() - inicio) / 1000;
            
            // Calcular tiempo activo desde el primer click hasta ahora (sin períodos de inactividad)
            const tiempoActivoSesion = this.tiempoActivoTotal / 1000; // Convertir a segundos
            
            // Incluir el tiempo de demora inicial en el tiempo activo total para el cálculo
            // Esto asegura que si el usuario se demora mucho al inicio, se refleje en el promedio
            const tiempoActivoConDemora = tiempoActivoSesion + (this.tiempoDemoraInicial / 1000);
            
            // Usar el tiempo de procesamiento de la acción, pero también registrar tiempo activo con demora
            const duracion = Math.max(0.1, duracionProcesamiento);
            
            this.enviarEvento(accion, duracion, !esError, tiempoActivoConDemora);
            console.log(`[TRACKER] ${accion} - ${duracion.toFixed(2)}s - Tiempo activo: ${tiempoActivoSesion.toFixed(1)}s - Demora inicial: ${(this.tiempoDemoraInicial / 1000).toFixed(1)}s - Total: ${tiempoActivoConDemora.toFixed(1)}s - ${esError ? 'ERROR' : 'OK'}`);
        }, 50);
    }
    
    detectarError(elemento, accion) {
        // Detectar errores más agresivamente
        let esError = false;
        
        // Errores obvios
        if (elemento.classList.contains('error') || 
            elemento.closest('.error') !== null ||
            elemento.disabled) {
            esError = true;
        }
        
        // NO considerar error: eliminar producto (es una acción válida)
        if (accion.includes('eliminar') || 
            accion.includes('remove') ||
            elemento.classList.contains('icon-btn') && elemento.textContent.includes('🗑️')) {
            return false; // Eliminar es una acción válida, no un error
        }
        
        // Clicks en lugares incorrectos (elementos sin funcionalidad clara)
        if (accion === 'click_generico') {
            // Verificar si es un elemento realmente interactivo
            const esInteractivo = elemento.closest('button') || 
                                 elemento.closest('.product-card') || 
                                 elemento.closest('.category-card') ||
                                 elemento.closest('a') ||
                                 elemento.closest('[onclick]') ||
                                 elemento.closest('[data-accion]') ||
                                 elemento.onclick ||
                                 elemento.dataset.accion;
            
            if (!esInteractivo) {
                // Click en área vacía o elemento no interactivo = ERROR
                esError = true;
            }
        }
        
        // Clicks en elementos que no deberían ser clickeables (texto, imágenes sin acción, etc.)
        if (elemento.tagName === 'DIV' && 
            !elemento.onclick && 
            !elemento.dataset.accion &&
            !elemento.closest('[onclick]') &&
            !elemento.closest('.product-card') &&
            !elemento.closest('.category-card') &&
            !elemento.closest('button') &&
            !elemento.closest('a')) {
            // Es un div sin funcionalidad = ERROR
            esError = true;
        }
        
        // Clicks en texto plano (p, span, etc.) sin acción asociada
        if ((elemento.tagName === 'P' || elemento.tagName === 'SPAN' || elemento.tagName === 'DIV') &&
            !elemento.closest('button') &&
            !elemento.closest('a') &&
            !elemento.closest('[onclick]') &&
            !elemento.closest('.product-card') &&
            !elemento.closest('.category-card')) {
            esError = true;
        }
        
        return esError;
    }

    registrarSubmit(form) {
        const inicio = performance.now();
        const accion = form.id || 'submit_formulario';
        
        // Validar formulario
        const esValido = form.checkValidity();
        const duracion = (performance.now() - inicio) / 1000;
        
        this.enviarEvento(accion, duracion, esValido);
    }

    enviarEvento(tipo, duracion, exito, tiempoActivoSesion = null) {
        // El tiempo activo se usará en el backend para calcular mejor el tiempo promedio
        // Aquí solo enviamos la duración de la acción individual
        let duracionFinal = Math.max(0.1, duracion);
        
        // Usar fetch para envío asíncrono
        fetch('/api/evento', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tipo_evento: tipo,
                duracion: duracionFinal,
                exito: exito,
                tiempo_activo: tiempoActivoSesion // Enviar tiempo activo para referencia
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                // Solo mostrar información si se completó una venta
                if (data.nivel !== null && data.nivel !== undefined) {
                    console.log(`[TRACKER] ✅ Venta completada. Nivel: ${data.nivel}, Interfaz: ${data.interfaz}`);
                    
                    // Si se completó una venta, SIEMPRE redirigir a la interfaz correcta
                    if (tipo === 'compra_finalizada') {
                        if (data.cambio_interfaz) {
                            console.log(`[CAMBIO DETECTADO] Cambiando a interfaz: ${data.interfaz}`);
                            this.mostrarNotificacionCambio(data.interfaz);
                        } else {
                            console.log(`[TRACKER] Sin cambio de interfaz. Nivel actual: ${data.nivel}, Interfaz: ${data.interfaz}`);
                        }
                        
                        // Resetear tracking para nueva sesión
                        this.resetTracking();
                        
                        // Redirigir a la interfaz correcta (siempre después de completar venta)
                        if (data.redirigir && data.url_redireccion) {
                            setTimeout(() => {
                                window.location.href = data.url_redireccion;
                            }, data.cambio_interfaz ? 600 : 300); // Más rápido si no hay cambio
                        } else if (data.interfaz) {
                            setTimeout(() => {
                                window.location.href = `/${data.interfaz}`;
                            }, data.cambio_interfaz ? 2000 : 1000);
                        }
                    }
                } else {
                    // Evento normal (durante el proceso) - solo registrar sin evaluar
                    console.log(`[TRACKER] Evento registrado: ${tipo} (esperando finalizar venta para evaluar)`);
                }
            } else {
                console.error('[TRACKER] Error al registrar evento:', data.mensaje);
            }
        })
        .catch(error => {
            console.error('[ERROR] No se pudo registrar evento:', error);
        });
    }

    verificarCambioInterfaz() {
        // Verificación periódica - usar /api/estado para no crear eventos
        fetch('/api/estado', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            // Solo verificar si no estamos en la interfaz original o de pago
            const rutaActual = window.location.pathname;
            if (!rutaActual.includes('original') && !rutaActual.includes('pago')) {
                console.log(`[VERIFICACIÓN] Estado actual: Nivel ${data.nivel}, Eventos: ${data.eventos}`);
            }
        })
        .catch(error => {
            console.error('[ERROR] Verificación fallida:', error);
        });
    }

    resetTracking() {
        // Resetear tracking de tiempo activo para nueva sesión
        this.primerClickTiempo = null;
        this.ultimoClickTiempo = null;
        this.tiempoActivoTotal = 0;
        this.tiempoUltimaAccion = null;
        console.log(`[TRACKER] 🔄 Tracking reseteado para nueva sesión`);
    }

    mostrarNotificacionCambio(nuevaInterfaz) {
        const notificacion = document.createElement('div');
        notificacion.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 10000;
            font-family: Arial, sans-serif;
            font-weight: 600;
        `;
        
        const niveles = {
            'novato': 'NOVATO',
            'intermedio': 'INTERMEDIO',
            'experto': 'EXPERTO'
        };
        
        notificacion.textContent = `🎯 Interfaz adaptada: ${niveles[nuevaInterfaz] || nuevaInterfaz.toUpperCase()}`;
        document.body.appendChild(notificacion);

        setTimeout(() => {
            notificacion.remove();
        }, 2000);
    }
}

// Inicializar cuando cargue el DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.tracker = new POSTracker();
    });
} else {
    window.tracker = new POSTracker();
}

// Helpers para tracking manual
window.registrarError = function(accion, duracion = 0) {
    if (window.tracker) {
        window.tracker.enviarEvento(accion, duracion, false);
    }
};

window.registrarExito = function(accion, duracion = 1) {
    if (window.tracker) {
        window.tracker.enviarEvento(accion, duracion, true);
    }
};

// Helper para registrar acciones específicas con tiempo real
window.registrarAccionConTiempo = function(tipo, inicioTiempo, exito = true) {
    if (window.tracker) {
        const duracion = (performance.now() - inicioTiempo) / 1000;
        window.tracker.enviarEvento(tipo, Math.max(0.1, duracion), exito);
    }
};
