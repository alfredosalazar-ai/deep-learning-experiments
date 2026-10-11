
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alfredosalazar-ai/deep-learning-experiments/blob/main/cima-nlp-huggingface/notebooks/CIMA_Comparacion_HuggingFace_Colab.ipynb)

# CHATBOT CIMA — Comparación de modelos NLP

## Actividad 4 | Gestión de Proyectos de Inteligencia Artificial

Proyecto experimental de Procesamiento de Lenguaje Natural (NLP)
para clasificar consultas operativas asociadas con movimientos
de pago de inmuebles adjudicados.

### Objetivo

Evaluar tres modelos preentrenados de Hugging Face para
identificar si una solicitud corresponde a:

- INDIVIDUAL
- PAQUETE
- AMBIGUA
- FUERA_ALCANCE

### Modelos evaluados

1. XLM-RoBERTa XNLI
2. mDeBERTa-v3 XNLI
3. BART-large MNLI

### Metodología

Los modelos se ejecutaron en Google Colab con GPU,
utilizando clasificación zero-shot y un dataset sintético
de 160 consultas basado en la estructura operativa de CIMA.

Se realizaron tres etapas experimentales:

- E1: evaluación inicial.
- E2: diagnóstico de errores y textos repetidos.
- E3: ajuste exploratorio de las descripciones zero-shot.

### Resultados

En la tercera ejecución, BART obtuvo el mejor F1 macro
(0.7936). Sin embargo, los resultados no justifican
su utilización como mecanismo autónomo de autorización.

### Alcance

Este prototipo clasifica la intención de las consultas.
No confirma pagos, modifica registros ni sustituye
las reglas de validación y supervisión humana de CIMA.

### Datos

El dataset es completamente sintético.
La base maestra Nueva CIE 2.1 no se publica en este repositorio.

### Estado

Experimento académico concluido.
Pendiente de validación con datos independientes y
condiciones operativas reales.
