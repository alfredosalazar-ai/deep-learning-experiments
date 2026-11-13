# CHATBOT CIMA — Actividad 8 | Observabilidad y respuesta a incidentes

**Estado:** primera versión funcional del laboratorio, no entrega académica final.

## Objetivo

Medir el servicio sintético CIMA ya desplegado, registrar métricas y registros estructurados, calcular SLO, gestionar alertas con control de ruido, detectar cambio de distribución de consultas y simular incidentes con runbooks. **No modifica FaseII, el modelo, Render ni datos institucionales.**

## Arquitectura

`Render (CIMA Fase II) → monitor HTTP bajo demanda (Python) → JSON/JSONL → alertas → dashboard HTML estático`.

El monitor produce registros de eventos con `trace_id` local (correlación de sondeo); no implementa trazado distribuido completo. Para el criterio de trazas de la rúbrica será necesario incorporar trazas reales e identificadores interoperables en una iteración posterior.

## Estructura

- `config/alerts.yaml`: parámetros SLO, umbrales y cooldown.
- `src/monitor.py`: sondeo GET /health y opcional POST /predict con solo cuatro consultas sintéticas.
- `src/alertas.py`, `src/pipeline.py`: reglas de alertas, presupuesto de muestras y deduplicación.
- `src/drift.py`: PSI de cambio en mezcla de categorías, no mide precisión.
- `src/incidentes.py`: tres incidentes **offline simulados** y comprobación de recuperación.
- `src/dashboard.py`: visualización **estática** de último lote; no se presenta como dashboard en tiempo real.
- `docs/Runbooks.md`, `docs/plan_evidencias.md`: respuesta estructurada y matriz de evidencia.
- `tests/`: pruebas `unittest` sin llamadas externas.

## Ejecución 100 % en la nube (Google Colab)

```python
!git clone https://github.com/alfredosalazar-ai/deep-learning-experiments.git
%cd /content/deep-learning-experiments/Actividad8
!pip install -r requirements.txt
!python -m unittest discover -s tests -v
!python -m src.incidentes
!python -m src.pipeline --simulado
```

Para generar **mediciones HTTP reales** en una segunda ejecución (bajo demanda):

```python
!python -m src.monitor --solo-health
!python -m src.pipeline
```

Para la inferencia sintética opcional (cuatro solicitudes como máximo):

```python
!python -m src.monitor --incluye-predict --consultas 4 --health-checks 5
!python -m src.pipeline
```

No añadir un cron que mantenga despierto Render Free. El primer sondeo puede activar el servicio; considerar arranque en frío. El script no introduce latencia ni genera errores deliberados en la API pública.

Los HTML y JSON quedan en `results/`. En Colab descargar o publicar únicamente outputs sintéticos revisados. **No subir archivos con credenciales ni datos operativos reales.**

## Umbrales experimentales

- SLO disponibilidad: `>= 99 %` en la ventana definida.
- SLO fallas HTTP 5xx: `<= 1 %`.
- P95 del POST `/predict`: `<= 3000 ms` con instancia caliente y al menos 5 muestras.
- Falsas elegibilidades: 0 observadas (requiere etiquetas independientes para interpretar).
- PSI de clases: advertencia `>= 0.10`, crítico `>= 0.25`; al menos 30 muestras.
- Antirruido: al menos 10 health checks para alertas de disponibilidad, 30 muestras para drift y cooldown de 30 minutos por código de alerta.

**Limitaciones:** con 3 a 5 comprobaciones no se pueden estimar SLO de disponibilidad. El error budget real exige una ventana de medición explícita y volumen suficiente; el script registra fracciones, pero no afirma cumplimiento mensual. El PSI de clases predichas puede confundir cambio de tráfico con deriva predictiva. La simulación es independiente del servicio vivo. No incluye notificación externa o rollback automático.

## GitHub Actions

Publicar el workflow del paquete en la **raíz del repositorio** como:

`.github/workflows/actividad8-observabilidad.yml`

El pipeline solo ejecuta tests y simulación offline. No consume recursos de Render ni ejecuta pruebas contra una API remota.

## Fuentes y continuidad

- Proyecto: https://github.com/alfredosalazar-ai/deep-learning-experiments
- API académica: https://chatbot-cima-fase2.onrender.com/
- Guía de métricas SLI/SLO: https://sre.google/sre-book/service-level-objectives/
- GitHub Actions: https://docs.github.com/en/actions
- Python urllib: https://docs.python.org/3/library/urllib.request.html
- Detector PSI: indicador de cambio poblacional; su interpretación exige contexto y etiquetado independiente.
