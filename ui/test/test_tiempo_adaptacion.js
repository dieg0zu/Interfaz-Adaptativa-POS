document.addEventListener("DOMContentLoaded", () => {
    const visor = document.getElementById("visor");
    const log = document.getElementById("log");
    const btn = document.getElementById("btnStart");

    const repeticiones = 5;

    // RUTAS DE TUS INTERFACES
    const pruebas = [
        {
            nombre: "Original - Nota de venta",
            url: "../interfaz_original.html",
            botonQuery: "#btnNotaVenta",     // AJUSTA con el ID real del botón
            elementoAdaptado: "#ui_adaptada" // elemento visible al cambiar
        },
        {
            nombre: "Original - Comprobante",
            url: "../interfaz_original.html",
            botonQuery: "#btnComprobante",
            elementoAdaptado: "#ui_adaptada"
        },
        {
            nombre: "Novato - Cobrar",
            url: "../interfaz_novato/productos.html",
            botonQuery: "#btnCobrar",
            elementoAdaptado: "#ui_adaptada"
        },
        {
            nombre: "Intermedio - Cobrar",
            url: "../interfaz_intermedio/productos.html",
            botonQuery: "#btnCobrar",
            elementoAdaptado: "#ui_adaptada"
        },
        {
            nombre: "Experto - Nota de venta",
            url: "../interfaz_experto/productos.html",
            botonQuery: "#btnNotaVenta",
            elementoAdaptado: "#ui_adaptada"
        }
    ];

    btn.onclick = () => ejecutarPruebas();

    function escribir(m) { log.textContent += m + "\n"; }

    async function ejecutarPruebas() {
        log.textContent = "";
        escribir("=== TEST DE ADAPTACIÓN INICIADO ===");

        for (const p of pruebas) {
            escribir(`\n--- ${p.nombre} ---`);

            let tiempos = [];

            for (let i = 0; i < repeticiones; i++) {
                const t = await medirAdaptacion(p);
                tiempos.push(t);
                escribir(`  Ciclo ${i+1}: ${t.toFixed(2)} ms`);
                await espera(400);
            }

            const prom = tiempos.reduce((a, b) => a + b) / tiempos.length;
            escribir(`>> PROMEDIO: ${prom.toFixed(2)} ms`);
        }

        escribir("\n=== TEST FINALIZADO ===");
    }

    function espera(ms) {
        return new Promise(res => setTimeout(res, ms));
    }

    function medirAdaptacion(prueba) {
        return new Promise(resolve => {

            // 1. Cargar la UI
            visor.src = prueba.url + "?t=" + Math.random();

            visor.onload = () => {
                const doc = visor.contentDocument;

                const boton = doc.querySelector(prueba.botonQuery);
                if (!boton) {
                    alert(`No se encontró el botón: ${prueba.botonQuery}`);
                    return;
                }

                // 2. Iniciar cronómetro
                const inicio = performance.now();

                // 3. Observar aparición de la interfaz adaptada
                const obs = new MutationObserver(() => {
                    const adaptada = doc.querySelector(prueba.elementoAdaptado);
                    if (adaptada && adaptada.offsetParent !== null) {
                        const fin = performance.now();
                        obs.disconnect();
                        resolve(fin - inicio);
                    }
                });

                obs.observe(doc.body, { childList: true, subtree: true });

                // 4. Ejecutar clic
                boton.click();
            };
        });
    }
});
