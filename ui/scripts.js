<script>
let startTime = Date.now();
let errorCount = 0;
let completedTasks = 0;

// Medir tiempo promedio por acción (simulación real)
function registrarAccionCorrecta() {
  completedTasks++;
}

function registrarError() {
  errorCount++;
}

// Ejemplo: Simular tareas o errores
document.querySelectorAll(".boton-tarea").forEach(btn => {
  btn.addEventListener("click", registrarAccionCorrecta);
});

document.querySelectorAll(".boton-error").forEach(btn => {
  btn.addEventListener("click", registrarError);
});

// Enviar métricas al cerrar la sesión
window.addEventListener("beforeunload", () => {
  let tiempoTotal = (Date.now() - startTime) / 1000; // segundos
  let tiempoPromedio = completedTasks > 0 ? tiempoTotal / completedTasks : tiempoTotal;

  fetch("http://localhost:5000/registrar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      tiempo: tiempoPromedio,
      errores: errorCount,
      tareas: completedTasks
    })
  });
});
</script>
