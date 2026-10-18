# CHANGELOG — Actividad 5 / CHATBOT CIMA

## [a5-v1.2] — Cierre experimental y evidencia exportada (2026-10-18)
- Se actualizó `fuentes/train.py` para utilizar seguimiento MLflow mediante SQLite (`mlflow.db`), eliminando referencias al backend `mlruns` de la configuración anterior.
- Se incorporó el notebook ejecutado con corrección de consulta/exportación de MLflow.
- Se agregaron los resultados observados: Regresión Logística (F1 macro 1.0000; cero falsas elegibilidades) y LinearSVC (F1 macro 0.9020; una falsa elegibilidad).
- Se incorporaron la base de datos MLflow, copias de artefactos y los dos modelos en formato nativo `MLmodel`.
- Se incorporó `informe_tecnico.pdf`, comparaciones, gráficas y matrices de confusión.
- Limitaciones: conjunto sintético, prueba de 26 ejemplos, solo dos ejemplos `AMBIGUA` y rutas originales de MLflow no portables directamente.

## [a5-v1.1] — Entrenamiento y trazabilidad
- Se implementaron TF-IDF + Regresión Logística y TF-IDF + LinearSVC con GridSearchCV de cuatro pliegues estratificados.
- Se registraron parámetros, métricas, artefactos y modelos de ambas ejecuciones mediante MLflow.
- Se registraron F1 macro, accuracy, precision, recall, ROC-AUC OvR y falsa elegibilidad.

## [a5-v1.0] — Preparación de datos
- Se incorporó una copia íntegra del dataset sintético original (160 consultas).
- Se crearon funciones de limpieza, normalización de texto y verificación de etiquetas.
- Se eliminaron 32 duplicaciones de texto (128 formulaciones únicas), manteniendo original inalterado.
- Se generó partición estratificada de 102 ejemplos de entrenamiento y 26 de prueba (semilla `20261015`).
- Se documentaron 6 textos compartidos entre particiones históricas de la Actividad 4; esas particiones no se reutilizaron.
- Se conservaron gráficas exploratorias, hashes SHA-256 y `resumen_preparacion.json`.
