
# Scripts de soporte — CHATBOT CIMA

## Propósito

Esta carpeta documenta los componentes técnicos utilizados
para evaluar tres modelos preentrenados de Hugging Face
mediante clasificación zero-shot.

## Implementación

La implementación principal se encuentra en:

`../notebooks/CIMA_Comparacion_HuggingFace_Colab.ipynb`

El notebook contiene los procedimientos necesarios para:

- Configurar Google Colab con GPU.
- Instalar las dependencias.
- Cargar el dataset sintético.
- Ejecutar los tres modelos preentrenados.
- Clasificar las solicitudes mediante zero-shot.
- Calcular accuracy, precision, recall y F1-score.
- Medir latencia.
- Generar matrices de confusión y gráficas.
- Evaluar umbrales de confianza.
- Exportar métricas, predicciones y metadatos.

## Reproducibilidad

Los modelos se descargan desde Hugging Face durante la
ejecución. No se almacenan pesos de modelos en GitHub.

El dataset utilizado se encuentra en `../data/`.

Los resultados experimentales se encuentran en `../results/`.

La ejecución original se realizó en Google Colab
utilizando una GPU Tesla T4.

## Alcance

Este prototipo evalúa la clasificación de consultas.
No confirma pagos, no modifica registros financieros y
no sustituye los controles de validación de CHATBOT CIMA.
