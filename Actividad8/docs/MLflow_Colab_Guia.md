# CHATBOT CIMA — Actividad 8 | MLflow desde Google Colab

## Alcance
El notebook registra **simulaciones offline** exportadas por GitHub Actions. No modifica Render, no reentrena ni publica modelos y no demuestra monitoreo continuo.

## Publicación en GitHub
Actualizar **la misma carpeta** `Actividad8`: subir `src/mlflow_registro.py`, `notebooks/CIMA_Actividad8_MLflow_Colab.ipynb`, `docs/MLflow_Colab_Guia.md`, y reemplazar `Actividad8/README.md`. No duplicar `Actividad8` ni los workflows. No publicar capturas antes de ejecutar el experimento.

## Ejecución en Google Colab (CPU)
1. Descargar `cima-a8-simulacion.zip` de la última ejecución verde de GitHub Actions (artifacts).
2. Abrir el notebook de MLflow desde el repositorio en Colab.
3. Ejecutar celdas 1–2: instalar MLflow y descargar código de GitHub.
4. Celda 3: subir el ZIP, sin descomprimir.
5. Celda 4: registrar **5 runs** en MLflow (3 incidentes, 1 calidad ficticia y 1 alertas/runbooks).
6. Celdas 5–6: capturar runs, evolución de latencia, calidad ficticia y artefactos.
7. Celda 7: descargar respaldo del almacén de MLflow y resumen JSON antes de cerrar Colab.

Los argumentos `--workflow-run 4` y `--commit c0d6991` se basan en la ejecución de GitHub mostrada en la conversación; modificarlos si cambia la ejecución. El script identifica la evidencia fuente mediante SHA-256.

## Estructura propuesta de evidencias, una vez ejecutado

```text
Actividad8/evidencias/mlflow/
  01_experimento_runs.png
  02_incidente_latencia.png
  03_calidad_simulada.png
  04_artefactos_runbooks.png
  resumen_registro_mlflow.json
```

## Interpretación y advertencias
- Los valores 450→7200→520 ms, PSI 0→2.869→0, y fallas HTTP 0→20→0 son **simulados**.
- Accuracy 87.50→68.75 % y F1 macro 88.09→69.68 % se calcularon con **32 pares ficticios**, no con consultas nuevas realizadas al modelo.
- El archivo `alertas_demo.json` puede registrar **cinco alertas suprimidas** porque el estado de deduplicación persistió dentro del laboratorio original; la comprobación antirruido independiente reporta 1 emisión inicial, 0 tras dos minutos y 1 después de 31 minutos.
- El notebook demuestra tracking de parámetros, métricas y artefactos; **no implementa trazas distribuidas reales** del backend ni registro de modelo en MLflow.
- Colab es temporal: respalda los runs antes de cerrar. No cargar datos bancarios ni claves.

Fuentes: https://mlflow.org/docs/latest/tracking/ y https://github.com/alfredosalazar-ai/deep-learning-experiments
