# Acta de verificacion inicial — CHATBOT CIMA Actividad 8

**Fecha de generacion:** 12 de noviembre de 2026 (fecha de trabajo del proyecto).

## Pruebas ejecutadas por el asistente

- `python -m unittest discover -s tests -v`: **10/10 pruebas correctas**.
- `python -m src.incidentes`: **3 escenarios aislados reproducibles**.
- `python -m src.pipeline --simulado`: genera alertas y dashboard HTML; la segunda ejecucion continua suprime alertas duplicadas durante cooldown.
- `python -m src.drift --referencia ... --actual ...`: **PSI sintetico 2.8689**, clasificacion critica.

## Registro de incidentes de laboratorio

| Incidente | Alerta observada en fase de falla | Recuperacion simulada |
|---|---|---|
| INC-01 - latencia | LATENCIA_P95 | Sí; P95 vuelve a menos de 3,000 ms |
| INC-02 - drift | DRIFT_CRITICO | Sí; distribucion sintetica restaurada |
| INC-03 - API HTTP | SLO_DISPONIBILIDAD y ERRORES_5XX | Sí; errores vuelven a 0 |

**Importante:** Los incidentes y recuperaciones son artificiales y aislados. No se ha ejecutado monitor real sobre el servidor publico, ni configurado un workflow en GitHub del usuario; esas evidencias deben obtenerse despues de publicar y ejecutar los archivos en GitHub/Colab.
