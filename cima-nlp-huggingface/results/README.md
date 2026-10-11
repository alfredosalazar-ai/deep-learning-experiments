
# Resultados experimentales — CHATBOT CIMA

## Tercera evaluación: ajuste final zero-shot

Esta carpeta contiene los resultados reales obtenidos mediante
Google Colab con GPU Tesla T4.

Se compararon tres modelos preentrenados:

- XLM-RoBERTa XNLI
- mDeBERTa-v3 XNLI
- BART-large MNLI

La evaluación se realizó sobre 140 consultas sintéticas.

## Resultados principales

| Modelo | Accuracy | F1 macro | Falsa elegibilidad |
|---|---:|---:|---:|
| BART MNLI | 80.71 % | 0.7936 | 17.14 % |
| mDeBERTa XNLI | 58.57 % | 0.5764 | 13.33 % |
| XLM-R XNLI | 54.29 % | 0.5454 | 35.24 % |

## Interpretación

BART obtuvo el mejor resultado global en la tercera
ejecución, aunque mantiene errores de clasificación
que impiden utilizarlo como único control de elegibilidad.

El experimento se considera exploratorio y no demuestra
viabilidad productiva.

## Archivos

- metrics.csv: métricas de desempeño y latencia.
- predictions.csv: predicciones individuales.
- thresholds.csv: análisis de umbrales.
- run_metadata.json: configuración y entorno de ejecución.
- Archivos PNG: gráficas y matrices de confusión.

## Consideraciones

Los resultados pertenecen exclusivamente a la tercera ejecución.
Las etapas E1 y E2 se documentan en el informe técnico.

El conjunto de evaluación contiene textos repetidos.
Los ajustes de E3 se realizaron después de analizar errores
de la evaluación inicial; por ello no constituyen una
validación independiente.

La decisión final para CHATBOT CIMA debe considerar
las reglas de negocio, la calidad de la información y
la supervisión humana.
