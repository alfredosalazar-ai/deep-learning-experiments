# Contenedor reproducible para el backend y el modelo NLP de CIMA.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MODEL_PATH=/app/modelos/Regresion_Logistica.joblib \
    INDIVIDUAL_THRESHOLD=0.276334

WORKDIR /app

# Instalar dependencias antes de copiar el código para aprovechar la caché del build.
COPY requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY backend ./backend
COPY frontend ./frontend
COPY modelos ./modelos

# Render asigna PORT dinámicamente; local y CI usan 8000 si PORT no está definido.
EXPOSE 8000
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
