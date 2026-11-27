# Matriz de evidencia — Fase III

| ID | Evidencia | Fuente | Estado al preparar los archivos |
|---|---|---|---|
| E01 | Pruebas unitarias locales (9/9) | `evidencias/pruebas_locales.txt` | Ejecutada en entorno de construcción, no GitHub |
| E02 | Validación de 16 consultas y SHA-256 del CSV | `evidencias/pipeline/manifest.json` | Generada fuera del repositorio; repetir en GitHub |
| E03 | Run de GitHub Actions Fase III en verde | Captura y link al run | PENDIENTE tras publicación |
| E04 | Hash del joblib Fase II | Manifiesto generado sobre el repositorio clonado | PENDIENTE: verificar ruta efectiva y existencia |
| E05 | Validación HTTP sobre Fase II | Captura real de /health y /predict | Evidencia histórica de Fase II; repetir solo bajo autorización |
| E06 | Observabilidad: 3 incidentes y alertas | `Actividad8/results`, run #4 y MLflow | Antecedente histórico, no ejecución Fase III |
| E07 | Aprobación y redeploy | Workflow de CD + Render logs | NO ejecutado; requiere consentimiento |
| E08 | Entrevista profesional | MP4 o enlace externo | PENDIENTE de grabación |

Nunca convertir un estado PENDIENTE en verificado sin una ejecución y un registro que lo respalde.
