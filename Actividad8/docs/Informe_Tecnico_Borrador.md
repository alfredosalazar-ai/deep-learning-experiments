# Actividad 8 — Diseño y ejecución inicial de observabilidad CIMA

**Estado:** borrador técnico para continuidad. Elaborar informe final Word/PDF al completar ejecuciones y capturas de GitHub Actions / Google Colab.

## 1. Contexto y objetivo
CHATBOT CIMA, prototipo académico, despliega una API FastAPI y un clasificador NLP sobre Render. La Fase II comprobó disponibilidad, integración frontend/backend y controles de entrada, pero no incorporó monitoreo sostenido del servicio ni demostró generalización del modelo. Se incorpora observabilidad no intrusiva para detectar fallas, latencia y variación de tráfico de prueba con datos sintéticos.

## 2. Métricas, logs y trazas
| Dimensión | Indicador | Fuente | Limitación |
|---|---|---|---|
| Disponibilidad | /health 200, `status=ok`, `model_loaded=true` | Sondeo HTTP | Ventana pequeña no estima disponibilidad mensual |
| Rendimiento | Latencia P95 de POST /predict | Sondeo HTTP | Excluye arranque en frío; muestra mínima 5 |
| Errores | Fracción respuestas 5xx | Sondeo HTTP | No identifica errores no observados |
| Operación | Decisión, clase y puntaje | JSON de /predict | Cuatro consultas sintéticas no son conjunto de evaluación |
| Calidad predictiva | Falsas elegibilidades en pruebas etiquetadas | Etiquetas sintéticas externas | Requiere conjunto suficientemente diverso |
| Drift | PSI de mezcla de predicciones | Dos archivos CSV | No mide drift de embeddings ni precisión |
| Logs | JSONL de mediciones, error HTTP, timestamps UTC | Archivo local Colab | No conserva registros privados del servidor |
| Trazas | `trace_id` local de cada sondeo | Archivo local Colab | No hay trazado distribuido completo |

## 3. SLO y error budget
Metas experimentales: disponibilidad >=99%, 5xx <=1%, P95 <=3000 ms, falsa elegibilidad observada igual a 0; PSI >=0.10 advertencia y >=0.25 crítico. En la ventana de disponibilidad: `fallos_permitidos = floor((1-SLO)*total_health)`; `fallos_consumidos = total_health - health_ok`; la tasa mensual requiere un ciclo de seguimiento más amplio y muestras suficientes.

## 4. Alarmas y reducción de ruido
La lógica solo alarma si se supera mínimo de observaciones; severidad P0 (falsa elegibilidad), P1 (indisponibilidad, fallas HTTP, drift crítico), P2 (latencia o drift moderado). Deduplicación por código durante 30 minutos; para cualquier integración futura de notificación se necesitarán credenciales, consentimiento y límites operativos.

## 5. Simulaciones ejecutadas offline
Tres incidentes deterministas con etapas antes/durante/después:

| ID | Indicador inicial | Fallo inyectado | Resultado tras intervención simulada |
|---|---|---|---|
| INC-01 | P95 450 ms | P95 7,200 ms | P95 520 ms, alerta resuelta |
| INC-02 | PSI 0 | Cambio 25/25/25/25 → 1/2/2/95 | PSI 0 al restaurar la distribución |
| INC-03 | Disponibilidad 100%, error 0% | Disponibilidad 80%, 5xx 20% | Recuperación simulada a 100%, 0% |

Estas salidas son **simulaciones artificiales** y no fallas ni recuperaciones de la API pública. La respuesta ejecutable consiste en detección, registro, clasificación, supresión de ruido y generación del dashboard; rollback real, notificación externa y reentrenamiento son propuestas, no implementaciones.

## 6. Limitaciones y próximas acciones
Ejecutar el workflow en GitHub Actions y guardar capturas. Efectuar monitoreo de `/health` y, de ser necesario, cuatro consultas sintéticas en Google Colab. Integrar evidencia con la rúbrica; medir error budget en ventana de observación suficiente, no confundir Render Free con SLA empresarial, agregar trazado distribuido solo si el curso lo exige y sin exponer datos operativos.

## 7. Fuentes
- Universidad Tecmilenio, Actividad 8 y rúbrica de evaluación (material de curso proporcionado).
- Google, *Site Reliability Engineering — Service Level Objectives*: https://sre.google/sre-book/service-level-objectives/
- GitHub, *GitHub Actions Documentation*: https://docs.github.com/en/actions
- Python, *urllib.request*: https://docs.python.org/3/library/urllib.request.html
- Proyecto CIMA: https://github.com/alfredosalazar-ai/deep-learning-experiments
