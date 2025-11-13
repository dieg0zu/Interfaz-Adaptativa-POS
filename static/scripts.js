/**
 * Sistema de Tracking para POS Adaptativo
 * Registra automáticamente las interacciones del usuario
 */

class POSTracker {
    constructor() {
        this.inicioAccion = null;
        this.contadorErrores = 0;
        this.ultimaEvaluacion = Date.now();
        this.intervaloEvaluacion = 30000; // Evaluar cada 30 segundos
        
        this.inicializar();
    }

    inicializar() {
        console.log('[TRACKER] Sistema de tracking inicializado');
        
        // Rastrear todos los botones y acciones
        document.addEventListener('click', (e) => {
            const elemento = e.target.closest('button, .btn, [data-accion], a[href="#"], .product-card, .category-card');
            if (elemento) {
                // No registrar si es un elemento específico que ya tiene su propio tracking
                if (!elemento.hasAttribute('data-tracked')) {
                    this.registrarAccion(elemento);
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

    registrarAccion(elemento) {
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
        
        // Simular duración de la acción (medición real)
        setTimeout(() => {
            const duracion = (performance.now() - inicio) / 1000;
            
            // Detectar si fue un error
            const esError = elemento.classList.contains('error') || 
                          elemento.closest('.error') !== null ||
                          elemento.disabled;
            
            // Solo registrar si la duración es razonable (evitar clicks muy rápidos accidentales)
            if (duracion > 0.05) {
                this.enviarEvento(accion, duracion, !esError);
                console.log(`[TRACKER] ${accion} - ${duracion.toFixed(2)}s - ${esError ? 'ERROR' : 'OK'}`);
            }
        }, 50);
    }

    registrarSubmit(form) {
        const inicio = performance.now();
        const accion = form.id || 'submit_formulario';
        
        // Validar formulario
        const esValido = form.checkValidity();
        const duracion = (performance.now() - inicio) / 1000;
        
        this.enviarEvento(accion, duracion, esValido);
    }

    enviarEvento(tipo, duracion, exito) {
        // Usar fetch para envío asíncrono
        fetch('/api/evento', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tipo_evento: tipo,
                duracion: Math.max(0.1, duracion), // Mínimo 0.1 segundos
                exito: exito
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                // Solo mostrar información si se completó una venta
                if (data.nivel !== null && data.nivel !== undefined) {
                    console.log(`[TRACKER] ✅ Venta completada. Nivel: ${data.nivel}, Interfaz: ${data.interfaz}`);
                    
                    if (data.cambio_interfaz) {
                        console.log(`[CAMBIO DETECTADO] Cambiando a interfaz: ${data.interfaz}`);
                        this.mostrarNotificacionCambio(data.interfaz);
                        setTimeout(() => {
                            window.location.href = `/${data.interfaz}`;
                        }, 2000);
                    } else {
                        console.log(`[TRACKER] Sin cambio de interfaz. Nivel actual: ${data.nivel}`);
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
