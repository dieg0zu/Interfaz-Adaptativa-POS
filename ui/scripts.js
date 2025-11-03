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
            const elemento = e.target.closest('button, .btn, [data-accion], a[href="#"]');
            if (elemento) {
                this.registrarAccion(elemento);
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

        // Registrar evento de carga de página
        this.enviarEvento('carga_pagina', 0.1, true);
    }

    registrarAccion(elemento) {
        const inicio = performance.now();
        const accion = elemento.dataset.accion || 
                      elemento.textContent.trim() || 
                      elemento.getAttribute('aria-label') ||
                      'click';

        // Simular duración de la acción
        setTimeout(() => {
            const duracion = (performance.now() - inicio) / 1000;
            
            // Detectar si fue un error (puedes personalizar esta lógica)
            const esError = elemento.classList.contains('error') || 
                          elemento.closest('.error') !== null;
            
            this.enviarEvento(accion, duracion, !esError);
            
            console.log(`[ACCIÓN] ${accion} - ${duracion.toFixed(2)}s - ${esError ? 'ERROR' : 'OK'}`);
        }, 100);
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
                duracion: duracion,
                exito: exito
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.cambio_interfaz) {
                console.log(`[CAMBIO DETECTADO] Cambiando a interfaz: ${data.interfaz}`);
                this.mostrarNotificacionCambio(data.interfaz);
                setTimeout(() => {
                    window.location.href = `/${data.interfaz}`;
                }, 2000);
            }
        })
        .catch(error => {
            console.error('[ERROR] No se pudo registrar evento:', error);
        });
    }

    verificarCambioInterfaz() {
        // Verificación periódica sin enviar evento
        fetch('/api/evento', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tipo_evento: 'verificacion_periodica',
                duracion: 0,
                exito: true
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.cambio_interfaz) {
                console.log(`[VERIFICACIÓN] Cambio detectado: ${data.interfaz}`);
                window.location.href = `/${data.interfaz}`;
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
        `;
        notificacion.textContent = `🎯 Interfaz adaptada: ${nuevaInterfaz.toUpperCase()}`;
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

// Helpers para tracking manual (opcional)
window.registrarError = function(accion) {
    if (window.tracker) {
        window.tracker.enviarEvento(accion, 0, false);
    }
};

window.registrarExito = function(accion, duracion = 1) {
    if (window.tracker) {
        window.tracker.enviarEvento(accion, duracion, true);
    }
};