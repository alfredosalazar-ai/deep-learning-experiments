# CHATBOT CIMA — Runbooks de incidentes (Actividad 8)

**Ámbito:** laboratorio académico, datos sintéticos; no autorización para operar sistemas reales.

## Matriz de severidad

| Nivel | Activación | Decisión segura | Responsable simulado |
|---|---|---|---|
| P0 | Falsa elegibilidad observada con etiqueta comprobada | Detener aceptación automática en laboratorio; revisión humana | Responsable de modelo |
| P1 | Disponibilidad <99%, 5xx >1% o PSI >=0.25 | Activar contingencia y revisar logs | Responsable de servicio |
| P2 | P95 >3000 ms o PSI >=0.10 | Diagnóstico y vigilancia; evitar alertas repetidas | Analista |

### RB-01 — Fallas de API / indisponibilidad
1. Confirmar estado del servicio mediante `/health` y el registro HTTP.
2. Verificar si es arranque en frío de Render Free; no confundir con una caída permanente.
3. Revisar errores HTTP, número de solicitudes y ventana de evaluación.
4. En simulación: aplicar contingencia, reintentos limitados y restaurar el servicio ficticio.
5. Comparar antes/durante/después y registrar duración e identificación del incidente.
6. Un rollback real requiere autorización y pipeline seguro; **este prototipo no ejecuta rollback en Render**.

### RB-02 — Latencia elevada
1. Identificar P95 y cantidad de mediciones; descartar muestras de arranque en frío de la latencia de instancia activa.
2. Revisar dependencia, saturación y tasas de error.
3. En el laboratorio: retirar la latencia artificial o limitar la carga simulada.
4. Volver a medir; cerrar únicamente si el indicador retorna al SLO.

### RB-03 — Drift / comportamiento anómalo
1. Inspeccionar PSI, tamaños muestrales y distribución de las cuatro clases.
2. Verificar si el cambio proviene del origen sintético o de un sesgo del muestreo.
3. En simulación: desactivar aceptación automática y escalar los casos a revisión.
4. Restablecer la distribución simulada de referencia; comprobar desaparición de la alerta.
5. Con etiquetas nuevas, estimar precisión, recall, F1 por clase y falsas elegibilidades; **PSI no mide precisión**.
6. No efectuar reentrenamiento automático sin aprobación y validación independiente.

## Registro mínimo de incidente
Identificador; inicio UTC; SLO afectado; indicador antes/durante/después; código de alerta; decisión; evidencia; cierre o escalamiento; responsable. No registrar textos sensibles.

## Automatizaciones implementadas y pendientes
**Implementadas:** detección por umbrales, prioridad P0/P1/P2, cooldown de 30 min, archivo JSON de alertas, dashboard HTML estático, simulación y comprobación de recuperación. **No implementadas:** notificaciones externas, intervención automática de Render, rollback de imagen o reentrenamiento real. Éstas requieren permisos y entorno controlado.

## Evidencia automatizada del laboratorio (iteración 2)

El comando `python -m src.laboratorio` ejecuta tres runbooks sobre **variables locales ficticias**, con tres verificaciones registradas por incidente: detección, acción sobre estado aislado y recuperación de los valores sintéticos. Produce:

- `results/incidentes/runbooks_ejecutados_demo.json`: bitácora de cada runbook, estado durante el incidente y estado final.
- `results/incidentes/consola_alertas_demo.txt`: alertas P1/P2, umbrales, acciones y resultado.
- Demostración antirruido: una alerta a T+0 se emite, la misma a T+2 minutos se suprime, y reaparece a T+31 minutos.
- `results/metricas/calidad_demo.json`: deterioro **fabricado** de accuracy/F1 calculado sobre 32 etiquetas ficticias; no es un ensayo del modelo desplegado.

El script escribe un archivo JSON dentro de `Actividad8/results/`. **No** reinicia una API, no crea tickets externos, no manda correos ni ejecuta rollback o reentrenamiento. Una recuperación simulada significa que el estado ficticio retornó a sus valores normales y desaparecieron las alertas, no que se restauró un servicio real.
