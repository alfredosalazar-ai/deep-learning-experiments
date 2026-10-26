# Deep Learning Experiments

Repositorio de trabajo académico para desarrollar, evaluar y documentar experimentos de aprendizaje automático y procesamiento de lenguaje natural. Los proyectos se organizan por actividad e incluyen notebooks, código fuente, resultados y documentación para facilitar su consulta y reproducción en Google Colab.

> **Alcance:** los experimentos se desarrollan con fines académicos y de evaluación técnica. Los resultados obtenidos con datos sintéticos o muestras reducidas no constituyen evidencia suficiente para autorizar un despliegue productivo.

## Índice de proyectos

| Proyecto | Enfoque | Acceso |
|---|---|---|
| **CIMA — Actividad 4** | Comparación experimental de modelos NLP de Hugging Face para clasificar consultas operativas de CHATBOT CIMA. | [Abrir carpeta](./cima-nlp-huggingface/) |
| **CHATBOT CIMA — Actividad 5** | Preparación de datos, clasificación supervisada, ajuste de hiperparámetros y trazabilidad experimental con MLflow. | [Abrir carpeta](./Actividad5/) |
| **CHATBOT CIMA — Actividad 6** | Evaluación y validación de modelos: métricas, matrices de confusión, ROC/AUC, baseline, validación cruzada, umbrales y comparación estadística. | [Abrir carpeta](./Actividad6/) · [Abrir en Colab](https://colab.research.google.com/github/alfredosalazar-ai/deep-learning-experiments/blob/main/Actividad6/fuentes/CIMA_Actividad6_Evaluacion_Validacion.ipynb) |

## Cómo empezar

1. Selecciona la carpeta de la actividad que deseas revisar.
2. Lee su `README.md` antes de ejecutar código; ahí se describen el alcance, las dependencias, las rutas de datos y las limitaciones conocidas.
3. Abre el notebook indicado desde GitHub con **Open in Colab** o utiliza el enlace de Colab incluido en la documentación de cada proyecto.
4. Ejecuta las celdas en orden. Algunas salidas se generan durante la ejecución y no se consideran resultados validados si no existe evidencia de la corrida.
5. Consulta los archivos de `resultados/` y `informe/` para revisar métricas, visualizaciones y conclusiones de cada experimento.

## Estructura del repositorio

```text
deep-learning-experiments/
├── README.md
├── cima-nlp-huggingface/   # Actividad 4: experimentos NLP con Hugging Face
├── Actividad5/             # Preparación, entrenamiento y seguimiento de modelos
└── Actividad6/             # Evaluación, validación y análisis de decisiones
```

Cada actividad mantiene su documentación y artefactos propios. Los resultados de una actividad anterior se conservan como referencia y no deben sobrescribirse con nuevas ejecuciones. Cuando una actividad utilice modelos o datasets de una entrega previa, la documentación específica debe indicar su origen y versión.

## Proyecto CHATBOT CIMA

CHATBOT CIMA es el caso de aplicación utilizado en estas actividades para explorar la clasificación de consultas relacionadas con movimientos y procesos de pago de inmuebles adjudicados. La experimentación considera cuatro categorías:

- `INDIVIDUAL`
- `PAQUETE`
- `AMBIGUA`
- `FUERA_ALCANCE`

Las actividades 5 y 6 utilizan datos sintéticos. En particular, la evaluación de la Actividad 6 trabaja con una prueba reservada pequeña; sus métricas son exploratorias y no demuestran por sí mismas la generalización sobre consultas reales. El modelo candidato y cualquier política de umbral requieren supervisión humana, validaciones deterministas y evidencia adicional antes de considerar un uso operativo.

## Reproducibilidad y trazabilidad

- Mantener fijas y documentadas las versiones de dependencias empleadas por cada notebook.
- Conservar la semilla, las particiones del dataset y la identificación de los archivos usados en cada ejecución.
- Separar los datos utilizados para ajustar modelos o umbrales de los datos reservados para evaluación final.
- Registrar métricas, predicciones, gráficas y metadatos como artefactos de una ejecución, evitando editar manualmente los resultados.
- Declarar las limitaciones del dataset, el tamaño de la muestra y cualquier simulación experimental.

## Estructura recomendada por actividad

```text
ActividadN/
├── README.md
├── CHANGELOG.md
├── requirements.txt
├── datos/
├── modelos/      # Cuando aplique
├── fuentes/      # Notebooks y scripts
├── resultados/   # Métricas, predicciones y gráficas generadas
├── informe/      # Reporte técnico
└── evidencias/   # Evidencias solicitadas por la actividad
```

No todas las carpetas aplican a todas las actividades; consulta el README específico de cada una.

## Aviso de uso

El repositorio documenta ejercicios académicos y experimentales. No contiene una autorización para procesar datos bancarios reales ni para automatizar decisiones financieras. No publiques credenciales, tokens, datos personales o información operativa confidencial.

## Navegación

- [Repositorio](https://github.com/alfredosalazar-ai/deep-learning-experiments)
- [Actividad 4 — CIMA NLP con Hugging Face](https://github.com/alfredosalazar-ai/deep-learning-experiments/tree/main/cima-nlp-huggingface)
- [Actividad 5 — CHATBOT CIMA](https://github.com/alfredosalazar-ai/deep-learning-experiments/tree/main/Actividad5)
- [Actividad 6 — CHATBOT CIMA](https://github.com/alfredosalazar-ai/deep-learning-experiments/tree/main/Actividad6)
