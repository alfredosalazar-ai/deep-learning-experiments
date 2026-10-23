# CHATBOT CIMA — Actividad 6

**Evaluación, validación y ajuste de decisiones para modelos NLP supervisados**

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alfredosalazar-ai/deep-learning-experiments/blob/main/Actividad6/fuentes/CIMA_Actividad6_Evaluacion_Validacion.ipynb)

## Propósito

Evaluación y validación complementaria de los clasificadores de la Actividad 5. El análisis incluye matrices de confusión, métricas por clase, ROC/AUC, baseline, validación cruzada, umbral de decisión, comparación estadística pareada y simulación offline de políticas A/B.

## Alcance y decisiones metodológicas

- Los datos son sintéticos; no incluyen movimientos bancarios reales.
- Se conservan los 26 registros de prueba de Actividad 5 y los modelos `.joblib` originales.
- Los modelos de Actividad 5 se utilizan congelados para las predicciones de prueba.
- La validación cruzada OOF de cuatro pliegues evalúa configuraciones fijadas en Actividad 5. Esta actividad no vuelve a realizar GridSearch.
- La selección del umbral usa predicciones y puntuaciones OOF de entrenamiento. La prueba reservada no se utiliza para elegirlo.
- La regla de umbral permite el flujo `INDIVIDUAL` si el modelo ya predice esa clase y el score rebasa el umbral OOF elegido para maximizar verdaderos positivos con cero falsas elegibilidades OOF. Los demás casos se envían a revisión manual.
- En Regresión Logística el score es una probabilidad estimada. En LinearSVC es un margen de decisión, no una probabilidad calibrada; los umbrales son específicos para cada modelo y no son comparables directamente.
- La comparación A/B es una simulación offline, pareada y retrospectiva, no un experimento real aleatorizado con usuarios.
- La prueba es pequeña (26 casos) y solo contiene dos ejemplos `AMBIGUA`; el análisis es exploratorio y no demuestra preparación para producción.

## Estructura

```text
Actividad6/
├── datos/
│   ├── datos_ini/
│   ├── datos_limp/
│   └── DICCIONARIO_DATOS.md
├── modelos/
│   ├── Regresion_Logistica.joblib
│   └── LinearSVC.joblib
├── fuentes/
│   ├── CIMA_Actividad6_Evaluacion_Validacion.ipynb
│   └── evaluacion.py
├── resultados/
│   └── referencia_actividad5/
├── informe/
├── evidencias/
├── requirements.txt
├── README.md
└── CHANGELOG.md
```

## Ejecución en Google Colab

Cuando la carpeta `Actividad6/` esté publicada en la rama `main`, abre el notebook con el botón **Open in Colab** de arriba. También puedes abrirlo directamente desde GitHub. El notebook clona el repositorio, instala las dependencias compatibles, ejecuta `fuentes/evaluacion.py`, muestra los CSV y gráficas, y permite descargar los resultados de la sesión.

Para la primera ejecución anterior a la publicación, se puede cargar el ZIP de preparación que contiene esta carpeta `Actividad6/`.

## Ejecución opcional desde Python

Desde la carpeta `Actividad6/`:

```bash
pip install -r requirements.txt
python fuentes/evaluacion.py
```

## Salidas creadas por la ejecución

- `resultados/metricas_actividad6.csv`
- `resultados/validacion_cruzada.csv`
- `resultados/analisis_umbrales.csv`
- `resultados/predicciones_actividad6.csv`
- `resultados/metricas_por_clase.csv`
- `resultados/comparacion_estadistica.csv`
- `resultados/simulacion_ab_politicas.csv`
- `resultados/metadatos_actividad6.json`
- `resultados/graficas/`: matrices, curvas ROC y comparación de CV
- `resultados/reportes/`: reportes de clasificación JSON
