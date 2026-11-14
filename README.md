# Deep Learning Experiments

Repositorio de trabajo académico para desarrollar, evaluar, desplegar y documentar experimentos de aprendizaje automático, procesamiento de lenguaje natural y observabilidad de sistemas de inteligencia artificial. Las actividades se organizan de manera independiente, con código, notebooks, resultados y evidencias verificables, privilegiando la ejecución en **Google Colab, GitHub Actions y servicios en la nube**.

> **Alcance:** los proyectos son prototipos académicos. Las métricas obtenidas con datos sintéticos, conjuntos reducidos o simulaciones offline **no acreditan desempeño productivo** ni autorizan decisiones financieras o tratamiento de datos bancarios reales.

## Índice de proyectos

| Proyecto | Propósito y entregables principales | Acceso |
|---|---|---|
| **CIMA — Actividad 4** | Comparación exploratoria de modelos NLP de Hugging Face para clasificación de consultas. | [Carpeta](./cima-nlp-huggingface/) |
| **CHATBOT CIMA — Actividad 5** | Preparación de datos sintéticos, clasificación supervisada, selección de modelos y trazabilidad de experimentos con MLflow. | [Carpeta](./Actividad5/) |
| **CHATBOT CIMA — Actividad 6** | Evaluación de Regresión Logística y LinearSVC mediante métricas por clase, validación cruzada, ROC/AUC, umbrales y comparación estadística. | [Carpeta](./Actividad6/) · [Colab](https://colab.research.google.com/github/alfredosalazar-ai/deep-learning-experiments/blob/main/Actividad6/fuentes/CIMA_Actividad6_Evaluacion_Validacion.ipynb) |
| **CHATBOT CIMA — Fase II** | API FastAPI, interfaz web, modelo supervisado, Docker, pruebas automatizadas con GitHub Actions y despliegue académico en Render. | [Carpeta](./FaseII/) · [Interfaz](https://chatbot-cima-fase2.onrender.com/) · [Swagger](https://chatbot-cima-fase2.onrender.com/docs) |
| **CHATBOT CIMA — Actividad 8** | Observabilidad, SLO y presupuestos de error, alertas, drift, simulaciones de incidentes, runbooks y registro de evidencias en MLflow. | [Carpeta](./Actividad8/) · [Notebook MLflow en Colab](https://colab.research.google.com/github/alfredosalazar-ai/deep-learning-experiments/blob/main/Actividad8/notebooks/CIMA_Actividad8_MLflow_Colab.ipynb) |
| **CHATBOT CIMA — Actividad 9** | Rediseño de escalabilidad vertical y horizontal, evaluación FinOps, auditoría de gobernanza y plan de escalamiento responsable. Incluye informe Word, anexo Excel y diagramas. | [Carpeta](./Actividad9/) · [Reporte](./Actividad9/Actividad_9_Analisis_Escalabilidad_FinOps_Gobernanza_CHATBOT_CIMA_Alfredo_Salazar.docx) · [Anexo](./Actividad9/Anexo_Tecnico_FinOps_CIMA_Actividad9.xlsx) |

## Evolución de CHATBOT CIMA

CHATBOT CIMA es el caso de estudio utilizado para clasificar consultas relacionadas con movimientos y procesos de pago de inmuebles adjudicados. Distingue cuatro intenciones:

`INDIVIDUAL` · `PAQUETE` · `AMBIGUA` · `FUERA_ALCANCE`

El alcance inicial se limita a **identificar y encaminar consultas**. La clasificación no confirma depósitos, no autoriza pagos y no sustituye las validaciones deterministas ni la revisión humana.

| Etapa | Resultado documentado | Alcance de la evidencia |
|---|---|---|
| Actividad 4 | Comparación de modelos preentrenados de NLP. | Experimentos exploratorios con consultas sintéticas. |
| Actividad 5 | Pipeline TF-IDF + modelos supervisados y artefactos de entrenamiento. | Desarrollo de modelos con datos sintéticos. |
| Actividad 6 | En prueba reservada de **26 consultas**, Regresión Logística obtuvo **accuracy 1.0000** y LinearSVC **0.9615**. | Muestra pequeña; resultados **no generalizables automáticamente**. |
| Fase II | API y frontend publicados; `/health` reportó servicio y modelo disponibles; pruebas web y API documentadas. | Despliegue académico funcional, con discrepancias de clasificación y política conservadora de revisión humana. |
| Actividad 8 | GitHub Actions completó simulaciones offline de incidentes; **cinco runs MLflow** registrados como `FINISHED`. | Evidencia de laboratorio, **no monitoreo continuo de Render**. |
| Actividad 9 | Propuesta documentada de escalabilidad y optimización FinOps; auditoría de riesgos y plan de gobernanza y escalamiento responsable. | **Análisis prospectivo**, no implementación ni certificación. Costos y cargas modelados con supuestos. |

### Resultados visibles — Actividad 8

Las siguientes métricas pertenecen a **escenarios simulados** y permiten comprobar la lógica de alertamiento y recuperación:

| Incidente | Condición normal | Condición de alerta | Recuperación simulada |
|---|---:|---:|---:|
| INC-01 · Latencia P95 | 450 ms | 7,200 ms | 520 ms |
| INC-02 · Drift PSI | 0.000 | 2.869 | 0.000 |
| INC-03 · Tasa HTTP 5xx | 0 % | 20 % | 0 % |

**Control antirruido:** primera detección, 1 alerta emitida; repetición a los 2 minutos, 1 suprimida; detección a los 31 minutos, 1 nueva emisión. Ventana de supresión de 30 minutos.

**Calidad predictiva ficticia:** accuracy de 87.50 % a 68.75 % y F1 macro de 88.09 % a 69.68 % en una prueba con 32 pares sintéticos de etiquetas y predicciones. Estos valores **no son métricas del modelo desplegado**.

[Resultados y gráficos de Actividad 8](./Actividad8/README.md) · [Evidencias MLflow](./Actividad8/evidencias/mlflow/) · [Notebook reproducible](./Actividad8/notebooks/CIMA_Actividad8_MLflow_Colab.ipynb)

## Actividad 9 — Escalabilidad, costos y gobernanza

La Actividad 9 estudia cómo evolucionaría CIMA desde un prototipo académico a una solución de mayor capacidad **sin confundir una propuesta arquitectónica con un despliegue ya ejecutado**. El análisis incluye:

| Dimensión | Resultado documentado | Evidencia |
|---|---|---|
| Escalabilidad | Comparación vertical/horizontal, cuellos de botella y arquitectura objetivo por etapas. | [Diagramas actual](./Actividad9/Arquitectura_Actual_CIMA.png) y [propuesta](./Actividad9/Arquitectura_Propuesta_CIMA.png) |
| FinOps | **6 configuraciones** y **3 volúmenes hipotéticos**, con escenarios editables de costo y capacidad. | [Anexo técnico XLSX](./Actividad9/Anexo_Tecnico_FinOps_CIMA_Actividad9.xlsx) |
| Gobernanza y ética | Matriz de riesgos, controles y estrategia de evaluación de fairness; sin afirmar una auditoría empírica de grupos protegidos. | [Reporte técnico](./Actividad9/Actividad_9_Analisis_Escalabilidad_FinOps_Gobernanza_CHATBOT_CIMA_Alfredo_Salazar.docx) |
| Escalamiento responsable | Etapas con puertas de control, métricas de aceptación y revisión humana. | [README de Actividad 9](./Actividad9/README.md) |

**Lectura de resultados:** los precios públicos son referencias de planificación, no cotizaciones; los volúmenes, tiempos de CPU y utilización son **hipótesis de escenario**, no mediciones en Render. Los resultados de fairness por población no están medidos porque el dataset sintético no es apropiado para ese propósito. La recomendación es fortalecer primero la calidad predictiva, controles y seguridad antes de escalar infraestructura o conectar fuentes institucionales.

## Arquitectura y trabajo completamente en la nube

El desarrollo se ha organizado para operar sin instalaciones locales: Google Colab permite ejecutar notebooks; GitHub almacena versiones, documentación y resultados; GitHub Actions realiza pruebas y simulaciones; Render aloja el prototipo FastAPI de Fase II.

La ejecución local de Docker fue sustituida **deliberadamente** por construcción y pruebas en la infraestructura de GitHub Actions, debido a las restricciones de uso del equipo laboral y la ausencia de un equipo personal disponible. Esta decisión está documentada en [Fase II](./FaseII/README.md); **no se presenta como una ejecución local efectuada**.

La Actividad 8 ejecuta pruebas de observabilidad **offline** de manera independiente del servicio público. Los registros MLflow se generan en sesiones temporales de Colab a partir de artefactos del laboratorio; la publicación de resultados en GitHub requiere una exportación explícita. La Actividad 9 es un ejercicio de diseño y análisis, no modifica el servicio de Fase II.

## Cómo consultar y reproducir

1. Entra a la carpeta del proyecto y lee su `README.md` para conocer alcance, dependencias, datos y resultados disponibles.
2. Cuando exista un notebook, utiliza el enlace **Open in Colab** y selecciona el entorno de ejecución indicado en la propia actividad.
3. Ejecuta las celdas en orden y conserva las salidas. Las simulaciones y las métricas derivadas de datos etiquetados deben identificarse por separado.
4. Para pipelines automatizados, revisa la pestaña **Actions** y las evidencias generadas por la ejecución correspondiente.
5. Contrasta tablas y visualizaciones con los artefactos publicados: un workflow en verde confirma que se ejecutó, **no demuestra por sí solo precisión predictiva ni disponibilidad continua**.

## Estructura principal

```text
deep-learning-experiments/
├── README.md
├── .github/
│   └── workflows/              # Validación, pruebas y simulaciones remotas
├── cima-nlp-huggingface/       # Actividad 4 — NLP preentrenado
├── Actividad5/                 # Entrenamiento y MLflow
├── Actividad6/                 # Evaluación estadística y umbrales
├── FaseII/                     # API, frontend, Docker y despliegue
├── Actividad8/                 # Observabilidad, incidentes y MLflow
└── Actividad9/                 # Escalabilidad, FinOps y gobernanza
```

Cada proyecto mantiene sus rutas específicas; no se impone una estructura idéntica a todas las actividades. Se conservan los resultados de etapas anteriores como referencia sin sobrescribirlos con nuevas pruebas.

## Reproducibilidad, trazabilidad y límites

- Documentar dependencias, versión de Python, particiones, semillas y artefactos de cada ejecución cuando apliquen.
- Mantener separados entrenamiento, selección de hiperparámetros, selección de umbrales y evaluación independiente.
- Reportar métricas por clase, incertidumbre estadística y limitaciones cuando la muestra sea pequeña.
- Diferenciar **monitoreo técnico** (disponibilidad, latencia y HTTP 5xx), **calidad predictiva** (requiere etiquetas) y **simulaciones de laboratorio**.
- Registrar incidentes, severidades, condiciones de alerta, runbooks, acciones simuladas y criterios de recuperación.
- No tratar la alerta de drift como prueba automática de deterioro de precisión: requiere análisis adicional.
- No publicar credenciales, datos personales, información bancaria real ni artefactos institucionales no autorizados.

## Documentación y navegación

| Recurso | Enlace |
|---|---|
| Repositorio | [deep-learning-experiments](https://github.com/alfredosalazar-ai/deep-learning-experiments) |
| Actividad 4 | [CIMA NLP Hugging Face](./cima-nlp-huggingface/README.md) |
| Actividad 5 | [Entrenamiento y experimentación](./Actividad5/) |
| Actividad 6 | [Evaluación y validación](./Actividad6/) |
| Fase II | [Despliegue y pruebas](./FaseII/README.md) · [Evidencias](./FaseII/evidencias/) |
| Actividad 8 | [Observabilidad y resultados](./Actividad8/README.md) · [Evidencias MLflow](./Actividad8/evidencias/mlflow/) |
| Actividad 9 | [Rediseño, FinOps y gobernanza](./Actividad9/README.md) · [Reporte Word](./Actividad9/Actividad_9_Analisis_Escalabilidad_FinOps_Gobernanza_CHATBOT_CIMA_Alfredo_Salazar.docx) · [Anexo Excel](./Actividad9/Anexo_Tecnico_FinOps_CIMA_Actividad9.xlsx) |
| Interfaz académica | [CHATBOT CIMA en Render](https://chatbot-cima-fase2.onrender.com/) |
| Documentación API | [Swagger `/docs`](https://chatbot-cima-fase2.onrender.com/docs) |

> **Aviso:** el servicio alojado en Render puede tardar en responder después de un periodo de inactividad debido a las condiciones del plan gratuito. Este repositorio documenta un prototipo académico, no una plataforma bancaria productiva.
